from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_security_safety_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_security_safety_review"
SUPPORTED_OUTPUT_TYPES = (
    "safety_brief",
    "risk_review",
    "privacy_checklist",
    "account_hygiene_plan",
    "device_safety_checklist",
    "phishing_scam_review",
    "travel_safety_plan",
    "incident_prep_plan",
)


@dataclass(frozen=True)
class LocalSecuritySafetyRequest:
    situation: str
    review_name: str = ""
    assets_or_accounts: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    current_controls: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    risk_tolerance: str = ""
    environment_notes: str = ""
    incident_notes: str = ""
    desired_output_type: str = "safety_brief"


class LocalSecuritySafetyAgentService:
    def create_review(self, request: LocalSecuritySafetyRequest) -> dict[str, Any]:
        review_name = _clean_text(request.review_name) or "Untitled local safety review"
        situation = _clean_text(request.situation)
        assets_or_accounts = _clean_list(request.assets_or_accounts)
        concerns = _clean_list(request.concerns)
        current_controls = _clean_list(request.current_controls)
        constraints = _clean_list(request.constraints)
        risk_tolerance = _clean_text(request.risk_tolerance)
        environment_notes = _clean_text(request.environment_notes)
        incident_notes = _clean_text(request.incident_notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            situation,
            assets_or_accounts,
            concerns,
            current_controls,
            constraints,
            risk_tolerance,
            environment_notes,
            incident_notes,
        )
        urgent_context = _looks_urgent(
            situation,
            " ".join(concerns),
            " ".join(constraints),
            environment_notes,
            incident_notes,
        )
        misuse_context = _looks_like_misuse(
            situation,
            " ".join(concerns),
            environment_notes,
            incident_notes,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "reviewName": review_name,
            "situation": situation,
            "desiredOutputType": desired_output_type,
            "safetyFocus": _safety_focus(review_name, desired_output_type, thin_input, urgent_context, misuse_context),
            "situationSummary": _situation_summary(situation, assets_or_accounts, risk_tolerance, environment_notes, thin_input),
            "riskSummary": _risk_summary(concerns, current_controls, constraints, urgent_context, misuse_context),
            "privacyChecklist": _privacy_checklist(assets_or_accounts, concerns, current_controls, constraints),
            "accountHygienePlan": _account_hygiene_plan(assets_or_accounts, concerns, current_controls, constraints),
            "deviceSafetyChecklist": _device_safety_checklist(assets_or_accounts, current_controls, environment_notes, constraints),
            "phishingScamReview": _phishing_scam_review(situation, concerns, incident_notes, misuse_context),
            "travelSafetyPlan": _travel_safety_plan(situation, assets_or_accounts, environment_notes, constraints),
            "incidentPrepPlan": _incident_prep_plan(situation, concerns, current_controls, incident_notes, urgent_context),
            "nextActions": _next_actions(desired_output_type, thin_input, urgent_context, misuse_context),
            "openQuestions": _open_questions(
                situation,
                assets_or_accounts,
                concerns,
                current_controls,
                constraints,
                risk_tolerance,
                environment_notes,
                incident_notes,
            ),
            "warnings": _warnings(thin_input, urgent_context, misuse_context),
            "limitations": _limitations(thin_input, urgent_context, misuse_context),
            "safety": local_security_safety_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_security_safety_dashboard_summary()


def local_security_safety_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Security/Safety Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/security-safety/local-review",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "fileReads": False,
        "secretReads": False,
        "browserCookieAccess": False,
        "passwordManagerAccess": False,
        "networkScanning": False,
        "vulnerabilityScanning": False,
        "malwareScanning": False,
        "shellExecution": False,
        "downloads": False,
        "remediation": False,
        "accountRecovery": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "dbWrites": False,
        "taskPersistence": False,
        "mutation": False,
        "forensicValidation": False,
        "legalValidation": False,
        "complianceCertification": False,
        "securityCertification": False,
        "limitations": ["based only on user-provided safety and security review inputs"],
    }


def local_security_safety_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "fileReads": False,
        "secretReads": False,
        "browserCookieAccess": False,
        "passwordManagerAccess": False,
        "networkScanning": False,
        "vulnerabilityScanning": False,
        "malwareScanning": False,
        "shellExecution": False,
        "downloads": False,
        "remediation": False,
        "accountRecovery": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "dbWrites": False,
        "taskPersistence": False,
        "mutation": False,
        "forensicValidation": False,
        "legalValidation": False,
        "complianceCertification": False,
        "securityCertification": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "safety_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "safety_brief"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _thin_input(
    situation: str,
    assets_or_accounts: list[str],
    concerns: list[str],
    current_controls: list[str],
    constraints: list[str],
    risk_tolerance: str,
    environment_notes: str,
    incident_notes: str,
) -> bool:
    return not any(
        [situation, assets_or_accounts, concerns, current_controls, constraints, risk_tolerance, environment_notes, incident_notes]
    )


def _looks_urgent(*values: str) -> bool:
    text = " ".join(values).lower()
    terms = (
        "emergency",
        "active threat",
        "compromise",
        "stalking",
        "violence",
        "extortion",
        "financial fraud",
        "legal exposure",
        "break-in",
        "threat",
        "unsafe",
    )
    return any(term in text for term in terms)


def _looks_like_misuse(*values: str) -> bool:
    text = " ".join(values).lower()
    terms = (
        "hack",
        "exploit",
        "bypass",
        "evade",
        "stealth",
        "credential theft",
        "malware",
        "phishing kit",
        "unauthorized access",
        "break into",
    )
    return any(term in text for term in terms)


def _safety_focus(review_name: str, desired_output_type: str, thin_input: bool, urgent_context: bool, misuse_context: bool) -> str:
    if misuse_context:
        return "Keep the response defensive and non-operational; do not provide hacking, evasion, malware, phishing, or unauthorized-access help."
    if urgent_context:
        return "Provide cautious preparation notes and route emergencies, active threats, compromise, fraud, violence, extortion, or legal exposure to appropriate help."
    if thin_input:
        return f"Clarify the user-provided safety situation for {review_name} before treating the response as a usable checklist."
    if desired_output_type == "privacy_checklist":
        return "Create a privacy checklist from supplied assets, concerns, controls, and constraints."
    if desired_output_type == "account_hygiene_plan":
        return "Create a manual account hygiene plan without accessing accounts or credential stores."
    if desired_output_type == "device_safety_checklist":
        return "Create a manual device-safety checklist without inspecting devices or running scans."
    if desired_output_type == "phishing_scam_review":
        return "Review user-provided scam or phishing notes defensively without contacting senders or opening links."
    if desired_output_type == "travel_safety_plan":
        return "Create a travel or personal-safety preparation plan from supplied notes."
    if desired_output_type == "incident_prep_plan":
        return "Create non-executing incident-prep steps from supplied notes."
    if desired_output_type == "risk_review":
        return "Summarize user-provided risks, controls, and gaps without confirming vulnerabilities."
    return f"Create a local response-only security and safety brief for {review_name}."


def _situation_summary(
    situation: str,
    assets_or_accounts: list[str],
    risk_tolerance: str,
    environment_notes: str,
    thin_input: bool,
) -> list[str]:
    summary = ["Summary is based only on the request body."]
    summary.append(f"Situation: {situation}." if situation else "Situation was not provided.")
    if assets_or_accounts:
        summary.append(f"User-named assets or accounts: {', '.join(assets_or_accounts[:5])}.")
    if risk_tolerance:
        summary.append(f"Risk tolerance: {risk_tolerance}.")
    if environment_notes:
        summary.append("Environment notes were supplied for manual context only.")
    if thin_input:
        summary.append("Input is thin; add situation, assets, concerns, current controls, constraints, risk tolerance, environment notes, or incident notes.")
    return summary


def _risk_summary(concerns: list[str], current_controls: list[str], constraints: list[str], urgent_context: bool, misuse_context: bool) -> list[str]:
    summary = []
    if concerns:
        summary.extend([f"Concern to review manually: {concern}." for concern in concerns[:4]])
    else:
        summary.append("No specific concerns were provided.")
    if current_controls:
        summary.append(f"Existing control to preserve or review: {current_controls[0]}.")
    if constraints:
        summary.append(f"Constraint to respect: {constraints[0]}.")
    if urgent_context:
        summary.append("Urgent or high-impact wording was detected; appropriate human, professional, emergency, or legal support may be needed.")
    if misuse_context:
        summary.append("Potential misuse wording was detected; the response stays defensive and avoids operational abuse steps.")
    summary.append("No device, account, file, secret, browser, network, log, or repository was inspected.")
    return summary


def _privacy_checklist(assets_or_accounts: list[str], concerns: list[str], current_controls: list[str], constraints: list[str]) -> list[str]:
    checklist = [
        "List what information should stay private and who should be allowed to see it.",
        "Review public-facing details manually before changing any setting elsewhere.",
        "Keep sensitive identifiers, secrets, tokens, and protected content out of shared notes.",
    ]
    if assets_or_accounts:
        checklist.append(f"Manual review target named by user: {assets_or_accounts[0]}.")
    if concerns:
        checklist.append(f"Privacy concern to assess manually: {concerns[0]}.")
    if current_controls:
        checklist.append(f"Current privacy control to consider: {current_controls[0]}.")
    if constraints:
        checklist.append(f"Constraint: {constraints[0]}.")
    checklist.append("No files, accounts, cookies, browsers, password managers, or cloud services were accessed.")
    return checklist


def _account_hygiene_plan(assets_or_accounts: list[str], concerns: list[str], current_controls: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Make an account inventory manually outside this response if account hygiene is in scope.",
        "Review sign-in, recovery, and contact details manually in the relevant service if appropriate.",
        "Use service-owned help pages and trusted support paths for recovery or compromise concerns.",
    ]
    if assets_or_accounts:
        plan.append(f"User-named account or asset to include in manual inventory: {assets_or_accounts[0]}.")
    if concerns:
        plan.append(f"Concern to consider while planning hygiene: {concerns[0]}.")
    if current_controls:
        plan.append(f"Existing control to keep visible: {current_controls[0]}.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    plan.append("No account was accessed, recovered, changed, or verified by this agent.")
    return plan


def _device_safety_checklist(assets_or_accounts: list[str], current_controls: list[str], environment_notes: str, constraints: list[str]) -> list[str]:
    checklist = [
        "Record the device or environment context manually before taking action elsewhere.",
        "Prefer vendor documentation or qualified help for device compromise or malware concerns.",
        "Avoid running unknown tools, scripts, downloads, or commands based on this response.",
    ]
    if assets_or_accounts:
        checklist.append(f"User-named device or asset: {assets_or_accounts[0]}.")
    if current_controls:
        checklist.append(f"Current control to preserve: {current_controls[0]}.")
    if environment_notes:
        checklist.append("Environment notes were considered only as user-provided context.")
    if constraints:
        checklist.append(f"Constraint: {constraints[0]}.")
    checklist.append("No device inspection, malware scan, vulnerability scan, network scan, or remediation was performed.")
    return checklist


def _phishing_scam_review(situation: str, concerns: list[str], incident_notes: str, misuse_context: bool) -> list[str]:
    review = [
        "Treat suspicious messages, links, payment asks, and attachments cautiously.",
        "Do not use this response as proof that something is safe or unsafe.",
        "Use trusted, separate channels for manual verification when appropriate.",
    ]
    if situation:
        review.append("Situation text was reviewed as user-provided context only.")
    if concerns:
        review.append(f"Scam or phishing concern to review manually: {concerns[0]}.")
    if incident_notes:
        review.append("Incident notes were included for non-executing preparation only.")
    if misuse_context:
        review.append("No phishing, impersonation, exploit, bypass, or unauthorized-access steps are provided.")
    review.append("No emails, links, attachments, senders, accounts, or websites were opened or verified.")
    return review


def _travel_safety_plan(situation: str, assets_or_accounts: list[str], environment_notes: str, constraints: list[str]) -> list[str]:
    plan = [
        "Prepare a manual contact and check-in plan outside this response if travel or personal safety is in scope.",
        "Keep important documents and emergency information accessible through trusted personal methods.",
        "Use local authorities, venue staff, or emergency services for active safety threats.",
    ]
    if situation:
        plan.append("Situation notes were used only to shape preparation suggestions.")
    if assets_or_accounts:
        plan.append(f"Item or account named by user for manual preparation: {assets_or_accounts[0]}.")
    if environment_notes:
        plan.append("Environment notes were considered as user-provided context only.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    return plan


def _incident_prep_plan(
    situation: str,
    concerns: list[str],
    current_controls: list[str],
    incident_notes: str,
    urgent_context: bool,
) -> list[str]:
    plan = [
        "Write down what happened, when it was noticed, and who should review it.",
        "Separate preparation notes from any remediation, recovery, or investigation work.",
        "Use qualified support for compromise, legal exposure, financial fraud, active threats, or safety risk.",
    ]
    if situation:
        plan.append("Situation notes were included without verifying facts or systems.")
    if concerns:
        plan.append(f"Incident concern to triage manually: {concerns[0]}.")
    if current_controls:
        plan.append(f"Current control to note: {current_controls[0]}.")
    if incident_notes:
        plan.append("Incident notes were treated as unverified user-provided context.")
    if urgent_context:
        plan.append("Urgent or high-impact wording means appropriate human, professional, emergency, or legal help may be needed.")
    plan.append("No forensic validation, account recovery, vulnerability confirmation, or incident resolution is claimed.")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, urgent_context: bool, misuse_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add situation details, assets, concerns, controls, constraints, risk tolerance, environment notes, or incident notes.")
    if urgent_context:
        actions.append("Contact appropriate human, professional, emergency, legal, financial, or platform support for active or high-impact concerns.")
    if misuse_context:
        actions.append("Keep the review defensive; do not seek or follow hacking, evasion, malware, phishing, or unauthorized-access instructions.")
    if desired_output_type == "privacy_checklist":
        actions.append("Use the privacy checklist for manual review only.")
    elif desired_output_type == "account_hygiene_plan":
        actions.append("Use trusted service-owned settings and support paths if manually reviewing accounts elsewhere.")
    elif desired_output_type == "device_safety_checklist":
        actions.append("Use vendor or qualified support before running tools, commands, downloads, or scans elsewhere.")
    elif desired_output_type == "incident_prep_plan":
        actions.append("Prepare notes for a qualified reviewer without treating this as incident resolution.")
    else:
        actions.append("Use this as local safety and security review support only.")
    actions.append("Do not use this response as forensic, legal, compliance, vulnerability, account-recovery, or security certification.")
    return actions[:6]


def _open_questions(
    situation: str,
    assets_or_accounts: list[str],
    concerns: list[str],
    current_controls: list[str],
    constraints: list[str],
    risk_tolerance: str,
    environment_notes: str,
    incident_notes: str,
) -> list[str]:
    questions = []
    if not situation:
        questions.append("What safety or security situation should be reviewed?")
    if not assets_or_accounts:
        questions.append("Which assets, accounts, devices, locations, or workflows are in scope?")
    if not concerns:
        questions.append("What specific concerns should be prioritized?")
    if not current_controls:
        questions.append("What controls or precautions are already in place?")
    if not constraints:
        questions.append("What actions, topics, or risks should be avoided?")
    if not risk_tolerance:
        questions.append("How cautious should the manual plan be?")
    if not environment_notes:
        questions.append("What environment context matters for the review?")
    if not incident_notes:
        questions.append("Are there incident notes or timeline details to preserve for human review?")
    return questions


def _warnings(thin_input: bool, urgent_context: bool, misuse_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Security/safety input is thin; output is a provisional local review scaffold.")
    if urgent_context:
        warnings.append("Emergency, active threat, compromise, stalking, violence, extortion, financial fraud, or legal exposure wording may require appropriate human, professional, emergency, or legal help.")
    if misuse_context:
        warnings.append("Potential misuse wording detected; no hacking, evasion, malware, phishing, exploit, credential theft, or unauthorized-access help is provided.")
    warnings.append("This response does not inspect, scan, recover, remediate, validate, certify, or access accounts, files, secrets, devices, browsers, networks, logs, or cloud services.")
    return warnings


def _limitations(thin_input: bool, urgent_context: bool, misuse_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided safety and security review inputs.",
        "No devices, accounts, files, repositories, networks, logs, secrets, browsers, cookies, password managers, tokens, emails, or cloud services were inspected.",
        "No scans, commands, scripts, downloads, malware checks, penetration tests, exploit checks, automated remediation, account recovery, email sending, posting, purchases, persistence, mutation, or external-service calls were performed.",
        "No forensic validation, compliance certification, legal validation, incident resolution, account recovery, vulnerability confirmation, system security, security certification, or readiness is claimed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add situation details, assets, concerns, controls, constraints, risk tolerance, environment notes, or incident notes.")
    if urgent_context:
        limitations.append("Emergencies, active threats, compromise, stalking, violence, extortion, financial fraud, or legal exposure require appropriate human, professional, emergency, financial, platform, or legal help.")
    if misuse_context:
        limitations.append("The response will not provide hacking, evasion, credential theft, malware, phishing, exploit, stealth, bypass, or unauthorized-access instructions.")
    return limitations
