from pathlib import Path


AGENT_DOCS = [
    Path("docs/local-research-agent.md"),
    Path("docs/file-data-agent.md"),
    Path("docs/local-planning-agent.md"),
    Path("docs/local-drafting-agent.md"),
    Path("docs/local-review-agent.md"),
    Path("docs/local-decision-agent.md"),
    Path("docs/local-troubleshooting-agent.md"),
    Path("docs/local-summarization-agent.md"),
    Path("docs/local-extraction-agent.md"),
    Path("docs/local-classification-agent.md"),
    Path("docs/local-transformation-agent.md"),
    Path("docs/local-business-agent.md"),
    Path("docs/local-creator-agent.md"),
    Path("docs/local-school-robotics-agent.md"),
    Path("docs/local-career-agent.md"),
    Path("docs/local-finance-budget-agent.md"),
    Path("docs/local-housing-move-travel-agent.md"),
    Path("docs/local-projects-portfolio-agent.md"),
    Path("docs/local-learning-study-agent.md"),
    Path("docs/local-social-networking-agent.md"),
    Path("docs/local-personal-admin-agent.md"),
    Path("docs/local-vehicle-devices-gear-agent.md"),
    Path("docs/local-life-direction-agent.md"),
    Path("docs/local-relationships-agent.md"),
    Path("docs/local-emotional-reflection-agent.md"),
    Path("docs/local-health-fitness-agent.md"),
    Path("docs/local-everyday-life-agent.md"),
    Path("docs/local-online-presence-agent.md"),
    Path("docs/local-security-safety-agent.md"),
]


def test_all_individual_local_response_agent_docs_exist():
    assert all(path.exists() for path in AGENT_DOCS)


def test_each_agent_doc_links_to_local_response_agents_index():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-index.md" in doc_text


def test_each_agent_doc_links_to_manual_smoke_runbook():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-smoke-runbook.md" in doc_text


def test_each_agent_doc_links_to_smoke_evidence_template():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-smoke-evidence-template.md" in doc_text


def test_each_agent_doc_says_smoke_and_evidence_docs_do_not_prove_validation_or_certification():
    for path in AGENT_DOCS:
        lower_doc = path.read_text(encoding="utf-8").lower()

        assert "manual evidence aids" in lower_doc
        assert "do not prove validation or certification" in lower_doc


def test_health_fitness_doc_includes_non_medical_non_connector_boundaries():
    lower_doc = Path("docs/local-health-fitness-agent.md").read_text(encoding="utf-8").lower()

    assert "not a medical, clinical, wearable, health-app, insurance, pharmacy, lab, or ehr connector" in lower_doc
    assert "does not diagnose, treat, prescribe, interpret labs, provide emergency triage" in lower_doc
    assert "outputs are based only on user-provided inputs" in lower_doc
    assert "qualified professional or emergency service" in lower_doc


def test_everyday_life_doc_includes_manual_only_non_execution_boundaries():
    lower_doc = Path("docs/local-everyday-life-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no calendar, task, email, contact, map, location, finance, smart-home" in lower_doc
    assert "no persistence" in lower_doc
    assert "no execution" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_online_presence_doc_includes_manual_only_non_platform_boundaries():
    lower_doc = Path("docs/local-online-presence-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no social, platform, account, analytics" in lower_doc
    assert "no persistence" in lower_doc
    assert "no execution" in lower_doc
    assert "no live reputation" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_security_safety_doc_includes_manual_only_non_scan_boundaries():
    lower_doc = Path("docs/local-security-safety-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no scans, commands, account access, file reads, secret reads" in lower_doc
    assert "no hacking, exploit, evasion, malware, phishing" in lower_doc
    assert "no forensic validation, legal validation, compliance certification, security certification" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_creator_doc_includes_manual_only_non_platform_boundaries():
    lower_doc = Path("docs/local-creator-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no youtube/social/account connectors" in lower_doc
    assert "no upload, posting, scheduling, scraping, analytics, messaging, live trend verification" in lower_doc
    assert "no copyright clearance, platform compliance validation, monetization guarantee" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_school_robotics_doc_includes_manual_only_non_school_system_boundaries():
    lower_doc = Path("docs/local-school-robotics-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no school portal, email, calendar, registrar, handshake, financial-aid" in lower_doc
    assert "no registration, submission, sending, class registration, job application" in lower_doc
    assert "no live verification" in lower_doc
    assert "no persistence" in lower_doc
    assert "official school or qualified professional confirmation" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_career_doc_includes_manual_only_non_job_system_boundaries():
    lower_doc = Path("docs/local-career-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no linkedin/handshake/job-board/email/calendar/contact/account connectors" in lower_doc
    assert "no applying, submitting, messaging, scheduling, uploading, scraping, browsing, live verification" in lower_doc
    assert "no persistence" in lower_doc
    assert "no job placement, interview guarantee, salary certainty, hiring certainty" in lower_doc
    assert "official or qualified professional confirmation" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_finance_budget_doc_includes_manual_only_non_financial_system_boundaries():
    lower_doc = Path("docs/local-finance-budget-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input-only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no bank/credit-card/loan/brokerage/payment/tax/financial-aid/account connectors" in lower_doc
    assert "no payments, trades, transfers, purchases, applications, submissions, account connections" in lower_doc
    assert "live verification" in lower_doc
    assert "no persistence" in lower_doc
    assert "no financial, tax, legal, accounting, investment, credit, loan-approval" in lower_doc
    assert "official or qualified professional confirmation" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_housing_move_travel_doc_includes_manual_only_non_booking_or_lease_system_boundaries():
    lower_doc = Path("docs/local-housing-move-travel-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no apartment sites, live listings, maps, location access, booking platforms" in lower_doc
    assert "no travel booking, room reservation, lease signing, application submission" in lower_doc
    assert "no claims of live availability, current prices, neighborhood safety validation" in lower_doc
    assert "no browsing, listings, maps, location access, booking" in lower_doc
    assert "official sources or qualified professionals" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_projects_portfolio_doc_includes_manual_only_non_repo_or_publishing_boundaries():
    lower_doc = Path("docs/local-projects-portfolio-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no github/repo/filesystem/account connectors" in lower_doc
    assert "no repo inspection" in lower_doc
    assert "file reads, file writes" in lower_doc
    assert "no file creation, repo edits, issue creation, commits, pushes, uploads, publishing" in lower_doc
    assert "no claims of live github verification" in lower_doc
    assert "employment, legal, ip/copyright, academic, and public-claim concerns" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_learning_study_doc_includes_manual_only_non_school_lms_app_or_validation_boundaries():
    lower_doc = Path("docs/local-learning-study-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no school/lms/calendar/task/file/app/account connectors" in lower_doc
    assert "no school portal access, lms access" in lower_doc
    assert "file reads, file writes" in lower_doc
    assert "no external flashcard creation, calendar event creation, task creation" in lower_doc
    assert "assignment submission" in lower_doc
    assert "no official tutoring, course credit, grade improvement certainty" in lower_doc
    assert "exam score certainty" in lower_doc
    assert "mastery validation" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_social_networking_doc_includes_manual_only_non_platform_tracking_or_manipulation_boundaries():
    lower_doc = Path("docs/local-social-networking-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "no contacts/email/calendar/social-platform/messaging/location/account connectors" in lower_doc
    assert "no contact access, email sending, calendar access" in lower_doc
    assert "public posting, profile scraping, location access" in lower_doc
    assert "no sending, posting, scheduling, scraping, tracking" in lower_doc
    assert "no manipulation, coercion, deception, harassment, stalking, doxxing, impersonation" in lower_doc
    assert "social outcome guarantees" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_personal_admin_doc_includes_manual_only_non_file_portal_submission_or_validation_boundaries():
    lower_doc = Path("docs/local-personal-admin-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "does not read documents, files, ids, pdfs, email, calendars, portals, accounts, cloud drives" in lower_doc
    assert "does not submit forms, send emails, schedule appointments" in lower_doc
    assert "upload files, sign documents, make payments, persist records, mutate files" in lower_doc
    assert "legal, tax, immigration, school, loan, government, compliance, identity, submission" in lower_doc
    assert "official or professional confirmation" in lower_doc
    assert "based only on request-provided data" in lower_doc


def test_vehicle_devices_gear_doc_includes_manual_only_non_diagnostics_control_or_live_verification_boundaries():
    lower_doc = Path("docs/local-vehicle-devices-gear-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "does not access devices, vehicles, drones, files, os settings, apps, accounts, obd, bluetooth" in lower_doc
    assert "gps/location, maps, drone controller data" in lower_doc
    assert "does not run diagnostics, commands, repairs, updates, resets" in lower_doc
    assert "purchases, bookings, flight actions, device control, vehicle control" in lower_doc
    assert "live airspace or map verification" in lower_doc
    assert "repair certainty, data recovery certainty" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_life_direction_doc_includes_manual_only_non_connector_persistence_or_therapy_boundaries():
    lower_doc = Path("docs/local-life-direction-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "does not access files, journals, calendars, tasks, accounts, messages, health data, finance data" in lower_doc
    assert "school portals, contacts, connectors" in lower_doc
    assert "does not persist goals, create tasks, create reminders, schedule events" in lower_doc
    assert "post publicly, purchase anything, mutate files" in lower_doc
    assert "therapy, mental-health diagnosis, treatment, crisis support" in lower_doc
    assert "legal advice, financial advice, medical advice" in lower_doc
    assert "guaranteed success, life-outcome certainty" in lower_doc
    assert "uses only the request body supplied by the local user" in lower_doc


def test_relationships_doc_includes_manual_only_non_contact_platform_or_therapy_boundaries():
    lower_doc = Path("docs/local-relationships-agent.md").read_text(encoding="utf-8").lower()

    assert "local-only" in lower_doc
    assert "manual-input" in lower_doc
    assert "response-only" in lower_doc
    assert "no contacts, messages, dms, email, calendar, social platforms" in lower_doc
    assert "location, photos, files, accounts, connectors" in lower_doc
    assert "no sending, scheduling, posting, scraping, tracking" in lower_doc
    assert "private-information identification" in lower_doc
    assert "no manipulation, coercion, deception, harassment, stalking, doxxing, impersonation" in lower_doc
    assert "jealousy-control, evasion" in lower_doc
    assert "therapy claims, diagnosis, treatment plans" in lower_doc
    assert "relationship outcome certainty" in lower_doc
    assert "conflict resolution guarantees" in lower_doc
    assert "all response content is based only on the request body" in lower_doc


def test_emotional_reflection_doc_includes_manual_only_non_health_journal_connector_or_therapy_boundaries():
    lower_doc = Path("docs/local-emotional-reflection-agent.md").read_text(encoding="utf-8").lower()

    assert "manual-input only" in lower_doc
    assert "local-only" in lower_doc
    assert "response-only" in lower_doc
    assert "not therapy, not diagnosis, not treatment, not crisis service" in lower_doc
    assert "medical advice" in lower_doc
    assert "psychiatric advice" in lower_doc
    assert "medication advice" in lower_doc
    assert "no health, journal, file, message, contact, account, calendar, task, wearable" in lower_doc
    assert "no persistence" in lower_doc
    assert "scheduling, messaging" in lower_doc
    assert "medical, or psychiatric validation" in lower_doc
    assert "output is based only on user-provided input" in lower_doc


def test_agent_docs_do_not_include_private_paths_or_sensitive_examples():
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

    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")
        lower_doc = doc_text.lower()

        assert all(item not in lower_doc for item in forbidden)
        assert "@" not in doc_text
