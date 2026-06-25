import inspect

import jarvis_core.app as app_module
from jarvis_core.local_research_agent import LocalResearchAgentService, LocalResearchBriefRequest
from jarvis_core.lan_security import require_dashboard_lan_access


def test_local_research_brief_endpoint_returns_structured_local_brief():
    payload = app_module.LocalResearchBriefInput(
        topic="Magnetic microrobots for vascular navigation",
        userProvidedNotes=(
            "Magnetic microrobots can be externally guided. Simulation can model flow, "
            "magnetic gradients, obstacles, and swarm behavior."
        ),
        sourceTitles=["Review paper on magnetic microrobots", "Paper on vascular flow simulation"],
        questions=["What should I study first?", "What are the gaps?"],
        desiredOutputType="brief",
    )

    result = app_module.create_local_research_brief(payload)

    assert result["agentId"] == "local_research_agent"
    assert result["status"] == "local_only"
    assert result["topic"] == "Magnetic microrobots for vascular navigation"
    assert result["desiredOutputType"] == "brief"
    assert result["thesisOrFocus"]
    assert any("Magnetic microrobots can be externally guided" in point for point in result["keyPoints"])
    assert result["openQuestions"] == ["What should I study first?", "What are the gaps?"]
    assert any("unverified labels" in gap for gap in result["sourceGaps"])
    assert "Based only on user-provided notes." in result["limitations"]
    assert "No web browsing or source verification was performed." in result["limitations"]


def test_local_research_brief_handles_thin_notes_honestly():
    service = LocalResearchAgentService()

    result = service.create_brief(
        LocalResearchBriefRequest(
            topic="Battery recycling",
            user_provided_notes="Interesting topic.",
            desired_output_type="outline",
        )
    )

    assert result["desiredOutputType"] == "outline"
    assert "limited" in result["thesisOrFocus"].lower()
    assert any("thin" in note.lower() for note in result["synthesisNotes"])
    assert any("More user-provided notes" in gap for gap in result["sourceGaps"])
    assert any("at least a paragraph" in step for step in result["suggestedLocalNextSteps"])


def test_local_research_brief_safety_flags_disable_external_behavior():
    service = LocalResearchAgentService()

    result = service.create_brief(
        LocalResearchBriefRequest(
            topic="Local-only research",
            user_provided_notes="Point one. Point two explains a local-only boundary for synthesis.",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["postingOrSending"] is False
    assert safety["fileMutation"] is False


def test_local_research_agent_source_has_no_network_file_or_api_calls():
    source = inspect.getsource(__import__("jarvis_core.local_research_agent").local_research_agent)
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "open(",
        "read_text",
        "write_text",
        ".write(",
        "subprocess",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source.lower() for token in forbidden)


def test_local_research_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/research/local-brief")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
