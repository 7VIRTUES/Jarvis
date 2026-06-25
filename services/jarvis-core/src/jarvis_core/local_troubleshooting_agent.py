from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_troubleshooting_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_troubleshooting"
SUPPORTED_TROUBLESHOOTING_TYPES = ("general", "pc_issue", "app_issue", "build_error", "workflow_issue", "network_issue")
SUPPORTED_URGENCY = ("low", "normal", "high")


@dataclass(frozen=True)
class LocalTroubleshootingRequest:
    problem: str
    symptoms: list[str] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)
    environment_notes: str = ""
    attempted_fixes: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    urgency: str = "normal"
    troubleshooting_type: str = "general"


class LocalTroubleshootingAgentService:
    def create_triage(self, request: LocalTroubleshootingRequest) -> dict[str, Any]:
        problem = request.problem.strip() or "Untitled local troubleshooting problem"
        troubleshooting_type = _normalize_troubleshooting_type(request.troubleshooting_type)
        urgency = _normalize_urgency(request.urgency)
        symptoms = _clean_list(request.symptoms)
        error_messages = _clean_list(request.error_messages)
        attempted_fixes = _clean_list(request.attempted_fixes)
        constraints = _clean_list(request.constraints)
        environment_notes = request.environment_notes.strip()
        environment_points = _extract_points(environment_notes)
        thin_input = not symptoms and not error_messages and not attempted_fixes and len(environment_notes) < 40

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "problem": problem,
            "troubleshootingType": troubleshooting_type,
            "urgency": urgency,
            "triageFocus": _triage_focus(problem, troubleshooting_type, urgency, thin_input),
            "observedSignals": _observed_signals(symptoms, error_messages, environment_points, attempted_fixes, thin_input),
            "likelyCauses": _likely_causes(troubleshooting_type, symptoms, error_messages, environment_points, thin_input),
            "safeChecks": _safe_checks(troubleshooting_type, symptoms, error_messages, constraints, thin_input),
            "nextSteps": _next_steps(troubleshooting_type, urgency, attempted_fixes, constraints, thin_input),
            "escalationTriggers": _escalation_triggers(troubleshooting_type, urgency),
            "informationNeeded": _information_needed(symptoms, error_messages, environment_points, attempted_fixes, constraints),
            "avoidedActions": _avoided_actions(),
            "warnings": _warnings(thin_input, urgency),
            "limitations": _limitations(thin_input),
            "safety": local_troubleshooting_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_troubleshooting_dashboard_summary()


def local_troubleshooting_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Troubleshooting Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/troubleshooting/local-triage",
        "troubleshootingTypes": list(SUPPORTED_TROUBLESHOOTING_TYPES),
        "urgencyLevels": list(SUPPORTED_URGENCY),
        "responseOnly": True,
        "ticketPersistence": False,
        "fixValidation": False,
        "externalVerification": False,
        "sourceValidation": False,
        "testExecution": False,
        "repoInspection": False,
        "logReading": False,
        "taskPersistence": False,
        "dbWrites": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailCalendarSocialAccess": False,
        "postingOrSending": False,
        "purchases": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "downloads": False,
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided troubleshooting inputs"],
    }


def local_troubleshooting_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "ticketPersistence": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailAccess": False,
        "calendarAccess": False,
        "socialAccess": False,
        "postingOrSending": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "taskPersistence": False,
        "dbWrites": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "downloads": False,
        "uploads": False,
        "mutation": False,
        "repoInspection": False,
        "testExecution": False,
        "sourceValidation": False,
        "externalVerification": False,
        "fixValidation": False,
        "logReading": False,
        "destructiveRepair": False,
        "settingsMutation": False,
    }


def _normalize_troubleshooting_type(value: str) -> str:
    normalized = (value or "general").strip().lower()
    return normalized if normalized in SUPPORTED_TROUBLESHOOTING_TYPES else "general"


def _normalize_urgency(value: str) -> str:
    normalized = (value or "normal").strip().lower()
    return normalized if normalized in SUPPORTED_URGENCY else "normal"


def _clean_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = re.sub(r"\s+", " ", value.strip())
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:10]


def _extract_points(notes: str) -> list[str]:
    if not notes.strip():
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;:•]+)", notes)
    points: list[str] = []
    seen: set[str] = set()
    for part in raw_parts:
        cleaned = re.sub(r"^\s*[-*#\d.)]+\s*", "", part).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        points.append(cleaned)
        if len(points) >= 8:
            break
    return points


def _triage_focus(problem: str, troubleshooting_type: str, urgency: str, thin_input: bool) -> str:
    if thin_input:
        return f"Initial local triage for {problem}; more symptoms, error text, and environment notes are needed."
    if urgency == "high":
        return f"Prioritize a safe, reversible triage path for {problem} before attempting any change."
    if troubleshooting_type == "build_error":
        return f"Organize the pasted build symptoms and errors for {problem} into manual checks and likely cause areas."
    if troubleshooting_type == "network_issue":
        return f"Separate local configuration, connectivity, and service-reachability clues for {problem}."
    if troubleshooting_type == "pc_issue":
        return f"Separate device, operating-system, resource, and recent-change clues for {problem}."
    if troubleshooting_type == "app_issue":
        return f"Separate application state, input, version, and environment clues for {problem}."
    if troubleshooting_type == "workflow_issue":
        return f"Separate process, handoff, expectation, and sequencing clues for {problem}."
    return f"Triage {problem} using only the symptoms, errors, attempted fixes, constraints, and notes supplied by the user."


def _observed_signals(
    symptoms: list[str],
    error_messages: list[str],
    environment_points: list[str],
    attempted_fixes: list[str],
    thin_input: bool,
) -> dict[str, list[str]]:
    return {
        "symptoms": symptoms or ["No symptoms were provided."],
        "errorMessages": error_messages or ["No pasted error messages were provided."],
        "environmentNotes": environment_points or ["No concrete environment notes were provided."],
        "attemptedFixes": attempted_fixes or ["No attempted fixes were provided."],
        "triageQuality": ["Input is thin; conclusions are provisional."] if thin_input else ["Enough user-provided signals exist for local triage scaffolding."],
    }


def _likely_causes(
    troubleshooting_type: str,
    symptoms: list[str],
    error_messages: list[str],
    environment_points: list[str],
    thin_input: bool,
) -> list[dict[str, str]]:
    if thin_input:
        return [
            {
                "cause": "Insufficient information",
                "reasoning": "The request does not include enough symptoms, pasted errors, attempted fixes, or environment notes for a confident local triage.",
            }
        ]

    causes = [
        {
            "cause": "Configuration or environment mismatch",
            "reasoning": "User-provided environment notes, symptoms, or errors may point to a mismatch between expected and actual setup.",
        },
        {
            "cause": "Recent change or incomplete prerequisite",
            "reasoning": "If the problem appeared after a change, the next manual check is to identify that change from user-provided notes.",
        },
    ]
    if troubleshooting_type == "build_error":
        causes.append(
            {
                "cause": "Build input, dependency, or command-context issue",
                "reasoning": "Pasted build errors often need manual separation of the first failure from later cascading messages.",
            }
        )
    elif troubleshooting_type == "network_issue":
        causes.append(
            {
                "cause": "Connectivity, DNS, firewall, or service availability issue",
                "reasoning": "Network symptoms should be manually checked at local, LAN, and service layers without changing security settings.",
            }
        )
    elif troubleshooting_type == "pc_issue":
        causes.append(
            {
                "cause": "Device, driver, resource, or operating-system state issue",
                "reasoning": "PC symptoms often need a manual check of visible status, recent updates, and reversible settings.",
            }
        )
    elif troubleshooting_type == "app_issue":
        causes.append(
            {
                "cause": "Application state, input, cache, version, or permission mismatch",
                "reasoning": "Application symptoms often depend on what the user was doing and what changed immediately before the issue.",
            }
        )
    elif troubleshooting_type == "workflow_issue":
        causes.append(
            {
                "cause": "Unclear handoff, ordering, or ownership",
                "reasoning": "Workflow issues often come from missing definitions of done, inputs, or next owner.",
            }
        )
    if error_messages:
        causes.append(
            {
                "cause": "Error-specific failure path",
                "reasoning": "The pasted error excerpt should be treated as the strongest clue, without claiming external verification or log reading.",
            }
        )
    elif symptoms or environment_points:
        causes.append(
            {
                "cause": "Symptom-driven failure path",
                "reasoning": "Symptoms and environment notes provide clues, but missing error text may limit specificity.",
            }
        )
    return causes[:5]


def _safe_checks(
    troubleshooting_type: str,
    symptoms: list[str],
    error_messages: list[str],
    constraints: list[str],
    thin_input: bool,
) -> list[str]:
    checks = [
        "User-performed manual check: restate the exact problem and when it started.",
        "User-performed manual check: identify the smallest safe reproduction step, without changing files or settings.",
    ]
    if symptoms:
        checks.append(f"User-performed manual check: compare the first symptom against what normally happens: {symptoms[0]}.")
    if error_messages:
        checks.append(f"User-performed manual check: read the first pasted error line as the primary clue: {error_messages[0]}.")
    if troubleshooting_type == "build_error":
        checks.append("User-performed manual check: distinguish the first build failure from later cascading messages.")
    elif troubleshooting_type == "network_issue":
        checks.append("User-performed manual check: compare local-only, LAN, and external-reachability observations without disabling security tools.")
    elif troubleshooting_type == "pc_issue":
        checks.append("User-performed manual check: note visible device status, power, resource pressure, and recent updates without making system-wide changes.")
    elif troubleshooting_type == "app_issue":
        checks.append("User-performed manual check: note app version, current screen/state, input used, and whether a restart changes visible behavior.")
    elif troubleshooting_type == "workflow_issue":
        checks.append("User-performed manual check: map expected owner, input, output, and handoff step.")
    if constraints:
        checks.append(f"User-performed manual check: confirm each next step respects the first stated constraint: {constraints[0]}.")
    if thin_input:
        checks.append("User-performed manual check: gather symptoms, pasted errors, attempted fixes, and environment notes before acting.")
    return checks[:7]


def _next_steps(
    troubleshooting_type: str,
    urgency: str,
    attempted_fixes: list[str],
    constraints: list[str],
    thin_input: bool,
) -> list[str]:
    steps = []
    if thin_input:
        steps.append("Add symptoms, pasted error excerpts, environment notes, attempted fixes, and constraints.")
    steps.append("Choose one reversible manual check from the safeChecks list and record the observation outside this agent.")
    if attempted_fixes:
        steps.append("Separate already-attempted fixes from new checks so repeated actions do not hide the original signal.")
    if constraints:
        steps.append("Discard any next step that violates the user-provided constraints.")
    if troubleshooting_type == "build_error":
        steps.append("Focus on the earliest pasted build error before interpreting later output.")
    elif troubleshooting_type == "network_issue":
        steps.append("Escalate to a network owner or provider if manual observations point outside the local machine or LAN.")
    elif troubleshooting_type == "workflow_issue":
        steps.append("Clarify owner, expected input, expected output, and next handoff.")
    if urgency == "high":
        steps.append("Prefer preserving current state and escalating over risky repair attempts.")
    return steps[:6]


def _escalation_triggers(troubleshooting_type: str, urgency: str) -> list[str]:
    triggers = [
        "The problem affects safety, security, money, critical access, or data loss risk.",
        "The next plausible action would require destructive changes, privileged access, secret handling, or system-wide settings changes.",
    ]
    if urgency == "high":
        triggers.append("High urgency remains after the first reversible manual check.")
    if troubleshooting_type == "network_issue":
        triggers.append("Multiple devices, users, or networks show the same issue.")
    if troubleshooting_type == "pc_issue":
        triggers.append("The device shows hardware failure signs, overheating, repeated crashes, or storage warnings.")
    if troubleshooting_type == "build_error":
        triggers.append("The pasted error indicates missing credentials, private infrastructure, or production deployment risk.")
    return triggers[:6]


def _information_needed(
    symptoms: list[str],
    error_messages: list[str],
    environment_points: list[str],
    attempted_fixes: list[str],
    constraints: list[str],
) -> list[str]:
    needed = []
    if not symptoms:
        needed.append("Specific symptoms and when they appear.")
    if not error_messages:
        needed.append("Exact pasted error excerpts, if any.")
    if not environment_points:
        needed.append("Environment notes such as OS/app/build context supplied by the user.")
    if not attempted_fixes:
        needed.append("Attempted fixes and what changed after each one.")
    if not constraints:
        needed.append("Constraints such as no installs, no settings changes, no account access, or downtime limits.")
    return needed or ["No obvious missing information was detected from the supplied troubleshooting inputs."]


def _avoided_actions() -> list[str]:
    return [
        "No files should be deleted or wiped as part of this response.",
        "No destructive registry, Git history, or rollback repair is suggested.",
        "No security tools should be disabled.",
        "No untrusted downloaded-script repair is suggested.",
        "No system-wide settings changes, purchases, sends, posts, uploads, downloads, or account actions are suggested.",
    ]


def _warnings(thin_input: bool, urgency: str) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Troubleshooting input is thin; output is provisional local triage.")
    if urgency == "high":
        warnings.append("High urgency: prefer reversible manual checks and escalation over risky repair attempts.")
    return warnings


def _limitations(thin_input: bool) -> list[str]:
    limitations = [
        "Based only on user-provided troubleshooting inputs.",
        "Safe checks are manual/user-performed only; Jarvis did not execute commands, inspect files, read logs, modify settings, validate fixes, or run tests.",
        "No external verification, source validation, repo inspection, web browsing, downloads, uploads, connectors, accounts, shell commands, files, database records, tasks, tickets, emails, posts, purchases, or external services were used.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add symptoms, pasted errors, environment notes, attempted fixes, and constraints for stronger triage.")
    return limitations
