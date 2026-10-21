from app.agent import graph


def test_run_agent_returns_friendly_message_when_llm_fails(db, make_user, monkeypatch):
    user = make_user()

    def boom(*args, **kwargs):
        raise RuntimeError("Groq is down")

    monkeypatch.setattr(graph, "build_agent", boom)
    reply = graph.run_agent(db, user.id, [("user", "hello")])
    assert reply == graph.FRIENDLY_ERROR


def test_run_agent_tries_fallback_model(db, make_user, monkeypatch):
    user = make_user()
    tried = []

    class FakeAgent:
        def invoke(self, *args, **kwargs):
            from langchain_core.messages import AIMessage

            return {"messages": [AIMessage(content="fallback reply")]}

    def fake_build(db, rep_id, model_name=None):
        tried.append(model_name)
        if len(tried) == 1:
            raise RuntimeError("primary model down")
        return FakeAgent()

    monkeypatch.setattr(graph, "build_agent", fake_build)
    reply = graph.run_agent(db, user.id, [("user", "hello")])
    assert reply == "fallback reply"
    assert len(tried) == 2
    assert tried[0] != tried[1]