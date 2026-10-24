from app.agent.tools import build_tools
from app.services import interaction_service


def get_tool(tools, name):
    return next(t for t in tools if t.name == name)


def log_one(db, user, sentiment="positive"):
    log = get_tool(build_tools(db, user.id), "log_interaction")
    return log.invoke(
        {"hcp_name": "Kapoor", "interaction_type": "visit", "sentiment": sentiment}
    )


def test_history_lists_interactions(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user)
    history = get_tool(build_tools(db, user.id), "get_interaction_history")
    result = history.invoke({"hcp_name": "Kapoor"})
    assert "Last 1 interaction(s)" in result
    assert "visit" in result


def test_history_empty(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    history = get_tool(build_tools(db, user.id), "get_interaction_history")
    assert "No interactions logged" in history.invoke({"hcp_name": "Kapoor"})


def test_edit_changes_most_recent_only_the_given_field(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user, sentiment="positive")
    edit = get_tool(build_tools(db, user.id), "edit_interaction")
    result = edit.invoke({"hcp_name": "Kapoor", "sentiment": "negative"})
    assert result.startswith("Updated interaction")
    row = interaction_service.list_interactions(db, user.id)[0]
    assert row.sentiment == "negative"
    assert row.interaction_type == "visit"


def test_edit_with_no_fields_changes_nothing(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user)
    edit = get_tool(build_tools(db, user.id), "edit_interaction")
    assert "Nothing to change" in edit.invoke({"hcp_name": "Kapoor"})


def test_edit_no_interactions(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    edit = get_tool(build_tools(db, user.id), "edit_interaction")
    result = edit.invoke({"hcp_name": "Kapoor", "sentiment": "neutral"})
    assert "No interactions logged" in result


def test_edit_cannot_touch_another_reps_interaction(db, make_user, make_hcp):
    owner = make_user(email="owner@test.com")
    other = make_user(email="other@test.com")
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, owner)
    row = interaction_service.list_interactions(db, owner.id)[0]

    edit = get_tool(build_tools(db, other.id), "edit_interaction")
    result = edit.invoke(
        {"hcp_name": "Kapoor", "interaction_id": row.id, "sentiment": "negative"}
    )
    assert result.startswith("Not changed.")
    db.expire_all()
    assert interaction_service.get_interaction(db, owner.id, row.id).sentiment == "positive"


def test_schedule_followup_adds_to_latest(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user)
    follow = get_tool(build_tools(db, user.id), "schedule_followup")
    result = follow.invoke(
        {"hcp_name": "Kapoor", "description": "Send chart", "due_date": "2026-10-30"}
    )
    assert result.startswith("Follow-up added")
    row = interaction_service.list_interactions(db, user.id)[0]
    assert len(row.follow_ups) == 1


def test_schedule_followup_blocks_duplicates(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user)
    follow = get_tool(build_tools(db, user.id), "schedule_followup")
    args = {"hcp_name": "Kapoor", "description": "Send chart", "due_date": "2026-10-30"}
    follow.invoke(args)
    result = follow.invoke(args)
    assert "already exists" in result
    row = interaction_service.list_interactions(db, user.id)[0]
    assert len(row.follow_ups) == 1


def test_schedule_followup_bad_date(db, make_user, make_hcp):
    user = make_user()
    make_hcp(full_name="Dr. Rohan Kapoor")
    log_one(db, user)
    follow = get_tool(build_tools(db, user.id), "schedule_followup")
    result = follow.invoke(
        {"hcp_name": "Kapoor", "description": "x", "due_date": "friday"}
    )
    assert "YYYY-MM-DD" in result