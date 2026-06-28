from pydantic import ValidationError
import pytest

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.web_research import (
    agent_context_preview,
    fetch_public_url,
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
    assert policy["agent_availability_summary"]["automatic_agent_browsing"] is False
    assert policy["agent_availability_summary"]["connector_behavior"] is False


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
