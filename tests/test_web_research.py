from pydantic import ValidationError
import pytest

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.web_research import (
    add_web_context_response_fields,
    agent_context_preview,
    apply_source_aware_response_fields,
    build_citation_labels,
    build_source_evidence,
    build_source_aware_context,
    build_source_cautions,
    build_source_followup_checks,
    build_source_quality_warnings,
    build_source_recency_notes,
    build_source_supported_points,
    build_sources_used,
    build_web_context_limitations,
    build_web_context_template_sample,
    fetch_public_url,
    normalize_web_context,
    summarize_web_context,
    validate_public_url,
    web_research_policy,
)


WEB_RESEARCH_ROUTES = [
    ("GET", "/web-research/policy"),
    ("POST", "/web-research/validate-url"),
    ("POST", "/web-research/fetch-public-url"),
    ("POST", "/web-research/agent-context-preview"),
]


def test_web_research_policy_exposes_read_only_public_web_boundaries():
    policy = web_research_policy(agent_count=37)

    assert policy["enabled"] is True
    assert policy["mode"] == "read_only_public_web"
    assert policy["allowed_methods"] == ["GET", "HEAD"]
    assert {"POST", "PUT", "PATCH", "DELETE"} <= set(policy["blocked_methods"])
    assert "max_response_bytes" in policy["content_limits"]
    assert "allowed_content_types" in policy["content_limits"]
    assert "Read-only public web only." in policy["safety_boundaries"]
    assert "No logins or accounts." in policy["safety_boundaries"]
    assert "No private networks or localhost." in policy["safety_boundaries"]
    assert policy["agent_availability_summary"]["local_response_agent_count"] == 37
    assert policy["agent_availability_summary"]["web_research_available"] is True
    assert policy["agent_availability_summary"]["web_research_mode"] == "read_only_public_url_context"
    assert policy["agent_availability_summary"]["web_research_requires_user_enabled"] is True
    assert policy["agent_availability_summary"]["web_research_is_optional"] is True
    assert policy["agent_availability_summary"]["web_context_supported"] is True
    assert policy["agent_availability_summary"]["agents_do_not_auto_browse"] is True
    assert policy["agent_availability_summary"]["automatic_agent_browsing"] is False
    assert policy["agent_availability_summary"]["connector_behavior"] is False


def test_web_context_helpers_normalize_reviewed_sources_and_response_fields():
    raw_context = [
        {
            "source_url": "https://example.com/public-source",
            "final_url": "https://example.com/public-source",
            "title": " Public Source ",
            "excerpt": " Reviewed excerpt. " * 400,
            "content_type": "text/plain",
            "fetched": True,
            "fetched_at": "2026-06-29T12:00:00+00:00",
            "limitations": ["Manual review only."],
        },
        {
            "source_url": "https://example.com/public-source",
            "title": "Duplicate Source",
            "excerpt": "Duplicate excerpt should be deduplicated.",
        },
        {"source_url": "http://127.0.0.1/private", "excerpt": "blocked"},
        {"source_url": "https://user:password@example.com/private", "excerpt": "credential-bearing source"},
        {"source_url": "https://example.com/no-excerpt", "excerpt": ""},
    ]

    normalized = normalize_web_context(raw_context)

    assert len(normalized) == 1
    assert normalized[0]["source_id"] == "S1"
    assert normalized[0]["citation_label"] == "[S1]"
    assert normalized[0]["domain"] == "example.com"
    assert normalized[0]["source_url"] == "https://example.com/public-source"
    assert normalized[0]["title"] == "Public Source"
    assert len(normalized[0]["excerpt"]) <= 4000
    assert summarize_web_context(raw_context).startswith("1 reviewed public source excerpt")
    assert build_sources_used(raw_context) == [
        {
            "source_id": "S1",
            "citation_label": "[S1]",
            "source_url": "https://example.com/public-source",
            "final_url": "https://example.com/public-source",
            "title": "Public Source",
            "domain": "example.com",
            "source_type": "public_web_excerpt",
        }
    ]
    assert build_source_evidence(raw_context)[0]["citation_label"] == "[S1]"
    assert build_citation_labels(raw_context) == ["[S1]"]
    assert "not independently verify" in " ".join(build_source_quality_warnings(raw_context))
    assert "fetched_at timestamp was supplied" in " ".join(build_source_recency_notes(raw_context))
    assert "do not browse" in " ".join(build_web_context_limitations(raw_context))

    response = add_web_context_response_fields({"title": "Local result"}, raw_context)
    assert response["title"] == "Local result"
    assert response["source_evidence"][0]["source_id"] == "S1"
    assert response["citation_labels"] == ["[S1]"]
    assert response["source_quality_warnings"]
    assert response["source_recency_notes"]
    assert response["source_context_summary"].startswith("1 reviewed public source excerpt")
    assert response["sources_used"][0]["source_url"] == "https://example.com/public-source"
    assert "not persisted" in " ".join(response["web_context_limitations"])


def test_web_context_helpers_expose_safe_empty_and_template_shapes():
    sample = build_web_context_template_sample()
    empty_response = add_web_context_response_fields({"title": "Local result"}, [])

    assert sample[0]["source_url"] == "https://example.com/public-source"
    assert sample[0]["user_notes"]
    assert sample[0]["source_type"] == "public_web_excerpt"
    assert empty_response["source_evidence"] == []
    assert empty_response["citation_labels"] == []
    assert empty_response["source_quality_warnings"] == []
    assert empty_response["source_recency_notes"] == []
    assert empty_response["source_context_summary"] == "No reviewed public source context was provided."
    assert empty_response["sources_used"] == []
    assert "No web_context was provided" in empty_response["web_context_limitations"][0]


def test_web_context_evidence_warns_on_missing_title_and_unknown_recency():
    raw_context = [
        {
            "source_url": "https://example.com/source-one",
            "excerpt": "Reviewed excerpt without title or fetched_at.",
        },
        {
            "source_url": "https://example.org/source-two",
            "title": "Second Source",
            "excerpt": "Reviewed excerpt with an unparsable fetched_at.",
            "fetched_at": "not-a-date",
        },
    ]

    evidence = build_source_evidence(raw_context)

    assert [source["source_id"] for source in evidence] == ["S1", "S2"]
    assert [source["citation_label"] for source in evidence] == ["[S1]", "[S2]"]
    assert any("no title" in warning.lower() for warning in evidence[0]["quality_warnings"])
    assert evidence[0]["recency_note"] == "[S1] recency unknown: no fetched_at timestamp was supplied."
    assert evidence[1]["recency_note"] == "[S2] recency unknown: fetched_at timestamp could not be parsed."


def test_web_context_evidence_preserves_source_and_excerpt_limits():
    raw_context = [
        {
            "source_url": f"https://example.com/source-{index}",
            "title": f"Source {index}",
            "excerpt": "Long reviewed excerpt. " * 500,
        }
        for index in range(1, 8)
    ]

    evidence = build_source_evidence(raw_context)

    assert len(evidence) == 5
    assert [source["source_id"] for source in evidence] == ["S1", "S2", "S3", "S4", "S5"]
    assert all(len(source["excerpt"]) <= 4000 for source in evidence)


def test_source_aware_helper_returns_stable_empty_values_without_web_context():
    context = build_source_aware_context("local_planning_agent", "Coding/Core", [])

    assert context["source_use_summary"] == "No reviewed source context was provided; source-aware response sections are empty."
    assert context["source_supported_points"] == []
    assert context["source_cautions"] == []
    assert context["source_followup_checks"] == []
    assert context["source_informed_assumptions"] == []
    assert context["citation_usage_note"] == "No citation labels were used because no web_context was provided."


def test_source_aware_helper_uses_citation_labels_without_overclaiming():
    raw_context = [
        {
            "source_url": "https://example.com/source-one",
            "title": "Source One",
            "excerpt": "Reviewed excerpt one for local planning.",
        },
        {
            "source_url": "https://example.org/source-two",
            "title": "Source Two",
            "excerpt": "Reviewed excerpt two for local planning.",
            "fetched_at": "not-a-date",
        },
    ]

    context = build_source_aware_context("local_planning_agent", "Coding/Core", raw_context)

    assert "[S1]" in " ".join(context["source_supported_points"])
    assert "[S2]" in " ".join(context["source_supported_points"])
    assert "did not browse, search, fetch, follow links, or independently verify" in context["source_use_summary"]
    assert "not proof" in context["citation_usage_note"]
    assert "could not be parsed" in " ".join(context["source_cautions"])
    assert "Verify source freshness" in " ".join(context["source_followup_checks"]) or "verify source freshness" in " ".join(context["source_followup_checks"]).lower()


def test_source_aware_helper_adds_high_stakes_category_cautions():
    raw_context = [
        {
            "source_url": "https://example.com/health-source",
            "title": "Health Source",
            "excerpt": "Reviewed health excerpt.",
        }
    ]

    health_cautions = " ".join(build_source_cautions(raw_context, "Health/Food/Home"))
    legal_cautions = " ".join(build_source_cautions(raw_context, "Safety/Emergency"))
    finance_checks = " ".join(build_source_followup_checks(raw_context, "Finance/Housing/Travel"))

    assert "not clinical advice" in health_cautions
    assert "diagnosis" in health_cautions
    assert "not legal advice" in legal_cautions
    assert "live emergency awareness" in legal_cautions
    assert "verify terms" in finance_checks.lower()


def test_apply_source_aware_response_fields_preserves_existing_source_metadata():
    raw_context = [
        {
            "source_url": "https://example.com/source",
            "title": "Reviewed Source",
            "excerpt": "Reviewed source excerpt.",
        }
    ]

    response = apply_source_aware_response_fields({"title": "Local result"}, "local_planning_agent", "Coding/Core", raw_context)

    assert response["title"] == "Local result"
    assert response["source_evidence"][0]["citation_label"] == "[S1]"
    assert response["citation_labels"] == ["[S1]"]
    assert response["source_supported_points"]
    assert response["source_cautions"]
    assert response["source_followup_checks"]
    assert response["source_informed_assumptions"]
    assert "not proof" in response["citation_usage_note"]


def test_url_validator_blocks_private_local_credential_and_non_http_urls():
    blocked_urls = [
        "file:///tmp/private.txt",
        "ftp://example.com/file.txt",
        "data:text/plain,hello",
        "javascript:alert(1)",
        "ws://example.com/socket",
        "http://localhost/status",
        "http://127.0.0.1/status",
        "http://[::1]/status",
        "http://0.0.0.0/status",
        "http://10.1.2.3/status",
        "http://172.16.1.1/status",
        "http://192.168.1.5/status",
        "http://169.254.169.254/latest/meta-data",
        "https://user:password@example.com/private",
        "https://example.com/installer.exe",
        "https://example.com/archive.zip",
        "https://intranet/status",
        "https://service.local/status",
    ]

    for url in blocked_urls:
        result = validate_public_url(url)

        assert result["url"] == url
        assert result["is_allowed"] is False
        assert result["blocked_reason"]
        assert "Read-only public web only." in result["safety_boundaries"]


def test_url_validator_allows_ordinary_public_https_urls():
    result = validate_public_url("https://example.com/public/page?topic=jarvis")

    assert result["is_allowed"] is True
    assert result["normalized_url"] == "https://example.com/public/page?topic=jarvis"
    assert result["blocked_reason"] == ""
    assert result["warnings"] == ["Query strings can contain identifiers; avoid secrets or account-specific URLs."]


def test_fetch_public_url_returns_blocked_reason_and_response_shape_for_disallowed_urls():
    result = fetch_public_url("http://127.0.0.1/private", purpose="local test")

    assert result["url"] == "http://127.0.0.1/private"
    assert result["final_url"] == ""
    assert result["is_allowed"] is False
    assert result["fetched"] is False
    assert result["status_code"] is None
    assert result["content_type"] == ""
    assert result["title"] == ""
    assert result["excerpt"] == ""
    assert result["citations_or_sources"] == []
    assert result["blocked_reason"]
    assert "No fetch was attempted" in " ".join(result["limitations"])
    assert "No private networks or localhost." in result["safety_boundaries"]


def test_agent_context_preview_does_not_invoke_agents_or_auto_submit():
    preview = agent_context_preview(
        agent_id="local_research_agent",
        user_request="Use these public sources for a local brief.",
        urls=["https://example.com/public", "http://127.0.0.1/private"],
        output_type="brief",
        web_research_enabled=True,
        constraints_or_notes="Manual preview only.",
    )

    assert preview["agent_id"] == "local_research_agent"
    assert preview["web_research_enabled"] is True
    assert len(preview["allowed_sources"]) == 1
    assert len(preview["blocked_sources"]) == 1
    assert preview["source_summaries"]
    assert "does not invoke agents" in preview["not_executed_notice"]
    assert "auto-submit" in preview["not_executed_notice"]
    assert "Read-only public web only." in preview["local_only_boundaries"]


def test_web_research_app_models_reject_extra_fields():
    payload = app_module.WebResearchUrlInput(
        url="https://example.com/source",
        purpose="manual public source review",
        max_excerpt_chars=1200,
        allow_redirects=True,
        constraintsOrNotes="No accounts.",
    )

    assert payload.url == "https://example.com/source"

    with pytest.raises(ValidationError):
        app_module.WebResearchUrlInput.model_validate(
            {
                "url": "https://example.com/source",
                "cookie": "not allowed",
            }
        )


def test_web_research_endpoints_exist_and_are_lan_guarded():
    for method, path in WEB_RESEARCH_ROUTES:
        route = next(
            route
            for route in app_module.app.routes
            if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
        )
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

        assert require_dashboard_lan_access in dependency_calls
