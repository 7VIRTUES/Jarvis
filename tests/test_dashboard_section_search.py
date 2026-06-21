import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def dashboard_page(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    dashboard = DashboardService(conn, workspace, tmp_path / "data" / "jarvis", workspace / "connectors")
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return app_module.local_dashboard().body.decode("utf-8")


def home_section(page):
    start = page.index('id="dashboard-home"')
    end = page.index('id="dashboard-status"')
    return page[start:end]


def test_search_input_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert 'id="dashboard-section-search"' in page
    assert 'type="search"' in page
    assert "Search dashboard sections" in page


def test_expand_collapse_and_clear_filter_controls_exist(tmp_path, monkeypatch):
    home = home_section(dashboard_page(tmp_path, monkeypatch))

    assert "Expand all sections" in home
    assert "Collapse all sections" in home
    assert "Clear filter" in home


def test_major_sections_have_searchable_collapsible_metadata(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)
    section_ids = [
        "dashboard-status",
        "settings-status",
        "lan-protection",
        "validation-agent-status",
        "private-alpha-readiness-snapshot",
        "redacted-diagnostics-bundle",
        "project-profiles",
        "security-safety-review",
        "safety-summary",
    ]

    for section_id in section_ids:
        start = page.index(f'id="{section_id}"')
        snippet = page[start : start + 240]
        assert "dashboard-section" in snippet
        assert "data-section-title=" in snippet
        assert "data-section-keywords=" in snippet
    assert "function initializeDashboardSectionControls()" in page
    assert "function filterDashboardSections(query)" in page
    assert "function setDashboardSectionsCollapsed(collapsed)" in page


def test_newer_centers_remain_searchable(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)
    for section_id, keyword in [
        ("evidence-report-center", "evidence report center"),
        ("agent-manifest-health-center", "agent manifest health"),
        ("docs-runbook-center", "docs runbook center"),
    ]:
        start = page.index(f'id="{section_id}"')
        snippet = page[start : start + 260].lower()
        assert "dashboard-section" in snippet
        assert keyword in snippet


def test_safety_note_text_still_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "Manual evidence only." in page
    assert "Local readiness summary only." in page
    assert "Local redacted diagnostics only." in page
    assert "Local report metadata only." in page
    assert "Known local manifest directories only." in page
    assert "Approved local Markdown docs only." in page


def test_forbidden_labels_absent_from_new_controls(tmp_path, monkeypatch):
    home = home_section(dashboard_page(tmp_path, monkeypatch)).lower()
    forbidden = [
        "deploy",
        "install",
        "release",
        "certify",
        "upload",
        "send",
        "share",
        "publish",
        "fix automatically",
        "enable connector",
        "disable connector",
        "connect account",
    ]

    assert all(label not in home for label in forbidden)


def test_no_new_backend_endpoint_required():
    route_paths = {route.path for route in app_module.app.routes}

    assert "/dashboard/search" not in route_paths
    assert "/api/dashboard/sections" not in route_paths
