from __future__ import annotations

import re
from typing import Any

from .local_response_agent_metadata import (
    LOCAL_RESPONSE_AGENT_CATEGORIES,
    LOCAL_RESPONSE_AGENT_COUNT,
    LOCAL_RESPONSE_AGENT_IDS,
    LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS,
    LOCAL_RESPONSE_AGENT_USE_WHEN,
    discovery_metadata_for_agent,
    enrich_local_response_agent,
    get_local_agent_metadata,
)
from .local_response_agents_catalog import (
    LOCAL_RESPONSE_AGENTS_INDEX,
    local_response_agent_route_preview,
)
from .prompt_assembly import classify_high_stakes


BUILTIN_PLAYBOOKS: list[dict[str, Any]] = [
    {
        "id": "plan_review_decision",
        "name": "Plan → Review → Decision",
        "description": "Standard deliberate execution flow: create a structured plan, critique it for risks/gaps, and evaluate tradeoffs for final decision.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_planning_agent",
                "name": "Planning Agent",
                "purpose": "Generate structured milestones, checklist, and requirements for the goal.",
                "defaultOutputType": "project_plan",
                "suggestedPrompt": "Create a detailed step-by-step plan for: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_review_agent",
                "name": "Review Agent",
                "purpose": "Critique the plan for edge cases, missing dependencies, safety risks, and ambiguities.",
                "defaultOutputType": "detailed",
                "suggestedPrompt": "Review this proposed plan for edge cases, missing steps, and risks: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_decision_agent",
                "name": "Decision Agent",
                "purpose": "Weigh tradeoffs and make the final decision with clear rationale.",
                "defaultOutputType": "tradeoff_matrix",
                "suggestedPrompt": "Compare these implementation approaches and recommend the safest choice: ",
            },
        ],
    },
    {
        "id": "research_summarize_decision",
        "name": "Research → Summarize → Decision",
        "description": "Information synthesis flow: organize notes/findings, condense into key takeaways, and decide on next action.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_research_agent",
                "name": "Research Agent",
                "purpose": "Structure research notes, questions, and reference points into a comprehensive brief.",
                "defaultOutputType": "brief",
                "suggestedPrompt": "Synthesize these research notes and questions: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_summarization_agent",
                "name": "Summarization Agent",
                "purpose": "Condense the research into executive bullet points and key takeaways.",
                "defaultOutputType": "executive_summary",
                "suggestedPrompt": "Summarize the key findings from this research into core takeaways: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_decision_agent",
                "name": "Decision Agent",
                "purpose": "Select the best path forward based on summarized evidence.",
                "defaultOutputType": "recommendation",
                "suggestedPrompt": "Based on the summarized findings, evaluate which option to proceed with: ",
            },
        ],
    },
    {
        "id": "troubleshoot_review",
        "name": "Troubleshoot → Review",
        "description": "Issue resolution flow: isolate root cause and generate hypotheses, then review proposed fix for side effects.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_troubleshooting_agent",
                "name": "Troubleshooting Agent",
                "purpose": "Triage symptoms, list potential root causes, and propose isolated verification steps.",
                "defaultOutputType": "triage_plan",
                "suggestedPrompt": "Troubleshoot this symptom and isolate potential root causes: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_review_agent",
                "name": "Review Agent",
                "purpose": "Review proposed troubleshooting fixes for safety, regression risk, and correctness.",
                "defaultOutputType": "safety_review",
                "suggestedPrompt": "Review this proposed fix for potential side effects and regressions: ",
            },
        ],
    },
    {
        "id": "career_draft_review",
        "name": "Career → Draft → Review",
        "description": "Professional communication flow: define career goal/positioning, draft communication or resume materials, and review tone/clarity.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_career_agent",
                "name": "Career Agent",
                "purpose": "Structure career positioning, milestone goals, and key talking points.",
                "defaultOutputType": "career_plan",
                "suggestedPrompt": "Outline talking points and positioning strategy for: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_drafting_agent",
                "name": "Drafting Agent",
                "purpose": "Draft polished cover letters, outreach messages, or resume bullets.",
                "defaultOutputType": "message",
                "suggestedPrompt": "Draft a professional communication based on these career points: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_review_agent",
                "name": "Review Agent",
                "purpose": "Review drafted materials for professional tone, conciseness, and impact.",
                "defaultOutputType": "critique",
                "suggestedPrompt": "Review this draft for clarity, tone, and professional impact: ",
            },
        ],
    },
    {
        "id": "school_plan_review",
        "name": "School/Robotics → Plan → Review",
        "description": "Academic & technical project flow: clarify robotics/academic milestones, schedule tasks, and check safety/readiness.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_school_robotics_agent",
                "name": "School / Robotics Agent",
                "purpose": "Define assignment scope, robotics architecture, or study milestones.",
                "defaultOutputType": "project_outline",
                "suggestedPrompt": "Break down this robotics/school assignment into technical requirements: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_planning_agent",
                "name": "Planning Agent",
                "purpose": "Create a timeline with daily/weekly checkpoints and deliverable milestones.",
                "defaultOutputType": "schedule",
                "suggestedPrompt": "Create a study/build schedule for these requirements: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_review_agent",
                "name": "Review Agent",
                "purpose": "Review plan for feasibility, scope creep, and safety compliance.",
                "defaultOutputType": "feasibility_review",
                "suggestedPrompt": "Review this schedule for feasibility and potential bottlenecks: ",
            },
        ],
    },
    {
        "id": "housing_decision_plan",
        "name": "Housing/Move → Decision → Plan",
        "description": "Relocation & home logistics flow: organize criteria, compare candidate options, and build a move checklist.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_housing_move_travel_agent",
                "name": "Housing / Move Agent",
                "purpose": "Structure move requirements, commute constraints, and budget bounds.",
                "defaultOutputType": "move_criteria",
                "suggestedPrompt": "Organize moving constraints, commute priorities, and budget for: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_decision_agent",
                "name": "Decision Agent",
                "purpose": "Compare housing/apartment options against criteria.",
                "defaultOutputType": "tradeoff_matrix",
                "suggestedPrompt": "Compare these candidate apartments based on rent, commute, and space: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_planning_agent",
                "name": "Planning Agent",
                "purpose": "Create a moving timeline, packing checklist, and utility setup schedule.",
                "defaultOutputType": "moving_checklist",
                "suggestedPrompt": "Create a moving preparation checklist for moving date: ",
            },
        ],
    },
    {
        "id": "cross_agent_weekly_review",
        "name": "Cross-Agent Weekly Review",
        "description": "Holistic life sync flow: coordinate priorities across areas, review budget and wellness habits, and generate next week's focus.",
        "steps": [
            {
                "stepIndex": 0,
                "agentId": "local_life_dashboard_cross_agent_coordinator",
                "name": "Life Dashboard Coordinator",
                "purpose": "Synthesize weekly progress across life domains (work, health, projects).",
                "defaultOutputType": "weekly_review",
                "suggestedPrompt": "Synthesize weekly achievements and open items across life domains: ",
            },
            {
                "stepIndex": 1,
                "agentId": "local_finance_budget_agent",
                "name": "Finance & Budget Agent",
                "purpose": "Review weekly spend, upcoming bills, and savings progress.",
                "defaultOutputType": "budget_check",
                "suggestedPrompt": "Review weekly expenses and upcoming financial commitments: ",
            },
            {
                "stepIndex": 2,
                "agentId": "local_health_fitness_agent",
                "name": "Health & Fitness Agent",
                "purpose": "Assess sleep, activity, workout adherence, and recovery.",
                "defaultOutputType": "wellness_check",
                "suggestedPrompt": "Check weekly workout, sleep, and wellness consistency: ",
            },
            {
                "stepIndex": 3,
                "agentId": "local_review_agent",
                "name": "Review Agent",
                "purpose": "Generate unified priorities and recommendations for the upcoming week.",
                "defaultOutputType": "priorities_summary",
                "suggestedPrompt": "Consolidate these reviews into top 3 focus priorities for next week: ",
            },
        ],
    },
]


def get_builtin_playbooks() -> list[dict[str, Any]]:
    return [dict(p) for p in BUILTIN_PLAYBOOKS]


def get_command_center_agents() -> list[dict[str, Any]]:
    """Returns discovery metadata for all 37 canonical response agents."""
    agents: list[dict[str, Any]] = []
    for item in LOCAL_RESPONSE_AGENTS_INDEX:
        meta = discovery_metadata_for_agent(item)
        keywords = LOCAL_RESPONSE_AGENT_ROUTE_KEYWORDS.get(meta["agentId"], ())
        is_hs = classify_high_stakes(meta["agentId"], meta["category"])
        agents.append({
            "agentId": meta["agentId"],
            "name": meta["name"],
            "displayName": meta["displayName"],
            "category": meta["category"],
            "useWhen": meta["useWhen"],
            "responseMode": meta["responseMode"],
            "badges": meta["badges"],
            "outputTypes": meta["outputTypes"],
            "safetyNotes": meta["safetyNotes"],
            "keywords": list(keywords),
            "isHighStakes": is_hs,
            "isLocalOnly": True,
            "isManualInputOnly": True,
        })
    agents.sort(key=lambda a: (a["category"], a["displayName"]))
    return agents


def evaluate_request_readiness(
    text: str,
    selected_agent_id: str | None = None,
    context_kit_chars: int = 0,
    has_reviewed_sources: bool = False,
    source_count: int = 0,
    selected_project: str | None = None,
) -> dict[str, Any]:
    """Deterministically evaluates the readiness of a composer request without model or network calls."""
    cleaned = str(text or "").strip()
    char_count = len(cleaned)

    # 1. Empty check
    if not cleaned:
        return {
            "status": "needs_input",
            "statusDisplay": "Needs Required Input",
            "badgeClass": "inactive",
            "reason": "Enter a description of what you need into the composer.",
            "suggestion": None,
            "isHighStakes": False,
            "highStakesCategory": None,
            "highStakesWarning": None,
            "charCount": 0,
            "contextKitChars": context_kit_chars,
            "hasReviewedSources": has_reviewed_sources,
            "sourceCount": source_count,
        }

    # 2. High-stakes detection
    agent_meta = get_local_agent_metadata(selected_agent_id) if selected_agent_id else None
    category = agent_meta.get("category", "") if agent_meta else ""
    is_high_stakes = classify_high_stakes(selected_agent_id or "", category) or bool(
        re.search(
            r"\b(health|medical|doctor|symptom|prescription|allergy|legal|lawsuit|visa|immigration|court|tax|irs|invest|crypto|loan|debt|bank|emergency|evacuation|fire|poison)\b",
            cleaned,
            re.IGNORECASE,
        )
    )

    high_stakes_cat = category or ("Health / Legal / Financial" if is_high_stakes else None)
    high_stakes_warning = None
    if is_high_stakes:
        high_stakes_warning = "High-stakes topic detected: Jarvis provides local support information only and does not replace certified professionals or verified facts."

    # 3. Agent-specific checks
    if selected_agent_id:
        if selected_agent_id == "file_data_agent" and not selected_project:
            return {
                "status": "needs_project",
                "statusDisplay": "Needs Required Input",
                "badgeClass": "blocked",
                "reason": "File/Data Agent requires a selected registered project to inspect.",
                "suggestion": "Select a registered target project from the project dropdown above.",
                "isHighStakes": is_high_stakes,
                "highStakesCategory": high_stakes_cat,
                "highStakesWarning": high_stakes_warning,
                "charCount": char_count,
                "contextKitChars": context_kit_chars,
                "hasReviewedSources": has_reviewed_sources,
                "sourceCount": source_count,
            }

        if selected_agent_id == "local_decision_agent":
            has_options = bool(re.search(r"(\bvs\b|\bor\b|option|choice|alternative|between|1\.|2\.)", cleaned, re.IGNORECASE))
            if not has_options and char_count < 80 and context_kit_chars < 50:
                return {
                    "status": "needs_context",
                    "statusDisplay": "Needs More Context",
                    "badgeClass": "waiting_for_approval",
                    "reason": "Decision Agent evaluates tradeoffs between alternatives. Specify at least two options to compare.",
                    "suggestion": "Options to compare:\n1. [Option A]\n2. [Option B]\nKey priorities: [Cost / Speed / Safety]",
                    "isHighStakes": is_high_stakes,
                    "highStakesCategory": high_stakes_cat,
                    "highStakesWarning": high_stakes_warning,
                    "charCount": char_count,
                    "contextKitChars": context_kit_chars,
                    "hasReviewedSources": has_reviewed_sources,
                    "sourceCount": source_count,
                }

        if selected_agent_id in ("local_review_agent", "local_summarization_agent", "local_extraction_agent", "local_transformation_agent"):
            if char_count < 40 and context_kit_chars < 50:
                return {
                    "status": "needs_context",
                    "statusDisplay": "Needs More Context",
                    "badgeClass": "waiting_for_approval",
                    "reason": "Selected agent requires substantive content or notes to review/summarize.",
                    "suggestion": "Content to evaluate:\n\"\"\"\n[Paste draft, notes, or code here]\n\"\"\"",
                    "isHighStakes": is_high_stakes,
                    "highStakesCategory": high_stakes_cat,
                    "highStakesWarning": high_stakes_warning,
                    "charCount": char_count,
                    "contextKitChars": context_kit_chars,
                    "hasReviewedSources": has_reviewed_sources,
                    "sourceCount": source_count,
                }

        if selected_agent_id == "local_troubleshooting_agent":
            has_symptoms = bool(re.search(r"(error|fail|bug|issue|crash|symptom|exception|stack|warning|broken|unexpected)", cleaned, re.IGNORECASE))
            if not has_symptoms and char_count < 60:
                return {
                    "status": "needs_context",
                    "statusDisplay": "Needs More Context",
                    "badgeClass": "waiting_for_approval",
                    "reason": "Troubleshooting Agent needs observed error messages, unexpected behaviors, or symptoms.",
                    "suggestion": "Observed error / symptom:\nExpected behavior:\nSteps to reproduce:",
                    "isHighStakes": is_high_stakes,
                    "highStakesCategory": high_stakes_cat,
                    "highStakesWarning": high_stakes_warning,
                    "charCount": char_count,
                    "contextKitChars": context_kit_chars,
                    "hasReviewedSources": has_reviewed_sources,
                    "sourceCount": source_count,
                }

    # 4. Very brief / vague check
    if char_count < 15 and context_kit_chars < 50:
        return {
            "status": "needs_context",
            "statusDisplay": "Needs More Context",
            "badgeClass": "waiting_for_approval",
            "reason": "Request is very brief. Provide more detail or select a Context Kit to ensure an accurate response.",
            "suggestion": "Add specific requirements, constraints, or goals for this request.",
            "isHighStakes": is_high_stakes,
            "highStakesCategory": high_stakes_cat,
            "highStakesWarning": high_stakes_warning,
            "charCount": char_count,
            "contextKitChars": context_kit_chars,
            "hasReviewedSources": has_reviewed_sources,
            "sourceCount": source_count,
        }

    # 5. High-stakes source gap check
    if is_high_stakes and not has_reviewed_sources and context_kit_chars < 50:
        return {
            "status": "high_stakes_source_gap",
            "statusDisplay": "High-Stakes Source Gap",
            "badgeClass": "moderate",
            "reason": f"High-stakes topic ({high_stakes_cat or 'Sensitive Area'}) without reviewed web evidence or context kit.",
            "suggestion": "Consider assembling a Context Kit with background notes or adding reviewed sources.",
            "isHighStakes": True,
            "highStakesCategory": high_stakes_cat,
            "highStakesWarning": high_stakes_warning,
            "charCount": char_count,
            "contextKitChars": context_kit_chars,
            "hasReviewedSources": False,
            "sourceCount": source_count,
        }

    # 6. Ambiguous route check if auto-routing
    if not selected_agent_id:
        try:
            route_preview = local_response_agent_route_preview(cleaned)
            if route_preview.get("confidence") == "weak":
                candidates = route_preview.get("top_candidates") or []
                cand_names = [c.get("displayName") or c.get("name") for c in candidates[:2] if isinstance(c, dict)]
                names_str = " or ".join(cand_names) if cand_names else "multiple agents"
                return {
                    "status": "ambiguous_route",
                    "statusDisplay": "Ambiguous Route",
                    "badgeClass": "moderate",
                    "reason": f"Request could match {names_str}. Specify intent more clearly or select an agent in Command Center.",
                    "suggestion": f"I want to [plan / review / summarize / troubleshoot]: {cleaned}",
                    "isHighStakes": is_high_stakes,
                    "highStakesCategory": high_stakes_cat,
                    "highStakesWarning": high_stakes_warning,
                    "charCount": char_count,
                    "contextKitChars": context_kit_chars,
                    "hasReviewedSources": has_reviewed_sources,
                    "sourceCount": source_count,
                }
        except Exception:
            pass

    # 7. Ready
    return {
        "status": "ready",
        "statusDisplay": "Ready",
        "badgeClass": "succeeded",
        "reason": "Request meets all deterministic readiness criteria.",
        "suggestion": None,
        "isHighStakes": is_high_stakes,
        "highStakesCategory": high_stakes_cat,
        "highStakesWarning": high_stakes_warning,
        "charCount": char_count,
        "contextKitChars": context_kit_chars,
        "hasReviewedSources": has_reviewed_sources,
        "sourceCount": source_count,
    }
