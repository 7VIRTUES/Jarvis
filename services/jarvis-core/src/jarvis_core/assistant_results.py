from __future__ import annotations

import re
from typing import Any


MAX_REVIEW_PACKET_CHARS = 16_000
MAX_RESULT_BOARD_ENTRIES = 20
SUPPORTED_DECISION_STYLES = ("balanced", "safest", "fastest", "cheapest", "highest_upside")


def build_review_packet(
    entries: list[dict[str, Any]],
    review_question: str = "",
    user_notes: str = "",
    unresolved_questions: list[str] | None = None,
) -> dict[str, Any]:
    """Assembles a transparent, bounded Review Packet from selected Result Board entries."""
    question = review_question.strip() or "Review and synthesize selected agent responses"
    notes = user_notes.strip()
    unresolved = [q.strip() for q in (unresolved_questions or []) if q.strip()]

    formatted_entries: list[dict[str, Any]] = []
    total_entry_chars = 0

    for idx, e in enumerate(entries, start=1):
        agent_name = e.get("agentDisplayName") or e.get("agentName") or e.get("agentId") or f"Agent {idx}"
        category = e.get("category") or "General"
        primary_text = str(e.get("primaryText") or e.get("text") or "").strip()
        key_points = [str(kp).strip() for kp in e.get("keyPoints", []) if str(kp).strip()]
        citations = [str(c).strip() for c in e.get("citations", []) if str(c).strip()]
        limitations = [str(l).strip() for l in e.get("limitations", []) if str(l).strip()]
        safety_notes = [str(s).strip() for s in e.get("safetyNotes", []) if str(s).strip()]
        is_high_stakes = bool(e.get("isHighStakes"))

        entry_summary = {
            "index": idx,
            "id": e.get("id") or f"entry_{idx}",
            "agentName": agent_name,
            "category": category,
            "excerpt": primary_text[:2000],
            "keyPoints": key_points[:5],
            "evidenceCount": len(citations),
            "citations": citations[:5],
            "limitations": limitations[:3],
            "safetyNotes": safety_notes[:3],
            "isHighStakes": is_high_stakes,
            "charCount": len(primary_text[:2000]),
        }
        total_entry_chars += entry_summary["charCount"]
        formatted_entries.append(entry_summary)

    markdown_preview = format_review_packet_markdown(
        question=question,
        entries=formatted_entries,
        user_notes=notes,
        unresolved_questions=unresolved,
    )

    is_over_budget = len(markdown_preview) > MAX_REVIEW_PACKET_CHARS

    return {
        "reviewQuestion": question,
        "userNotes": notes,
        "unresolvedQuestions": unresolved,
        "entryCount": len(formatted_entries),
        "entries": formatted_entries,
        "markdown": markdown_preview[:MAX_REVIEW_PACKET_CHARS] if is_over_budget else markdown_preview,
        "totalCharacters": len(markdown_preview),
        "maxCharacters": MAX_REVIEW_PACKET_CHARS,
        "isOverBudget": is_over_budget,
    }


def format_review_packet_markdown(
    question: str,
    entries: list[dict[str, Any]],
    user_notes: str = "",
    unresolved_questions: list[str] | None = None,
) -> str:
    lines = [
        f"# Review Packet: {question}",
        "",
        f"**Selected Responses:** {len(entries)}",
    ]

    if user_notes:
        lines.extend([
            "",
            "## Reviewer Notes & Context",
            user_notes,
        ])

    lines.extend(["", "## Source Summaries"])
    for e in entries:
        hs_marker = " ⚠️ [High-Stakes]" if e.get("isHighStakes") else ""
        lines.extend([
            f"### [{e.get('index')}] {e.get('agentName')} ({e.get('category')}){hs_marker}",
            f"{e.get('excerpt')}",
        ])
        if e.get("keyPoints"):
            lines.append("**Key Points:**")
            for kp in e["keyPoints"]:
                lines.append(f"- {kp}")
        if e.get("citations"):
            lines.append(f"**Referenced Evidence ({e.get('evidenceCount', 0)} item(s)):**")
            for c in e["citations"]:
                lines.append(f"- {c}")
        if e.get("limitations"):
            lines.append(f"**Limitations:** {', '.join(e['limitations'])}")
        lines.append("")

    if unresolved_questions:
        lines.extend([
            "## Unresolved Questions",
            *[f"- {q}" for q in unresolved_questions],
            "",
        ])

    return "\n".join(lines).strip()


def evaluate_decision_readiness(
    decision_question: str,
    options: list[str],
    criteria: list[str] | None = None,
    constraints: list[str] | None = None,
    priorities: list[str] | None = None,
    context_notes: str = "",
    decision_style: str = "balanced",
    is_high_stakes: bool = False,
    option_source_counts: list[int] | None = None,
) -> dict[str, Any]:
    """Deterministically evaluates the readiness of the Decision Composer inputs."""
    question = (decision_question or "").strip()
    clean_options = [opt.strip() for opt in (options or []) if opt.strip()]
    clean_criteria = [c.strip() for c in (criteria or []) if c.strip()]
    clean_constraints = [c.strip() for c in (constraints or []) if c.strip()]
    clean_priorities = [p.strip() for p in (priorities or []) if p.strip()]
    clean_notes = (context_notes or "").strip()

    # 1. Question check
    if not question:
        return {
            "status": "needs_question",
            "statusDisplay": "Needs Decision Question",
            "badgeClass": "inactive",
            "reason": "Enter a clear decision question or choice statement.",
            "suggestion": "Example: 'Choose the best database migration strategy between PostgreSQL and SQLite'",
            "isReady": False,
        }

    # 2. Options check
    if len(clean_options) < 2:
        return {
            "status": "needs_options",
            "statusDisplay": "Needs Options",
            "badgeClass": "blocked",
            "reason": f"Decision Agent requires at least 2 distinct options (currently {len(clean_options)}).",
            "suggestion": "Add at least one additional candidate option to compare.",
            "isReady": False,
        }

    # 3. Duplicate options check
    unique_options = set(opt.lower() for opt in clean_options)
    if len(unique_options) < len(clean_options):
        return {
            "status": "duplicate_options",
            "statusDisplay": "Duplicate Options",
            "badgeClass": "moderate",
            "reason": "Two or more options appear identical. Clarify option names.",
            "suggestion": "Ensure each option represents a distinct alternative.",
            "isReady": False,
        }

    # 4. High-stakes check
    hs_detected = is_high_stakes or bool(
        re.search(
            r"\b(medical|health|legal|lawsuit|visa|immigration|court|loan|debt|bank|invest|crypto|emergency|fire|safety)\b",
            f"{question} {clean_notes} {' '.join(clean_options)}",
            re.IGNORECASE,
        )
    )

    if hs_detected and not clean_notes and not clean_criteria:
        return {
            "status": "high_stakes_source_gap",
            "statusDisplay": "High-Stakes Source Gap",
            "badgeClass": "moderate",
            "reason": "High-stakes decision topic detected without explicit criteria or reviewed evidence.",
            "suggestion": "Add concrete criteria (e.g. legal compliance, health safety) and background notes.",
            "isReady": True,
            "isHighStakes": True,
        }

    # 5. Evidence asymmetry check
    if option_source_counts and len(option_source_counts) >= 2:
        max_sources = max(option_source_counts)
        min_sources = min(option_source_counts)
        if max_sources > 0 and min_sources == 0:
            return {
                "status": "evidence_imbalance",
                "statusDisplay": "Evidence Imbalance",
                "badgeClass": "moderate",
                "reason": f"Evidence coverage differs between options ({max_sources} sources vs {min_sources} sources).",
                "suggestion": "Ensure lower-evidence options have enough context notes for fair evaluation.",
                "isReady": True,
                "isHighStakes": hs_detected,
            }

    # 6. Thin criteria warning
    if not clean_criteria and not clean_priorities and len(clean_notes) < 30:
        return {
            "status": "thin_criteria",
            "statusDisplay": "Thin Criteria",
            "badgeClass": "waiting_for_approval",
            "reason": "No explicit evaluation criteria or priorities provided. Fit ratings will be provisional.",
            "suggestion": "Add key priorities (e.g. 'Cost', 'Speed', 'Safety') for more decisive tradeoffs.",
            "isReady": True,
            "isHighStakes": hs_detected,
        }

    # 7. Ready
    return {
        "status": "ready",
        "statusDisplay": "Ready to Prepare",
        "badgeClass": "succeeded",
        "reason": f"Decision request is well-formed ({len(clean_options)} options, style: {decision_style}).",
        "suggestion": None,
        "isReady": True,
        "isHighStakes": hs_detected,
    }


def format_decision_prompt(
    decision_question: str,
    options: list[str],
    criteria: list[str] | None = None,
    constraints: list[str] | None = None,
    priorities: list[str] | None = None,
    context_notes: str = "",
    decision_style: str = "balanced",
) -> str:
    """Builds a formatted decision prompt ready for the Unified Assistant composer."""
    lines = [
        f"Decision: {decision_question.strip()}",
        f"Options: {', '.join(opt.strip() for opt in options if opt.strip())}",
    ]
    if criteria:
        lines.append(f"Criteria: {', '.join(c.strip() for c in criteria if c.strip())}")
    if constraints:
        lines.append(f"Constraints: {', '.join(c.strip() for c in constraints if c.strip())}")
    if priorities:
        lines.append(f"Priorities: {', '.join(p.strip() for p in priorities if p.strip())}")
    if decision_style and decision_style != "balanced":
        lines.append(f"Decision Style: {decision_style}")
    if context_notes and context_notes.strip():
        lines.extend(["", "Context Notes:", context_notes.strip()])

    return "\n".join(lines)


def format_comparison_matrix_summary(entries: list[dict[str, Any]]) -> str:
    """Builds a side-by-side textual comparison summary from selected board entries."""
    if not entries:
        return "No entries selected for comparison."

    lines = [
        "# Multi-Result Comparison Summary",
        "",
        f"**Comparing {len(entries)} Responses:**",
    ]

    for idx, e in enumerate(entries, start=1):
        name = e.get("agentDisplayName") or e.get("agentName") or e.get("agentId") or f"Option {idx}"
        cat = e.get("category") or "General"
        primary = str(e.get("primaryText") or e.get("text") or "").strip()[:600]
        ev_count = len(e.get("citations", []))
        lim_count = len(e.get("limitations", []))
        hs = "Yes ⚠️" if e.get("isHighStakes") else "No"
        mode = e.get("generationMode") or "deterministic"

        lines.extend([
            f"",
            f"### Option {idx}: {name} [{cat}]",
            f"- **Primary Answer:** {primary}...",
            f"- **Evidence Items:** {ev_count}",
            f"- **Limitations:** {lim_count}",
            f"- **High Stakes:** {hs}",
            f"- **Generation Mode:** {mode}",
        ])

    return "\n".join(lines)
