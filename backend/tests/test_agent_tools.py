from app.agent.resolvers import resolve_hcp, resolve_products
from app.agent.tools import build_tools


def get_tool(tools, name):
    return next(t for t in tools if t.name == name)


def test_resolve_hcp_single_match(db, make_hcp):
    make_hcp(full_name="Dr. Rohan Kapoor")
    result = resolve_hcp(db, "Kapoor")
    assert result.hcp is not None
    assert result.hcp.full_name == "Dr. Rohan Kapoor"


def test_resolve_hcp_short_form_name(db, make_hcp):
    make_hcp(full_name="Dr. Rohan Kapoor")
    result = resolve_hcp(db, "Dr. Kapoor")
    assert result.hcp is not None


def test_resolve_hcp_no_match(db, make_hcp):
    make_hcp(full_name="Dr. Rohan Kapoor")
    result = resolve_hcp(db, "Zzz")
    assert result.hcp is None
    assert "No HCP found" in result.message # type: ignore


def test_resolve_hcp_several_matches_asks(db, make_hcp):
    make_hcp(full_name="Dr. Rohan Kapoor")
    make_hcp(full_name="Dr. Anil Kapoor")
    result = resolve_hcp(db, "Kapoor")
    assert result.hcp is None
    assert "Several HCPs match" in result.message # type: ignore


def test_resolve_products(db, make_product):
    make_product("CardioSafe 10mg")
    ids, problems = resolve_products(db, ["cardio", "nothing"])
    assert len(ids) == 1
    assert len(problems) == 1


def test_search_hcp_tool_finds_and_misses(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. A", specialty="Cardiology")
    search = get_tool(build_tools(db, user.id), "search_hcp")
    assert "Dr. A" in search.invoke({"query": "cardio"})
    assert "No HCPs found" in search.invoke({"query": "zzz"})


def test_search_hcp_plural_matches_specialty(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. A", specialty="Cardiology")
    search = get_tool(build_tools(db, user.id), "search_hcp")
    assert "Dr. A" in search.invoke({"query": "cardiologists"})


def test_log_interaction_saves_as_ai_chat(db, make_user, make_hcp, make_product):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    make_product("CardioSafe 10mg")
    log = get_tool(build_tools(db, user.id), "log_interaction")
    result = log.invoke(
        {
            "hcp_name": "Dr. Kapoor",
            "interaction_type": "visit",
            "sentiment": "positive",
            "product_names": ["cardio"],
            "follow_up_description": "Send PDF",
            "follow_up_due_date": "2026-10-30",
        }
    )
    assert result.startswith("Saved interaction #")

    from app.services import interaction_service

    rows = interaction_service.list_interactions(db, user.id)
    assert len(rows) == 1
    assert rows[0].source == "ai_chat"
    assert rows[0].sentiment == "positive"
    assert len(rows[0].follow_ups) == 1


def test_log_interaction_unknown_hcp_not_saved(db, make_user):
    user = make_user()
    log = get_tool(build_tools(db, user.id), "log_interaction")
    result = log.invoke({"hcp_name": "Dr. Zzz", "interaction_type": "visit"})
    assert "No HCP found" in result

    from app.services import interaction_service

    assert interaction_service.list_interactions(db, user.id) == []


def test_log_interaction_unknown_product_not_saved(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log = get_tool(build_tools(db, user.id), "log_interaction")
    result = log.invoke(
        {
            "hcp_name": "Kapoor",
            "interaction_type": "visit",
            "product_names": ["nothing"],
        }
    )
    assert result.startswith("Not saved.")


def test_log_interaction_bad_date_not_saved(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log = get_tool(build_tools(db, user.id), "log_interaction")
    result = log.invoke(
        {
            "hcp_name": "Kapoor",
            "interaction_type": "visit",
            "interaction_date": "not-a-date",
        }
    )
    assert result.startswith("Not saved.")


def test_log_interaction_bad_followup_date_not_saved(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log = get_tool(build_tools(db, user.id), "log_interaction")
    result = log.invoke(
        {
            "hcp_name": "Kapoor",
            "interaction_type": "visit",
            "follow_up_description": "Send PDF",
            "follow_up_due_date": "next friday",
        }
    )
    assert "YYYY-MM-DD" in result


def _log_one(db, user, tool_log, **extra):
    args = {"hcp_name": "Kapoor", "interaction_type": "visit"}
    args.update(extra)
    return tool_log.invoke(args)


def test_history_tool_lists_and_handles_empty(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    make_hcp(full_name="Dr. Empty")
    tools = build_tools(db, user.id)
    log = get_tool(tools, "log_interaction")
    history = get_tool