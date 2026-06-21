from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote


AGENT_ID = "dashboard_surface_health_agent"


@dataclass(frozen=True)
class SurfaceRequirement:
    surface_id: str
    name: str
    section_id: str
    summary_key: str | None
    required_endpoints: tuple[str, ...]
    safety_note_markers: tuple[str, ...]
    doc_links: tuple[str, ...] = ()


REQUIRED_SURFACES: tuple[SurfaceRequirement, ...] = (
    SurfaceRequirement(
        "validation-workflow",
        "Validation Workflow",
        "validation-agent-status",
        "validationAgent",
        ("/validation/runbooks", "/validation/runs"),
        ("Manual evidence only.",),
    ),
    SurfaceRequirement(
        "private-alpha-readiness-snapshot",
        "Private-Alpha Readiness Snapshot",
        "private-alpha-readiness-snapshot",
        "privateAlphaReadinessSnapshot",
        ("/readiness/snapshot", "/readiness/snapshot/latest"),
        ("Local readiness summary only.",),
    ),
    SurfaceRequirement(
        "redacted-diagnostics-bundle",
        "Redacted Diagnostics Bundle",
        "redacted-diagnostics-bundle",
        "redactedDiagnosticsBundle",
        ("/diagnostics/bundle", "/diagnostics/bundle/latest"),
        ("Local redacted diagnostics only.",),
    ),
    SurfaceRequirement(
        "evidence-report-center",
        "Evidence Report Center",
        "evidence-report-center",
        "evidenceReportCenter",
        ("/evidence/reports", "/evidence/reports/{report_id}", "/evidence/reports/{report_id}/metadata"),
        ("Local report metadata only.",),
    ),
    SurfaceRequirement(
        "agent-manifest-health-center",
        "Agent Manifest Health Center",
        "agent-manifest-health-center",
        "agentManifestHealth",
        ("/agents/manifest-health", "/agents/manifest-health/{manifest_id}"),
        ("Known local manifest directories only.",),
    ),
    SurfaceRequirement(
        "docs-runbook-center",
        "Docs/Runbook Center",
        "docs-runbook-center",
        "docsCenter",
        ("/docs/index", "/docs/{doc_id}", "/docs/{doc_id}/metadata"),
        ("Approved local Markdown docs only.",),
    ),
    SurfaceRequirement(
        "dashboard-surface-health-center",
        "Dashboard Surface Health Center",
        "dashboard-surface-health-center",
        None,
        ("/dashboard/surface-health", "/dashboard/surface-health/{surface_id}"),
        ("Local dashboard/API wiring check only.",),
        ("/docs/dashboard-surface-health.md", "/docs/dashboard-surface-health-runbook.md"),
    ),
)


class DashboardSurfaceHealthService:
    def __init__(self, routes: list[Any], dashboard_summary: dict[str, Any], dashboard_html: str):
        self.routes = routes
        self.dashboard_summary = dashboard_summary
        self.dashboard_html = dashboard_html

    def surface_health(self) -> dict[str, Any]:
        surfaces = [self._surface_status(requirement) for requirement in REQUIRED_SURFACES]
        warning_count = sum(len(surface["warnings"]) for surface in surfaces)
        healthy_count = sum(1 for surface in surfaces if surface["status"] == "healthy")
        return {
            "agentId": AGENT_ID,
            "mode": "local_read_only_dashboard_surface_health",
            "totalSurfaces": len(surfaces),
            "healthySurfaces": healthy_count,
            "warningSurfaces": len(surfaces) - healthy_count,
            "warningCount": warning_count,
            "surfaces": surfaces,
            "checkedSurfaceIds": [surface["surfaceId"] for surface in surfaces],
            "routeMutation": False,
            "reportMutation": False,
            "docMutation": False,
            "manifestMutation": False,
            "settingsMutation": False,
            "commandExecution": False,
            "externalServices": False,
            "certification": False,
            "uploads": False,
        }

    def surface_detail(self, surface_id: str) -> dict[str, Any]:
        safe_id = unquote(surface_id)
        if "/" in safe_id or "\\" in safe_id or safe_id in {"", ".", ".."} or ".." in safe_id:
            raise PermissionError("surface_id must be a known dashboard surface id")
        for surface in self.surface_health()["surfaces"]:
            if surface["surfaceId"] == safe_id:
                return surface
        raise FileNotFoundError(f"dashboard surface not found: {safe_id}")

    def _surface_status(self, requirement: SurfaceRequirement) -> dict[str, Any]:
        html = self.dashboard_html
        route_paths = self._route_paths()
        missing_sections = [] if f'id="{requirement.section_id}"' in html else [requirement.section_id]
        missing_summary_keys = []
        if requirement.summary_key and requirement.summary_key not in self.dashboard_summary:
            missing_summary_keys.append(requirement.summary_key)
        missing_endpoints = [endpoint for endpoint in requirement.required_endpoints if endpoint not in route_paths]
        unguarded_endpoints = [
            endpoint
            for endpoint in requirement.required_endpoints
            if endpoint in route_paths and not self._route_guarded(endpoint)
        ]
        missing_notes = [marker for marker in requirement.safety_note_markers if marker not in html]
        missing_docs = [link for link in requirement.doc_links if link not in html]
        warnings = []
        if missing_sections:
            warnings.append("dashboard section missing")
        if missing_summary_keys:
            warnings.append("dashboard summary key missing")
        if missing_endpoints:
            warnings.append("guarded endpoint missing")
        if unguarded_endpoints:
            warnings.append("endpoint missing dashboard LAN guard")
        if missing_notes:
            warnings.append("safety note missing")
        if missing_docs:
            warnings.append("dashboard docs link missing")
        return {
            "surfaceId": requirement.surface_id,
            "name": requirement.name,
            "status": "warning" if warnings else "healthy",
            "sectionId": requirement.section_id,
            "summaryKey": requirement.summary_key,
            "requiredEndpoints": list(requirement.required_endpoints),
            "missingSections": missing_sections,
            "missingSummaryKeys": missing_summary_keys,
            "missingEndpoints": missing_endpoints,
            "unguardedEndpoints": unguarded_endpoints,
            "missingSafetyNotes": missing_notes,
            "missingDocs": missing_docs,
            "warnings": warnings,
        }

    def _route_paths(self) -> set[str]:
        return {route.path for route in self.routes if getattr(route, "path", None)}

    def _route_guarded(self, path: str) -> bool:
        for route in self.routes:
            if getattr(route, "path", None) != path:
                continue
            dependencies = getattr(getattr(route, "dependant", None), "dependencies", [])
            return any(getattr(dependency.call, "__name__", "") == "require_dashboard_lan_access" for dependency in dependencies)
        return False

