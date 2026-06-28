from pathlib import Path


CLOSEOUT = Path("docs/local-response-agents-closeout-status.md")
README = Path("README.md")
INDEX = Path("docs/local-response-agents-index.md")

EXPECTED_AGENTS = [
    "Local Research Agent",
    "File/Data Agent",
    "Local Planning Agent",
    "Local Drafting Agent",
    "Local Review Agent",
    "Local Decision Agent",
    "Local Troubleshooting Agent",
    "Local Summarization Agent",
    "Local Extraction Agent",
    "Local Classification Agent",
    "Local Transformation Agent",
    "Local Business Agent",
    "Local Creator Agent",
    "Local School / Robotics Agent",
    "Local Career / Job Search Agent",
    "Local Finance / Loans / Budget Agent",
    "Local Housing / Move / Travel Agent",
    "Local Projects / Portfolio Agent",
    "Local Learning / Study Coach Agent",
    "Local Social / Networking / High-Class Coach Agent",
    "Local Personal Admin / Documents Agent",
    "Local Vehicle / Devices / Gear Agent",
    "Local Life Direction / Values Agent",
    "Local Relationship / Family Agent",
    "Local Emotional Reflection / Resilience Agent",
    "Local Health/Fitness Agent",
    "Local Food / Cooking / Grocery Agent",
    "Local Home / Room / Living Space Agent",
    "Local Legal / Immigration / Official Matters Agent",
    "Local Emergency / Preparedness Agent",
    "Local Culture / Taste / High-Class Lifestyle Agent",
    "Local Hobbies / Adventure Agent",
    "Local Personal Knowledge / Memory Organizer Agent",
    "Local Life Dashboard / Cross-Agent Coordinator",
    "Local Everyday Life Agent",
    "Local Online Presence Agent",
    "Local Security/Safety Agent",
]


def test_closeout_status_docs_file_exists():
    assert CLOSEOUT.exists()


def test_readme_links_closeout_status_note():
    readme_text = README.read_text(encoding="utf-8")

    assert "[Local Response Agents Closeout Status](docs/local-response-agents-closeout-status.md)" in readme_text


def test_index_page_links_closeout_status_note():
    index_text = INDEX.read_text(encoding="utf-8")

    assert "[Local Response Agents Closeout Status](local-response-agents-closeout-status.md)" in index_text


def test_closeout_note_lists_exactly_the_implemented_local_response_agents():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")
    completed_section = closeout_text.split("## Current Local Response-Agent Set", 1)[1].split("## Supporting Docs", 1)[0]
    listed_agents = [line.removeprefix("- ") for line in completed_section.splitlines() if line.startswith("- ")]

    assert listed_agents == EXPECTED_AGENTS


def test_closeout_note_links_supporting_docs():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")

    assert "local-response-agents-index.md" in closeout_text
    assert "local-response-agents-smoke-runbook.md" in closeout_text
    assert "local-response-agents-smoke-evidence-template.md" in closeout_text


def test_closeout_note_includes_evidence_level():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "targeted test files cover the local response-agent docs and catalog expectations" in lower_closeout
    assert "does not claim a fresh test run" in lower_closeout
    assert "github read-only verification after manual push" in lower_closeout
    assert "no ci run claimed" in lower_closeout
    assert "no full-suite validation claimed" in lower_closeout
    assert "no clean windows vm validation claimed" in lower_closeout


def test_closeout_note_includes_safety_boundaries():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "response-only or metadata-only local behavior" in lower_closeout
    assert "no paid apis" in lower_closeout
    assert "no connectors" in lower_closeout
    assert "no oauth or account access" in lower_closeout
    assert "no browser automation" in lower_closeout
    assert "no cloud sync" in lower_closeout
    assert "no sending, posting, or purchases" in lower_closeout
    assert "no task persistence for response-only agents" in lower_closeout
    assert "no file mutation for response-only agents" in lower_closeout
    assert "no validation or certification claims" in lower_closeout
    assert "no creator youtube, social, account, analytics" in lower_closeout
    assert "copyright-clearance" in lower_closeout
    assert "monetization-guarantee" in lower_closeout
    assert "no school/robotics school portal, registrar, handshake" in lower_closeout
    assert "official-academic-validation" in lower_closeout
    assert "research-placement" in lower_closeout
    assert "no career/job-search linkedin, handshake, job-board" in lower_closeout
    assert "resume-upload" in lower_closeout
    assert "official-career-validation" in lower_closeout
    assert "hiring-certainty" in lower_closeout
    assert "salary-certainty" in lower_closeout
    assert "no finance/budget bank, credit-card, loan-servicer" in lower_closeout
    assert "payments, transfers, purchases, trades" in lower_closeout
    assert "no housing/move/travel apartment-site, listing, map, location" in lower_closeout
    assert "lease-signing, application-submission, landlord-messaging" in lower_closeout
    assert "neighborhood-safety-validation" in lower_closeout
    assert "no projects/portfolio github, repo, filesystem, account" in lower_closeout
    assert "repo-inspection" in lower_closeout
    assert "code-review-validation" in lower_closeout
    assert "no learning/study school-portal, lms, calendar, task" in lower_closeout
    assert "assignment-submission" in lower_closeout
    assert "mastery-validation" in lower_closeout
    assert "no social/networking contacts, email, calendar" in lower_closeout
    assert "private-information-identification" in lower_closeout
    assert "etiquette-certification" in lower_closeout
    assert "no personal-admin/document-reading" in lower_closeout
    assert "portal, account, cloud-drive" in lower_closeout
    assert "official-submission-validation" in lower_closeout
    assert "no vehicle/devices/gear device-access" in lower_closeout
    assert "obd-access, bluetooth-access, network-scanning" in lower_closeout
    assert "airspace-validation" in lower_closeout
    assert "no life-direction/values files" in lower_closeout
    assert "health-data, finance-data, school-portals" in lower_closeout
    assert "therapy-claims, diagnosis, treatment-plan, crisis-intervention" in lower_closeout
    assert "no relationship/family contacts, messages, dms, email" in lower_closeout
    assert "social-platform, location, photos, files, accounts" in lower_closeout
    assert "private-information-identification" in lower_closeout
    assert "manipulation, coercion, deception, harassment, stalking" in lower_closeout
    assert "relationship-outcome-certainty" in lower_closeout
    assert "conflict-resolution-guarantee" in lower_closeout
    assert "no emotional-reflection/resilience journals, files, health-records" in lower_closeout
    assert "messages, contacts, accounts, calendars, tasks, wearables" in lower_closeout
    assert "appointment-scheduling, contact-action, file-mutation" in lower_closeout
    assert "medical-advice, psychiatric-advice, medication-advice" in lower_closeout
    assert "mental-health-validation, medical-validation, psychiatric-validation" in lower_closeout
    assert "isolation-from-support" in lower_closeout
    assert "financial-advice-validation" in lower_closeout
    assert "investment-advice-validation" in lower_closeout
    assert "repayment-certainty" in lower_closeout
    assert "no health, fitness, medical, clinical" in lower_closeout
    assert "diagnosis, treatment, medication, supplement" in lower_closeout
    assert "no everyday-life calendar, task, email, contact, location" in lower_closeout
    assert "execution, persistence, completion, scheduling" in lower_closeout
    assert "no online-presence social, platform, account, analytics" in lower_closeout
    assert "reputation-verification" in lower_closeout
    assert "follower-growth" in lower_closeout
    assert "no security/safety scans, commands, device inspection" in lower_closeout
    assert "secret reads" in lower_closeout
    assert "security-certification" in lower_closeout


def test_closeout_note_says_it_does_not_start_future_work():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "does not start v0.2" in lower_closeout
    assert "packaging" in lower_closeout
    assert "production tauri" in lower_closeout
    assert "full pairing" in lower_closeout
    assert "future connectors" in lower_closeout
    assert "private-alpha certification" in lower_closeout


def test_closeout_note_avoids_private_paths_and_sensitive_examples():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")
    lower_closeout = closeout_text.lower()
    forbidden = [
        "c:\\users\\",
        "c:/users/",
        ".env",
        "sk-",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password:",
        "credential:",
        "credentials:",
    ]

    assert all(item not in lower_closeout for item in forbidden)
    assert "@" not in closeout_text


def test_closeout_note_does_not_say_response_agent_set_is_fixed_at_11_or_12():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "fixed at 11" not in lower_closeout
    assert "fixed at 12" not in lower_closeout
    assert "expanding local response-agent set" in lower_closeout
