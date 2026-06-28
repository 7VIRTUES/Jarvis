from pathlib import Path


TEMPLATE = Path("docs/local-response-agents-smoke-evidence-template.md")
README = Path("README.md")
RUNBOOK = Path("docs/local-response-agents-smoke-runbook.md")
INDEX = Path("docs/local-response-agents-index.md")

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
    "POST /agents/health-fitness/local-plan",
    "POST /agents/everyday-life/local-plan",
    "POST /agents/online-presence/local-plan",
    "POST /agents/security-safety/local-review",
    "POST /agents/food-cooking-grocery/local-plan",
    "POST /agents/home-room-living-space/local-plan",
    "POST /agents/legal-immigration-official/local-plan",
    "POST /agents/emergency-preparedness/local-plan",
    "POST /agents/culture-taste-high-class-lifestyle/local-plan",
    "POST /agents/hobbies-adventure/local-plan",
    "POST /agents/personal-knowledge-memory-organizer/local-plan",
    "POST /agents/life-dashboard-coordinator/local-plan",
]


def test_evidence_template_docs_file_exists():
    assert TEMPLATE.exists()


def test_readme_links_evidence_template():
    readme_text = README.read_text(encoding="utf-8")

    assert "[Local Response Agents Smoke Evidence Template](docs/local-response-agents-smoke-evidence-template.md)" in readme_text


def test_smoke_runbook_links_evidence_template():
    runbook_text = RUNBOOK.read_text(encoding="utf-8")

    assert "[Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)" in runbook_text


def test_index_page_links_evidence_template():
    index_text = INDEX.read_text(encoding="utf-8")

    assert "[Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)" in index_text


def test_template_includes_exactly_the_expected_endpoint_strings():
    template_text = TEMPLATE.read_text(encoding="utf-8")

    assert [endpoint for endpoint in EXPECTED_ENDPOINTS if endpoint in template_text] == EXPECTED_ENDPOINTS
    assert template_text.count("POST /agents/") == 37


def test_template_includes_required_metadata_fields():
    lower_template = TEMPLATE.read_text(encoding="utf-8").lower()

    assert "tester:" in lower_template
    assert "date/time:" in lower_template
    assert "machine/environment:" in lower_template
    assert "jarvis commit sha:" in lower_template
    assert "jarvis run mode:" in lower_template
    assert "local url used:" in lower_template
    assert "loopback or lan:" in lower_template
    assert "lan token behavior tested separately: yes/no" in lower_template


def test_template_includes_per_endpoint_evidence_fields():
    lower_template = TEMPLATE.read_text(encoding="utf-8").lower()
    fields = [
        "request sent: yes/no",
        "response received: yes/no",
        "agentid matched: yes/no",
        "local-only status/mode present: yes/no",
        "safety fields checked: yes/no",
        "no external/connector behavior observed: yes/no",
        "notes:",
    ]

    for field in fields:
        assert lower_template.count(field) == 30


def test_template_includes_known_limitations():
    lower_template = TEMPLATE.read_text(encoding="utf-8").lower()

    assert "known limitations of this evidence" in lower_template
    assert "does not prove ci validation" in lower_template
    assert "does not prove full-suite validation" in lower_template
    assert "does not prove clean windows vm validation" in lower_template
    assert "does not prove lan token boundary unless separately tested" in lower_template
    assert "does not prove private-alpha certification" in lower_template
    assert "does not prove production readiness" in lower_template
    assert "does not prove security certification" in lower_template


def test_template_includes_do_not_include_exclusions():
    template_text = TEMPLATE.read_text(encoding="utf-8")

    assert "Do Not Include" in template_text
    assert "Secrets." in template_text
    assert "Tokens." in template_text
    assert "Credentials." in template_text
    assert "`.env` values." in template_text
    assert "Private paths." in template_text
    assert "Account identifiers." in template_text
    assert "Real email addresses." in template_text
    assert "Protected file contents." in template_text


def test_template_avoids_private_paths_fake_secrets_credentials_and_email_examples():
    template_text = TEMPLATE.read_text(encoding="utf-8")
    lower_template = template_text.lower()
    forbidden = [
        "c:\\users\\",
        "c:/users/",
        "sk-",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password:",
        "credential:",
    ]

    assert all(item not in lower_template for item in forbidden)
    assert "@" not in template_text
