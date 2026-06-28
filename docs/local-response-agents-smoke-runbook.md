# Local Response Agents Manual Smoke Runbook

This runbook gives safe manual request-body examples for the 29 implemented local response agents.

These examples are manual local checks only. They are not automated certification, CI validation, full-suite validation, clean Windows VM validation, LAN token validation, private-alpha certification, production readiness, or security certification.

To record manual observations, use the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md).

## Prerequisites

- Jarvis Core is running locally.
- Use loopback/local dashboard access, such as `http://127.0.0.1:8000`.
- For non-loopback LAN access, existing dashboard token rules apply.
- Use the JSON request bodies below with a local API client or other loopback-only manual request tool.
- Do not include secrets, tokens, login details, account names, real emails, private local paths, or protected content in smoke inputs.

## Global Safety Note

- No paid APIs.
- No connectors.
- No OAuth or account access.
- No browser automation.
- No cloud sync.
- No sending, posting, or purchases.
- No file mutation for response-only agents.
- No task persistence for response-only agents.
- No CI, clean VM, private-alpha, production, or security certification claims.

## Expected Response Checks

For each manual response, check the relevant fields without treating the result as validation or certification:

- `agentId` matches the target agent.
- `status` is local-only, or the response includes a local-only `mode`.
- Safety fields show no external services.
- Safety fields show no connector execution.
- Safety fields show no persistence or mutation for response-only agents.
- Limitations or warnings do not claim external verification, CI validation, clean VM validation, LAN token boundary proof, private-alpha certification, production readiness, or security certification.

## 1. Local Research Agent

Endpoint: `POST /agents/research/local-brief`

Example JSON request body:

```json
{
  "topic": "Local alpha reviewer notes",
  "notes": "Reviewers need a concise local-only brief. The work should avoid external services and avoid validation claims.",
  "sourceTitles": ["Reviewer notes"],
  "questions": ["What should reviewers focus on?"],
  "outputType": "brief"
}
```

Expected response checks:

- `agentId` is `local_research_agent`.
- `status` or `mode` indicates local-only operation.
- Safety fields show no browsing, paid APIs, connectors, account access, or file mutation.

## 2. File/Data Agent

Endpoint: `POST /agents/files/local-summary`

This example requires a registered project named `Jarvis`. The File/Data Agent accepts a registered `projectName` only and does not accept raw arbitrary paths.

Example JSON request body:

```json
{
  "projectName": "Jarvis"
}
```

Expected response checks:

- `agentId` is `file_data_agent`.
- `status` or `mode` indicates local-only registered-project metadata.
- Safety fields show no arbitrary path scanning, protected-content reads, uploads, command execution, or mutation.

## 3. Local Planning Agent

Endpoint: `POST /agents/planning/local-plan`

Example JSON request body:

```json
{
  "goal": "Prepare a local manual smoke checklist",
  "contextNotes": "The checklist should exercise response-only agents without claiming certification.",
  "constraints": ["No external services", "No task creation"],
  "resources": ["Existing local docs"],
  "blockers": ["Needs human review"],
  "timeframe": "One local session",
  "desiredOutputType": "checklist"
}
```

Expected response checks:

- `agentId` is `local_planning_agent`.
- `status` or `mode` indicates local-only response-only planning.
- Safety fields show no task persistence, reminders, calendar/email actions, external services, or mutation.

## 4. Local Drafting Agent

Endpoint: `POST /agents/drafting/local-draft`

Example JSON request body:

```json
{
  "purpose": "Draft a note for local reviewers",
  "audience": "Local manual testers",
  "notes": "Ask reviewers to try the local smoke examples and report confusing wording.",
  "tone": "clear",
  "format": "message",
  "constraints": ["No hype", "No certification claims"],
  "mustInclude": ["manual local checks only"],
  "mustAvoid": ["guaranteed"]
}
```

Expected response checks:

- `agentId` is `local_drafting_agent`.
- `status` or `mode` indicates local-only response-only drafting.
- Safety fields show no draft persistence, email sending, public posting, account access, file writes, or connectors.

## 5. Local Review Agent

Endpoint: `POST /agents/review/local-review`

Example JSON request body:

```json
{
  "subject": "Manual smoke runbook wording",
  "content": "The runbook should be clear that checks are local and manual. It should not claim CI, clean VM validation, or certification.",
  "reviewType": "safety",
  "audience": "Local maintainers",
  "criteria": ["Clear scope", "No validation overclaims"],
  "constraints": ["No external verification claims"],
  "severity": "balanced"
}
```

Expected response checks:

- `agentId` is `local_review_agent`.
- `status` or `mode` indicates local-only response-only review.
- Safety fields show no fact verification, repo inspection, tests, persistence, file access, or connectors.

## 6. Local Decision Agent

Endpoint: `POST /agents/decision/local-decision`

Example JSON request body:

```json
{
  "decision": "Choose a manual smoke check format",
  "options": ["Short checklist", "Long worksheet"],
  "criteria": ["Easy to repeat", "Low risk of overclaiming"],
  "constraints": ["No automation", "No external services"],
  "priorities": ["Clarity", "Safety"],
  "contextNotes": "The result should help local testers without creating persistent decisions.",
  "decisionStyle": "safest"
}
```

Expected response checks:

- `agentId` is `local_decision_agent`.
- `status` or `mode` indicates local-only response-only decision support.
- Safety fields show no professional validation, purchases, sending, posting, persistence, file access, or external calls.

## 7. Local Troubleshooting Agent

Endpoint: `POST /agents/troubleshooting/local-triage`

Example JSON request body:

```json
{
  "problem": "A manual smoke response looks incomplete",
  "symptoms": ["Expected safety fields are missing from the response"],
  "errorMessages": ["No error message was shown"],
  "environmentNotes": "Local Jarvis Core manual smoke session on loopback.",
  "attemptedFixes": ["Refreshed the local API client"],
  "constraints": ["No command execution", "No file inspection"],
  "urgency": "normal",
  "troubleshootingType": "workflow_issue"
}
```

Expected response checks:

- `agentId` is `local_troubleshooting_agent`.
- `status` or `mode` indicates local-only response-only troubleshooting.
- Safety fields show no command execution, file or log reads, repo inspection, repair actions, downloads, uploads, or mutation.

## 8. Local Summarization Agent

Endpoint: `POST /agents/summarization/local-summary`

Example JSON request body:

```json
{
  "title": "Manual smoke notes",
  "content": "The local response agents returned structured outputs. Reviewers should check agent IDs, local-only status, and safety flags.",
  "summaryType": "bullets",
  "audience": "Local maintainers",
  "detailLevel": "medium",
  "focusAreas": ["safety fields", "manual checks"],
  "mustPreserve": ["local-only status"],
  "mustAvoid": ["certified"]
}
```

Expected response checks:

- `agentId` is `local_summarization_agent`.
- `status` or `mode` indicates local-only response-only summarization.
- Safety fields show no file reads, document retrieval, source or citation verification, persistence, repo inspection, or tests.

## 9. Local Extraction Agent

Endpoint: `POST /agents/extraction/local-extract`

Example JSON request body:

```json
{
  "title": "Manual smoke findings",
  "content": "Agent ID should match. Status should be local-only. Safety flags should show no connectors, no persistence, and no mutation.",
  "extractionType": "requirements",
  "focusAreas": ["response checks", "safety boundaries"],
  "mustCapture": ["no connectors"],
  "mustIgnore": ["certified"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_extraction_agent`.
- `status` or `mode` indicates local-only response-only extraction.
- Safety fields show no file reads, document retrieval, source or citation verification, task creation, persistence, repo inspection, or tests.

## 10. Local Classification Agent

Endpoint: `POST /agents/classification/local-classify`

Example JSON request body:

```json
{
  "title": "Manual smoke triage",
  "content": "README link updates are documentation work. Safety wording review is high priority.",
  "items": ["Check README link", "Review safety wording"],
  "classificationType": "priority",
  "labels": ["docs", "safety"],
  "criteria": ["manual review impact"],
  "constraints": ["no task creation"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_classification_agent`.
- `status` or `mode` indicates local-only response-only classification.
- Safety fields show no file reads, document retrieval, source or citation verification, task creation, agent calls, persistence, or certification.

## 11. Local Transformation Agent

Endpoint: `POST /agents/transformation/local-transform`

Example JSON request body:

```json
{
  "title": "Manual smoke notes",
  "content": "Check agent ID. Confirm local-only status. Review safety flags.",
  "items": ["Check agent ID", "Confirm local-only status", "Review safety flags"],
  "targetFormat": "checklist",
  "audience": "Local maintainers",
  "constraints": ["No file export"],
  "mustPreserve": ["local-only status"],
  "mustAvoid": ["certified"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_transformation_agent`.
- `status` or `mode` indicates local-only response-only transformation.
- Safety fields show no file reads or writes, document/spreadsheet/deck/export creation, persistence, repo inspection, tests, or connectors.

## 12. Local Business Agent

Endpoint: `POST /agents/business/local-brief`

Example JSON request body:

```json
{
  "businessName": "Neighborhood Meal Prep Studio",
  "businessIdea": "Offer small-batch weekly meal prep kits for busy local households.",
  "targetCustomer": "Busy families who want simple weeknight meals",
  "problem": "Weeknight cooking feels rushed and planning takes too much time.",
  "offer": "Pre-portioned local meal prep kits with simple instructions.",
  "pricingNotes": "Pilot a simple per-kit price and review customer feedback manually.",
  "operationsNotes": "Start with a small menu, local pickup window, and manual order tracking.",
  "marketingNotes": "Explain convenience, freshness, and predictable weekly planning.",
  "constraints": ["Manual local pilot only", "No paid ads until the offer is clearer"],
  "resources": ["Home kitchen planning notes", "Local ingredient supplier list"],
  "risks": ["Demand may be uncertain", "Operational capacity may be limited"],
  "goals": ["Validate interest manually", "Prepare a small launch checklist"],
  "desiredOutputType": "business_brief"
}
```

Expected response checks:

- `agentId` is `local_business_agent`.
- `status` or `mode` indicates local-only response-only business planning.
- Safety fields show manual-input-only behavior with no connectors, paid APIs, account access, payment actions, purchases, CRM access, file access, persistence, command execution, mutation, professional-advice validation, or compliance certification.
- Limitations do not claim market validation, revenue validation, legal/tax/financial/accounting advice, compliance review, private-alpha certification, production readiness, or security certification.

## 13. Local Creator Agent

Endpoint: `POST /agents/creator/local-plan`

Example JSON request body:

```json
{
  "creatorName": "Local Workshop Channel",
  "platforms": ["Video channel", "Short-form clips"],
  "niche": "Local-first software workflows",
  "audience": "Builders who want practical local tools",
  "contentIdea": "Explain how a local-only planning assistant stays review-friendly.",
  "goals": ["Clarify the idea", "Draft an outline", "Plan repurposing options"],
  "tone": "Practical and clear",
  "formatNotes": "Short explainer with a simple three-part structure.",
  "productionResources": ["Screen notes", "Demo outline"],
  "constraints": ["No platform claims", "No live trend verification"],
  "existingContentNotes": "Previous notes focus on local-only boundaries and manual review.",
  "desiredOutputType": "creator_brief"
}
```

Expected response checks:

- `agentId` is `local_creator_agent`.
- `status` or `mode` indicates local-only response-only creator planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, YouTube access, social platform access, analytics access, scraping, upload, public posting, scheduling, messaging, file access, database writes, task persistence, shell execution, mutation, copyright clearance, platform compliance validation, monetization guarantee, or certification claims.
- Limitations do not claim follower growth, monetization success, trend validation, copyright clearance, brand deal validation, platform compliance, algorithm certainty, private-alpha certification, production readiness, or security certification.

## 14. Local School / Robotics Agent

Endpoint: `POST /agents/school-robotics/local-plan`

Example JSON request body:

```json
{
  "studentName": "Local Student",
  "schoolName": "Northeastern",
  "programName": "Robotics-focused engineering plan",
  "termOrTimeline": "Next two academic terms",
  "academicGoal": "Prepare for robotics research, Vascular-Twin planning, and a stronger co-op search.",
  "roboticsFocus": "Robot perception, controls, simulation, and applied health robotics.",
  "courses": ["Robotics foundations", "Computer vision", "Control systems"],
  "professorsOrLabs": ["User-provided robotics lab note", "User-provided health robotics research note"],
  "projects": ["Vascular-Twin planning prototype", "Small robot perception demo"],
  "constraints": ["Manual planning only", "No live course availability verification"],
  "resources": ["Advisor notes", "Campus career center notes", "Robotics club notes"],
  "currentPreparation": "Completed introductory programming and early robotics reading.",
  "desiredOutputType": "school_brief"
}
```

Expected response checks:

- `agentId` is `local_school_robotics_agent`.
- `status` or `mode` indicates local-only response-only school and robotics planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, school portal access, email sending, calendar access, registrar access, financial-aid access, job application submission, file access, database writes, task persistence, shell execution, mutation, official academic validation, or certification claims.
- Limitations do not claim school portal access, live course verification, email sending, class registration, job submission, admission, enrollment, financial-aid, visa, course-registration, co-op, professor-response, research-placement, graduation, employment, private-alpha certification, production readiness, or security certification.

## 15. Local Career / Job Search Agent

Endpoint: `POST /agents/career/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Career Profile",
  "careerGoal": "Prepare for robotics software internships and co-op conversations.",
  "targetRoles": ["Robotics software intern", "Computer vision intern"],
  "targetIndustries": ["Robotics", "Health technology"],
  "currentExperience": "Course projects and local planning work in robotics and software.",
  "educationNotes": "Engineering student building robotics and applied software experience.",
  "skills": ["Python", "C++", "Computer vision", "Controls", "Technical writing"],
  "projects": ["Vascular-Twin planning prototype", "Robot perception demo"],
  "resumeNotes": "Emphasize project evidence, measurable scope, and manual review wording.",
  "jobSearchNotes": "Focus on a small manually reviewed target list.",
  "networkingNotes": "Prepare respectful informational conversation scripts.",
  "constraints": ["Manual planning only", "No live job-board verification"],
  "desiredOutputType": "career_brief"
}
```

Expected response checks:

- `agentId` is `local_career_agent`.
- `status` or `mode` indicates local-only response-only career and job-search planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, job-board access, school portal access, email sending, calendar access, contact access, job application submission, resume upload, messaging, file access, database writes, task persistence, shell execution, mutation, official career validation, legal validation, or certification claims.
- Limitations do not claim account access, live job verification, applying, messaging, scheduling, resume upload, job placement, interview guarantee, hiring certainty, salary certainty, visa or legal validation, employment-law advice, private-alpha certification, production readiness, or security certification.

## 16. Local Finance / Loans / Budget Agent

Endpoint: `POST /agents/finance-budget/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Finance Plan",
  "financialGoal": "Prepare a manual budget for Boston move costs, student loans, and savings.",
  "incomeNotes": "Monthly income estimate from user-provided notes only.",
  "expenseNotes": "Recurring food, transit, phone, utilities, and school-related costs.",
  "debtNotes": "Student loan and small revolving balance notes for manual review.",
  "loanNotes": "Student loan repayment options need official servicer confirmation.",
  "rentHousingNotes": "Compare rent affordability for shared Boston housing.",
  "moveCostNotes": "Estimate deposit, first month, moving supplies, and transit setup.",
  "savingsNotes": "Build a small emergency cushion before optional spending.",
  "spendingNotes": "Review dining out, subscriptions, and hobby spending manually.",
  "constraints": ["Manual planning only", "No account connections or live balance checks"],
  "priorities": ["Avoid missed payments", "Protect move-in cash cushion"],
  "desiredOutputType": "finance_brief"
}
```

Expected response checks:

- `agentId` is `local_finance_budget_agent`.
- `status` or `mode` indicates local-only response-only finance, loan, and budget planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, bank access, credit-card access, loan-servicer access, brokerage access, payment actions, purchases, trading actions, credit-report access, tax-portal access, financial-aid access, file access, database writes, task persistence, shell execution, mutation, financial advice validation, tax validation, legal validation, investment advice validation, accounting validation, or certification claims.
- Limitations do not claim account access, payments, trades, transfers, applications, submissions, live verification, financial-advisor validation, tax validation, legal validation, accounting validation, investment validation, credit validation, loan approval, repayment certainty, private-alpha certification, production readiness, or security certification.

## 17. Local Housing / Move / Travel Agent

Endpoint: `POST /agents/housing-move-travel/local-plan`

Example JSON request body:

```json
{
  "planName": "Boston Move Plan",
  "destination": "Boston campus area",
  "housingGoal": "Compare user-provided housing options and prepare a manual move checklist.",
  "timeline": "Move before the fall term starts",
  "budgetNotes": "Estimate rent, deposit, utilities, moving supplies, travel, and emergency buffer manually.",
  "housingOptions": ["Shared apartment near transit", "Student housing option from user notes"],
  "moveItems": ["Laptop and chargers", "Clothes", "Bedding", "Important documents"],
  "transportationNotes": "Compare driving with shipped boxes against flying with checked bags.",
  "commuteNotes": "Review walking, transit, and backup commute assumptions from user notes.",
  "utilitySetupNotes": "Internet, mail forwarding, renter insurance, and move-in inspection need manual confirmation.",
  "constraints": ["Manual planning only", "No live listings or map checks"],
  "priorities": ["Protect budget buffer", "Keep commute reliable", "Avoid rushed move-in"],
  "desiredOutputType": "move_brief"
}
```

Expected response checks:

- `agentId` is `local_housing_move_travel_agent`.
- `status` or `mode` indicates local-only response-only housing, move, commute, setup, and travel planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, map access, location access, booking actions, lease actions, application submission, payment actions, email sending, calendar access, contact access, file access, database writes, task persistence, shell execution, mutation, legal validation, safety validation, price or availability validation, or certification claims.
- Limitations do not claim live listings, apartment-site access, map checks, location access, booking, reservation, lease signing, applications, landlord messaging, tour scheduling, calendar creation, payments, ticket purchases, live availability, current prices, neighborhood safety validation, legal lease review, housing approval, travel booking, commute-time certainty, private-alpha certification, production readiness, or security certification.

## 18. Local Projects / Portfolio Agent

Endpoint: `POST /agents/projects-portfolio/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Portfolio Profile",
  "portfolioGoal": "Prepare a project portfolio plan for robotics software internship conversations.",
  "targetAudience": "Recruiters and technical reviewers reading user-provided portfolio notes.",
  "targetRoles": ["Robotics software intern", "Computer vision intern"],
  "projectNotes": ["Vascular-Twin planning prototype", "Robot perception demo", "Local Jarvis response-agent work"],
  "skills": ["Python", "C++", "Computer vision", "Technical writing"],
  "proofArtifacts": ["Case study draft", "Demo outline", "Screenshot checklist"],
  "currentStatus": "Projects need clearer summaries and manually reviewed proof artifacts.",
  "constraints": ["Manual planning only", "No repo or GitHub inspection"],
  "priorities": ["Show technical depth", "Keep claims human-reviewed", "Make proof easy to scan"],
  "timeline": "Prepare a first portfolio pass before internship outreach.",
  "desiredOutputType": "portfolio_brief"
}
```

Expected response checks:

- `agentId` is `local_projects_portfolio_agent`.
- `status` or `mode` indicates local-only response-only projects and portfolio planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, GitHub access, repo inspection, file access, database writes, task persistence, shell execution, commit actions, push actions, publishing actions, upload actions, mutation, official validation, code review validation, hiring outcome guarantee, or certification claims.
- Limitations do not claim repo access, file reads, GitHub verification, commits, pushes, uploads, publishing, project completion, technical correctness validation, code review validation, hiring certainty, portfolio certification, private-alpha certification, production readiness, or security certification.

## 19. Local Learning / Study Coach Agent

Endpoint: `POST /agents/learning-study/local-plan`

Example JSON request body:

```json
{
  "learnerName": "Local Learner",
  "learningGoal": "Build a steady study plan for robotics controls and computer vision foundations.",
  "topics": ["PID control", "State estimation", "Image filtering", "Camera calibration"],
  "currentLevel": "Comfortable with programming basics; weaker on math-heavy explanations.",
  "timeline": "Prepare over the next six weeks before project work intensifies.",
  "availableTime": "Four 45-minute blocks during the week and one weekend review block.",
  "resources": ["Class notes", "Practice problem set", "User-provided project notes"],
  "weakAreas": ["Deriving equations", "Explaining assumptions", "Remembering formulas"],
  "preferredMethods": ["Active recall", "Practice problems", "Feynman explanations"],
  "constraints": ["Manual planning only", "No LMS or calendar connection"],
  "motivationNotes": "Connect each study block to stronger robotics project confidence.",
  "desiredOutputType": "learning_brief"
}
```

Expected response checks:

- `agentId` is `local_learning_study_agent`.
- `status` or `mode` indicates local-only response-only learning and study planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, school portal access, LMS access, calendar access, task persistence, file access, database writes, external app writes, assignment submission, shell execution, mutation, official academic validation, grade guarantee, exam score guarantee, mastery certification, or certification claims.
- Limitations do not claim portal access, LMS access, file reads, app writes, task or calendar creation, assignment submission, persistence, official tutoring, course credit, academic validation, grade guarantees, exam score certainty, mastery certification, private-alpha certification, production readiness, or security certification.

## 20. Local Social / Networking / High-Class Coach Agent

Endpoint: `POST /agents/social-networking/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Social Profile",
  "socialGoal": "Prepare for a polished robotics networking reception with respectful conversation and follow-up options.",
  "setting": "University networking reception",
  "peopleContext": "Students, alumni, professors, and robotics industry guests may attend.",
  "eventNotes": "Short conversations, light refreshments, and informal introductions after a project showcase.",
  "conversationTopics": ["Robotics projects", "Career paths", "Research interests"],
  "networkingGoals": ["Practice concise introductions", "Ask thoughtful questions", "Identify welcome follow-up opportunities"],
  "presentationNotes": "Aim for calm, clear, and sincere rather than flashy.",
  "constraints": ["Manual planning only", "No contact, email, calendar, or social platform access"],
  "comfortLevel": "Somewhat nervous but willing to practice.",
  "desiredOutputType": "social_brief"
}
```

Expected response checks:

- `agentId` is `local_social_networking_agent`.
- `status` or `mode` indicates local-only response-only social and networking planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, contact access, email sending, calendar access, social platform access, messaging, public posting, profile scraping, location access, file access, database writes, task persistence, shell execution, mutation, manipulation guidance, harassment guidance, stalking guidance, impersonation guidance, outcome guarantees, or certification claims.
- Limitations do not claim contact, email, calendar, social, account, messaging, posting, scheduling, scraping, tracking, location, file, or platform access; sending; persistence; manipulation, harassment, stalking, doxxing, impersonation, evasion help; social outcome guarantees; private-alpha certification; production readiness; or security certification.

## 21. Local Personal Admin / Documents Agent

Endpoint: `POST /agents/personal-admin/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Admin Profile",
  "adminGoal": "Prepare a manual checklist for school forms and loan paperwork before an office appointment.",
  "documentTypes": ["School enrollment form", "Loan deferment paperwork", "Photo ID copy checklist"],
  "deadlines": ["Forms due before the next advising appointment", "Loan paperwork review needed this month"],
  "requirements": ["Confirm required fields", "List supporting records", "Mark signature fields", "Prepare questions for the office"],
  "currentStatus": "Forms are gathered but not fully reviewed.",
  "constraints": ["Manual planning only", "No file, portal, email, calendar, or cloud-drive access"],
  "peopleOrOfficesInvolved": ["School advising office", "Loan servicer help desk"],
  "notes": "User wants a calm readiness review before submitting anything outside Jarvis.",
  "desiredOutputType": "admin_brief"
}
```

Expected response checks:

- `agentId` is `local_personal_admin_agent`.
- `status` or `mode` indicates local-only response-only personal admin and document planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, file reads, file writes, cloud drive access, email sending, calendar access, task persistence, portal access, form submission, upload actions, signature actions, payment actions, database writes, shell execution, mutation, legal validation, tax validation, immigration validation, government validation, school validation, loan validation, identity validation, or certification claims.
- Limitations do not claim document reading, file reading, ID reading, PDF reading, email access, calendar access, portal access, account access, cloud-drive access, submission, upload, signing, payment, scheduling, task creation, persistence, official validation, private-alpha certification, production readiness, or security certification.

## 22. Local Vehicle / Devices / Gear Agent

Endpoint: `POST /agents/vehicle-devices-gear/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Gear Profile",
  "gearGoal": "Prepare a manual readiness checklist for a campus project day with laptop, scooter, and drone gear.",
  "vehicleNotes": "Car may be used for transport; confirm tire pressure and fuel manually before leaving.",
  "deviceNotes": "Laptop, phone, chargers, portable battery, and camera need a pre-trip check.",
  "droneScooterNotes": "Drone and scooter should be reviewed only after checking local rules and battery condition manually.",
  "inventoryItems": ["Laptop", "Phone", "Chargers", "Portable battery", "Camera", "Drone case", "Scooter helmet"],
  "maintenanceConcerns": ["Battery condition", "Tire pressure", "Loose accessories"],
  "troubleshootingNotes": "Phone battery has drained quickly recently; avoid destructive troubleshooting.",
  "packingNotes": "Pack light but include backup charging and safety gear.",
  "constraints": ["Manual planning only", "No diagnostics, device control, vehicle control, maps, or flight actions"],
  "priorities": ["Safety", "Battery readiness", "Reliable project capture"],
  "desiredOutputType": "gear_brief"
}
```

Expected response checks:

- `agentId` is `local_vehicle_devices_gear_agent`.
- `status` or `mode` indicates local-only response-only vehicle, device, and gear planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, file reads, file writes, database writes, task persistence, shell execution, device diagnostics, device control, vehicle diagnostics, vehicle control, OBD access, Bluetooth access, network scanning, location access, map access, drone control, flight actions, repair actions, update actions, reset actions, download actions, purchase actions, booking actions, mutation, professional validation, legal validation, warranty validation, airspace validation, or certification claims.
- Limitations do not claim diagnostics, commands, device control, vehicle control, OBD access, Bluetooth access, network scanning, location or map access, file reads, repairs, updates, resets, downloads, purchases, bookings, flight actions, live verification, guaranteed repair or data recovery outcomes, private-alpha certification, production readiness, or security certification.

## 23. Local Life Direction / Values Agent

Endpoint: `POST /agents/life-direction/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Direction Profile",
  "lifeQuestion": "Clarify the next season across school, career, money, health, projects, relationships, and personal growth.",
  "currentSeason": "Building technical skill, preparing career options, and trying to become more disciplined without burning out.",
  "values": ["Competence", "Integrity", "Health", "Family", "Creative independence"],
  "longTermGoals": ["Become a strong technical builder", "Create durable projects", "Build stable finances"],
  "currentPriorities": ["School progress", "Portfolio projects", "Health habits"],
  "tensionsOrTradeoffs": ["Ambition versus rest", "Many project ideas versus finishing a few"],
  "constraints": ["Manual reflection only", "No calendar, task, account, health, finance, or school portal access"],
  "areasToImprove": ["Consistency", "Focus", "Follow-through"],
  "strengths": ["Curiosity", "Systems thinking", "Persistence"],
  "nonNegotiables": ["No fake claims", "Protect health", "Keep commitments realistic"],
  "reflectionNotes": "User wants a grounded season plan and standards, not therapy or guaranteed outcomes.",
  "desiredOutputType": "life_direction_brief"
}
```

Expected response checks:

- `agentId` is `local_life_direction_agent`.
- `status` or `mode` indicates local-only response-only life direction and values planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, file reads, file writes, database writes, task persistence, calendar access, message sending, public posting, purchases, health data access, finance data access, school portal access, contact access, shell execution, mutation, therapy claims, diagnosis, treatment plan, crisis intervention, legal validation, financial validation, medical validation, outcome guarantee, or certification claims.
- Limitations do not claim file, journal, calendar, task, account, message, health, finance, school portal, contact, connector, persistence, scheduling, posting, purchase, therapy, diagnosis, treatment, crisis intervention, legal validation, financial validation, medical validation, outcome guarantee, private-alpha certification, production readiness, or security certification.

## 24. Local Relationship / Family Agent

Endpoint: `POST /agents/relationships/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Relationship Profile",
  "relationshipGoal": "Prepare a respectful check-in conversation with a family member about improving communication.",
  "relationshipType": "Family",
  "peopleContext": "The user wants to talk with a family member after several tense conversations.",
  "situationNotes": "The goal is to lower tension, ask for clearer expectations, and avoid blame.",
  "communicationGoals": ["Open calmly", "Ask what would help", "Agree on one next step"],
  "concerns": ["Conversation may become defensive", "Avoid sounding accusatory"],
  "boundaries": ["Pause if voices rise", "No name-calling"],
  "desiredTone": "Warm, direct, and low-pressure",
  "constraints": ["Manual planning only", "No messages, calendar access, contacts, or external services"],
  "desiredOutputType": "relationship_brief"
}
```

Expected response checks:

- `agentId` is `local_relationships_agent`.
- `status` or `mode` indicates local-only response-only relationship and family communication planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, contact access, message access, email sending, calendar access, social platform access, public posting, messaging, profile scraping, location access, file reads, file writes, database writes, task persistence, shell execution, mutation, manipulation guidance, coercion guidance, harassment guidance, stalking guidance, doxxing guidance, impersonation guidance, therapy claims, diagnosis, treatment plan, relationship outcome guarantee, legal validation, safety validation, or certification claims.
- Limitations do not claim contact, message, DM, email, calendar, social-platform, location, photo, file, account, connector, browsing, scraping, sending, posting, scheduling, tracking, persistence, mutation, therapy, diagnosis, treatment, relationship outcome certainty, conflict resolution guarantee, legal validation, safety validation, emotional certainty, private-alpha certification, production readiness, or security certification.

## 25. Local Emotional Reflection / Resilience Agent

Endpoint: `POST /agents/emotional-reflection/local-reflect`

Example JSON request body:

```json
{
  "profileName": "Local Reflection Profile",
  "reflectionGoal": "Reset after a stressful school and project week without turning it into self-criticism.",
  "currentMoodNotes": "Tired, frustrated, and trying to regain momentum.",
  "stressors": ["Behind on study plan", "Project uncertainty", "Low sleep"],
  "energyNotes": "Energy is better in the morning and lower after dinner.",
  "recentWins": ["Finished one project task", "Asked for clarification", "Went for a walk"],
  "currentChallenges": ["Restarting discipline", "Avoiding all-or-nothing thinking"],
  "patternsNoticed": ["Overcommits when motivated", "Skips recovery after hard days"],
  "supportOptions": ["Talk with a trusted person", "Use campus support if distress worsens"],
  "constraints": ["Manual reflection only", "No journals, health records, messages, contacts, calendars, tasks, or external services"],
  "desiredOutputType": "reflection_brief"
}
```

Expected response checks:

- `agentId` is `local_emotional_reflection_agent`.
- `status` or `mode` indicates local-only response-only emotional reflection and resilience planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, file reads, file writes, database writes, task persistence, calendar access, message sending, contact access, health data access, wearable access, shell execution, mutation, therapy claims, diagnosis, treatment plan, crisis intervention, medical validation, psychiatric validation, medication advice, outcome guarantee, or certification claims.
- Limitations do not claim therapy, diagnosis, treatment, crisis service, medical advice, psychiatric advice, medication advice, mental-health validation, medical validation, psychiatric validation, persistence, scheduling, messaging, task creation, reminder creation, journal/file/health-record/message/contact/account/calendar/task/wearable access, private-alpha certification, production readiness, or security certification.

## 26. Local Health/Fitness Agent

Endpoint: `POST /agents/health-fitness/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Wellness Plan",
  "primaryGoal": "Build a steady beginner strength and walking routine.",
  "currentFitnessLevel": "Beginner returning to consistent activity.",
  "ageRange": "adult",
  "heightWeightNotes": "General body-composition goals only; no clinical interpretation requested.",
  "scheduleNotes": "Three short weekday sessions and one longer weekend walk.",
  "equipmentAvailable": ["Adjustable dumbbells", "Yoga mat"],
  "preferredActivities": ["Walking", "Strength training"],
  "dislikedActivities": ["High-impact jumping"],
  "nutritionNotes": "Wants simple balanced meal planning ideas for busy days.",
  "sleepRecoveryNotes": "Wants to improve sleep consistency and avoid overdoing workouts.",
  "constraints": ["Keep sessions short", "No calendar or reminder creation"],
  "injuriesOrLimitations": ["Use conservative intensity and seek professional review for pain."],
  "habitsToBuild": ["Walk after lunch", "Prepare simple breakfast options"],
  "habitsToReduce": ["Skipping movement on busy days"],
  "desiredOutputType": "fitness_brief"
}
```

Expected response checks:

- `agentId` is `local_health_fitness_agent`.
- `status` or `mode` indicates local-only response-only health/fitness planning.
- Safety fields show manual-input-only behavior with no connectors, paid APIs, account access, health connector access, wearable access, medical record access, insurance/pharmacy access, calendar access, persistence, file access, command execution, purchases, email sending, posting, diagnosis, treatment, medication advice, supplement prescription, emergency triage, clinical validation, or mutation.
- Limitations do not claim medical diagnosis, treatment, medical safety validation, nutritionist review, trainer certification, wearable validation, outcome guarantees, private-alpha certification, production readiness, or security certification.

## 27. Local Everyday Life Agent

Endpoint: `POST /agents/everyday-life/local-plan`

Example JSON request body:

```json
{
  "lifeArea": "Household reset",
  "situation": "Prepare for a busy week with chores, errands, and personal admin.",
  "goals": ["Reduce clutter", "Batch errands", "Set up simple evening routines"],
  "constraints": ["Keep the plan manual", "Avoid adding new apps or accounts"],
  "scheduleNotes": "Two short evening blocks and one weekend planning block.",
  "householdNotes": "Shared spaces need a quick reset before the week starts.",
  "errands": ["Return library books", "Pick up basic groceries"],
  "peopleInvolved": ["Household members"],
  "resources": ["Existing checklist", "Reusable bags"],
  "energyNotes": "Energy is lower after work, so keep weekday steps small.",
  "budgetNotes": "Use items already on hand where possible.",
  "desiredOutputType": "life_brief"
}
```

Expected response checks:

- `agentId` is `local_everyday_life_agent`.
- `status` or `mode` indicates local-only response-only everyday-life planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, calendar access, email sending, public posting, purchases, file access, database writes, task persistence, shell execution, smart-home control, location access, mutation, or certification claims.
- Limitations do not claim validation, automation, completion, scheduling, delivery, execution, professional validation, private-alpha certification, production readiness, or security certification.

## 28. Local Online Presence Agent

Endpoint: `POST /agents/online-presence/local-plan`

Example JSON request body:

```json
{
  "profileName": "Local Portfolio Profile",
  "platforms": ["Portfolio site", "Professional profile"],
  "currentBio": "Builder of practical local-first tools and documentation.",
  "goals": ["Clarify positioning", "Draft profile copy", "Plan a few content ideas"],
  "targetAudience": "Collaborators and reviewers interested in local-first software",
  "tone": "Clear, grounded, and practical",
  "strengths": ["Local-first product thinking", "Careful documentation", "Review-friendly implementation"],
  "projects": ["Local assistant dashboard", "Manual evidence runbooks"],
  "contentIdeas": ["Explain a local-only design choice", "Share a short project lesson"],
  "constraints": ["No hype", "No live profile verification"],
  "reputationConcerns": ["Avoid unsupported claims"],
  "desiredOutputType": "presence_brief"
}
```

Expected response checks:

- `agentId` is `local_online_presence_agent`.
- `status` or `mode` indicates local-only response-only online presence planning.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, web browsing, paid APIs, social posting, scheduling, messaging, scraping, analytics access, email sending, public posting, file access, database writes, task persistence, shell execution, mutation, or certification claims.
- Limitations do not claim brand success, follower growth, hiring results, live reputation verification, platform compliance review, public posting, private-alpha certification, production readiness, or security certification.

## 29. Local Security/Safety Agent

Endpoint: `POST /agents/security-safety/local-review`

Example JSON request body:

```json
{
  "reviewName": "Local Account Hygiene Review",
  "situation": "Prepare a manual safety review for a personal account and shared device after a suspicious message.",
  "assetsOrAccounts": ["Personal email account", "Shared laptop"],
  "concerns": ["Suspicious message", "Unclear recovery settings"],
  "currentControls": ["Two-step sign-in is believed to be enabled"],
  "constraints": ["No account access from Jarvis", "No scans or downloads"],
  "riskTolerance": "Cautious",
  "environmentNotes": "Use only user-provided notes for a local checklist.",
  "incidentNotes": "No active emergency reported; prepare notes for manual review.",
  "desiredOutputType": "safety_brief"
}
```

Expected response checks:

- `agentId` is `local_security_safety_agent`.
- `status` or `mode` indicates local-only response-only security/safety review.
- Safety fields show manual-input-only behavior with no external services, connectors, OAuth, account access, file reads, secret reads, browser/cookie access, password-manager access, network scanning, vulnerability scanning, malware scanning, shell execution, downloads, remediation, account recovery, email sending, public posting, purchases, database writes, task persistence, mutation, forensic validation, legal validation, compliance certification, or security certification.
- Limitations do not claim scans, device inspection, account/file/secret access, remediation, forensic validation, legal validation, compliance certification, vulnerability confirmation, incident resolution, system security, private-alpha certification, production readiness, or security certification.

## What This Does Not Prove

- Does not prove CI validation.
- Does not prove full-suite validation.
- Does not prove clean Windows VM validation.
- Does not prove LAN token boundary behavior.
- Does not prove private-alpha certification.
- Does not prove production readiness.
- Does not prove security certification.
