from langchain_core.messages import AIMessage

from app.agent import graph


def test_run_agent_returns_friendly_message_when_llm_fails(db, make_user, monkeypatch):
    user = make_user()

    def boom(*args, **kwargs):
        raise RuntimeError("Groq is down")

    monkeypatch.setattr(graph, "build_agent", boom)
    reply, events = graph.run_agent(db, user.id, [("user", "hello")])
    assert reply == graph.FRIENDLY_ERROR
    assert events == []


def test_run_agent_tries_fallback_model(db, make_user, monkeypatch):
    user = make_user()
    tried = []

    class FakeAgent:
        def invoke(self, *args, **kwargs):
            return {"messages": [AIMessage(content="fallback reply")]}

    def fake_build(db, rep_id, model_name=None, events=None):
        tried.append(model_name)
        if len(tried) == 1:
            raise RuntimeError("primary model down")
        return FakeAgent()

    monkeypatch.setattr(graph, "build_agent", fake_build)
    reply, events = graph.run_agent(db, user.id, [("user", "hello")])
    assert reply == "fallback reply"
    assert events == []
    assert len(tried) == 2
    assert tried[0] != tried[1]


def test_run_agent_does_not_retry_after_something_was_saved(db, make_user, monkeypatch):
    user = make_user()
    tried = []

    class FailingAgent:
        def __init__(self, events):
            self.events = events

        def invoke(self, *args, **kwargs):
            self.events.append({"type": "logged", "interaction_id": 1})
            raise RuntimeError("failed after saving")

    def fake_build(db, rep_id, model_name=None, events=None):
        tried.append(model_name)
        return FailingAgent(events)

    monkeypatch.setattr(graph, "build_agent", fake_build)
    reply, events = graph.run_agent(db, user.id, [("user", "hello")])
    assert len(tried) == 1
    assert "check My Interactions" in reply
    assert events == [{"type": "logged", "interaction_id": 1}]