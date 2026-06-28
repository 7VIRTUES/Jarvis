from __future__ import annotations

from typing import Any

from .web_research import WEB_RESEARCH_AGENT_MODE, WEB_RESEARCH_LIMITATIONS, web_research_agent_metadata


LOCAL_RESPONSE_AGENT_COUNT = 37

LOCAL_RESPONSE_AGENT_BADGES = [
    "manual-input",
    "local-only",
    "response-only",
    "non-persistent",
    "no-connectors",
]

LOCAL_RESPONSE_AGENT_BOUNDARY_FLAGS = {
    "manualInputOnly": True,
    "localOnly": True,
    "responseOnly": True,
    "nonPersistent": True,
    "connectorBehavior": False,
    "accountAccess": False,
    "externalServices": False,
    "automationActions": False,
    "persistence": False,
    "fileMutation": False,
    "emailCalendarSocialPosting": False,
    "purchasesBookingsPaymentsSubmissions": False,
    "officialFilingsEmergencyLegalMedicalFinancialActions": False,
}

LOCAL_RESPONSE_AGENT_CATEGORIES = {
    "Coding/Core": {
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
    },
    "Health/Food/Home": {
        "POST /agents/health-fitness/local-plan",
        "POST /agents/food-cooking-grocery/local-plan",
        "POST /agents/home-room-living-space/local-plan",
    },
    "Safety/Emergency": {
        "POST /agents/legal-immigration-official/local-plan",
        "POST /agents/emergency-preparedness/local-plan",
        "POST /agents/security-safety/local-review",
    },
    "Creativity/Hobbies": {
        "POST /agents/culture-taste-high-class-lifestyle/local-plan",
        "POST /agents/hobbies-adventure/local-plan",
        "POST /agents/creator/local-plan",
    },
    "Knowledge/Coordinator": {
        "POST /agents/personal-knowledge-memory-organizer/local-plan",
        "POST /agents/life-dashboard-coordinator/local-plan",
    },
    "Life/Admin": {
        "POST /agents/everyday-life/local-plan",
        "POST /agents/personal-admin/local-plan",
        "POST /agents/vehicle-devices-gear/local-plan",
        "POST /agents/life-direction/local-plan",
    },
    "Social/Family": {
        "POST /agents/online-presence/local-plan",
        "POST /agents/social-networking/local-plan",
        "POST /agents/relationships/local-plan",
        "POST /agents/emotional-reflection/local-reflect",
    },
    "School/Career": {
        "POST /agents/school-robotics/local-plan",
        "POST /agents/career/local-plan",
        "POST /agents/projects-portfolio/local-plan",
        "POST /agents/learning-study/local-plan",
    },
    "Finance/Housing/Travel": {
        "POST /agents/finance-budget/local-plan",
        "POST /agents/housing-move-travel/local-plan",
    },
}

LOCAL_RESPONSE_AGENT_IDS = {
    "POST /agents/research/local-brief": "local_research_agent",
    "POST /agents/files/local-summary": "file_data_agent",
    "POST /agents/planning/local-plan": "local_planning_agent",
    "POST /agents/drafting/local-draft": "local_drafting_agent",
    "POST /agents/review/local-review": "local_review_agent",
    "POST /agents/decision/local-decision": "local_decision_agent",
    "POST /agents/troubleshooting/local-triage": "local_troubleshooting_agent",
    "POST /agents/summarization/local-summary": "local_summarization_agent",
    "POST /agents/extraction/local-extract": "local_extraction_agent",
    "POST /agents/classification/local-classify": "local_classification_agent",
    "POST /agents/transformation/local-transform": "local_transformation_agent",
    "POST /agents/business/local-brief": "local_business_agent",
    "POST /agents/health-fitness/local-plan": "local_health_fitness_agent",
    "POST /agents/food-cooking-grocery/local-plan": "local_food_cooking_grocery",
    "POST /agents/home-room-living-space/local-plan": "local_home_room_living_space",
    "POST /agents/legal-immigration-official/local-plan": "local_legal_immigration_official_matters",
    "POST /agents/emergency-preparedness/local-plan": "local_emergency_preparedness",
    "POST /agents/culture-taste-high-class-lifestyle/local-plan": "local_culture_taste_high_class_lifestyle",
    "POST /agents/hobbies-adventure/local-plan": "local_hobbies_adventure",
    "POST /agents/personal-knowledge-memory-organizer/local-plan": "local_personal_knowledge_memory_organizer",
    "POST /agents/life-dashboard-coordinator/local-plan": "local_life_dashboard_cross_agent_coordinator",
    "POST /agents/everyday-life/local-plan": "local_everyday_life_agent",
    "POST /agents/online-presence/local-plan": "local_online_presence_agent",
    "POST /agents/security-safety/local-review": "local_security_safety_agent",
    "POST /agents/creator/local-plan": "local_creator_agent",
    "POST /agents/school-robotics/local-plan": "local_school_robotics_agent",
    "POST /agents/career/local-plan": "local_career_agent",
    "POST /agents/finance-budget/local-plan": "local_finance_budget_agent",
    "POST /agents/housing-move-travel/local-plan": "local_housing_move_travel_agent",
    "POST /agents/projects-portfolio/local-plan": "local_projects_portfolio_agent",
    "POST /agents/learning-study/local-plan": "local_learning_study_agent",
    "POST /agents/social-networking/local-plan": "local_social_networking_agent",
    "POST /agents/personal-admin/local-plan": "local_personal_admin_agent",
    "POST /agents/vehicle-devices-gear/local-plan": "local_vehicle_devices_gear_agent",
    "POST /agents/life-direction/local-plan": "local_life_direction_agent",
    "POST /agents/relationships/local-plan": "local_relationships_agent",
    "POST /agents/emotional-reflection/local-reflect": "local_emotional_reflection_agent",
}

LOCAL_RESPONSE_AGENT_USE_WHEN = {
    "Coding/Core": "Use for local notes, planning, review, decision support, summarization, extraction, classification, transformation, and business-planning drafts.",
    "School/Career": "Use for user-provided school, robotics, career, portfolio, and learning/study planning.",
    "Life/Admin": "Use for everyday-life, personal-admin, gear, and life-direction planning from user-provided notes.",
    "Health/Food/Home": "Use for wellness, food, grocery, cooking, room, and home setup planning without clinical, ordering, or device-control behavior.",
    "Social/Family": "Use for online presence, social networking, relationships, and emotional reflection without posting, contact access, therapy, or diagnosis claims.",
    "Finance/Housing/Travel": "Use for budget, loans, housing, moving, commute, and travel planning without transactions, bookings, applications, or live verification.",
    "Safety/Emergency": "Use for legal/official organization, emergency preparedness, and security/safety review without filings, emergency calls, scans, or live awareness.",
    "Creativity/Hobbies": "Use for creator, culture/taste, and hobbies/adventure planning without posting, reservations, purchases, permits, or live rule checks.",
    "Knowledge/Coordinator": "Use for personal knowledge organization and dashboard coordination without file reads, persistence, memory writes, or agent handoffs.",
}

HIGH_STAKES_LIMITATIONS_BY_CATEGORY = {
    "Health/Food/Home": [
        "No clinical certainty, medical diagnosis, treatment, medication, supplement, allergy-safety certainty, or food-safety certification.",
    ],
    "Safety/Emergency": [
        "No legal advice, filing certainty, live emergency awareness, emergency-service calling, scanning, or security certification.",
    ],
    "Finance/Housing/Travel": [
        "No financial-advisor certainty, transactions, payments, bookings, applications, submissions, or live availability/price verification.",
    ],
    "Social/Family": [
        "No therapy, diagnosis, treatment, crisis-intervention certainty, contact access, sending, posting, tracking, or relationship outcome guarantee.",
    ],
    "School/Career": [
        "No admission, grade, mastery, placement, interview, hiring, salary, or job guarantee.",
    ],
}

LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS = {
    "local_research_agent": ("research", "brief", "notes", "questions", "reviewer"),
    "file_data_agent": ("project metadata", "registered project", "project summary"),
    "local_planning_agent": ("plan", "checklist", "schedule", "organize", "workflow"),
    "local_drafting_agent": ("draft", "message", "write", "copy", "announcement"),
    "local_review_agent": ("review", "critique", "feedback", "safety wording"),
    "local_decision_agent": ("decision", "choose", "compare", "options", "tradeoff"),
    "local_troubleshooting_agent": ("troubleshoot", "issue", "problem", "symptom", "error"),
    "local_summarization_agent": ("summarize", "summary", "condense", "recap"),
    "local_extraction_agent": ("extract", "requirements", "pull out", "capture"),
    "local_classification_agent": ("classify", "tag", "label", "priority"),
    "local_transformation_agent": ("transform", "convert", "rewrite", "format"),
    "local_business_agent": ("business", "customer", "offer", "pricing", "operations"),
    "local_health_fitness_agent": ("health", "fitness", "workout", "sleep", "nutrition", "habit"),
    "local_food_cooking_grocery": ("food", "meal", "grocery", "cooking", "pantry", "recipe"),
    "local_home_room_living_space": ("home", "room", "apartment", "cleaning", "furniture", "storage"),
    "local_legal_immigration_official_matters": ("legal", "immigration", "visa", "court", "official", "deadline"),
    "local_emergency_preparedness": ("emergency", "preparedness", "go bag", "fire", "storm", "power outage"),
    "local_culture_taste_high_class_lifestyle": ("culture", "taste", "etiquette", "wardrobe", "dining"),
    "local_hobbies_adventure": ("hobby", "adventure", "drone", "camping", "fishing", "photography"),
    "local_personal_knowledge_memory_organizer": ("knowledge", "memory", "notes", "wiki", "ideas"),
    "local_life_dashboard_cross_agent_coordinator": ("dashboard", "coordinate", "cross-agent", "life areas", "priorities"),
    "local_everyday_life_agent": ("everyday", "errands", "routine", "chores", "household"),
    "local_online_presence_agent": ("online presence", "profile", "bio", "reputation", "platform"),
    "local_security_safety_agent": ("security", "safety", "privacy", "threat", "risk"),
    "local_creator_agent": ("creator", "content", "video", "post idea", "audience"),
    "local_school_robotics_agent": ("school", "robotics", "class", "course", "assignment"),
    "local_career_agent": ("career", "job", "internship", "resume", "interview"),
    "local_finance_budget_agent": ("finance", "budget", "loan", "debt", "rent", "savings"),
    "local_housing_move_travel_agent": ("housing", "move", "travel", "commute", "apartment"),
    "local_projects_portfolio_agent": ("project", "portfolio", "proof", "case study", "demo"),
    "local_learning_study_agent": ("learning", "study", "exam", "topic", "practice"),
    "local_social_networking_agent": ("social", "networking", "event", "conversation", "introduction"),
    "local_personal_admin_agent": ("admin", "document", "paperwork", "form", "appointment"),
    "local_vehicle_devices_gear_agent": ("vehicle", "device", "gear", "drone", "scooter", "packing"),
    "local_life_direction_agent": ("life direction", "values", "goals", "season", "identity"),
    "local_relationships_agent": ("relationship", "family", "friend", "roommate", "communication"),
    "local_emotional_reflection_agent": ("emotion", "stress", "reflection", "resilience", "burnout"),
}


def local_response_agent_category(endpoint: str) -> str:
    for category, endpoints in LOCAL_RESPONSE_AGENT_CATEGORIES.items():
        if endpoint in endpoints:
            return category
    return "Uncategorized"


def local_response_agent_output_types(agent: dict[str, Any]) -> list[str]:
    example = agent.get("exampleRequestBody") if isinstance(agent.get("exampleRequestBody"), dict) else {}
    values = []
    for key in ("outputType", "desiredOutputType", "summaryType", "reviewType", "classificationType", "extractionType", "targetFormat"):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    return list(dict.fromkeys(values or ["summary"]))


def enrich_local_response_agent(agent: dict[str, Any]) -> dict[str, Any]:
    endpoint = str(agent.get("endpoint", ""))
    category = local_response_agent_category(endpoint)
    enriched = dict(agent)
    enriched.setdefault("agentId", LOCAL_RESPONSE_AGENT_IDS.get(endpoint, _fallback_agent_id(enriched.get("name", ""))))
    enriched.setdefault("displayName", enriched.get("name", "Local Response Agent"))
    enriched.setdefault("category", category)
    enriched.setdefault("badges", list(LOCAL_RESPONSE_AGENT_BADGES))
    enriched.setdefault("boundaryFlags", dict(LOCAL_RESPONSE_AGENT_BOUNDARY_FLAGS))
    enriched.setdefault("outputTypes", local_response_agent_output_types(enriched))
    enriched.setdefault("useWhen", LOCAL_RESPONSE_AGENT_USE_WHEN.get(category, "Use for manual local response-agent planning from user-provided inputs."))
    enriched.setdefault("recommendedFor", enriched["useWhen"])
    enriched.update(web_research_agent_metadata())
    return enriched


def get_expected_local_response_agent_count() -> int:
    return LOCAL_RESPONSE_AGENT_COUNT


def discovery_metadata_for_agent(agent: dict[str, Any]) -> dict[str, Any]:
    enriched = enrich_local_response_agent(agent)
    return {
        "agent_id": enriched["agentId"],
        "agentId": enriched["agentId"],
        "name": enriched.get("name", enriched["displayName"]),
        "display_name": enriched["displayName"],
        "displayName": enriched["displayName"],
        "status": enriched.get("status", "implemented_local_only"),
        "mode": enriched.get("mode", ""),
        "category": enriched["category"],
        "endpoint": enriched["endpoint"],
        "docs_link": enriched.get("docsLink", ""),
        "docsLink": enriched.get("docsLink", ""),
        "response_mode": enriched.get("responseMode", "response_only"),
        "responseMode": enriched.get("responseMode", "response_only"),
        "badges": list(enriched["badges"]),
        "boundary_flags": dict(enriched["boundaryFlags"]),
        "boundaryFlags": dict(enriched["boundaryFlags"]),
        "output_types": list(enriched["outputTypes"]),
        "outputTypes": list(enriched["outputTypes"]),
        "use_when": enriched["useWhen"],
        "useWhen": enriched["useWhen"],
        "safety_notes": list(enriched.get("safetyNotes", [])),
        "safetyNotes": list(enriched.get("safetyNotes", [])),
        "examples": [enriched["exampleRequestBody"]],
        "has_connector": False,
        "hasConnector": False,
        "is_local_only": True,
        "isLocalOnly": True,
        "is_manual_input_only": True,
        "isManualInputOnly": True,
        "is_response_only": True,
        "isResponseOnly": True,
        "is_non_persistent": True,
        "isNonPersistent": True,
        "web_research_available": enriched["web_research_available"],
        "webResearchAvailable": enriched["webResearchAvailable"],
        "web_research_mode": enriched["web_research_mode"],
        "webResearchMode": enriched["webResearchMode"],
        "web_research_requires_user_enabled": enriched["web_research_requires_user_enabled"],
        "webResearchRequiresUserEnabled": enriched["webResearchRequiresUserEnabled"],
        "web_research_is_optional": enriched["web_research_is_optional"],
        "webResearchIsOptional": enriched["webResearchIsOptional"],
        "web_research_limitations": list(enriched["web_research_limitations"]),
        "webResearchLimitations": list(enriched["webResearchLimitations"]),
    }


def list_local_agent_categories(agents: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for agent in agents:
        enriched = enrich_local_response_agent(agent)
        groups.setdefault(enriched["category"], []).append(enriched)
    categories = []
    for category_name in LOCAL_RESPONSE_AGENT_CATEGORIES:
        category_agents = groups.get(category_name, [])
        categories.append(
            {
                "id": _category_id(category_name),
                "name": category_name,
                "count": len(category_agents),
                "agent_ids": [agent["agentId"] for agent in category_agents],
                "agents": [
                    {
                        "agent_id": agent["agentId"],
                        "display_name": agent["displayName"],
                        "endpoint": agent["endpoint"],
                    }
                    for agent in category_agents
                ],
            }
        )
    return {
        "status": "local_response_agent_categories",
        "total_count": sum(category["count"] for category in categories),
        "totalCount": sum(category["count"] for category in categories),
        "expected_count": LOCAL_RESPONSE_AGENT_COUNT,
        "expectedCount": LOCAL_RESPONSE_AGENT_COUNT,
        "categories": categories,
    }


def get_local_agent_metadata(agent_id: str, agents: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = _normalize_id(agent_id)
    for agent in agents:
        enriched = enrich_local_response_agent(agent)
        if _normalize_id(enriched["agentId"]) == normalized:
            return {"found": True, "agent": discovery_metadata_for_agent(enriched)}
    return {
        "found": False,
        "agent_id": agent_id,
        "message": "Local response agent metadata was not found.",
        "not_executed_notice": "No local response agent was invoked.",
    }


def build_local_agent_request_template(agent_id: str, agents: list[dict[str, Any]]) -> dict[str, Any]:
    metadata_result = get_local_agent_metadata(agent_id, agents)
    if not metadata_result["found"]:
        return {
            "found": False,
            "agent_id": agent_id,
            "message": "Local response agent request template was not found.",
            "not_executed_notice": "No local response agent was invoked.",
        }
    agent = metadata_result["agent"]
    sample_payload = dict(agent["examples"][0])
    return {
        "found": True,
        "agent_id": agent["agent_id"],
        "endpoint": agent["endpoint"].split(maxsplit=1)[1],
        "catalog_endpoint": agent["endpoint"],
        "method": "POST",
        "recommended_request_fields": list(sample_payload.keys()),
        "default_output_type": _default_output_type(agent["output_types"]),
        "supported_output_types": list(agent["output_types"]),
        "sample_payload": sample_payload,
        "boundary_reminder": "Manual input only, local only, response only, non-persistent, no connectors, no accounts, no external services, and no automatic actions.",
        "high_stakes_limitations": HIGH_STAKES_LIMITATIONS_BY_CATEGORY.get(agent["category"], []),
        "web_research_available": True,
        "web_research_mode": WEB_RESEARCH_AGENT_MODE,
        "web_research_requires_user_enabled": True,
        "web_research_is_optional": True,
        "web_research_limitations": list(WEB_RESEARCH_LIMITATIONS),
        "web_research_context_fields": [
            "Manual public source excerpts may be pasted into an existing text field for review.",
            "No source context is submitted automatically.",
            "Do not add unsupported fields to strict agent schemas unless the user reviews the payload first.",
        ],
    }


def preview_local_agent_route(
    text: str,
    domains_to_consider: list[str] | None,
    preferred_output_type: str,
    urgency_level: str,
    constraints_or_notes: str,
    agents: list[dict[str, Any]],
) -> dict[str, Any]:
    request_text = _clean_text(text)
    domains = [_clean_text(domain).lower() for domain in domains_to_consider or [] if _clean_text(domain)]
    combined = " ".join([request_text, " ".join(domains), preferred_output_type or "", urgency_level or "", constraints_or_notes or ""]).lower()
    scored: list[tuple[int, dict[str, Any], list[str]]] = []
    for agent in agents:
        enriched = enrich_local_response_agent(agent)
        keywords = LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS.get(enriched["agentId"], ())
        reasons = [keyword for keyword in keywords if keyword in combined]
        if domains and enriched["category"].lower() in domains:
            reasons.append(f"category:{enriched['category']}")
        if reasons:
            scored.append((len(reasons), enriched, reasons))
    scored.sort(key=lambda item: (-item[0], item[1]["displayName"]))
    if not scored:
        scored = _fallback_route_agents(agents)
    suggestions = [
        {
            "agent_id": agent["agentId"],
            "display_name": agent["displayName"],
            "category": agent["category"],
            "endpoint": agent["endpoint"],
            "reason": ", ".join(reasons[:4]) if reasons else "Broad manual fallback suggestion.",
            "suggested_only": True,
            "invoked": False,
            "handoff_created": False,
        }
        for _, agent, reasons in scored[:6]
    ]
    return {
        "title": "Local Response-Agent Route Preview",
        "summary": "Suggested local response agents from catalog metadata only. No agent was invoked, no handoff was created, and no state was persisted.",
        "suggested_agents": suggestions,
        "routing_reasoning": [
            f"{suggestion['display_name']}: {suggestion['reason']}" for suggestion in suggestions
        ],
        "not_executed_notice": "Route preview is suggestions only; it does not invoke agents, create handoffs, create tasks, schedule reminders, mutate files, or access external services.",
        "local_only_boundaries": [
            "Manual-input only.",
            "Local-only.",
            "Response-only.",
            "Non-persistent.",
            "No connectors, accounts, external services, file mutation, task creation, reminders, purchases, bookings, submissions, filings, emergency calls, legal actions, medical decisions, or financial transactions.",
        ],
        "limitations": [
            "Uses simple deterministic keyword/category matching against local catalog metadata.",
            "Ambiguous requests should be reviewed manually before choosing an agent.",
            "High-stakes requests require qualified professionals or official sources before action.",
        ],
        "follow_up_questions": _route_follow_up_questions(request_text, domains, preferred_output_type, urgency_level),
    }


def validate_catalog_consistency(agents: list[dict[str, Any]]) -> dict[str, Any]:
    enriched_agents = [enrich_local_response_agent(agent) for agent in agents]
    agent_ids = [agent["agentId"] for agent in enriched_agents]
    endpoints = [agent["endpoint"] for agent in enriched_agents]
    categories = [agent["category"] for agent in enriched_agents]
    return {
        "expected_count": LOCAL_RESPONSE_AGENT_COUNT,
        "actual_count": len(enriched_agents),
        "agent_ids_unique": len(set(agent_ids)) == len(agent_ids),
        "endpoints_unique": len(set(endpoints)) == len(endpoints),
        "categories_known": all(category in LOCAL_RESPONSE_AGENT_CATEGORIES for category in categories),
        "valid": len(enriched_agents) == LOCAL_RESPONSE_AGENT_COUNT
        and len(set(agent_ids)) == len(agent_ids)
        and len(set(endpoints)) == len(endpoints)
        and all(category in LOCAL_RESPONSE_AGENT_CATEGORIES for category in categories),
    }


def _fallback_agent_id(name: object) -> str:
    slug = str(name or "local_response_agent").lower()
    slug = "".join(char if char.isalnum() else "_" for char in slug)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "local_response_agent"


def _fallback_route_agents(agents: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any], list[str]]]:
    fallback_order = [
        ("local_life_dashboard_cross_agent_coordinator", "Ambiguous manual coordination request."),
        ("local_planning_agent", "Broad planning fallback."),
        ("local_decision_agent", "Broad priority or tradeoff fallback."),
    ]
    agents_by_id = {}
    for agent in agents:
        enriched = enrich_local_response_agent(agent)
        agents_by_id[enriched["agentId"]] = enriched
    results = []
    for agent_id, reason in fallback_order:
        if agent_id in agents_by_id:
            results.append((1, agents_by_id[agent_id], [reason]))
    return results


def _default_output_type(output_types: list[str]) -> str:
    return output_types[0] if output_types else "summary"


def _category_id(category: str) -> str:
    return _normalize_id(category.replace("/", "_"))


def _normalize_id(value: str) -> str:
    return _fallback_agent_id(value)


def _clean_text(value: str) -> str:
    return " ".join(str(value or "").split())


def _route_follow_up_questions(request_text: str, domains: list[str], preferred_output_type: str, urgency_level: str) -> list[str]:
    questions = []
    if not request_text:
        questions.append("What manual request should be routed?")
    if not domains:
        questions.append("Which domains or life areas should be considered?")
    if not preferred_output_type:
        questions.append("What output shape would be most useful?")
    if not urgency_level:
        questions.append("How urgent is this request?")
    questions.append("Should the user choose one suggested endpoint manually from the workbench?")
    return questions[:5]
