from __future__ import annotations

import re
from typing import Any

from .local_response_agent_metadata import (
    HIGH_STAKES_LIMITATIONS_BY_CATEGORY,
    LOCAL_RESPONSE_AGENT_CATEGORIES,
    LOCAL_RESPONSE_AGENT_COUNT,
    LOCAL_RESPONSE_AGENT_IDS,
    LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS,
    LOCAL_RESPONSE_AGENT_USE_WHEN,
    enrich_local_response_agent,
    get_local_agent_metadata,
)
from .local_response_agents_catalog import LOCAL_RESPONSE_AGENTS_INDEX
from .prompt_assembly import classify_high_stakes


# Explicit mapping for primary input fields across the 37 local response agents.
# Every agent maps its primary user-content field and any required supplementary fields.
AGENT_PRIMARY_FIELD_MAPPINGS: dict[str, dict[str, Any]] = {
    "local_research_agent": {
        "primary_field": "userProvidedNotes",
        "secondary_field": "topic",
        "required_fields": ["topic", "userProvidedNotes"],
        "default_output_type": "brief",
        "output_type_key": "desiredOutputType",
    },
    "file_data_agent": {
        "primary_field": "projectName",
        "required_fields": ["projectName"],
        "default_output_type": "summary",
        "output_type_key": None,
    },
    "local_planning_agent": {
        "primary_field": "goal",
        "required_fields": ["goal"],
        "default_output_type": "project_plan",
        "output_type_key": "desiredOutputType",
    },
    "local_drafting_agent": {
        "primary_field": "notes",
        "secondary_field": "purpose",
        "required_fields": ["purpose", "notes"],
        "default_output_type": "message",
        "output_type_key": "format",
    },
    "local_review_agent": {
        "primary_field": "content",
        "secondary_field": "subject",
        "required_fields": ["subject", "content"],
        "default_output_type": "general",
        "output_type_key": "reviewType",
    },
    "local_decision_agent": {
        "primary_field": "decision",
        "required_fields": ["decision", "options"],
        "default_output_type": "balanced",
        "output_type_key": "decisionStyle",
    },
    "local_troubleshooting_agent": {
        "primary_field": "problem",
        "required_fields": ["problem"],
        "default_output_type": "general",
        "output_type_key": "troubleshootingType",
    },
    "local_summarization_agent": {
        "primary_field": "content",
        "required_fields": ["content"],
        "default_output_type": "general",
        "output_type_key": "summaryType",
    },
    "local_extraction_agent": {
        "primary_field": "content",
        "required_fields": ["content"],
        "default_output_type": "general",
        "output_type_key": "extractionType",
    },
    "local_classification_agent": {
        "primary_field": "content",
        "required_fields": ["content"],
        "default_output_type": "general",
        "output_type_key": "classificationType",
    },
    "local_transformation_agent": {
        "primary_field": "content",
        "required_fields": ["content"],
        "default_output_type": "outline",
        "output_type_key": "targetFormat",
    },
    "local_business_agent": {
        "primary_field": "businessIdea",
        "required_fields": ["businessIdea"],
        "default_output_type": "business_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_health_fitness_agent": {
        "primary_field": "primaryGoal",
        "required_fields": ["primaryGoal"],
        "default_output_type": "fitness_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_food_cooking_grocery": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "budget_grocery_plan",
        "output_type_key": "outputType",
    },
    "local_home_room_living_space": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "room_setup_plan",
        "output_type_key": "outputType",
    },
    "local_legal_immigration_official_matters": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "document_checklist",
        "output_type_key": "outputType",
    },
    "local_emergency_preparedness": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "car_emergency_kit",
        "output_type_key": "outputType",
    },
    "local_culture_taste_high_class_lifestyle": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "event_prep_plan",
        "output_type_key": "outputType",
    },
    "local_hobbies_adventure": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "adventure_brief",
        "output_type_key": "outputType",
    },
    "local_personal_knowledge_memory_organizer": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "knowledge_brief",
        "output_type_key": "outputType",
    },
    "local_life_dashboard_cross_agent_coordinator": {
        "primary_field": "request",
        "required_fields": ["request"],
        "default_output_type": "cross_agent_brief",
        "output_type_key": "outputType",
    },
    "local_everyday_life_agent": {
        "primary_field": "situation",
        "required_fields": ["situation"],
        "default_output_type": "life_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_online_presence_agent": {
        "primary_field": "currentBio",
        "required_fields": [],
        "default_output_type": "presence_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_security_safety_agent": {
        "primary_field": "situation",
        "required_fields": ["situation"],
        "default_output_type": "safety_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_creator_agent": {
        "primary_field": "contentIdea",
        "required_fields": ["contentIdea"],
        "default_output_type": "creator_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_school_robotics_agent": {
        "primary_field": "academicGoal",
        "required_fields": ["academicGoal"],
        "default_output_type": "school_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_career_agent": {
        "primary_field": "careerGoal",
        "required_fields": ["careerGoal"],
        "default_output_type": "career_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_finance_budget_agent": {
        "primary_field": "financialGoal",
        "required_fields": ["financialGoal"],
        "default_output_type": "finance_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_housing_move_travel_agent": {
        "primary_field": "housingGoal",
        "required_fields": ["housingGoal"],
        "default_output_type": "move_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_projects_portfolio_agent": {
        "primary_field": "portfolioGoal",
        "required_fields": ["portfolioGoal"],
        "default_output_type": "portfolio_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_learning_study_agent": {
        "primary_field": "learningGoal",
        "required_fields": ["learningGoal"],
        "default_output_type": "learning_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_social_networking_agent": {
        "primary_field": "socialGoal",
        "required_fields": ["socialGoal"],
        "default_output_type": "social_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_personal_admin_agent": {
        "primary_field": "adminGoal",
        "required_fields": ["adminGoal"],
        "default_output_type": "admin_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_vehicle_devices_gear_agent": {
        "primary_field": "gearGoal",
        "required_fields": ["gearGoal"],
        "default_output_type": "gear_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_life_direction_agent": {
        "primary_field": "lifeQuestion",
        "required_fields": ["lifeQuestion"],
        "default_output_type": "life_direction_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_relationships_agent": {
        "primary_field": "relationshipGoal",
        "required_fields": ["relationshipGoal"],
        "default_output_type": "relationship_brief",
        "output_type_key": "desiredOutputType",
    },
    "local_emotional_reflection_agent": {
        "primary_field": "reflectionGoal",
        "required_fields": ["reflectionGoal"],
        "default_output_type": "reflection_brief",
        "output_type_key": "desiredOutputType",
    },
}

# Domain specific intent signals to supplement keyword matching deterministically
DOMAIN_INTENT_SIGNALS: dict[str, tuple[str, ...]] = {
    "local_research_agent": ("research", "investigate", "brief", "literature", "find out about", "learn about", "look up", "overview"),
    "file_data_agent": ("project name", "project summary", "registered project", "repo metadata", "file metadata"),
    "local_planning_agent": ("plan", "checklist", "milestone", "timeline", "steps to", "how to organize", "project plan", "roadmap"),
    "local_drafting_agent": ("draft", "write an email", "write a message", "compose", "announcement", "letter", "wording"),
    "local_review_agent": ("review", "critique", "feedback", "check this text", "proofread", "inspect wording", "audit text"),
    "local_decision_agent": ("choose between", "compare options", "pros and cons", "tradeoff", "which should i pick", "decision support", "decide"),
    "local_troubleshooting_agent": ("troubleshoot", "debug", "issue", "bug", "broken", "why is this failing", "error message", "symptom", "crash"),
    "local_summarization_agent": ("summarize", "tl;dr", "tldr", "condense", "key takeaways", "recap", "executive summary", "shorten"),
    "local_extraction_agent": ("extract", "pull out", "key requirements", "bullet points from", "extract data", "find items"),
    "local_classification_agent": ("classify", "categorize", "tag", "sort into", "group these", "labels", "priority level"),
    "local_transformation_agent": ("transform", "convert to", "rewrite as", "format as", "change format", "translate structure"),
    "local_business_agent": ("business idea", "startup", "pricing strategy", "target market", "customer segment", "business model", "value proposition", "pitch"),
    "local_health_fitness_agent": ("workout", "exercise", "fitness", "gym", "cardio", "sleep routine", "wellness", "stretching", "mobility", "habit tracking"),
    "local_food_cooking_grocery": ("grocery", "pantry", "recipe", "cook", "meal prep", "dinner idea", "ingredients", "dietary", "lunch plan", "breakfast"),
    "local_home_room_living_space": ("room setup", "apartment", "furniture layout", "declutter", "closet", "living room", "desk setup", "storage space", "cleaning routine"),
    "local_legal_immigration_official_matters": ("visa", "immigration", "official documents", "passport", "legal paperwork", "court appointment", "notary", "permit", "agency form"),
    "local_emergency_preparedness": ("emergency", "go-bag", "go bag", "disaster", "first aid kit", "power outage", "storm prep", "winter storm", "emergency supplies"),
    "local_culture_taste_high_class_lifestyle": ("wardrobe", "etiquette", "dress code", "formal dinner", "taste", "style", "fine dining", "hosting guests", "manners"),
    "local_hobbies_adventure": ("hobby", "camping", "hiking", "adventure", "drone", "fishing", "woodworking", "photography", "weekend trip"),
    "local_personal_knowledge_memory_organizer": ("organize notes", "knowledge base", "pkm", "second brain", "wiki", "idea organization", "note-taking structure"),
    "local_life_dashboard_cross_agent_coordinator": ("cross-agent", "life dashboard", "balance priorities", "weekly review", "coordinate life areas", "holistic planning"),
    "local_everyday_life_agent": ("errands", "chores", "daily routine", "household", "laundry schedule", "everyday tasks", "time management"),
    "local_online_presence_agent": ("bio", "social media profile", "portfolio bio", "linkedin summary", "online brand", "public profile"),
    "local_security_safety_agent": ("security review", "password hygiene", "privacy check", "threat model", "home security", "safety audit"),
    "local_creator_agent": ("youtube idea", "content creation", "video script outline", "podcast idea", "blog topic", "creative project", "story outline"),
    "local_school_robotics_agent": ("robotics", "arduino", "stem", "class project", "sensor", "motor control", "school assignment", "coursework"),
    "local_career_agent": ("resume", "interview prep", "job search", "cover letter", "promotion", "career switch", "linkedin networking", "salary negotiation preparation"),
    "local_finance_budget_agent": ("budget", "savings goal", "debt payoff", "monthly expenses", "spending plan", "frugal", "personal finance", "loan payoff"),
    "local_housing_move_travel_agent": ("moving plan", "relocation", "apartment search checklist", "travel itinerary", "packing list", "commute planning"),
    "local_projects_portfolio_agent": ("portfolio project", "case study", "showcase project", "project milestone", "proof of work", "side project"),
    "local_learning_study_agent": ("study plan", "flashcards", "learn python", "exam prep", "learning roadmap", "master a topic", "study schedule"),
    "local_social_networking_agent": ("networking event", "conversation starters", "introduction", "make friends", "social interaction", "meetup prep"),
    "local_personal_admin_agent": ("paperwork", "forms", "renew license", "appointments", "billing disputes", "admin tasks", "record keeping"),
    "local_vehicle_devices_gear_agent": ("car maintenance checklist", "electronics setup", "gear packing", "scooter maintenance", "laptop setup", "device management"),
    "local_life_direction_agent": ("life goals", "values reflection", "personal mission", "long-term vision", "identity", "next chapter", "life transition"),
    "local_relationships_agent": ("roommate communication", "friendship conflict", "family boundary", "relationship discussion", "interpersonal advice"),
    "local_emotional_reflection_agent": ("stress relief", "burnout recovery", "mindfulness reflection", "venting", "emotional balance", "anxiety reflection"),
}


def _clean_text(text: str | None) -> str:
    return str(text or "").strip()


def _extract_title_or_topic(text: str, max_chars: int = 80) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return "Untitled Request"
    first_line = cleaned.splitlines()[0].strip()
    if len(first_line) <= max_chars:
        return first_line
    return first_line[:max_chars].rstrip() + "..."


class UnifiedRoutingEngine:
    """Deterministic routing engine over the 37 local response agents."""

    def __init__(self, agents_index: list[dict[str, Any]] | None = None) -> None:
        self.agents_index = agents_index or LOCAL_RESPONSE_AGENTS_INDEX
        self.enriched_agents = [enrich_local_response_agent(agent) for agent in self.agents_index]
        self.agents_by_id = {agent["agentId"]: agent for agent in self.enriched_agents}

    def analyze_route(
        self,
        text: str,
        explicit_agent_id: str | None = None,
        category_preference: str | None = None,
    ) -> dict[str, Any]:
        cleaned_text = _clean_text(text)
        lower_text = cleaned_text.lower()

        # Handle explicit override
        if explicit_agent_id and explicit_agent_id.strip():
            normalized_override = explicit_agent_id.strip()
            if normalized_override in self.agents_by_id:
                agent = self.agents_by_id[normalized_override]
                is_high_stakes = classify_high_stakes(agent["agentId"], agent["category"])
                alternatives = self._find_alternatives(lower_text, exclude_id=agent["agentId"], count=3)
                return {
                    "selected_agent_id": agent["agentId"],
                    "selected_display_name": agent["displayName"],
                    "endpoint": agent["endpoint"],
                    "category": agent["category"],
                    "confidence_tier": "explicit_override",
                    "matched_signals": ["Explicit user override selection"],
                    "routing_rationale": f"Explicitly selected by user: {agent['displayName']}.",
                    "alternatives": alternatives,
                    "is_ambiguous": False,
                    "ambiguity_reason": None,
                    "high_stakes": is_high_stakes,
                    "high_stakes_category": agent["category"] if is_high_stakes else None,
                    "safety_reminders": self._get_safety_reminders(agent["category"], is_high_stakes),
                }

        # Calculate deterministic score for each agent
        scored_candidates: list[dict[str, Any]] = []
        for agent in self.enriched_agents:
            agent_id = agent["agentId"]
            score = 0
            signals: list[str] = []

            # 1. Route keywords match
            keywords = LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS.get(agent_id, ())
            for kw in keywords:
                if kw in lower_text:
                    score += 3
                    signals.append(f"keyword: '{kw}'")

            # 2. Domain intent signals match
            intent_signals = DOMAIN_INTENT_SIGNALS.get(agent_id, ())
            for sig in intent_signals:
                if sig in lower_text:
                    score += 4
                    signals.append(f"signal: '{sig}'")

            # 3. Agent display name match
            display_name_lower = agent["displayName"].lower()
            if display_name_lower in lower_text:
                score += 5
                signals.append("agent name mentioned")

            # 4. Category preference
            if category_preference and category_preference.strip():
                if agent["category"].lower() == category_preference.strip().lower():
                    score += 3
                    signals.append(f"preferred category: {agent['category']}")

            # 5. Category keywords in text
            if agent["category"].lower() in lower_text:
                score += 2
                signals.append(f"category match: {agent['category']}")

            scored_candidates.append({
                "agent": agent,
                "score": score,
                "signals": signals,
            })

        # Sort descending by score, then alphabetically by display name
        scored_candidates.sort(key=lambda item: (-item["score"], item["agent"]["displayName"]))

        top_candidate = scored_candidates[0]
        top_agent = top_candidate["agent"]
        top_score = top_candidate["score"]
        top_signals = top_candidate["signals"]

        # If no signals matched at all (score == 0), deliberately select a defined general fallback
        if top_score == 0:
            fallback_id = "local_planning_agent"
            if any(term in lower_text for term in ("coordinate", "cross-agent", "dashboard", "overall", "life areas")):
                fallback_id = "local_life_dashboard_cross_agent_coordinator"
            top_agent = self.agents_by_id.get(fallback_id, top_agent)
            top_signals = ["General fallback — no specific domain keywords matched"]
            confidence_tier = "weak"
            routing_rationale = (
                f"No specific domain keywords matched. Recommended {top_agent['displayName']} "
                f"({top_agent['category']}) as a safe general fallback."
            )
            # General fallback alternatives
            fallback_alt_ids = [
                "local_life_dashboard_cross_agent_coordinator",
                "local_decision_agent",
                "local_summarization_agent",
                "local_research_agent",
            ]
            alternatives = []
            for alt_id in fallback_alt_ids:
                if alt_id != top_agent["agentId"] and alt_id in self.agents_by_id:
                    alt_agent = self.agents_by_id[alt_id]
                    alternatives.append({
                        "agent_id": alt_agent["agentId"],
                        "display_name": alt_agent["displayName"],
                        "category": alt_agent["category"],
                        "endpoint": alt_agent["endpoint"],
                        "score": 0,
                        "reason": alt_agent.get("useWhen", "General fallback response agent."),
                        "use_when": alt_agent.get("useWhen", ""),
                    })
                    if len(alternatives) >= 4:
                        break
            is_ambiguous = False
            ambiguity_reason = None
        else:
            # Determine confidence tier
            if top_score >= 6:
                confidence_tier = "strong"
            elif top_score >= 3:
                confidence_tier = "moderate"
            else:
                confidence_tier = "weak"

            # Determine ambiguity
            is_ambiguous = False
            ambiguity_reason = None
            if len(scored_candidates) > 1:
                second = scored_candidates[1]
                if top_score > 0 and (top_score - second["score"]) <= 1 and confidence_tier != "strong":
                    is_ambiguous = True
                    ambiguity_reason = (
                        f"Both '{top_agent['displayName']}' (score {top_score}) and "
                        f"'{second['agent']['displayName']}' (score {second['score']}) match closely."
                    )

            # Build alternatives from scored candidates
            alternatives = []
            for cand in scored_candidates:
                alt_agent = cand["agent"]
                if alt_agent["agentId"] == top_agent["agentId"]:
                    continue
                alt_signals = cand["signals"] or ["General secondary candidate"]
                alternatives.append({
                    "agent_id": alt_agent["agentId"],
                    "display_name": alt_agent["displayName"],
                    "category": alt_agent["category"],
                    "endpoint": alt_agent["endpoint"],
                    "score": cand["score"],
                    "reason": ", ".join(alt_signals[:3]),
                    "use_when": alt_agent.get("useWhen", ""),
                })
                if len(alternatives) >= 4:
                    break

            routing_rationale = (
                f"Selected {top_agent['displayName']} ({top_agent['category']}) based on matched signals: "
                + ", ".join(top_signals[:4]) + "."
            )

        is_high_stakes = classify_high_stakes(top_agent["agentId"], top_agent["category"])

        return {
            "selected_agent_id": top_agent["agentId"],
            "selected_display_name": top_agent["displayName"],
            "endpoint": top_agent["endpoint"],
            "category": top_agent["category"],
            "confidence_tier": confidence_tier,
            "matched_signals": top_signals,
            "routing_rationale": routing_rationale,
            "alternatives": alternatives,
            "is_ambiguous": is_ambiguous,
            "ambiguity_reason": ambiguity_reason,
            "high_stakes": is_high_stakes,
            "high_stakes_category": top_agent["category"] if is_high_stakes else None,
            "safety_reminders": self._get_safety_reminders(top_agent["category"], is_high_stakes),
        }

    def _find_alternatives(self, lower_text: str, exclude_id: str, count: int = 4) -> list[dict[str, Any]]:
        scored: list[dict[str, Any]] = []
        for agent in self.enriched_agents:
            agent_id = agent["agentId"]
            if agent_id == exclude_id:
                continue
            score = 0
            signals: list[str] = []
            keywords = LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS.get(agent_id, ())
            for kw in keywords:
                if kw in lower_text:
                    score += 3
                    signals.append(f"keyword: '{kw}'")
            intent_signals = DOMAIN_INTENT_SIGNALS.get(agent_id, ())
            for sig in intent_signals:
                if sig in lower_text:
                    score += 4
                    signals.append(f"signal: '{sig}'")
            if agent["displayName"].lower() in lower_text:
                score += 5
                signals.append("agent name mentioned")
            if agent["category"].lower() in lower_text:
                score += 2
                signals.append(f"category match: {agent['category']}")
            scored.append({"agent": agent, "score": score, "signals": signals})

        scored.sort(key=lambda item: (-item["score"], item["agent"]["displayName"]))
        alts: list[dict[str, Any]] = []
        for cand in scored:
            agent = cand["agent"]
            signals = cand["signals"] or [agent.get("useWhen", "Alternative response agent.")]
            alts.append({
                "agent_id": agent["agentId"],
                "display_name": agent["displayName"],
                "category": agent["category"],
                "endpoint": agent["endpoint"],
                "score": cand["score"],
                "reason": ", ".join(signals[:3]) if isinstance(signals, list) else str(signals),
                "use_when": agent.get("useWhen", ""),
            })
            if len(alts) >= count:
                break
        return alts

    def _get_safety_reminders(self, category: str, is_high_stakes: bool) -> list[str]:
        reminders = [
            "Jarvis operates in manual-input, local-only, response-only mode.",
            "No accounts, external APIs, emails, bookings, submissions, or background actions are performed.",
        ]
        if is_high_stakes:
            category_limits = HIGH_STAKES_LIMITATIONS_BY_CATEGORY.get(category, [])
            if category_limits:
                reminders.extend(category_limits)
            else:
                reminders.append(
                    "High-stakes area: Consult qualified professionals or authoritative sources before taking action."
                )
        return reminders


def _parse_structured_decision_request(text: str) -> dict[str, Any] | None:
    start_tag = "[Decision Request]"
    end_tag = "[/Decision Request]"
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None

    block = text[start_idx + len(start_tag) : end_idx].strip()
    lines = block.splitlines()

    decision = ""
    decision_style = "balanced"
    options: list[str] = []
    criteria: list[str] = []
    constraints: list[str] = []
    priorities: list[str] = []
    context_notes_lines: list[str] = []

    current_section: str | None = None

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("decision:"):
            decision = stripped[len("decision:") :].strip()
            current_section = None
            continue
        elif lower.startswith("decision style:") or lower.startswith("style:"):
            style_val = stripped.split(":", 1)[1].strip().lower()
            if style_val in ("balanced", "safest", "fastest", "cheapest", "highest_upside"):
                decision_style = style_val
            else:
                decision_style = "balanced"
            current_section = None
            continue
        elif lower.startswith("options:"):
            current_section = "options"
            opt_inline = stripped[len("options:") :].strip()
            if opt_inline:
                for item in opt_inline.split(","):
                    val = item.strip().lstrip("-*• ").strip()
                    if val and val not in options and len(options) < 12:
                        options.append(val)
            continue
        elif lower.startswith("criteria:"):
            current_section = "criteria"
            crit_inline = stripped[len("criteria:") :].strip()
            if crit_inline:
                for item in crit_inline.split(","):
                    val = item.strip().lstrip("-*• ").strip()
                    if val and val not in criteria:
                        criteria.append(val)
            continue
        elif lower.startswith("constraints:"):
            current_section = "constraints"
            const_inline = stripped[len("constraints:") :].strip()
            if const_inline:
                for item in const_inline.split(","):
                    val = item.strip().lstrip("-*• ").strip()
                    if val and val not in constraints:
                        constraints.append(val)
            continue
        elif lower.startswith("priorities:"):
            current_section = "priorities"
            prio_inline = stripped[len("priorities:") :].strip()
            if prio_inline:
                for item in prio_inline.split(","):
                    val = item.strip().lstrip("-*• ").strip()
                    if val and val not in priorities:
                        priorities.append(val)
            continue
        elif lower.startswith("context notes:") or lower.startswith("context:"):
            current_section = "contextNotes"
            cn_inline = stripped.split(":", 1)[1].strip()
            if cn_inline:
                context_notes_lines.append(cn_inline)
            continue

        if current_section == "options":
            val = stripped.lstrip("-*• ").strip()
            if val and val not in options:
                if len(options) < 12:
                    options.append(val)
        elif current_section == "criteria":
            val = stripped.lstrip("-*• ").strip()
            if val and val not in criteria:
                criteria.append(val)
        elif current_section == "constraints":
            val = stripped.lstrip("-*• ").strip()
            if val and val not in constraints:
                constraints.append(val)
        elif current_section == "priorities":
            val = stripped.lstrip("-*• ").strip()
            if val and val not in priorities:
                priorities.append(val)
        elif current_section == "contextNotes":
            context_notes_lines.append(line)

    return {
        "decision": decision,
        "options": options[:12],
        "criteria": criteria,
        "constraints": constraints,
        "priorities": priorities,
        "contextNotes": "\n".join(context_notes_lines).strip(),
        "decisionStyle": decision_style,
    }


class UnifiedRequestAdapter:
    """Adapts natural-language requests into schema-compatible request bodies for the 37 agents."""

    @staticmethod
    def prepare_payload(
        agent_id: str,
        user_request: str,
        *,
        memory_option: dict[str, Any] | None = None,
        knowledge_option: dict[str, Any] | None = None,
        generation_mode: str | None = None,
        prior_agent_context: dict[str, Any] | None = None,
        web_context: list[dict[str, Any]] | None = None,
        custom_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mapping = AGENT_PRIMARY_FIELD_MAPPINGS.get(agent_id, {
            "primary_field": "request",
            "required_fields": ["request"],
            "default_output_type": "summary",
            "output_type_key": "outputType",
        })

        cleaned_request = _clean_text(user_request)
        payload: dict[str, Any] = {}

        # Fill agent-specific fields
        primary_field = mapping.get("primary_field")
        default_output = mapping.get("default_output_type", "summary")
        output_type_key = mapping.get("output_type_key")

        if agent_id == "local_research_agent":
            payload["topic"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["userProvidedNotes"] = cleaned_request
            payload["sourceTitles"] = []
            payload["questions"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "file_data_agent":
            payload["projectName"] = cleaned_request
        elif agent_id == "local_planning_agent":
            payload["goal"] = cleaned_request
            payload["contextNotes"] = ""
            payload["constraints"] = []
            payload["resources"] = []
            payload["blockers"] = []
            payload["timeframe"] = None
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_drafting_agent":
            payload["purpose"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["notes"] = cleaned_request
            payload["audience"] = ""
            payload["tone"] = "clear"
            payload["format"] = default_output
            payload["constraints"] = []
            payload["mustInclude"] = []
            payload["mustAvoid"] = []
        elif agent_id == "local_review_agent":
            payload["subject"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["content"] = cleaned_request
            payload["reviewType"] = default_output
            payload["audience"] = ""
            payload["criteria"] = []
            payload["constraints"] = []
            payload["severity"] = "balanced"
        elif agent_id == "local_decision_agent":
            parsed = _parse_structured_decision_request(cleaned_request)
            if parsed:
                payload["decision"] = parsed["decision"] or cleaned_request
                payload["options"] = parsed["options"]
                payload["criteria"] = parsed["criteria"]
                payload["constraints"] = parsed["constraints"]
                payload["priorities"] = parsed["priorities"]
                payload["contextNotes"] = parsed["contextNotes"]
                payload["decisionStyle"] = parsed["decisionStyle"]
            else:
                payload["decision"] = cleaned_request
                payload["options"] = []
                payload["criteria"] = []
                payload["constraints"] = []
                payload["priorities"] = []
                payload["contextNotes"] = ""
                payload["decisionStyle"] = default_output
        elif agent_id == "local_troubleshooting_agent":
            payload["problem"] = cleaned_request
            payload["symptoms"] = []
            payload["errorMessages"] = []
            payload["environmentNotes"] = ""
            payload["attemptedFixes"] = []
            payload["constraints"] = []
            payload["urgency"] = "normal"
            payload["troubleshootingType"] = default_output
        elif agent_id == "local_summarization_agent":
            payload["title"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["content"] = cleaned_request
            payload["summaryType"] = default_output
            payload["audience"] = ""
            payload["detailLevel"] = "medium"
            payload["focusAreas"] = []
            payload["mustPreserve"] = []
            payload["mustAvoid"] = []
        elif agent_id == "local_extraction_agent":
            payload["title"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["content"] = cleaned_request
            payload["extractionType"] = default_output
            payload["focusAreas"] = []
            payload["mustCapture"] = []
            payload["mustIgnore"] = []
            payload["detailLevel"] = "medium"
        elif agent_id == "local_classification_agent":
            payload["title"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["content"] = cleaned_request
            payload["items"] = []
            payload["classificationType"] = default_output
            payload["labels"] = []
            payload["criteria"] = []
            payload["constraints"] = []
            payload["detailLevel"] = "medium"
        elif agent_id == "local_transformation_agent":
            payload["title"] = _extract_title_or_topic(cleaned_request, max_chars=80)
            payload["content"] = cleaned_request
            payload["items"] = []
            payload["targetFormat"] = default_output
            payload["audience"] = ""
            payload["constraints"] = []
            payload["mustPreserve"] = []
            payload["mustAvoid"] = []
            payload["detailLevel"] = "medium"
        elif agent_id == "local_business_agent":
            payload["businessName"] = ""
            payload["businessIdea"] = cleaned_request
            payload["targetCustomer"] = ""
            payload["problem"] = ""
            payload["offer"] = ""
            payload["pricingNotes"] = ""
            payload["operationsNotes"] = ""
            payload["marketingNotes"] = ""
            payload["constraints"] = []
            payload["resources"] = []
            payload["risks"] = []
            payload["goals"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_health_fitness_agent":
            payload["profileName"] = ""
            payload["primaryGoal"] = cleaned_request
            payload["currentFitnessLevel"] = ""
            payload["ageRange"] = ""
            payload["heightWeightNotes"] = ""
            payload["scheduleNotes"] = ""
            payload["equipmentAvailable"] = []
            payload["preferredActivities"] = []
            payload["dislikedActivities"] = []
            payload["nutritionNotes"] = ""
            payload["sleepRecoveryNotes"] = ""
            payload["constraints"] = []
            payload["injuriesOrLimitations"] = []
            payload["habitsToBuild"] = []
            payload["habitsToReduce"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_everyday_life_agent":
            payload["lifeArea"] = ""
            payload["situation"] = cleaned_request
            payload["goals"] = []
            payload["constraints"] = []
            payload["scheduleNotes"] = ""
            payload["householdNotes"] = ""
            payload["errands"] = []
            payload["peopleInvolved"] = []
            payload["resources"] = []
            payload["energyNotes"] = ""
            payload["budgetNotes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_online_presence_agent":
            payload["profileName"] = ""
            payload["platforms"] = []
            payload["currentBio"] = cleaned_request
            payload["goals"] = []
            payload["targetAudience"] = ""
            payload["tone"] = ""
            payload["strengths"] = []
            payload["projects"] = []
            payload["contentIdeas"] = []
            payload["constraints"] = []
            payload["reputationConcerns"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_security_safety_agent":
            payload["reviewName"] = ""
            payload["situation"] = cleaned_request
            payload["assetsOrAccounts"] = []
            payload["concerns"] = []
            payload["currentControls"] = []
            payload["constraints"] = []
            payload["riskTolerance"] = ""
            payload["environmentNotes"] = ""
            payload["incidentNotes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_creator_agent":
            payload["creatorName"] = ""
            payload["platforms"] = []
            payload["niche"] = ""
            payload["audience"] = ""
            payload["contentIdea"] = cleaned_request
            payload["goals"] = []
            payload["tone"] = ""
            payload["formatNotes"] = ""
            payload["productionResources"] = []
            payload["constraints"] = []
            payload["existingContentNotes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_school_robotics_agent":
            payload["studentName"] = ""
            payload["schoolName"] = ""
            payload["programName"] = ""
            payload["termOrTimeline"] = ""
            payload["academicGoal"] = cleaned_request
            payload["roboticsFocus"] = ""
            payload["courses"] = []
            payload["professorsOrLabs"] = []
            payload["projects"] = []
            payload["constraints"] = []
            payload["resources"] = []
            payload["currentPreparation"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_career_agent":
            payload["profileName"] = ""
            payload["careerGoal"] = cleaned_request
            payload["targetRoles"] = []
            payload["targetIndustries"] = []
            payload["currentExperience"] = ""
            payload["educationNotes"] = ""
            payload["skills"] = []
            payload["projects"] = []
            payload["resumeNotes"] = ""
            payload["jobSearchNotes"] = ""
            payload["networkingNotes"] = ""
            payload["constraints"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_finance_budget_agent":
            payload["profileName"] = ""
            payload["financialGoal"] = cleaned_request
            payload["incomeNotes"] = ""
            payload["expenseNotes"] = ""
            payload["debtNotes"] = ""
            payload["loanNotes"] = ""
            payload["rentHousingNotes"] = ""
            payload["moveCostNotes"] = ""
            payload["savingsNotes"] = ""
            payload["spendingNotes"] = ""
            payload["constraints"] = []
            payload["priorities"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_housing_move_travel_agent":
            payload["planName"] = ""
            payload["destination"] = ""
            payload["housingGoal"] = cleaned_request
            payload["timeline"] = ""
            payload["budgetNotes"] = ""
            payload["housingOptions"] = []
            payload["moveItems"] = []
            payload["transportationNotes"] = ""
            payload["commuteNotes"] = ""
            payload["utilitySetupNotes"] = ""
            payload["constraints"] = []
            payload["priorities"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_projects_portfolio_agent":
            payload["profileName"] = ""
            payload["portfolioGoal"] = cleaned_request
            payload["targetAudience"] = ""
            payload["targetRoles"] = []
            payload["projectNotes"] = []
            payload["skills"] = []
            payload["proofArtifacts"] = []
            payload["currentStatus"] = ""
            payload["constraints"] = []
            payload["priorities"] = []
            payload["timeline"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_learning_study_agent":
            payload["learnerName"] = ""
            payload["learningGoal"] = cleaned_request
            payload["topics"] = []
            payload["currentLevel"] = ""
            payload["timeline"] = ""
            payload["availableTime"] = ""
            payload["resources"] = []
            payload["weakAreas"] = []
            payload["preferredMethods"] = []
            payload["constraints"] = []
            payload["motivationNotes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_social_networking_agent":
            payload["profileName"] = ""
            payload["socialGoal"] = cleaned_request
            payload["setting"] = ""
            payload["peopleContext"] = ""
            payload["eventNotes"] = ""
            payload["conversationTopics"] = []
            payload["networkingGoals"] = []
            payload["presentationNotes"] = ""
            payload["constraints"] = []
            payload["comfortLevel"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_personal_admin_agent":
            payload["profileName"] = ""
            payload["adminGoal"] = cleaned_request
            payload["documentTypes"] = []
            payload["deadlines"] = []
            payload["requirements"] = []
            payload["currentStatus"] = ""
            payload["constraints"] = []
            payload["peopleOrOfficesInvolved"] = []
            payload["notes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_vehicle_devices_gear_agent":
            payload["profileName"] = ""
            payload["gearGoal"] = cleaned_request
            payload["vehicleNotes"] = ""
            payload["deviceNotes"] = ""
            payload["droneScooterNotes"] = ""
            payload["inventoryItems"] = []
            payload["maintenanceConcerns"] = []
            payload["troubleshootingNotes"] = ""
            payload["packingNotes"] = ""
            payload["constraints"] = []
            payload["priorities"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_life_direction_agent":
            payload["profileName"] = ""
            payload["lifeQuestion"] = cleaned_request
            payload["currentSeason"] = ""
            payload["values"] = []
            payload["longTermGoals"] = []
            payload["currentPriorities"] = []
            payload["tensionsOrTradeoffs"] = []
            payload["constraints"] = []
            payload["areasToImprove"] = []
            payload["strengths"] = []
            payload["nonNegotiables"] = []
            payload["reflectionNotes"] = ""
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_relationships_agent":
            payload["profileName"] = ""
            payload["relationshipGoal"] = cleaned_request
            payload["relationshipType"] = ""
            payload["peopleContext"] = ""
            payload["situationNotes"] = ""
            payload["communicationGoals"] = []
            payload["concerns"] = []
            payload["boundaries"] = []
            payload["desiredTone"] = ""
            payload["constraints"] = []
            payload["desiredOutputType"] = default_output
        elif agent_id == "local_emotional_reflection_agent":
            payload["profileName"] = ""
            payload["reflectionGoal"] = cleaned_request
            payload["currentMoodNotes"] = ""
            payload["stressors"] = []
            payload["energyNotes"] = ""
            payload["recentWins"] = []
            payload["currentChallenges"] = []
            payload["patternsNoticed"] = []
            payload["supportOptions"] = []
            payload["constraints"] = []
            payload["desiredOutputType"] = default_output
        else:
            # Life / domain agents with 'request' and 'outputType'
            payload["request"] = cleaned_request
            payload["promptText"] = ""
            if output_type_key:
                payload[output_type_key] = default_output

        # Context and Generation enrichments
        payload["web_context"] = web_context or []
        payload["prior_agent_context"] = prior_agent_context

        if memory_option:
            payload["memory"] = memory_option

        if knowledge_option:
            payload["knowledge"] = knowledge_option

        if generation_mode:
            payload["generation"] = {
                "mode": generation_mode,
            }

        # Apply any custom overrides
        if custom_overrides and isinstance(custom_overrides, dict):
            payload.update(custom_overrides)

        return payload

    @staticmethod
    def assess_readiness(agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping = AGENT_PRIMARY_FIELD_MAPPINGS.get(agent_id, {
            "required_fields": ["request"],
        })
        required_fields = mapping.get("required_fields", [])
        missing_fields: list[str] = []

        for field in required_fields:
            val = payload.get(field)
            if val is None:
                missing_fields.append(field)
            elif isinstance(val, str) and not val.strip():
                missing_fields.append(field)
            elif isinstance(val, list) and field == "options" and len(val) < 2 and agent_id == "local_decision_agent":
                # Decision agent requires at least 2 options to compare
                missing_fields.append("options (needs at least 2 choices)")
            elif isinstance(val, list) and not val and field in required_fields:
                missing_fields.append(field)

        is_ready = len(missing_fields) == 0
        if is_ready:
            readiness_notes = "All required fields are present and schema-compatible."
        else:
            readiness_notes = f"Missing or incomplete required field(s): {', '.join(missing_fields)}."

        return {
            "is_ready": is_ready,
            "missing_fields": missing_fields,
            "readiness_notes": readiness_notes,
        }


class UnifiedAssistantService:
    """Unified Assistant supervisor coordinating deterministic routing and request adaptation."""

    def __init__(self, agents_index: list[dict[str, Any]] | None = None) -> None:
        self.routing_engine = UnifiedRoutingEngine(agents_index)
        self.request_adapter = UnifiedRequestAdapter()

    def analyze(
        self,
        request_text: str,
        *,
        explicit_agent_id: str | None = None,
        category_preference: str | None = None,
        memory_option: dict[str, Any] | None = None,
        knowledge_option: dict[str, Any] | None = None,
        generation_mode: str | None = None,
        prior_agent_context: dict[str, Any] | None = None,
        web_context: list[dict[str, Any]] | None = None,
        custom_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        route = self.routing_engine.analyze_route(
            request_text,
            explicit_agent_id=explicit_agent_id,
            category_preference=category_preference,
        )
        selected_agent_id = route["selected_agent_id"]
        prepared_payload = self.request_adapter.prepare_payload(
            selected_agent_id,
            request_text,
            memory_option=memory_option,
            knowledge_option=knowledge_option,
            generation_mode=generation_mode,
            prior_agent_context=prior_agent_context,
            web_context=web_context,
            custom_overrides=custom_overrides,
        )
        readiness = self.request_adapter.assess_readiness(selected_agent_id, prepared_payload)

        return {
            "status": "analyzed",
            "request_text": request_text,
            "route": route,
            "readiness": readiness,
            "prepared_payload": prepared_payload,
            "expected_agent_count": LOCAL_RESPONSE_AGENT_COUNT,
            "boundary_notice": (
                "Jarvis Unified Assistant is local-only, response-only, and non-persistent. "
                "No automatic execution or chaining is performed."
            ),
        }
