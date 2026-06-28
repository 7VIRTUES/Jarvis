import re

from jarvis_core.local_response_agents_catalog import (
    local_response_agents_global_boundaries,
    local_response_agents_index,
    local_response_agents_summary,
)


EXPECTED_ENDPOINTS = [
    "POST /agents/research/local-brief",
    "POST /agents/files/local-summary",
    "POST /agents/planning/local-plan",
    "POST /agents/drafting/local-draft",
    "POST /agents/review/local-review",
    "POST /agents/decision/local-decision",
    "POST /agents/troubleshooting/local-triage",
    "POST /agents/summarization/local-summary",
    "POST /agents/extraction/local-extract",
    "POST /agents/classification/local-classify",
    "POST /agents/transformation/local-transform",
    "POST /agents/business/local-brief",
    "POST /agents/health-fitness/local-plan",
    "POST /agents/everyday-life/local-plan",
    "POST /agents/online-presence/local-plan",
    "POST /agents/security-safety/local-review",
    "POST /agents/creator/local-plan",
    "POST /agents/school-robotics/local-plan",
    "POST /agents/career/local-plan",
    "POST /agents/finance-budget/local-plan",
    "POST /agents/housing-move-travel/local-plan",
    "POST /agents/projects-portfolio/local-plan",
    "POST /agents/learning-study/local-plan",
    "POST /agents/social-networking/local-plan",
    "POST /agents/personal-admin/local-plan",
    "POST /agents/vehicle-devices-gear/local-plan",
    "POST /agents/life-direction/local-plan",
    "POST /agents/relationships/local-plan",
    "POST /agents/emotional-reflection/local-reflect",
]

REQUIRED_FIELDS = {
    "name",
    "endpoint",
    "status",
    "mode",
    "docsLink",
    "responseMode",
    "safetyNotes",
    "exampleRequestBody",
}


def test_catalog_exposes_exactly_29_agents_with_required_fields():
    agents = local_response_agents_index()

    assert len(agents) == 29
    for agent in agents:
        assert REQUIRED_FIELDS <= set(agent)
        assert agent["name"]
        assert agent["endpoint"].startswith("POST /agents/")
        assert agent["status"] == "implemented_local_only"
        assert agent["mode"]
        assert agent["docsLink"].startswith("/docs/")
        assert agent["docsLink"].endswith(".md")
        assert agent["responseMode"] in {"response_only", "metadata_only"}
        assert agent["safetyNotes"]
        assert isinstance(agent["exampleRequestBody"], dict)
        assert agent["exampleRequestBody"]


def test_catalog_includes_all_expected_endpoints_once():
    endpoints = [agent["endpoint"] for agent in local_response_agents_index()]

    assert endpoints == EXPECTED_ENDPOINTS
    assert len(set(endpoints)) == len(EXPECTED_ENDPOINTS)


def test_catalog_global_boundaries_cover_required_safety_limits():
    boundaries_text = " ".join(local_response_agents_global_boundaries()).lower()

    assert "no paid apis" in boundaries_text
    assert "no connectors" in boundaries_text
    assert "no oauth or account access" in boundaries_text
    assert "no browser automation" in boundaries_text
    assert "no cloud sync" in boundaries_text
    assert "no email sending, posting, or purchases" in boundaries_text
    assert "no task persistence for response-only agents" in boundaries_text
    assert "certification" in boundaries_text


def test_catalog_example_request_bodies_are_safe_local_examples():
    forbidden_fragments = [
        ".env",
        "c:\\",
        "c:/",
        "/users/",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password",
        "credential",
        "account id",
        "account_id",
        "rm -rf",
        "del /",
        "format ",
        "shutdown",
        "http://",
        "https://",
    ]

    for agent in local_response_agents_index():
        example_text = str(agent["exampleRequestBody"]).lower()

        assert all(fragment not in example_text for fragment in forbidden_fragments)
        assert not re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", example_text)


def test_file_data_example_uses_only_registered_project_name():
    file_data_agent = next(agent for agent in local_response_agents_index() if agent["name"] == "File/Data Agent")

    assert file_data_agent["exampleRequestBody"] == {"projectName": "Jarvis"}
    assert any("registered project" in note.lower() for note in file_data_agent["safetyNotes"])
    assert any("raw arbitrary local paths" in note.lower() for note in file_data_agent["safetyNotes"])


def test_catalog_summary_preserves_dashboard_index_shape():
    summary = local_response_agents_summary()

    assert summary["status"] == "read_only_index"
    assert summary["agentCount"] == 29
    assert summary["agents"] == local_response_agents_index()
    assert summary["globalBoundaries"] == local_response_agents_global_boundaries()
    assert summary["docsLink"] == "/docs/local-response-agents-index.md"
    assert summary["addsAgents"] is False
    assert summary["addsEndpoint"] is False
    assert summary["mutation"] is False
    assert summary["connectorExecution"] is False
    assert summary["paidApis"] is False
    assert summary["certificationClaims"] is False


def test_catalog_includes_local_business_agent_once_with_safe_example():
    agents = local_response_agents_index()
    business_agents = [agent for agent in agents if agent["name"] == "Local Business Agent"]

    assert len(business_agents) == 1
    business_agent = business_agents[0]
    assert business_agent["endpoint"] == "POST /agents/business/local-brief"
    assert business_agent["mode"] == "response_only_user_provided_business_planning"
    assert business_agent["docsLink"] == "/docs/local-business-agent.md"
    assert business_agent["responseMode"] == "response_only"
    assert any("user-provided business planning inputs only" in note.lower() for note in business_agent["safetyNotes"])
    assert any("payment" in note.lower() and "account" in note.lower() for note in business_agent["safetyNotes"])
    assert business_agent["exampleRequestBody"]["desiredOutputType"] == "business_brief"
    assert "businessIdea" in business_agent["exampleRequestBody"]


def test_catalog_includes_local_creator_agent_once_with_safe_example():
    agents = local_response_agents_index()
    creator_agents = [agent for agent in agents if agent["name"] == "Local Creator Agent"]

    assert len(creator_agents) == 1
    creator_agent = creator_agents[0]
    assert creator_agent["endpoint"] == "POST /agents/creator/local-plan"
    assert creator_agent["mode"] == "response_only_user_provided_creator_planning"
    assert creator_agent["docsLink"] == "/docs/local-creator-agent.md"
    assert creator_agent["responseMode"] == "response_only"
    assert any("user-provided creator" in note.lower() for note in creator_agent["safetyNotes"])
    assert any("no youtube" in note.lower() and "upload" in note.lower() for note in creator_agent["safetyNotes"])
    assert any("monetization success" in note.lower() for note in creator_agent["safetyNotes"])
    assert creator_agent["exampleRequestBody"]["desiredOutputType"] == "creator_brief"
    assert "contentIdea" in creator_agent["exampleRequestBody"]


def test_catalog_includes_local_school_robotics_agent_once_with_safe_example():
    agents = local_response_agents_index()
    school_agents = [agent for agent in agents if agent["name"] == "Local School / Robotics Agent"]

    assert len(school_agents) == 1
    school_agent = school_agents[0]
    assert school_agent["endpoint"] == "POST /agents/school-robotics/local-plan"
    assert school_agent["mode"] == "response_only_user_provided_school_robotics_planning"
    assert school_agent["docsLink"] == "/docs/local-school-robotics-agent.md"
    assert school_agent["responseMode"] == "response_only"
    assert any("user-provided school" in note.lower() for note in school_agent["safetyNotes"])
    assert any("school portal" in note.lower() and "registrar" in note.lower() for note in school_agent["safetyNotes"])
    assert any("official academic validation" in note.lower() for note in school_agent["safetyNotes"])
    assert school_agent["exampleRequestBody"]["desiredOutputType"] == "school_brief"
    assert "academicGoal" in school_agent["exampleRequestBody"]


def test_catalog_includes_local_career_agent_once_with_safe_example():
    agents = local_response_agents_index()
    career_agents = [agent for agent in agents if agent["name"] == "Local Career / Job Search Agent"]

    assert len(career_agents) == 1
    career_agent = career_agents[0]
    assert career_agent["endpoint"] == "POST /agents/career/local-plan"
    assert career_agent["mode"] == "response_only_user_provided_career_planning"
    assert career_agent["docsLink"] == "/docs/local-career-agent.md"
    assert career_agent["responseMode"] == "response_only"
    assert any("user-provided career" in note.lower() for note in career_agent["safetyNotes"])
    assert any("linkedin" in note.lower() and "job-board" in note.lower() for note in career_agent["safetyNotes"])
    assert any("official career validation" in note.lower() for note in career_agent["safetyNotes"])
    assert career_agent["exampleRequestBody"]["desiredOutputType"] == "career_brief"
    assert "careerGoal" in career_agent["exampleRequestBody"]


def test_catalog_includes_local_finance_budget_agent_once_with_safe_example():
    agents = local_response_agents_index()
    finance_agents = [agent for agent in agents if agent["name"] == "Local Finance / Loans / Budget Agent"]

    assert len(finance_agents) == 1
    finance_agent = finance_agents[0]
    assert finance_agent["endpoint"] == "POST /agents/finance-budget/local-plan"
    assert finance_agent["mode"] == "response_only_user_provided_finance_budget_planning"
    assert finance_agent["docsLink"] == "/docs/local-finance-budget-agent.md"
    assert finance_agent["responseMode"] == "response_only"
    assert any("user-provided finance" in note.lower() for note in finance_agent["safetyNotes"])
    assert any("bank" in note.lower() and "loan-servicer" in note.lower() for note in finance_agent["safetyNotes"])
    assert any("financial advice validation" in note.lower() for note in finance_agent["safetyNotes"])
    assert finance_agent["exampleRequestBody"]["desiredOutputType"] == "finance_brief"
    assert "financialGoal" in finance_agent["exampleRequestBody"]


def test_catalog_includes_local_housing_move_travel_agent_once_with_safe_example():
    agents = local_response_agents_index()
    housing_agents = [agent for agent in agents if agent["name"] == "Local Housing / Move / Travel Agent"]

    assert len(housing_agents) == 1
    housing_agent = housing_agents[0]
    assert housing_agent["endpoint"] == "POST /agents/housing-move-travel/local-plan"
    assert housing_agent["mode"] == "response_only_user_provided_housing_move_travel_planning"
    assert housing_agent["docsLink"] == "/docs/local-housing-move-travel-agent.md"
    assert housing_agent["responseMode"] == "response_only"
    assert any("user-provided housing" in note.lower() for note in housing_agent["safetyNotes"])
    assert any("maps" in note.lower() and "booking platforms" in note.lower() for note in housing_agent["safetyNotes"])
    assert any("legal lease review" in note.lower() for note in housing_agent["safetyNotes"])
    assert housing_agent["exampleRequestBody"]["desiredOutputType"] == "move_brief"
    assert "housingGoal" in housing_agent["exampleRequestBody"]


def test_catalog_includes_local_projects_portfolio_agent_once_with_safe_example():
    agents = local_response_agents_index()
    project_agents = [agent for agent in agents if agent["name"] == "Local Projects / Portfolio Agent"]

    assert len(project_agents) == 1
    project_agent = project_agents[0]
    assert project_agent["endpoint"] == "POST /agents/projects-portfolio/local-plan"
    assert project_agent["mode"] == "response_only_user_provided_projects_portfolio_planning"
    assert project_agent["docsLink"] == "/docs/local-projects-portfolio-agent.md"
    assert project_agent["responseMode"] == "response_only"
    assert any("user-provided project" in note.lower() for note in project_agent["safetyNotes"])
    assert any("github" in note.lower() and "repo" in note.lower() for note in project_agent["safetyNotes"])
    assert any("code review validation" in note.lower() for note in project_agent["safetyNotes"])
    assert project_agent["exampleRequestBody"]["desiredOutputType"] == "portfolio_brief"
    assert "portfolioGoal" in project_agent["exampleRequestBody"]


def test_catalog_includes_local_learning_study_agent_once_with_safe_example():
    agents = local_response_agents_index()
    learning_agents = [agent for agent in agents if agent["name"] == "Local Learning / Study Coach Agent"]

    assert len(learning_agents) == 1
    learning_agent = learning_agents[0]
    assert learning_agent["endpoint"] == "POST /agents/learning-study/local-plan"
    assert learning_agent["mode"] == "response_only_user_provided_learning_study_planning"
    assert learning_agent["docsLink"] == "/docs/local-learning-study-agent.md"
    assert learning_agent["responseMode"] == "response_only"
    assert any("user-provided learning" in note.lower() for note in learning_agent["safetyNotes"])
    assert any("school portal" in note.lower() and "lms" in note.lower() for note in learning_agent["safetyNotes"])
    assert any("grade guarantee" in note.lower() for note in learning_agent["safetyNotes"])
    assert learning_agent["exampleRequestBody"]["desiredOutputType"] == "learning_brief"
    assert "learningGoal" in learning_agent["exampleRequestBody"]


def test_catalog_includes_local_social_networking_agent_once_with_safe_example():
    agents = local_response_agents_index()
    social_agents = [agent for agent in agents if agent["name"] == "Local Social / Networking / High-Class Coach Agent"]

    assert len(social_agents) == 1
    social_agent = social_agents[0]
    assert social_agent["endpoint"] == "POST /agents/social-networking/local-plan"
    assert social_agent["mode"] == "response_only_user_provided_social_networking_planning"
    assert social_agent["docsLink"] == "/docs/local-social-networking-agent.md"
    assert social_agent["responseMode"] == "response_only"
    assert any("user-provided social" in note.lower() for note in social_agent["safetyNotes"])
    assert any("contacts" in note.lower() and "social platform" in note.lower() for note in social_agent["safetyNotes"])
    assert any("manipulation" in note.lower() and "stalking" in note.lower() for note in social_agent["safetyNotes"])
    assert social_agent["exampleRequestBody"]["desiredOutputType"] == "social_brief"
    assert "socialGoal" in social_agent["exampleRequestBody"]


def test_catalog_includes_local_personal_admin_agent_once_with_safe_example():
    agents = local_response_agents_index()
    personal_admin_agents = [agent for agent in agents if agent["name"] == "Local Personal Admin / Documents Agent"]

    assert len(personal_admin_agents) == 1
    personal_admin_agent = personal_admin_agents[0]
    assert personal_admin_agent["endpoint"] == "POST /agents/personal-admin/local-plan"
    assert personal_admin_agent["mode"] == "response_only_user_provided_personal_admin_planning"
    assert personal_admin_agent["docsLink"] == "/docs/local-personal-admin-agent.md"
    assert personal_admin_agent["responseMode"] == "response_only"
    assert any("user-provided personal admin" in note.lower() for note in personal_admin_agent["safetyNotes"])
    assert any("document" in note.lower() and "portal" in note.lower() for note in personal_admin_agent["safetyNotes"])
    assert any("legal validation" in note.lower() and "identity validation" in note.lower() for note in personal_admin_agent["safetyNotes"])
    assert personal_admin_agent["exampleRequestBody"]["desiredOutputType"] == "admin_brief"
    assert "adminGoal" in personal_admin_agent["exampleRequestBody"]


def test_catalog_includes_local_vehicle_devices_gear_agent_once_with_safe_example():
    agents = local_response_agents_index()
    gear_agents = [agent for agent in agents if agent["name"] == "Local Vehicle / Devices / Gear Agent"]

    assert len(gear_agents) == 1
    gear_agent = gear_agents[0]
    assert gear_agent["endpoint"] == "POST /agents/vehicle-devices-gear/local-plan"
    assert gear_agent["mode"] == "response_only_user_provided_vehicle_devices_gear_planning"
    assert gear_agent["docsLink"] == "/docs/local-vehicle-devices-gear-agent.md"
    assert gear_agent["responseMode"] == "response_only"
    assert any("user-provided vehicle" in note.lower() for note in gear_agent["safetyNotes"])
    assert any("obd" in note.lower() and "bluetooth" in note.lower() for note in gear_agent["safetyNotes"])
    assert any("flight legality" in note.lower() and "warranty validation" in note.lower() for note in gear_agent["safetyNotes"])
    assert gear_agent["exampleRequestBody"]["desiredOutputType"] == "gear_brief"
    assert "gearGoal" in gear_agent["exampleRequestBody"]


def test_catalog_includes_local_life_direction_agent_once_with_safe_example():
    agents = local_response_agents_index()
    direction_agents = [agent for agent in agents if agent["name"] == "Local Life Direction / Values Agent"]

    assert len(direction_agents) == 1
    direction_agent = direction_agents[0]
    assert direction_agent["endpoint"] == "POST /agents/life-direction/local-plan"
    assert direction_agent["mode"] == "response_only_user_provided_life_direction_planning"
    assert direction_agent["docsLink"] == "/docs/local-life-direction-agent.md"
    assert direction_agent["responseMode"] == "response_only"
    assert any("user-provided life direction" in note.lower() for note in direction_agent["safetyNotes"])
    assert any("health data" in note.lower() and "finance data" in note.lower() for note in direction_agent["safetyNotes"])
    assert any("therapy claim" in note.lower() and "life-outcome certainty" in note.lower() for note in direction_agent["safetyNotes"])
    assert direction_agent["exampleRequestBody"]["desiredOutputType"] == "life_direction_brief"
    assert "lifeQuestion" in direction_agent["exampleRequestBody"]


def test_catalog_includes_local_relationships_agent_once_with_safe_example():
    agents = local_response_agents_index()
    relationship_agents = [agent for agent in agents if agent["name"] == "Local Relationship / Family Agent"]

    assert len(relationship_agents) == 1
    relationship_agent = relationship_agents[0]
    assert relationship_agent["endpoint"] == "POST /agents/relationships/local-plan"
    assert relationship_agent["mode"] == "response_only_user_provided_relationship_planning"
    assert relationship_agent["docsLink"] == "/docs/local-relationships-agent.md"
    assert relationship_agent["responseMode"] == "response_only"
    assert any("user-provided relationship" in note.lower() for note in relationship_agent["safetyNotes"])
    assert any("contacts" in note.lower() and "social platforms" in note.lower() for note in relationship_agent["safetyNotes"])
    assert any("manipulation" in note.lower() and "therapy claims" in note.lower() for note in relationship_agent["safetyNotes"])
    assert relationship_agent["exampleRequestBody"]["desiredOutputType"] == "relationship_brief"
    assert "relationshipGoal" in relationship_agent["exampleRequestBody"]


def test_catalog_includes_local_emotional_reflection_agent_once_with_safe_example():
    agents = local_response_agents_index()
    reflection_agents = [agent for agent in agents if agent["name"] == "Local Emotional Reflection / Resilience Agent"]

    assert len(reflection_agents) == 1
    reflection_agent = reflection_agents[0]
    assert reflection_agent["endpoint"] == "POST /agents/emotional-reflection/local-reflect"
    assert reflection_agent["mode"] == "response_only_user_provided_emotional_reflection"
    assert reflection_agent["docsLink"] == "/docs/local-emotional-reflection-agent.md"
    assert reflection_agent["responseMode"] == "response_only"
    assert any("user-provided emotional reflection" in note.lower() for note in reflection_agent["safetyNotes"])
    assert any("health-record" in note.lower() and "wearable" in note.lower() for note in reflection_agent["safetyNotes"])
    assert any("therapy claims" in note.lower() and "psychiatric validation" in note.lower() for note in reflection_agent["safetyNotes"])
    assert reflection_agent["exampleRequestBody"]["desiredOutputType"] == "reflection_brief"
    assert "reflectionGoal" in reflection_agent["exampleRequestBody"]


def test_catalog_includes_local_health_fitness_agent_once_with_safe_example():
    agents = local_response_agents_index()
    health_agents = [agent for agent in agents if agent["name"] == "Local Health/Fitness Agent"]

    assert len(health_agents) == 1
    health_agent = health_agents[0]
    assert health_agent["endpoint"] == "POST /agents/health-fitness/local-plan"
    assert health_agent["mode"] == "response_only_user_provided_health_fitness_planning"
    assert health_agent["docsLink"] == "/docs/local-health-fitness-agent.md"
    assert health_agent["responseMode"] == "response_only"
    assert any("user-provided wellness" in note.lower() for note in health_agent["safetyNotes"])
    assert any("no medical diagnosis" in note.lower() for note in health_agent["safetyNotes"])
    assert any("health connector" in note.lower() and "account" in note.lower() for note in health_agent["safetyNotes"])
    assert health_agent["exampleRequestBody"]["desiredOutputType"] == "fitness_brief"
    assert "primaryGoal" in health_agent["exampleRequestBody"]


def test_catalog_includes_local_everyday_life_agent_once_with_safe_example():
    agents = local_response_agents_index()
    everyday_agents = [agent for agent in agents if agent["name"] == "Local Everyday Life Agent"]

    assert len(everyday_agents) == 1
    everyday_agent = everyday_agents[0]
    assert everyday_agent["endpoint"] == "POST /agents/everyday-life/local-plan"
    assert everyday_agent["mode"] == "response_only_user_provided_everyday_life_planning"
    assert everyday_agent["docsLink"] == "/docs/local-everyday-life-agent.md"
    assert everyday_agent["responseMode"] == "response_only"
    assert any("user-provided everyday-life planning inputs only" in note.lower() for note in everyday_agent["safetyNotes"])
    assert any("calendar" in note.lower() and "account" in note.lower() for note in everyday_agent["safetyNotes"])
    assert any("no validation" in note.lower() for note in everyday_agent["safetyNotes"])
    assert everyday_agent["exampleRequestBody"]["desiredOutputType"] == "life_brief"
    assert "situation" in everyday_agent["exampleRequestBody"]


def test_catalog_includes_local_online_presence_agent_once_with_safe_example():
    agents = local_response_agents_index()
    online_agents = [agent for agent in agents if agent["name"] == "Local Online Presence Agent"]

    assert len(online_agents) == 1
    online_agent = online_agents[0]
    assert online_agent["endpoint"] == "POST /agents/online-presence/local-plan"
    assert online_agent["mode"] == "response_only_user_provided_online_presence_planning"
    assert online_agent["docsLink"] == "/docs/local-online-presence-agent.md"
    assert online_agent["responseMode"] == "response_only"
    assert any("user-provided online presence planning" in note.lower() for note in online_agent["safetyNotes"])
    assert any("no posting" in note.lower() and "scheduling" in note.lower() for note in online_agent["safetyNotes"])
    assert any("reputation verification" in note.lower() for note in online_agent["safetyNotes"])
    assert online_agent["exampleRequestBody"]["desiredOutputType"] == "presence_brief"
    assert "profileName" in online_agent["exampleRequestBody"]


def test_catalog_includes_local_security_safety_agent_once_with_safe_example():
    agents = local_response_agents_index()
    security_agents = [agent for agent in agents if agent["name"] == "Local Security/Safety Agent"]

    assert len(security_agents) == 1
    security_agent = security_agents[0]
    assert security_agent["endpoint"] == "POST /agents/security-safety/local-review"
    assert security_agent["mode"] == "response_only_user_provided_security_safety_review"
    assert security_agent["docsLink"] == "/docs/local-security-safety-agent.md"
    assert security_agent["responseMode"] == "response_only"
    assert any("user-provided security and safety" in note.lower() for note in security_agent["safetyNotes"])
    assert any("no scans" in note.lower() and "secret reads" in note.lower() for note in security_agent["safetyNotes"])
    assert any("security certification" in note.lower() for note in security_agent["safetyNotes"])
    assert security_agent["exampleRequestBody"]["desiredOutputType"] == "safety_brief"
    assert "situation" in security_agent["exampleRequestBody"]
