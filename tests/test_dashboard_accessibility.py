import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def dashboard_page(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    dashboard = DashboardService(conn, workspace, tmp_path / "data" / "jarvis", workspace / "connectors")
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return app_module.local_dashboard().body.decode("utf-8")


def dashboard_home(page):
    start = page.index('id="dashboard-home"')
    end = page.index('id="dashboard-status"')
    return page[start:end]


def test_skip_link_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert 'class="skip-link"' in page
    assert 'href="#dashboard-home"' in page
    assert "Skip to Dashboard Home" in page


def test_focus_style_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert ":focus-visible" in page
    assert "outline: 3px solid" in page
    assert ".skip-link:focus" in page


def test_shortcut_help_text_exists(tmp_path, monkeypatch):
    home = dashboard_home(dashboard_page(tmp_path, monkeypatch))

    assert 'id="dashboard-shortcut-help"' in home
    assert "/ focuses section search" in home
    assert "Escape clears the filter" in home
    assert "e expands all sections" in home
    assert "c collapses all sections" in home


def test_search_focus_shortcut_handler_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "event.key === '/'" in page
    assert "bindDashboardKeyboardShortcuts();" in page
    assert "search.focus()" in page
    assert "event.preventDefault()" in page


def test_escape_clear_filter_handler_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "event.key === 'Escape'" in page
    assert "clearDashboardSectionFilter()" in page
    assert "filterDashboardSections('')" in page


def test_expand_and_collapse_keyboard_shortcuts_exist(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "event.key.toLowerCase() === 'e'" in page
    assert "setDashboardSectionsCollapsed(false)" in page
    assert "event.key.toLowerCase() === 'c'" in page
    assert "setDashboardSectionsCollapsed(true)" in page


def test_shortcuts_ignore_typing_inside_inputs_textareas_selects_only(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "function isDashboardTypingTarget(target)" in page
    assert "tagName === 'input'" in page
    assert "tagName === 'textarea'" in page
    assert "tagName === 'select'" in page


def test_no_new_backend_endpoint_required():
    route_paths = {route.path for route in app_module.app.routes}

    assert "/dashboard/keyboard" not in route_paths
    assert "/api/dashboard/accessibility" not in route_paths


def test_safety_note_text_still_exists(tmp_path, monkeypatch):
    page = dashboard_page(tmp_path, monkeypatch)

    assert "Manual evidence only." in page
    assert "Local readiness summary only." in page
    assert "Local redacted diagnostics only." in page
    assert "Local report metadata only." in page
    assert "Known local manifest directories only." in page
    assert "Approved local Markdown docs only." in page


def test_forbidden_labels_absent_from_new_accessibility_area(tmp_path, monkeypatch):
    home = dashboard_home(dashboard_page(tmp_path, monkeypatch)).lower()
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
