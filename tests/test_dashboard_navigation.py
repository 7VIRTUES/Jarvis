import re

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def dashboard_page(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    dashboard = DashboardService(conn, workspace, tmp_path / "data" / "jarvis", workspace / "connectors")
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return app_module.local_dashboard().body.decode("utf-8")


def section(page_text, section_id):
    start = page_text.index(f'id="{section_id}"')
    match = re.search(r'\n    <section id="[^"]+"', page_text[start + 1 :])
    end = start + 1 + match.start() if match else len(page_text)
    return page_text[start:end]


def test_dashboard_home_section_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert 'id="dashboard-home"' in page
    assert "Dashboard Home" in page


def test_quick_links_point_to_existing_section_anchors(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)
    home = section(page, "dashboard-home")
    expected = [
        "safety-summary",
        "project-profiles",
        "security-safety-review",
        "validation-agent-status",
        "private-alpha-readiness-snapshot",
        "redacted-diagnostics-bundle",
        "evidence-report-center",
        "agent-manifest-health-center",
        "docs-runbook-center",
        "settings-status",
        "lan-protection",
        "dashboard-status",
    ]

    for anchor in expected:
        assert f'href="#{anchor}"' in home
        assert f'id="{anchor}"' in page


def test_status_chips_render_from_existing_safe_summary_keys(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert 'id="dashboard-home-status-chips"' in page
    assert "function renderDashboardHome(summary)" in page
    for key in ["summary.phase", "summary.counts", "summary.lanProtection", "summary.docsCenter"]:
        assert key in page


def test_all_newer_centers_are_linked(tmp_path, monkeypatch):
    home = section(dashboard_page(tmp_path, monkeypatch), "dashboard-home")

    assert "View Evidence Report Center" in home
    assert "View Agent Manifest Health Center" in home
    assert "View Docs/Runbook Center" in home


def test_existing_safety_notes_remain(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "Manual evidence only." in page
    assert "Local readiness summary only." in page
    assert "Local redacted diagnostics only." in page
    assert "Local report metadata only." in page
    assert "Known local manifest directories only." in page
    assert "Approved local Markdown docs only." in page


def test_dashboard_home_has_no_forbidden_new_labels(tmp_path, monkeypatch):
    home = section(dashboard_page(tmp_path, monkeypatch), "dashboard-home").lower()
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

    assert "/dashboard/home" not in route_paths
    assert "/api/dashboard/navigation" not in route_paths
