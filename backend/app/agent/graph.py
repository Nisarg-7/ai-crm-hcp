import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr
from sqlalchemy.orm import Session

from groq import RateLimitError

from app.agent.prompts import build_system_prompt
from app.agent.tools import build_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_STEPS = 12
FRIENDLY_ERROR = "Sorry, the assistant is unavailable right now. Please try again, or use the form."

RATE_LIMIT_MESSAGE = "The assistant is busy right now (usage limit reached). Please wait about a minute and try again, or use the Structured Form."


def build_agent(
    db: Session,
    rep_id: int,
    model_name: str | None = None,
    events: list[dict] | None = None,
):
    tools = build_tools(db, rep_id, events)
    llm = ChatGroq(
        model=model_name or settings.groq_model,
        api_key=SecretStr(settings.groq_api_key),
        temperature=0,
        timeout=30,
        max_retries=1,
    ).bind_tools(tools)

    def agent_node(state: MessagesState):
        messages = [SystemMessage(content=build_system_prompt())] + state["messages"]
        return {"messages": [llm.invoke(messages)]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


def _final_text(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content and not message.tool_calls:
            return str(message.content)
    return "I could not produce a reply. Please try again."


def run_agent(
    db: Session, rep_id: int, history: list[tuple[str, str]]
) -> tuple[str, list[dict]]:
    """history is a list of (role, text) pairs. Returns (reply, events)."""
    messages: list[BaseMessage] = [
        HumanMessage(content=text) if role == "user" else AIMessage(content=text)
        for role, text in history
    ]
    rate_limited = False
    for model_name in (settings.groq_model, settings.groq_fallback_model):
        events: list[dict] = []
        try:
            agent = build_agent(db, rep_id, model_name, events)
            result = agent.invoke(
                MessagesState(messages=messages), #type: ignore 
                {"recursion_limit": MAX_STEPS},
            )
            return _final_text(result["messages"]), events
        except GraphRecursionError:
            logger.warning("Agent hit the step limit")
            return (
                "I got stuck on that request. Could you rephrase it or give more detail?",
                events,
            )
        except Exception as err:
            logger.exception("Agent failed with model %s", model_name)
            db.rollback()
            if events:
                # Something was already saved before the failure; don't retry and duplicate it.
                return (
                    "Something went wrong after saving. Please check My Interactions before retrying.",
                    events,
                )
            rate_limited = isinstance(err, RateLimitError)
    return (RATE_LIMIT_MESSAGE if rate_limited else FRIENDLY_ERROR), []