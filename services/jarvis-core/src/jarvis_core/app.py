from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from . import APP_NAME, VERSION
from .activity_timeline import ActivityTimelineService
from .backup_readiness import BackupReadinessService
from .agent_manifest_health import AgentManifestHealthService
from .approvals import ApprovalQueue
from .audit import JsonlLogger
from .feedback import (
    FeedbackConflictError,
    FeedbackNotFoundError,
    FeedbackService,
    FeedbackValidationError,
)
from .codex_plans import CodexPlanInput, CodexPlanService
from .codex_execution import CodexExecutionService
from .assistant_coding import AssistantCodingBridge, AssistantCodingPrepareInput
from .db import init_db
from .dashboard import DashboardService, dashboard_html, first_run_setup_html
from .dashboard_surface_health import DashboardSurfaceHealthService
from .diagnostics import DiagnosticExporter
from .docs_center import DocsCenterService
from .evidence_report_center import EvidenceReportCenterService
from .events import EventBus
from .project_text_reader import ProjectTextReader
from .report_tool import ReportTool
from .file_data_agent import FileDataAgentService
from .knowledge import (
    KnowledgeConflictError,
    KnowledgeNotFoundError,
    KnowledgeSecretError,
    KnowledgeService,
    KnowledgeValidationError,
)
from .knowledge_dashboard import knowledge_dashboard_html
from .knowledge_embeddings import KnowledgeEmbeddingError, KnowledgeEmbeddingService
from .knowledge_retrieval import (
    KnowledgeRetrievalNotFoundError,
    KnowledgeRetrievalRequest,
    KnowledgeSemanticUnavailableError,
    KnowledgeRetrievalService,
)
from .knowledge_ingestion import KnowledgeIngestionService
from .inspector import inspect_project, write_markdown_report
from .local_business_agent import LocalBusinessAgentService, LocalBusinessRequest
from .local_career_agent import LocalCareerAgentService, LocalCareerRequest
from .local_classification_agent import LocalClassificationAgentService, LocalClassificationRequest
from .local_creator_agent import LocalCreatorAgentService, LocalCreatorRequest
from .local_culture_taste_high_class_lifestyle_agent import LocalCultureTasteHighClassLifestyleAgentService, LocalCultureTasteHighClassLifestyleRequest
from .local_decision_agent import LocalDecisionAgentService, LocalDecisionRequest
from .local_drafting_agent import LocalDraftingAgentService, LocalDraftingRequest
from .local_emotional_reflection_agent import LocalEmotionalReflectionAgentService, LocalEmotionalReflectionRequest
from .local_emergency_preparedness_agent import LocalEmergencyPreparednessAgentService, LocalEmergencyPreparednessRequest
from .local_everyday_life_agent import LocalEverydayLifeAgentService, LocalEverydayLifeRequest
from .local_extraction_agent import LocalExtractionAgentService, LocalExtractionRequest
from .local_finance_budget_agent import LocalFinanceBudgetAgentService, LocalFinanceBudgetRequest
from .local_food_cooking_grocery_agent import LocalFoodCookingGroceryAgentService, LocalFoodCookingGroceryRequest
from .local_home_room_living_space_agent import LocalHomeRoomLivingSpaceAgentService, LocalHomeRoomLivingSpaceRequest
from .local_hobbies_adventure_agent import LocalHobbiesAdventureAgentService, LocalHobbiesAdventureRequest
from .local_health_fitness_agent import LocalHealthFitnessAgentService, LocalHealthFitnessRequest
from .local_housing_move_travel_agent import LocalHousingMoveTravelAgentService, LocalHousingMoveTravelRequest
from .local_learning_study_agent import LocalLearningStudyAgentService, LocalLearningStudyRequest
from .local_legal_immigration_official_agent import LocalLegalImmigrationOfficialAgentService, LocalLegalImmigrationOfficialRequest
from .local_life_dashboard_coordinator_agent import LocalLifeDashboardCoordinatorAgentService, LocalLifeDashboardCoordinatorRequest
from .local_life_direction_agent import LocalLifeDirectionAgentService, LocalLifeDirectionRequest
from .local_online_presence_agent import LocalOnlinePresenceAgentService, LocalOnlinePresenceRequest
from .local_personal_admin_agent import LocalPersonalAdminAgentService, LocalPersonalAdminRequest
from .local_personal_knowledge_memory_organizer_agent import LocalPersonalKnowledgeMemoryOrganizerAgentService, LocalPersonalKnowledgeMemoryOrganizerRequest
from .local_planning_agent import LocalPlanningAgentService, LocalPlanningRequest
from .local_projects_portfolio_agent import LocalProjectsPortfolioAgentService, LocalProjectsPortfolioRequest
from .local_relationships_agent import LocalRelationshipsAgentService, LocalRelationshipsRequest
from .local_response_agents_catalog import (
    local_response_agent_categories,
    local_response_agent_manual_workflow_preview,
    local_response_agent_metadata,
    local_response_agent_request_template,
    local_response_agent_route_preview,
    local_response_agents_discovery_catalog,
)
from .memory import (
    MemoryConflictError,
    MemoryNotFoundError,
    MemorySecretError,
    MemoryService,
    MemoryUseContext,
    MemoryValidationError,
)
from .memory_retrieval import (
    MemoryRetrievalNotFoundError,
    MemoryRetrievalRequest,
    MemoryRetrievalService,
)
from .memory_dashboard import memory_dashboard_html
from .local_generation import LocalGenerationError, LocalGenerationService
from .models_dashboard import models_dashboard_html
from .unified_assistant import UnifiedAssistantService
from .unified_assistant_dashboard import unified_assistant_html
from .assistant_actions import AssistantActionBridge
from .assistant_actions_dashboard import assistant_actions_dashboard_html
from .assistant_productivity import (
    evaluate_request_readiness,
    get_builtin_playbooks,
    get_command_center_agents,
)
from .prompt_assembly import classify_high_stakes
from .lan_security import lan_setup_html, lan_setup_status, require_dashboard_lan_access, require_loopback_request
from .local_research_agent import LocalResearchAgentService, LocalResearchBriefRequest
from .local_review_agent import LocalReviewAgentService, LocalReviewRequest
from .local_security_safety_agent import LocalSecuritySafetyAgentService, LocalSecuritySafetyRequest
from .local_social_networking_agent import LocalSocialNetworkingAgentService, LocalSocialNetworkingRequest
from .local_school_robotics_agent import LocalSchoolRoboticsAgentService, LocalSchoolRoboticsRequest
from .local_summarization_agent import LocalSummarizationAgentService, LocalSummarizationRequest
from .local_transformation_agent import LocalTransformationAgentService, LocalTransformationRequest
from .local_troubleshooting_agent import LocalTroubleshootingAgentService, LocalTroubleshootingRequest
from .memory_proposals import MemoryProposalSuggestionService
from .local_vehicle_devices_gear_agent import LocalVehicleDevicesGearAgentService, LocalVehicleDevicesGearRequest
from .project_profiles import ProjectProfileService
from .project_registry import ProjectRegistry
from .readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from .redacted_diagnostics_agent import RedactedDiagnosticsBundleService
from .reports import missing_implementation_report_sections
from .runtime import ActionRequest, SafeActionRuntime
from .security_review_agent import SecurityReviewService
from .task_control import TaskControlService
from .tasks import TaskQueue
from .validation_agent import ValidationAgentService
from .time_utils import utc_now
from .vm_validation_prep import VmValidationPrepService
from .web_research import (
    agent_context_preview,
    apply_source_aware_response_fields,
    fetch_public_url,
    validate_public_url,
    web_research_policy,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = WORKSPACE_ROOT / "data" / "jarvis"
conn = init_db(DATA_ROOT / "jarvis.sqlite")
logger = JsonlLogger(DATA_ROOT / "logs")
events = EventBus(conn, logger)
projects = ProjectRegistry(conn, WORKSPACE_ROOT)
knowledge_service = KnowledgeService(
    conn,
    events,
    agent_exists=lambda agent_id: bool(local_response_agent_metadata(agent_id).get("found")),
    project_exists=lambda project_name: projects.get_project(project_name) is not None,
)
knowledge_embedding_service = KnowledgeEmbeddingService(conn, events)
knowledge_retrieval_service = KnowledgeRetrievalService(
    conn,
    events,
    agent_exists=lambda agent_id: bool(local_response_agent_metadata(agent_id).get("found")),
    embedding_service=knowledge_embedding_service,
)
knowledge_ingestion = KnowledgeIngestionService(knowledge_service, projects, WORKSPACE_ROOT)
memory_service = MemoryService(
    conn,
    events,
    agent_exists=lambda agent_id: bool(local_response_agent_metadata(agent_id).get("found")),
)
memory_retrieval_service = MemoryRetrievalService(
    conn,
    events,
    agent_exists=lambda agent_id: bool(local_response_agent_metadata(agent_id).get("found")),
)
local_generation = LocalGenerationService(conn, events)
runtime = SafeActionRuntime(logger, conn, events)
memory_proposal_suggestions = MemoryProposalSuggestionService()
feedback_service = FeedbackService(
    conn,
    events,
    memory_service,
    agent_exists=lambda agent_id: bool(local_response_agent_metadata(agent_id).get("found")),
)
approvals = ApprovalQueue(conn, events)
tasks = TaskQueue(conn, events, runtime, approvals)
task_control = TaskControlService(tasks)
codex_plans = CodexPlanService(conn, events, runtime, approvals, projects)
codex_execution = CodexExecutionService(conn, events, runtime, approvals, projects, codex_plans)
diagnostics = DiagnosticExporter(conn, WORKSPACE_ROOT, DATA_ROOT / "logs", WORKSPACE_ROOT / "connectors")
dashboard = DashboardService(
    conn,
    WORKSPACE_ROOT,
    DATA_ROOT,
    WORKSPACE_ROOT / "connectors",
    generation_status=local_generation.status,
)
security_reviews = SecurityReviewService(DATA_ROOT / "reports", WORKSPACE_ROOT, WORKSPACE_ROOT / "connectors")
project_profiles = ProjectProfileService(WORKSPACE_ROOT, WORKSPACE_ROOT / "connectors")
validation_agent = ValidationAgentService(conn, DATA_ROOT / "reports")
readiness_snapshots = PrivateAlphaReadinessSnapshotService(
    conn,
    DATA_ROOT / "reports",
    WORKSPACE_ROOT,
    WORKSPACE_ROOT / "connectors",
)
redacted_diagnostics = RedactedDiagnosticsBundleService(
    conn,
    DATA_ROOT / "reports",
    WORKSPACE_ROOT,
    WORKSPACE_ROOT / "connectors",
)
evidence_reports = EvidenceReportCenterService(DATA_ROOT / "reports")
agent_manifest_health = AgentManifestHealthService(WORKSPACE_ROOT / "connectors")
docs_center = DocsCenterService(WORKSPACE_ROOT)
activity_timeline = ActivityTimelineService(conn)
backup_readiness = BackupReadinessService()
vm_validation_prep = VmValidationPrepService()
local_research_agent = LocalResearchAgentService()
file_data_agent = FileDataAgentService(projects, WORKSPACE_ROOT)
local_planning_agent = LocalPlanningAgentService()
local_drafting_agent = LocalDraftingAgentService()
local_review_agent = LocalReviewAgentService()
local_decision_agent = LocalDecisionAgentService()
local_troubleshooting_agent = LocalTroubleshootingAgentService()
local_summarization_agent = LocalSummarizationAgentService()
local_extraction_agent = LocalExtractionAgentService()
local_classification_agent = LocalClassificationAgentService()
local_transformation_agent = LocalTransformationAgentService()
local_business_agent = LocalBusinessAgentService()
local_creator_agent = LocalCreatorAgentService()
local_food_cooking_grocery_agent = LocalFoodCookingGroceryAgentService()
local_home_room_living_space_agent = LocalHomeRoomLivingSpaceAgentService()
local_legal_immigration_official_agent = LocalLegalImmigrationOfficialAgentService()
local_emergency_preparedness_agent = LocalEmergencyPreparednessAgentService()
local_culture_taste_high_class_lifestyle_agent = LocalCultureTasteHighClassLifestyleAgentService()
local_hobbies_adventure_agent = LocalHobbiesAdventureAgentService()
local_personal_knowledge_memory_organizer_agent = LocalPersonalKnowledgeMemoryOrganizerAgentService()
local_life_dashboard_coordinator_agent = LocalLifeDashboardCoordinatorAgentService()
local_health_fitness_agent = LocalHealthFitnessAgentService()
local_everyday_life_agent = LocalEverydayLifeAgentService()
local_online_presence_agent = LocalOnlinePresenceAgentService()
local_security_safety_agent = LocalSecuritySafetyAgentService()
local_school_robotics_agent = LocalSchoolRoboticsAgentService()
local_career_agent = LocalCareerAgentService()
local_finance_budget_agent = LocalFinanceBudgetAgentService()
local_housing_move_travel_agent = LocalHousingMoveTravelAgentService()
local_learning_study_agent = LocalLearningStudyAgentService()
local_projects_portfolio_agent = LocalProjectsPortfolioAgentService()
local_social_networking_agent = LocalSocialNetworkingAgentService()
local_personal_admin_agent = LocalPersonalAdminAgentService()
local_vehicle_devices_gear_agent = LocalVehicleDevicesGearAgentService()
local_life_direction_agent = LocalLifeDirectionAgentService()
local_relationships_agent = LocalRelationshipsAgentService()
local_emotional_reflection_agent = LocalEmotionalReflectionAgentService()
unified_assistant = UnifiedAssistantService()
report_tool = ReportTool(DATA_ROOT / "reports" / "assistant")
project_text_reader = ProjectTextReader(projects, WORKSPACE_ROOT)
assistant_actions = AssistantActionBridge(
    projects,
    tasks,
    runtime,
    approvals,
    file_data_agent=file_data_agent,
    report_tool=report_tool,
    project_text_reader=project_text_reader,
    workspace_root=WORKSPACE_ROOT,
)
assistant_coding = AssistantCodingBridge(
    projects,
    project_text_reader,
    codex_plans,
    codex_execution,
    tasks,
    runtime,
    approvals,
    events,
)

app = FastAPI(title=APP_NAME, version=VERSION)


class ProjectInput(BaseModel):
    name: str
    path: str


class ActionInput(BaseModel):
    agentId: str
    actionType: str
    target: str | None = None
    taskId: str | None = None
    toolId: str = "policy_engine"
    riskLevel: str = "low"


class ProposedActionInput(BaseModel):
    toolId: str = "policy_engine"
    actionType: str
    target: str | None = None
    riskLevel: str = "low"


class TaskInput(BaseModel):
    projectName: str
    agentId: str = "coding_agent"
    taskType: str
    autonomyLevel: str = "supervised"
    dryRun: bool = True
    writeCapable: bool | None = None
    proposedActions: list[ProposedActionInput] = Field(default_factory=list)
    riskPlan: dict[str, int] = Field(default_factory=dict)


class ApprovalResolutionInput(BaseModel):
    resolvedBy: str = "local_user"
    resolutionNote: str | None = None


class MemoryProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memoryType: str
    content: str
    scopeType: str
    scopeValue: str | None = None
    sourceType: str
    sourceAgentId: str | None = None
    sourceReference: str | None = None
    proposalReason: str | None = None
    confidence: str
    sensitivity: str
    expiresAt: str | None = None
    actor: str = "local_user"


class MemoryEditInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memoryType: str | None = None
    content: str | None = None
    scopeType: str | None = None
    scopeValue: str | None = None
    sourceType: str | None = None
    sourceAgentId: str | None = None
    sourceReference: str | None = None
    proposalReason: str | None = None
    confidence: str | None = None
    sensitivity: str | None = None
    expiresAt: str | None = None
    actor: str = "local_user"


class MemoryApprovalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution: Literal["approve"]
    approvedBy: str = "local_user"


class MemoryRejectionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution: Literal["reject"]
    rejectedBy: str = "local_user"
    rejectionReason: str | None = None


class MemoryActorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = "local_user"


class MemoryContextPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    privateSession: bool = False
    projectName: str | None = Field(default=None, max_length=200)
    agentId: str | None = Field(default=None, max_length=200)
    limit: int = Field(default=50, ge=1, le=200)

class MemoryRetrievalPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    privateSession: bool = False
    projectName: str | None = Field(default=None, max_length=200)
    agentId: str | None = Field(default=None, max_length=200)
    includeSensitive: bool = False
    maxItems: int = Field(default=5, ge=1, le=10)



class FeedbackCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    responseId: str
    agentId: str
    rating: str
    issueTags: list[str] = Field(default_factory=list)
    note: str = Field(default="", max_length=1500)
    privateSession: bool = False
    actor: str = "local_user"


class FeedbackUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: str | None = None
    issueTags: list[str] | None = None
    note: str | None = Field(default=None, max_length=1500)
    actor: str = "local_user"


class FeedbackPreferenceProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str
    scopeType: str
    projectName: str | None = Field(default=None, max_length=200)
    confidence: str
    sensitivity: str
    expiresAt: str | None = None
    actor: str = "local_user"

class KnowledgePastePreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=250000)
    scopeType: str
    scopeValue: str | None = Field(default=None, max_length=200)
    sensitivity: str
    mediaType: str
    tags: list[str] = Field(default_factory=list, max_length=12)
    privateSession: bool = False


class KnowledgePasteImportInput(KnowledgePastePreviewInput):
    expectedContentHash: str = Field(min_length=64, max_length=64)
    confirmation: Literal["IMPORT"]
    actor: str = "local_user"


class KnowledgeProjectFilePreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projectName: str = Field(min_length=1, max_length=200)
    relativePath: str = Field(min_length=1, max_length=500)
    sensitivity: str
    tags: list[str] = Field(default_factory=list, max_length=12)
    privateSession: bool = False


class KnowledgeProjectFileImportInput(KnowledgeProjectFilePreviewInput):
    expectedContentHash: str = Field(min_length=64, max_length=64)
    expectedSizeBytes: int = Field(ge=0, le=500000)
    expectedModifiedAt: str
    confirmation: Literal["IMPORT"]
    actor: str = "local_user"


class KnowledgeMetadataEditInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    tags: list[str] | None = Field(default=None, max_length=12)
    sensitivity: str | None = None
    scopeType: str | None = None
    scopeValue: str | None = Field(default=None, max_length=200)
    actor: str = "local_user"


class KnowledgeReplaceContentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=250000)
    actor: str = "local_user"


class KnowledgeRefreshPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KnowledgeRefreshInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expectedContentHash: str = Field(min_length=64, max_length=64)
    expectedSizeBytes: int = Field(ge=0, le=500000)
    expectedModifiedAt: str
    confirmation: Literal["REFRESH"]
    actor: str = "local_user"


class KnowledgeActorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = "local_user"


class KnowledgeRetrievalPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=1000)
    privateSession: bool = False
    projectName: str | None = Field(default=None, max_length=200)
    agentId: str | None = Field(default=None, max_length=200)
    includeSensitive: bool = False
    maxItems: int = Field(default=5, ge=1, le=10)
    mode: Literal["lexical", "semantic", "hybrid"] = "lexical"

class KnowledgeEmbeddingProbeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(min_length=1, max_length=120)
    privateSession: bool = False


class KnowledgeEmbeddingConfigureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(min_length=1, max_length=120)
    confirmation: Literal["ENABLE EMBEDDINGS"]
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class KnowledgeEmbeddingDisableInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation: Literal["DISABLE EMBEDDINGS"]
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class KnowledgeEmbeddingClearInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: Literal["active_profile", "source", "all_profiles"]
    sourceId: str | None = Field(default=None, max_length=200)
    confirmation: Literal["DELETE EMBEDDINGS"]
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class KnowledgeEmbeddingRebuildPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sourceId: str | None = Field(default=None, max_length=200)
    includeSensitive: bool = False
    onlyMissing: bool = True
    limit: int = Field(default=32, ge=1, le=64)
    cursor: str | None = Field(default=None, max_length=1000)
    privateSession: bool = False


class KnowledgeEmbeddingRebuildInput(KnowledgeEmbeddingRebuildPreviewInput):
    confirmation: Literal["EMBED"]
    actor: str = Field(default="local_user", min_length=1, max_length=200)

_MEMORY_EDIT_FIELD_MAP = {
    "memoryType": "memory_type",
    "content": "content",
    "scopeType": "scope_type",
    "scopeValue": "scope_value",
    "sourceType": "source_type",
    "sourceAgentId": "source_agent_id",
    "sourceReference": "source_reference",
    "proposalReason": "proposal_reason",
    "confidence": "confidence",
    "sensitivity": "sensitivity",
    "expiresAt": "expires_at",
}


class ReportValidationInput(BaseModel):
    text: str


class LocalResponseAgentRoutePreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    prompt_text: str = ""
    domainsToConsider: list[str] = Field(default_factory=list)
    domains_to_consider: list[str] = Field(default_factory=list)
    preferredOutputType: str = ""
    preferred_output_type: str = ""
    urgencyLevel: str = ""
    urgency_level: str = ""
    constraintsOrNotes: str = ""
    constraints_or_notes: str = ""


class LocalResponseAgentManualWorkflowPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_goal: str = ""
    userGoal: str = ""
    candidate_agent_ids: list[str] = Field(default_factory=list)
    candidateAgentIds: list[str] = Field(default_factory=list)
    route_preview_suggestions: list[Any] = Field(default_factory=list)
    routePreviewSuggestions: list[Any] = Field(default_factory=list)
    max_steps: int = 4
    maxSteps: int | None = None
    include_web_context: bool = False
    includeWebContext: bool | None = None
    constraints_or_notes: str = ""
    constraintsOrNotes: str = ""


class WebResearchUrlInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = ""
    purpose: str = ""
    max_excerpt_chars: int = Field(default=1600, ge=200, le=6000)
    allow_redirects: bool = True
    constraintsOrNotes: str = ""
    constraints_or_notes: str = ""


class WebResearchAgentContextPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    agentId: str = ""
    user_request: str = ""
    userRequest: str = ""
    urls: list[str] = Field(default_factory=list)
    output_type: str = ""
    outputType: str = ""
    web_research_enabled: bool = False
    webResearchEnabled: bool = False
    constraintsOrNotes: str = ""
    constraints_or_notes: str = ""


class SecurityReviewInput(BaseModel):
    projectName: str | None = None
    projectPath: str | None = None
    project_name: str | None = None
    project_path: str | None = None
    mode: str = "read_only"


class CodexPlanRequest(BaseModel):
    taskId: str
    projectName: str
    agentId: str = "coding_agent"
    toolId: str = "codex_tool"
    actionType: str = "codex.plan_execution"
    taskGoal: str = ""
    exactScope: str = ""
    nonGoals: str = ""
    allowedFiles: list[str] = Field(default_factory=list)
    testCommands: list[str] = Field(default_factory=list)
    riskPlan: dict[str, int] = Field(default_factory=dict)
    sandboxMode: str = "workspace-write"
    promptPath: str = ".jarvis/prompts/current-task.md"
    outputPath: str = ".jarvis/reports/latest-codex-output.md"
    conservative: bool = False
    executionMode: str = "standard"


class CodexExecutionCancelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmation: str
    expectedExecutionId: str | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantCodingPrepareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    projectName: str = Field(min_length=1, max_length=200)
    allowedFiles: list[str] = Field(min_length=1, max_length=10)
    taskGoal: str = Field(min_length=1, max_length=4000)
    exactScope: str = Field(min_length=1, max_length=6000)
    nonGoals: str = Field(default="", max_length=4000)
    sourceResponseId: str | None = None
    sourceTurnIndex: int | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantCodingApproveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    planId: str = Field(min_length=1, max_length=100)
    confirmation: str = Field(min_length=1, max_length=200)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantCodingRejectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    planId: str = Field(min_length=1, max_length=100)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantCodingExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    planId: str = Field(min_length=1, max_length=100)
    projectName: str = Field(min_length=1, max_length=200)
    confirmation: str = Field(min_length=1, max_length=200)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantReadinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(default="", max_length=20000)
    selectedAgentId: str | None = None
    contextKitChars: int = Field(default=0, ge=0, le=100000)
    hasReviewedSources: bool = False
    sourceCount: int = Field(default=0, ge=0, le=100)
    selectedProject: str | None = None


class ValidationRunInput(BaseModel):
    runbookId: str | None = None
    runbook_id: str | None = None
    targetEnvironment: str | None = None
    target_environment: str | None = None


class ValidationStepResultInput(BaseModel):
    status: str
    notes: str | None = None
    evidence: str | None = None


class WebContextSourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = ""
    citation_label: str = ""
    source_url: str = ""
    final_url: str = ""
    title: str = ""
    domain: str = ""
    excerpt: str = Field(default="", max_length=4000)
    content_type: str = ""
    fetched: bool = False
    fetched_at: str = ""
    user_notes: str = ""
    source_type: str = "public_web_excerpt"
    recency_note: str = ""
    quality_warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class PriorAgentContextInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previous_agent_id: str = Field(default="", max_length=4000)
    previous_agent_name: str = Field(default="", max_length=4000)
    previous_output_type: str = Field(default="", max_length=4000)
    previous_summary: str = Field(default="", max_length=4000)
    previous_key_points: list[str] | str = Field(default_factory=list)
    previous_next_actions: list[str] | str = Field(default_factory=list)
    previous_limitations: list[str] | str = Field(default_factory=list)
    user_notes: str = Field(default="", max_length=4000)
    source_type: str = "manual_prior_agent_output"


class MemoryRetrievalOptionsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    privateSession: bool = False
    query: str = ""
    projectName: str | None = None
    includeSensitive: bool = False
    maxItems: int = Field(default=5, ge=1, le=10)


class KnowledgeRetrievalOptionsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    privateSession: bool = False
    query: str = ""
    projectName: str | None = Field(default=None, max_length=200)
    includeSensitive: bool = False
    maxItems: int = Field(default=5, ge=1, le=10)
    mode: Literal["lexical", "semantic", "hybrid"] = "lexical"


class MemoryProposalSuggestionOptionsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    privateSession: bool = False
    allowedTypes: list[str] = Field(default_factory=list)
    projectName: str | None = Field(default=None, max_length=200)
    maxSuggestions: int = Field(default=3, ge=1, le=3)


class GenerationOptionsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    privateSession: bool = False
    mode: Literal["deterministic", "local_model", "local_model_with_fallback"] = "deterministic"
    modelProfileId: str | None = Field(default=None, max_length=200)
    outputStyle: Literal["concise", "standard", "detailed"] = "standard"
    maxOutputCharacters: int = Field(default=4000, ge=500, le=12000)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    previewOnly: bool = False
    includeFullPromptPreview: bool = False


class LocalResponseAgentInputBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    web_context: list[WebContextSourceInput] = Field(default_factory=list)
    prior_agent_context: PriorAgentContextInput | None = None
    memory: MemoryRetrievalOptionsInput | None = None
    knowledge: KnowledgeRetrievalOptionsInput | None = None
    memoryProposalSuggestions: MemoryProposalSuggestionOptionsInput | None = None
    generation: GenerationOptionsInput | None = None


class UnifiedAssistantAnalyzeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requestText: str
    explicitAgentId: str | None = None
    categoryPreference: str | None = None
    memoryEnabled: bool | None = False
    knowledgeEnabled: bool | None = False
    generationMode: str | None = "local_model_with_fallback"
    priorAgentContext: PriorAgentContextInput | None = None
    webContext: list[WebContextSourceInput] = Field(default_factory=list)
    customOverrides: dict[str, Any] | None = None


class UnifiedAssistantExecuteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agentId: str
    payload: dict[str, Any]


class AssistantActionIntentDetectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requestText: str
    agentId: str | None = None


class AssistantActionPrepareInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requestText: str
    actionType: str
    projectName: str | None = None
    selectedRelativePaths: list[str] | None = None
    sourceAgentId: str = "unified_assistant"
    sourceResponseId: str | None = None
    sourceTurnIndex: int | None = None
    reportTitle: str | None = None
    customNotes: str | None = None


class AssistantActionPolicyPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actionType: str
    projectName: str | None = None


class AssistantActionValidateDryRunInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actionType: str
    projectName: str
    selectedRelativePaths: list[str] | None = None
    proposalId: str | None = None
    sourceAgentId: str = "unified_assistant"
    sourceResponseId: str | None = None
    reportTitle: str | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantActionExecuteReadOnlyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dryRunTaskId: str
    projectName: str
    expectedReceiptId: str | None = None
    confirmation: str
    sourceAgentId: str = "unified_assistant"
    sourceResponseId: str | None = None
    sourceTurnIndex: int | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantActionExecuteProjectTextReadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dryRunTaskId: str
    projectName: str
    relativePaths: list[str] = Field(min_length=1, max_length=5)
    expectedReceiptId: str | None = None
    confirmation: str
    sourceAgentId: str = "unified_assistant"
    sourceResponseId: str | None = None
    sourceTurnIndex: int | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class AssistantActionExecuteReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dryRunTaskId: str
    projectName: str
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=50000)
    expectedReceiptId: str | None = None
    confirmation: str
    sourceAgentId: str = "unified_assistant"
    sourceResponseId: str | None = None
    sourceTurnIndex: int | None = None
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class GenerationProbeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(min_length=1, max_length=120)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class GenerationConfigureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(min_length=1, max_length=120)
    contextCharacterLimit: int = Field(default=24000, ge=8000, le=120000)
    maximumOutputCharacters: int = Field(default=4000, ge=500, le=12000)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    keepAliveSeconds: int = Field(default=300, ge=0, le=3600)
    confirmation: str
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class GenerationDisableInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation: str
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class GenerationUnloadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation: str
    modelProfileId: str | None = Field(default=None, max_length=200)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class GenerationCancelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation: str
    expectedRuntimeId: str | None = Field(default=None, max_length=200)
    actor: str = Field(default="local_user", min_length=1, max_length=200)


class LocalResearchBriefInput(LocalResponseAgentInputBase):
    topic: str
    userProvidedNotes: str
    sourceTitles: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    desiredOutputType: str = "brief"


class FileDataSummaryInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    projectName: str


class LocalPlanningInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    goal: str
    contextNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    timeframe: str | None = None
    desiredOutputType: str = "project_plan"


class LocalDraftingInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    purpose: str
    audience: str = ""
    notes: str
    tone: str = "clear"
    format: str = "message"
    constraints: list[str] = Field(default_factory=list)
    mustInclude: list[str] = Field(default_factory=list)
    mustAvoid: list[str] = Field(default_factory=list)


class LocalReviewInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    subject: str
    content: str
    reviewType: str = "general"
    audience: str = ""
    criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    severity: str = "balanced"


class LocalDecisionInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    decision: str
    options: list[str]
    criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    contextNotes: str = ""
    decisionStyle: str = "balanced"


class LocalTroubleshootingInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    problem: str
    symptoms: list[str] = Field(default_factory=list)
    errorMessages: list[str] = Field(default_factory=list)
    environmentNotes: str = ""
    attemptedFixes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    urgency: str = "normal"
    troubleshootingType: str = "general"


class LocalSummarizationInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    content: str
    summaryType: str = "general"
    audience: str = ""
    detailLevel: str = "medium"
    focusAreas: list[str] = Field(default_factory=list)
    mustPreserve: list[str] = Field(default_factory=list)
    mustAvoid: list[str] = Field(default_factory=list)


class LocalExtractionInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    content: str
    extractionType: str = "general"
    focusAreas: list[str] = Field(default_factory=list)
    mustCapture: list[str] = Field(default_factory=list)
    mustIgnore: list[str] = Field(default_factory=list)
    detailLevel: str = "medium"


class LocalClassificationInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    content: str = ""
    items: list[str] = Field(default_factory=list)
    classificationType: str = "general"
    labels: list[str] = Field(default_factory=list)
    criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    detailLevel: str = "medium"


class LocalTransformationInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    content: str = ""
    items: list[str] = Field(default_factory=list)
    targetFormat: str = "outline"
    audience: str = ""
    constraints: list[str] = Field(default_factory=list)
    mustPreserve: list[str] = Field(default_factory=list)
    mustAvoid: list[str] = Field(default_factory=list)
    detailLevel: str = "medium"


class LocalBusinessInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    businessName: str = ""
    businessIdea: str
    targetCustomer: str = ""
    problem: str = ""
    offer: str = ""
    pricingNotes: str = ""
    operationsNotes: str = ""
    marketingNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    desiredOutputType: str = "business_brief"


class LocalHealthFitnessInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    primaryGoal: str
    currentFitnessLevel: str = ""
    ageRange: str = ""
    heightWeightNotes: str = ""
    scheduleNotes: str = ""
    equipmentAvailable: list[str] = Field(default_factory=list)
    preferredActivities: list[str] = Field(default_factory=list)
    dislikedActivities: list[str] = Field(default_factory=list)
    nutritionNotes: str = ""
    sleepRecoveryNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    injuriesOrLimitations: list[str] = Field(default_factory=list)
    habitsToBuild: list[str] = Field(default_factory=list)
    habitsToReduce: list[str] = Field(default_factory=list)
    desiredOutputType: str = "fitness_brief"


class LocalFoodCookingGroceryInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    mealGoal: str = ""
    availableIngredients: list[str] = Field(default_factory=list)
    pantryItems: list[str] = Field(default_factory=list)
    groceryItemsNeeded: list[str] = Field(default_factory=list)
    dietaryPreferences: list[str] = Field(default_factory=list)
    allergiesOrAvoidances: list[str] = Field(default_factory=list)
    budgetLevel: str = ""
    budgetNotes: str = ""
    servings: str = ""
    timeAvailableMinutes: int | None = None
    cookingSkillLevel: str = ""
    kitchenEquipment: list[str] = Field(default_factory=list)
    mealType: str = ""
    cuisinePreferences: list[str] = Field(default_factory=list)
    leftoversOrBatchPrepGoal: str = ""
    constraintsOrNotes: str = ""


class LocalHomeRoomLivingSpaceInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    roomType: str = ""
    livingSituation: str = ""
    spaceGoal: str = ""
    currentItems: list[str] = Field(default_factory=list)
    itemsToBuyOrConsider: list[str] = Field(default_factory=list)
    budgetLevel: str = ""
    budgetNotes: str = ""
    roomDimensionsOrConstraints: str = ""
    storageConstraints: str = ""
    cleaningOrMaintenanceNeeds: list[str] = Field(default_factory=list)
    aestheticPreferences: list[str] = Field(default_factory=list)
    productivityOrSleepGoals: list[str] = Field(default_factory=list)
    safetyOrAccessibilityNotes: str = ""
    timeline: str = ""
    constraintsOrNotes: str = ""


class LocalLegalImmigrationOfficialInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    matterType: str = ""
    jurisdictionOrCountryIfUserProvided: str = ""
    currentStatus: str = ""
    documentList: list[str] = Field(default_factory=list)
    deadlinesOrDates: list[str] = Field(default_factory=list)
    officeOrAgencyNameIfUserProvided: str = ""
    userQuestions: list[str] = Field(default_factory=list)
    desiredOutcome: str = ""
    riskLevelOrUrgency: str = ""
    constraintsOrNotes: str = ""


class LocalEmergencyPreparednessInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    scenarioType: str = ""
    householdSize: str = ""
    pets: list[str] = Field(default_factory=list)
    locationContextIfUserProvided: str = ""
    currentSupplies: list[str] = Field(default_factory=list)
    vehicleOrTravelContext: str = ""
    medicalOrAccessibilityNeeds: list[str] = Field(default_factory=list)
    budgetLevel: str = ""
    budgetNotes: str = ""
    timeHorizon: str = ""
    communicationContactsSummary: str = ""
    constraintsOrNotes: str = ""


class LocalCultureTasteHighClassLifestyleInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    situationOrEvent: str = ""
    cultureGoal: str = ""
    currentStyleOrBaseline: str = ""
    desiredImpression: str = ""
    budgetLevel: str = ""
    budgetNotes: str = ""
    wardrobeOrItemsAvailable: list[str] = Field(default_factory=list)
    diningOrEventContext: str = ""
    conversationContext: str = ""
    readingArtMusicFilmInterests: list[str] = Field(default_factory=list)
    etiquetteFocus: list[str] = Field(default_factory=list)
    timeline: str = ""
    constraintsOrNotes: str = ""


class LocalHobbiesAdventureInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    hobbyOrActivity: str = ""
    experienceLevel: str = ""
    adventureGoal: str = ""
    availableGear: list[str] = Field(default_factory=list)
    budgetLevel: str = ""
    budgetNotes: str = ""
    locationContextIfUserProvided: str = ""
    timeAvailable: str = ""
    groupSize: str = ""
    transportationContext: str = ""
    riskTolerance: str = ""
    safetyOrAccessibilityNotes: str = ""
    constraintsOrNotes: str = ""


class LocalPersonalKnowledgeMemoryOrganizerInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    knowledgeArea: str = ""
    sourceNotesOrSummary: str = ""
    organizationGoal: str = ""
    categoriesOrTags: list[str] = Field(default_factory=list)
    projectsOrLifeAreas: list[str] = Field(default_factory=list)
    reviewFrequency: str = ""
    priorityLevel: str = ""
    retentionGoal: str = ""
    decisionOrMemoryContext: str = ""
    constraintsOrNotes: str = ""


class LocalLifeDashboardCoordinatorInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    request: str = ""
    promptText: str = ""
    outputType: str = "summary"
    lifeAreas: list[str] = Field(default_factory=list)
    currentGoals: list[str] = Field(default_factory=list)
    currentProjects: list[str] = Field(default_factory=list)
    urgentItems: list[str] = Field(default_factory=list)
    timeHorizon: str = ""
    availableTime: str = ""
    energyLevel: str = ""
    constraintsOrNotes: str = ""
    priorityPreference: str = ""
    domainsToCoordinate: list[str] = Field(default_factory=list)
    existingAgentOutputsOrNotes: list[str] = Field(default_factory=list)
    decisionContext: str = ""
    weeklyFocus: str = ""
    riskOrStressFlags: list[str] = Field(default_factory=list)
    desiredDashboardStyle: str = ""


class LocalEverydayLifeInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    lifeArea: str = ""
    situation: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    scheduleNotes: str = ""
    householdNotes: str = ""
    errands: list[str] = Field(default_factory=list)
    peopleInvolved: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    energyNotes: str = ""
    budgetNotes: str = ""
    desiredOutputType: str = "life_brief"


class LocalOnlinePresenceInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    platforms: list[str] = Field(default_factory=list)
    currentBio: str = ""
    goals: list[str] = Field(default_factory=list)
    targetAudience: str = ""
    tone: str = ""
    strengths: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    contentIdeas: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    reputationConcerns: list[str] = Field(default_factory=list)
    desiredOutputType: str = "presence_brief"


class LocalSecuritySafetyInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    reviewName: str = ""
    situation: str
    assetsOrAccounts: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    currentControls: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    riskTolerance: str = ""
    environmentNotes: str = ""
    incidentNotes: str = ""
    desiredOutputType: str = "safety_brief"


class LocalCreatorInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    creatorName: str = ""
    platforms: list[str] = Field(default_factory=list)
    niche: str = ""
    audience: str = ""
    contentIdea: str
    goals: list[str] = Field(default_factory=list)
    tone: str = ""
    formatNotes: str = ""
    productionResources: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    existingContentNotes: str = ""
    desiredOutputType: str = "creator_brief"


class LocalSchoolRoboticsInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    studentName: str = ""
    schoolName: str = ""
    programName: str = ""
    termOrTimeline: str = ""
    academicGoal: str
    roboticsFocus: str = ""
    courses: list[str] = Field(default_factory=list)
    professorsOrLabs: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    currentPreparation: str = ""
    desiredOutputType: str = "school_brief"


class LocalCareerInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    careerGoal: str
    targetRoles: list[str] = Field(default_factory=list)
    targetIndustries: list[str] = Field(default_factory=list)
    currentExperience: str = ""
    educationNotes: str = ""
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    resumeNotes: str = ""
    jobSearchNotes: str = ""
    networkingNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    desiredOutputType: str = "career_brief"


class LocalFinanceBudgetInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    financialGoal: str
    incomeNotes: str = ""
    expenseNotes: str = ""
    debtNotes: str = ""
    loanNotes: str = ""
    rentHousingNotes: str = ""
    moveCostNotes: str = ""
    savingsNotes: str = ""
    spendingNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    desiredOutputType: str = "finance_brief"


class LocalHousingMoveTravelInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    planName: str = ""
    destination: str = ""
    housingGoal: str
    timeline: str = ""
    budgetNotes: str = ""
    housingOptions: list[str] = Field(default_factory=list)
    moveItems: list[str] = Field(default_factory=list)
    transportationNotes: str = ""
    commuteNotes: str = ""
    utilitySetupNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    desiredOutputType: str = "move_brief"


class LocalProjectsPortfolioInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    portfolioGoal: str
    targetAudience: str = ""
    targetRoles: list[str] = Field(default_factory=list)
    projectNotes: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    proofArtifacts: list[str] = Field(default_factory=list)
    currentStatus: str = ""
    constraints: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    timeline: str = ""
    desiredOutputType: str = "portfolio_brief"


class LocalLearningStudyInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    learnerName: str = ""
    learningGoal: str
    topics: list[str] = Field(default_factory=list)
    currentLevel: str = ""
    timeline: str = ""
    availableTime: str = ""
    resources: list[str] = Field(default_factory=list)
    weakAreas: list[str] = Field(default_factory=list)
    preferredMethods: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    motivationNotes: str = ""
    desiredOutputType: str = "learning_brief"


class LocalSocialNetworkingInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    socialGoal: str
    setting: str = ""
    peopleContext: str = ""
    eventNotes: str = ""
    conversationTopics: list[str] = Field(default_factory=list)
    networkingGoals: list[str] = Field(default_factory=list)
    presentationNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    comfortLevel: str = ""
    desiredOutputType: str = "social_brief"


class LocalPersonalAdminInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    adminGoal: str
    documentTypes: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    currentStatus: str = ""
    constraints: list[str] = Field(default_factory=list)
    peopleOrOfficesInvolved: list[str] = Field(default_factory=list)
    notes: str = ""
    desiredOutputType: str = "admin_brief"


class LocalVehicleDevicesGearInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    gearGoal: str
    vehicleNotes: str = ""
    deviceNotes: str = ""
    droneScooterNotes: str = ""
    inventoryItems: list[str] = Field(default_factory=list)
    maintenanceConcerns: list[str] = Field(default_factory=list)
    troubleshootingNotes: str = ""
    packingNotes: str = ""
    constraints: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    desiredOutputType: str = "gear_brief"


class LocalLifeDirectionInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    lifeQuestion: str
    currentSeason: str = ""
    values: list[str] = Field(default_factory=list)
    longTermGoals: list[str] = Field(default_factory=list)
    currentPriorities: list[str] = Field(default_factory=list)
    tensionsOrTradeoffs: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    areasToImprove: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    nonNegotiables: list[str] = Field(default_factory=list)
    reflectionNotes: str = ""
    desiredOutputType: str = "life_direction_brief"


class LocalRelationshipsInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    relationshipGoal: str
    relationshipType: str = ""
    peopleContext: str = ""
    situationNotes: str = ""
    communicationGoals: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    desiredTone: str = ""
    constraints: list[str] = Field(default_factory=list)
    desiredOutputType: str = "relationship_brief"


class LocalEmotionalReflectionInput(LocalResponseAgentInputBase):
    model_config = ConfigDict(extra="forbid")

    profileName: str = ""
    reflectionGoal: str
    currentMoodNotes: str = ""
    stressors: list[str] = Field(default_factory=list)
    energyNotes: str = ""
    recentWins: list[str] = Field(default_factory=list)
    currentChallenges: list[str] = Field(default_factory=list)
    patternsNoticed: list[str] = Field(default_factory=list)
    supportOptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    desiredOutputType: str = "reflection_brief"


LOCAL_RESPONSE_AGENT_SOURCE_CONTEXT: dict[str, tuple[str, str]] = {
    "LocalResearchBriefInput": ("local_research_agent", "Coding/Core"),
    "FileDataSummaryInput": ("file_data_agent", "Coding/Core"),
    "LocalPlanningInput": ("local_planning_agent", "Coding/Core"),
    "LocalDraftingInput": ("local_drafting_agent", "Coding/Core"),
    "LocalReviewInput": ("local_review_agent", "Coding/Core"),
    "LocalDecisionInput": ("local_decision_agent", "Coding/Core"),
    "LocalTroubleshootingInput": ("local_troubleshooting_agent", "Coding/Core"),
    "LocalSummarizationInput": ("local_summarization_agent", "Coding/Core"),
    "LocalExtractionInput": ("local_extraction_agent", "Coding/Core"),
    "LocalClassificationInput": ("local_classification_agent", "Coding/Core"),
    "LocalTransformationInput": ("local_transformation_agent", "Coding/Core"),
    "LocalBusinessInput": ("local_business_agent", "Coding/Core"),
    "LocalHealthFitnessInput": ("local_health_fitness_agent", "Health/Food/Home"),
    "LocalFoodCookingGroceryInput": ("local_food_cooking_grocery", "Health/Food/Home"),
    "LocalHomeRoomLivingSpaceInput": ("local_home_room_living_space", "Health/Food/Home"),
    "LocalLegalImmigrationOfficialInput": ("local_legal_immigration_official_matters", "Safety/Emergency"),
    "LocalEmergencyPreparednessInput": ("local_emergency_preparedness", "Safety/Emergency"),
    "LocalCultureTasteHighClassLifestyleInput": ("local_culture_taste_high_class_lifestyle", "Creativity/Hobbies"),
    "LocalHobbiesAdventureInput": ("local_hobbies_adventure", "Creativity/Hobbies"),
    "LocalPersonalKnowledgeMemoryOrganizerInput": ("local_personal_knowledge_memory_organizer", "Knowledge/Coordinator"),
    "LocalLifeDashboardCoordinatorInput": ("local_life_dashboard_cross_agent_coordinator", "Knowledge/Coordinator"),
    "LocalEverydayLifeInput": ("local_everyday_life_agent", "Life/Admin"),
    "LocalOnlinePresenceInput": ("local_online_presence_agent", "Social/Family"),
    "LocalSecuritySafetyInput": ("local_security_safety_agent", "Safety/Emergency"),
    "LocalCreatorInput": ("local_creator_agent", "Creativity/Hobbies"),
    "LocalSchoolRoboticsInput": ("local_school_robotics_agent", "School/Career"),
    "LocalCareerInput": ("local_career_agent", "School/Career"),
    "LocalFinanceBudgetInput": ("local_finance_budget_agent", "Finance/Housing/Travel"),
    "LocalHousingMoveTravelInput": ("local_housing_move_travel_agent", "Finance/Housing/Travel"),
    "LocalProjectsPortfolioInput": ("local_projects_portfolio_agent", "School/Career"),
    "LocalLearningStudyInput": ("local_learning_study_agent", "School/Career"),
    "LocalSocialNetworkingInput": ("local_social_networking_agent", "Social/Family"),
    "LocalPersonalAdminInput": ("local_personal_admin_agent", "Life/Admin"),
    "LocalVehicleDevicesGearInput": ("local_vehicle_devices_gear_agent", "Life/Admin"),
    "LocalLifeDirectionInput": ("local_life_direction_agent", "Life/Admin"),
    "LocalRelationshipsInput": ("local_relationships_agent", "Social/Family"),
    "LocalEmotionalReflectionInput": ("local_emotional_reflection_agent", "Social/Family"),
}


def _clean_prior_agent_text(value: object, max_length: int = 4000) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:max_length]


def _clean_prior_agent_list(value: object, max_items: int = 20) -> list[str]:
    if value is None:
        return []
    raw_items = value if isinstance(value, list) else [value]
    cleaned: list[str] = []
    for item in raw_items:
        text = _clean_prior_agent_text(item)
        if text:
            cleaned.append(text)
        if len(cleaned) >= max_items:
            break
    return cleaned


def normalize_prior_agent_context(raw_context: PriorAgentContextInput | dict[str, object] | None) -> dict[str, object] | None:
    if raw_context is None:
        return None
    raw = raw_context.model_dump() if isinstance(raw_context, PriorAgentContextInput) else dict(raw_context)
    normalized = {
        "previous_agent_id": _clean_prior_agent_text(raw.get("previous_agent_id")),
        "previous_agent_name": _clean_prior_agent_text(raw.get("previous_agent_name")),
        "previous_output_type": _clean_prior_agent_text(raw.get("previous_output_type")),
        "previous_summary": _clean_prior_agent_text(raw.get("previous_summary")),
        "previous_key_points": _clean_prior_agent_list(raw.get("previous_key_points")),
        "previous_next_actions": _clean_prior_agent_list(raw.get("previous_next_actions")),
        "previous_limitations": _clean_prior_agent_list(raw.get("previous_limitations")),
        "user_notes": _clean_prior_agent_text(raw.get("user_notes")),
        "source_type": _clean_prior_agent_text(raw.get("source_type")) or "manual_prior_agent_output",
    }
    if not any(
        normalized[key]
        for key in (
            "previous_agent_id",
            "previous_agent_name",
            "previous_output_type",
            "previous_summary",
            "previous_key_points",
            "previous_next_actions",
            "previous_limitations",
            "user_notes",
        )
    ):
        return None
    return normalized


def prior_context_response_fields(raw_context: PriorAgentContextInput | dict[str, object] | None) -> dict[str, object]:
    context = normalize_prior_agent_context(raw_context)
    if context is None:
        return {
            "prior_context_used": False,
            "prior_context_summary": "No manual prior agent context was provided.",
            "prior_context_limitations": [
                "No prior_agent_context was provided; no previous agent result was loaded or inferred.",
            ],
        }
    previous_name = context["previous_agent_name"] or context["previous_agent_id"] or "a prior local response agent"
    previous_output_type = context["previous_output_type"] or "unspecified output type"
    previous_summary = context["previous_summary"] or "No prior summary text was provided."
    return {
        "prior_context_used": True,
        "prior_context_summary": (
            f"Manual prior context from {previous_name} ({previous_output_type}) was included. "
            f"Summary: {previous_summary}"
        ),
        "prior_context": context,
        "prior_context_limitations": [
            "Prior context was provided manually in this request.",
            "Jarvis did not load previous runs automatically.",
            "No previous agent was automatically invoked.",
            "Prior context is not persisted by this response.",
            "Review prior output before using it as input.",
        ],
    }


def apply_prior_context_response_fields(
    response: dict[str, object],
    raw_context: PriorAgentContextInput | dict[str, object] | None,
) -> dict[str, object]:
    enriched = dict(response)
    enriched.update(prior_context_response_fields(raw_context))
    return enriched


_MEMORY_CONTEXT_LIMITATIONS = [
    "Memory context is supplementary; the current request remains authoritative.",
    "Retrieved memory may be outdated.",
    "Review sensitive or consequential context before using it.",
    "No model training occurred.",
    "No memory was automatically created or changed.",
]


def _private_session_requested(payload: LocalResponseAgentInputBase) -> bool:
    memory_private = bool(payload.memory and payload.memory.privateSession)
    knowledge_private = bool(payload.knowledge and payload.knowledge.privateSession)
    suggestions_private = bool(
        payload.memoryProposalSuggestions and payload.memoryProposalSuggestions.privateSession
    )
    generation_private = bool(payload.generation and payload.generation.privateSession)
    return memory_private or knowledge_private or suggestions_private or generation_private


def _memory_context(
    payload: LocalResponseAgentInputBase,
    agent_id: str,
    *,
    private_session: bool,
) -> dict[str, object]:
    options = payload.memory
    if options is None or not options.enabled:
        return {
            "requested": False,
            "used": False,
            "blocked": False,
            "blockReason": None,
            "retrievalId": None,
            "selectedCount": 0,
            "items": [],
            "considerations": [],
            "limitations": [],
        }
    if private_session:
        return {
            "requested": True,
            "used": False,
            "blocked": True,
            "blockReason": "private_session",
            "retrievalId": None,
            "selectedCount": 0,
            "items": [],
            "considerations": [],
            "limitations": [
                "Private session blocked retrieval and all retrieval auditing.",
                *_MEMORY_CONTEXT_LIMITATIONS,
            ],
        }
    try:
        retrieval = memory_retrieval_service.retrieve(
            MemoryRetrievalRequest(
                query=options.query,
                agent_id=agent_id,
                project_name=options.projectName,
                private_session=private_session,
                include_sensitive=options.includeSensitive,
                max_items=options.maxItems,
                purpose="agent_response",
                server_known_agent=True,
            )
        )
    except MemoryValidationError as exc:
        _raise_memory_http_error(exc)
    items = list(retrieval["items"])
    considerations = [
        {
            "memoryId": item["memoryId"],
            "memoryType": item["memoryType"],
            "content": item["content"],
            "scopeType": item["scopeType"],
            "scopeValue": item["scopeValue"],
            "reason": "; ".join(item["matchReasons"]),
        }
        for item in items
    ]
    return {
        "requested": True,
        "used": bool(items) and not retrieval["blocked"],
        "blocked": retrieval["blocked"],
        "blockReason": retrieval["blockReason"],
        "retrievalId": retrieval["retrievalId"],
        "retrievalMode": retrieval["retrievalMode"],
        "fts5Available": retrieval["fts5Available"],
        "projectName": retrieval["projectName"],
        "includeSensitive": retrieval["includeSensitive"],
        "selectedCount": retrieval["selectedCount"],
        "items": items,
        "considerations": considerations,
        "limitations": list(retrieval["limitations"]) + list(_MEMORY_CONTEXT_LIMITATIONS),
    }


_KNOWLEDGE_CONTEXT_LIMITATIONS = [
    "Knowledge context is supplementary; current user instructions remain authoritative.",
    "Imported sources may be outdated or incomplete.",
    "Source content was not independently verified.",
    "Sensitive or consequential material requires review.",
    "No source was modified.",
    "No model training occurred.",
    "No original project file was opened during retrieval.",
]

def _knowledge_context(
    payload: LocalResponseAgentInputBase,
    agent_id: str,
    *,
    private_session: bool,
) -> dict[str, object]:
    options = payload.knowledge
    if options is None or not options.enabled:
        return {
            "requested": False,
            "used": False,
            "blocked": False,
            "blockReason": None,
            "retrievalId": None,
            "requestedMode": options.mode if options is not None else "lexical",
            "actualMode": None,
            "retrievalMode": None,
            "semanticAvailable": False,
            "semanticUsed": False,
            "embeddingProvider": None,
            "embeddingModel": None,
            "embeddingProfileId": None,
            "embeddingDimensions": None,
            "selectedChunkCount": 0,
            "selectedSourceCount": 0,
            "items": [],
            "considerations": [],
            "limitations": [],
        }
    try:
        retrieval = knowledge_retrieval_service.retrieve(
            KnowledgeRetrievalRequest(
                query=options.query,
                agent_id=agent_id,
                project_name=options.projectName,
                private_session=private_session,
                include_sensitive=options.includeSensitive,
                max_items=options.maxItems,
                purpose="agent_response",
                server_known_agent=True,
                mode=options.mode,
            )
        )
    except (KnowledgeValidationError, KnowledgeSemanticUnavailableError) as exc:
        _raise_knowledge_http_error(exc)
    items = list(retrieval["items"])
    considerations = [
        {
            "citationLabel": item["citationLabel"],
            "sourceId": item["sourceId"],
            "sourceTitle": item["sourceTitle"],
            "chunkId": item["chunkId"],
            "content": item["content"],
            "scopeType": item["scopeType"],
            "scopeValue": item["scopeValue"],
            "reason": "; ".join(item["matchReasons"]),
        }
        for item in items
    ]
    context = dict(retrieval)
    context.pop("query", None)
    context["used"] = bool(items) and not bool(retrieval["blocked"])
    context["considerations"] = considerations
    context["limitations"] = list(retrieval["limitations"]) + list(
        _KNOWLEDGE_CONTEXT_LIMITATIONS
    )
    return context


def _local_context_summary(
    memory_context: dict[str, object],
    knowledge_context: dict[str, object],
    *,
    private_session: bool,
) -> dict[str, object]:
    return {
        "privateSession": private_session,
        "memoryRequested": bool(memory_context.get("requested")),
        "memoryUsed": bool(memory_context.get("used")),
        "memoryRetrievalId": memory_context.get("retrievalId"),
        "memoryItemCount": int(memory_context.get("selectedCount") or 0),
        "knowledgeRequested": bool(knowledge_context.get("requested")),
        "knowledgeUsed": bool(knowledge_context.get("used")),
        "knowledgeRetrievalId": knowledge_context.get("retrievalId"),
        "knowledgeRequestedMode": knowledge_context.get("requestedMode"),
        "knowledgeActualMode": knowledge_context.get("actualMode") or knowledge_context.get("retrievalMode"),
        "knowledgeRetrievalMode": knowledge_context.get("retrievalMode"),
        "knowledgeSemanticUsed": bool(knowledge_context.get("semanticUsed")),
        "knowledgeEmbeddingModel": knowledge_context.get("embeddingModel") if knowledge_context.get("semanticUsed") else None,
        "knowledgeChunkCount": int(knowledge_context.get("selectedChunkCount") or 0),
        "knowledgeSourceCount": int(knowledge_context.get("selectedSourceCount") or 0),
        "currentRequestAuthoritative": True,
        "automaticPersistence": False,
        "limitations": [
            "Memory and knowledge keep separate provenance and retrieval IDs.",
            "Local context is supplementary; the current request remains authoritative.",
            "No memory or knowledge was persisted automatically.",
        ],
    }


def _memory_proposal_suggestion_context(
    payload: LocalResponseAgentInputBase,
    agent_id: str,
    response_id: str,
    *,
    private_session: bool,
) -> dict[str, object]:
    options = payload.memoryProposalSuggestions
    if options is None:
        return memory_proposal_suggestions.suggest(
            request_fields={},
            response_id=response_id,
            agent_id=agent_id,
            enabled=False,
            private_session=False,
            allowed_types=[],
            project_name=None,
            max_suggestions=3,
        )
    request_fields = payload.model_dump(exclude_unset=True)
    request_fields.pop("knowledge", None)
    request_fields.pop("generation", None)
    try:
        return memory_proposal_suggestions.suggest(
            request_fields=request_fields,
            response_id=response_id,
            agent_id=agent_id,
            enabled=options.enabled,
            private_session=private_session,
            allowed_types=options.allowedTypes,
            project_name=options.projectName,
            max_suggestions=options.maxSuggestions,
        )
    except MemoryValidationError as exc:
        _raise_memory_http_error(exc)


def _response_context(agent_id: str, response_id: str, *, private_session: bool) -> dict[str, object]:
    limitations = [
        "The response itself was not automatically saved.",
        "No feedback was stored automatically.",
        "The response ID is only an ephemeral reference until explicit feedback submission.",
    ]
    if private_session:
        limitations.append("Private session blocks feedback persistence for this response.")
    return {
        "responseId": response_id,
        "agentId": agent_id,
        "generatedAt": utc_now(),
        "feedbackEligible": not private_session,
        "persisted": False,
        "limitations": limitations,
    }


def _local_response_with_web_context(
    response: dict[str, object],
    payload: LocalResponseAgentInputBase,
) -> dict[str, object]:
    agent_id, category = LOCAL_RESPONSE_AGENT_SOURCE_CONTEXT.get(
        payload.__class__.__name__, ("local_response_agent", "General")
    )
    source_response = apply_source_aware_response_fields(
        response,
        agent_id,
        category,
        [source.model_dump() for source in payload.web_context],
    )
    enriched = apply_prior_context_response_fields(source_response, payload.prior_agent_context)
    private_session = _private_session_requested(payload)
    response_id = str(uuid4())
    memory_context = _memory_context(payload, agent_id, private_session=private_session)
    enriched["memoryContext"] = memory_context
    knowledge_context = _knowledge_context(payload, agent_id, private_session=private_session)
    enriched["knowledgeContext"] = knowledge_context
    local_context = _local_context_summary(
        memory_context, knowledge_context, private_session=private_session
    )
    enriched["localContext"] = local_context
    agent_metadata = local_response_agent_metadata(agent_id)
    agent_name = str(
        agent_metadata.get("displayName")
        or agent_metadata.get("display_name")
        or agent_metadata.get("name")
        or agent_id.replace("_", " ").title()
    )
    generation_result = local_generation.process_agent_response(
        deterministic_response=response,
        request_fields=payload.model_dump(exclude_unset=True),
        agent_id=agent_id,
        agent_name=agent_name,
        category=category,
        web_context=[source.model_dump() for source in payload.web_context],
        prior_agent_context=normalize_prior_agent_context(payload.prior_agent_context),
        memory_context=memory_context,
        knowledge_context=knowledge_context,
        local_context_summary=local_context,
        generation_options=payload.generation.model_dump() if payload.generation else None,
        response_id=response_id,
        private_session=private_session,
        high_stakes=classify_high_stakes(agent_id, category),
    )
    enriched.update(generation_result)
    enriched["memoryProposalSuggestions"] = _memory_proposal_suggestion_context(
        payload,
        agent_id,
        response_id,
        private_session=private_session,
    )
    enriched["responseContext"] = _response_context(
        agent_id, response_id, private_session=private_session
    )
    return enriched


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": VERSION, "mode": "local"}


@app.get("/assistant", response_class=HTMLResponse)
def unified_assistant_page(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(unified_assistant_html())


@app.get("/actions", response_class=HTMLResponse)
def actions_center_page(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(assistant_actions_dashboard_html())


@app.get("/dashboard", response_class=HTMLResponse)
def local_dashboard(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(dashboard_html())



@app.get("/memory", response_class=HTMLResponse)
def memory_center_page(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(memory_dashboard_html())


@app.get("/knowledge", response_class=HTMLResponse)
def knowledge_library_page(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(knowledge_dashboard_html())


@app.get("/models", response_class=HTMLResponse)
def models_center_page(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(models_dashboard_html())


@app.get("/setup/lan", response_class=HTMLResponse)
def lan_setup_page(_: None = Depends(require_loopback_request)) -> HTMLResponse:
    return HTMLResponse(lan_setup_html())


@app.get("/setup/first-run", response_class=HTMLResponse)
def first_run_setup_page(_: None = Depends(require_loopback_request)) -> HTMLResponse:
    return HTMLResponse(first_run_setup_html())


@app.get("/api/dashboard/summary")
def dashboard_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.summary()


def _raise_generation_http_error(exc: LocalGenerationError) -> None:
    if exc.code in {"generation_in_progress", "generation_state_changed"}:
        status_code = 409
    elif exc.code in {"provider_unavailable", "model_unavailable", "provider_timeout"}:
        status_code = 503
    elif exc.code == "profile_not_found":
        status_code = 404
    else:
        status_code = 400
    raise HTTPException(status_code=status_code, detail=exc.safe_detail()) from exc


@app.get("/api/generation/status")
def generation_status(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return local_generation.status()


@app.post("/api/generation/probe")
def generation_probe(
    payload: GenerationProbeInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.probe(model_name=payload.modelName, actor=payload.actor)
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.post("/api/generation/configure")
def generation_configure(
    payload: GenerationConfigureInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.configure(
            model_name=payload.modelName,
            context_char_limit=payload.contextCharacterLimit,
            max_output_chars=payload.maximumOutputCharacters,
            temperature=payload.temperature,
            keep_alive_seconds=payload.keepAliveSeconds,
            confirmation=payload.confirmation,
            actor=payload.actor,
        )
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.post("/api/generation/disable")
def generation_disable(
    payload: GenerationDisableInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.disable(confirmation=payload.confirmation, actor=payload.actor)
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.post("/api/generation/unload")
def generation_unload(
    payload: GenerationUnloadInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.unload(
            confirmation=payload.confirmation,
            profile_id=payload.modelProfileId,
            actor=payload.actor,
        )
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.get("/api/generation/active")
def generation_active(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return local_generation.active_runtime_status()


@app.post("/api/generation/cancel")
def generation_cancel(
    payload: GenerationCancelInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.cancel_active(
            confirmation=payload.confirmation,
            expected_runtime_id=payload.expectedRuntimeId,
            actor=payload.actor,
        )
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.get("/api/generation/profiles")
def generation_profiles(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return local_generation.list_profiles()


@app.get("/api/generation/runs")
def generation_runs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0, le=100000),
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return local_generation.list_runs(limit=limit, offset=offset)
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.get("/api/generation/runs/{run_id}")
def generation_run_detail(
    run_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return local_generation.get_run(run_id)
    except LocalGenerationError as exc:
        _raise_generation_http_error(exc)


@app.get("/agents/local-response-agents/catalog")
def get_local_response_agents_catalog(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return local_response_agents_discovery_catalog()


@app.get("/agents/local-response-agents/categories")
def get_local_response_agent_categories(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return local_response_agent_categories()


@app.get("/agents/local-response-agents/{agent_id}/request-template")
def get_local_response_agent_request_template(
    agent_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return local_response_agent_request_template(agent_id)


@app.get("/agents/local-response-agents/{agent_id}")
def get_local_response_agent_metadata(
    agent_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return local_response_agent_metadata(agent_id)


@app.post("/agents/local-response-agents/route-preview")
def preview_local_response_agent_route(
    payload: LocalResponseAgentRoutePreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return local_response_agent_route_preview(
        text=payload.request or payload.promptText or payload.prompt_text,
        domains_to_consider=payload.domainsToConsider or payload.domains_to_consider,
        preferred_output_type=payload.preferredOutputType or payload.preferred_output_type,
        urgency_level=payload.urgencyLevel or payload.urgency_level,
        constraints_or_notes=payload.constraintsOrNotes or payload.constraints_or_notes,
    )


@app.post("/agents/local-response-agents/manual-workflow-preview")
def preview_local_response_agent_manual_workflow(
    payload: LocalResponseAgentManualWorkflowPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return local_response_agent_manual_workflow_preview(
        user_goal=payload.user_goal or payload.userGoal,
        candidate_agent_ids=payload.candidate_agent_ids or payload.candidateAgentIds,
        route_preview_suggestions=payload.route_preview_suggestions or payload.routePreviewSuggestions,
        max_steps=payload.maxSteps if payload.maxSteps is not None else payload.max_steps,
        include_web_context=payload.includeWebContext if payload.includeWebContext is not None else payload.include_web_context,
        constraints_or_notes=payload.constraints_or_notes or payload.constraintsOrNotes,
    )


@app.get("/web-research/policy")
def get_web_research_policy(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return web_research_policy(agent_count=37)


@app.post("/web-research/validate-url")
def validate_web_research_url(
    payload: WebResearchUrlInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return validate_public_url(payload.url)


@app.post("/web-research/fetch-public-url")
def fetch_web_research_public_url(
    payload: WebResearchUrlInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return fetch_public_url(
        payload.url,
        purpose=payload.purpose,
        max_excerpt_chars=payload.max_excerpt_chars,
        allow_redirects=payload.allow_redirects,
        constraints_or_notes=payload.constraintsOrNotes or payload.constraints_or_notes,
    )


@app.post("/web-research/agent-context-preview")
def preview_web_research_agent_context(
    payload: WebResearchAgentContextPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return agent_context_preview(
        agent_id=payload.agent_id or payload.agentId,
        user_request=payload.user_request or payload.userRequest,
        urls=payload.urls,
        output_type=payload.output_type or payload.outputType,
        web_research_enabled=payload.web_research_enabled or payload.webResearchEnabled,
        constraints_or_notes=payload.constraintsOrNotes or payload.constraints_or_notes,
    )


@app.post("/agents/research/local-brief")
def create_local_research_brief(
    payload: LocalResearchBriefInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_research_agent.create_brief(
        LocalResearchBriefRequest(
            topic=payload.topic,
            user_provided_notes=payload.userProvidedNotes,
            source_titles=payload.sourceTitles,
            questions=payload.questions,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/files/local-summary")
def create_file_data_summary(
    payload: FileDataSummaryInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return _local_response_with_web_context(file_data_agent.local_summary(payload.projectName), payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/agents/planning/local-plan")
def create_local_plan(
    payload: LocalPlanningInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_planning_agent.create_plan(
        LocalPlanningRequest(
            goal=payload.goal,
            context_notes=payload.contextNotes,
            constraints=payload.constraints,
            resources=payload.resources,
            blockers=payload.blockers,
            timeframe=payload.timeframe,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/drafting/local-draft")
def create_local_draft(
    payload: LocalDraftingInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_drafting_agent.create_draft(
        LocalDraftingRequest(
            purpose=payload.purpose,
            audience=payload.audience,
            notes=payload.notes,
            tone=payload.tone,
            draft_format=payload.format,
            constraints=payload.constraints,
            must_include=payload.mustInclude,
            must_avoid=payload.mustAvoid,
        )
    ), payload)






@app.post("/agents/review/local-review")
def create_local_review(
    payload: LocalReviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_review_agent.create_review(
        LocalReviewRequest(
            subject=payload.subject,
            content=payload.content,
            review_type=payload.reviewType,
            audience=payload.audience,
            criteria=payload.criteria,
            constraints=payload.constraints,
            severity=payload.severity,
        )
    ), payload)


@app.post("/agents/decision/local-decision")
def create_local_decision(
    payload: LocalDecisionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_decision_agent.compare_options(
        LocalDecisionRequest(
            decision=payload.decision,
            options=payload.options,
            criteria=payload.criteria,
            constraints=payload.constraints,
            priorities=payload.priorities,
            context_notes=payload.contextNotes,
            decision_style=payload.decisionStyle,
        )
    ), payload)


@app.post("/agents/troubleshooting/local-triage")
def create_local_troubleshooting_triage(
    payload: LocalTroubleshootingInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_troubleshooting_agent.create_triage(
        LocalTroubleshootingRequest(
            problem=payload.problem,
            symptoms=payload.symptoms,
            error_messages=payload.errorMessages,
            environment_notes=payload.environmentNotes,
            attempted_fixes=payload.attemptedFixes,
            constraints=payload.constraints,
            urgency=payload.urgency,
            troubleshooting_type=payload.troubleshootingType,
        )
    ), payload)


@app.post("/agents/summarization/local-summary")
def create_local_summarization(
    payload: LocalSummarizationInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_summarization_agent.create_summary(
        LocalSummarizationRequest(
            title=payload.title,
            content=payload.content,
            summary_type=payload.summaryType,
            audience=payload.audience,
            detail_level=payload.detailLevel,
            focus_areas=payload.focusAreas,
            must_preserve=payload.mustPreserve,
            must_avoid=payload.mustAvoid,
        )
    ), payload)


@app.post("/agents/extraction/local-extract")
def create_local_extraction(
    payload: LocalExtractionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_extraction_agent.extract_items(
        LocalExtractionRequest(
            title=payload.title,
            content=payload.content,
            extraction_type=payload.extractionType,
            focus_areas=payload.focusAreas,
            must_capture=payload.mustCapture,
            must_ignore=payload.mustIgnore,
            detail_level=payload.detailLevel,
        )
    ), payload)


@app.post("/agents/classification/local-classify")
def create_local_classification(
    payload: LocalClassificationInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_classification_agent.classify(
        LocalClassificationRequest(
            title=payload.title,
            content=payload.content,
            items=payload.items,
            classification_type=payload.classificationType,
            labels=payload.labels,
            criteria=payload.criteria,
            constraints=payload.constraints,
            detail_level=payload.detailLevel,
        )
    ), payload)


@app.post("/agents/transformation/local-transform")
def create_local_transformation(
    payload: LocalTransformationInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_transformation_agent.transform(
        LocalTransformationRequest(
            title=payload.title,
            content=payload.content,
            items=payload.items,
            target_format=payload.targetFormat,
            audience=payload.audience,
            constraints=payload.constraints,
            must_preserve=payload.mustPreserve,
            must_avoid=payload.mustAvoid,
            detail_level=payload.detailLevel,
        )
    ), payload)


@app.post("/agents/business/local-brief")
def create_local_business_brief(
    payload: LocalBusinessInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_business_agent.create_brief(
        LocalBusinessRequest(
            business_name=payload.businessName,
            business_idea=payload.businessIdea,
            target_customer=payload.targetCustomer,
            problem=payload.problem,
            offer=payload.offer,
            pricing_notes=payload.pricingNotes,
            operations_notes=payload.operationsNotes,
            marketing_notes=payload.marketingNotes,
            constraints=payload.constraints,
            resources=payload.resources,
            risks=payload.risks,
            goals=payload.goals,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/health-fitness/local-plan")
def create_local_health_fitness_plan(
    payload: LocalHealthFitnessInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_health_fitness_agent.create_plan(
        LocalHealthFitnessRequest(
            profile_name=payload.profileName,
            primary_goal=payload.primaryGoal,
            current_fitness_level=payload.currentFitnessLevel,
            age_range=payload.ageRange,
            height_weight_notes=payload.heightWeightNotes,
            schedule_notes=payload.scheduleNotes,
            equipment_available=payload.equipmentAvailable,
            preferred_activities=payload.preferredActivities,
            disliked_activities=payload.dislikedActivities,
            nutrition_notes=payload.nutritionNotes,
            sleep_recovery_notes=payload.sleepRecoveryNotes,
            constraints=payload.constraints,
            injuries_or_limitations=payload.injuriesOrLimitations,
            habits_to_build=payload.habitsToBuild,
            habits_to_reduce=payload.habitsToReduce,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/food-cooking-grocery/local-plan")
def create_local_food_cooking_grocery_plan(
    payload: LocalFoodCookingGroceryInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_food_cooking_grocery_agent.create_plan(
        LocalFoodCookingGroceryRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            meal_goal=payload.mealGoal,
            available_ingredients=payload.availableIngredients,
            pantry_items=payload.pantryItems,
            grocery_items_needed=payload.groceryItemsNeeded,
            dietary_preferences=payload.dietaryPreferences,
            allergies_or_avoidances=payload.allergiesOrAvoidances,
            budget_level=payload.budgetLevel,
            budget_notes=payload.budgetNotes,
            servings=payload.servings,
            time_available_minutes=payload.timeAvailableMinutes,
            cooking_skill_level=payload.cookingSkillLevel,
            kitchen_equipment=payload.kitchenEquipment,
            meal_type=payload.mealType,
            cuisine_preferences=payload.cuisinePreferences,
            leftovers_or_batch_prep_goal=payload.leftoversOrBatchPrepGoal,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/home-room-living-space/local-plan")
def create_local_home_room_living_space_plan(
    payload: LocalHomeRoomLivingSpaceInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_home_room_living_space_agent.create_plan(
        LocalHomeRoomLivingSpaceRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            room_type=payload.roomType,
            living_situation=payload.livingSituation,
            space_goal=payload.spaceGoal,
            current_items=payload.currentItems,
            items_to_buy_or_consider=payload.itemsToBuyOrConsider,
            budget_level=payload.budgetLevel,
            budget_notes=payload.budgetNotes,
            room_dimensions_or_constraints=payload.roomDimensionsOrConstraints,
            storage_constraints=payload.storageConstraints,
            cleaning_or_maintenance_needs=payload.cleaningOrMaintenanceNeeds,
            aesthetic_preferences=payload.aestheticPreferences,
            productivity_or_sleep_goals=payload.productivityOrSleepGoals,
            safety_or_accessibility_notes=payload.safetyOrAccessibilityNotes,
            timeline=payload.timeline,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/legal-immigration-official/local-plan")
def create_local_legal_immigration_official_plan(
    payload: LocalLegalImmigrationOfficialInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_legal_immigration_official_agent.create_plan(
        LocalLegalImmigrationOfficialRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            matter_type=payload.matterType,
            jurisdiction_or_country_if_user_provided=payload.jurisdictionOrCountryIfUserProvided,
            current_status=payload.currentStatus,
            document_list=payload.documentList,
            deadlines_or_dates=payload.deadlinesOrDates,
            office_or_agency_name_if_user_provided=payload.officeOrAgencyNameIfUserProvided,
            user_questions=payload.userQuestions,
            desired_outcome=payload.desiredOutcome,
            risk_level_or_urgency=payload.riskLevelOrUrgency,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/emergency-preparedness/local-plan")
def create_local_emergency_preparedness_plan(
    payload: LocalEmergencyPreparednessInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_emergency_preparedness_agent.create_plan(
        LocalEmergencyPreparednessRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            scenario_type=payload.scenarioType,
            household_size=payload.householdSize,
            pets=payload.pets,
            location_context_if_user_provided=payload.locationContextIfUserProvided,
            current_supplies=payload.currentSupplies,
            vehicle_or_travel_context=payload.vehicleOrTravelContext,
            medical_or_accessibility_needs=payload.medicalOrAccessibilityNeeds,
            budget_level=payload.budgetLevel,
            budget_notes=payload.budgetNotes,
            time_horizon=payload.timeHorizon,
            communication_contacts_summary=payload.communicationContactsSummary,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/culture-taste-high-class-lifestyle/local-plan")
def create_local_culture_taste_high_class_lifestyle_plan(
    payload: LocalCultureTasteHighClassLifestyleInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_culture_taste_high_class_lifestyle_agent.create_plan(
        LocalCultureTasteHighClassLifestyleRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            situation_or_event=payload.situationOrEvent,
            culture_goal=payload.cultureGoal,
            current_style_or_baseline=payload.currentStyleOrBaseline,
            desired_impression=payload.desiredImpression,
            budget_level=payload.budgetLevel,
            budget_notes=payload.budgetNotes,
            wardrobe_or_items_available=payload.wardrobeOrItemsAvailable,
            dining_or_event_context=payload.diningOrEventContext,
            conversation_context=payload.conversationContext,
            reading_art_music_film_interests=payload.readingArtMusicFilmInterests,
            etiquette_focus=payload.etiquetteFocus,
            timeline=payload.timeline,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/hobbies-adventure/local-plan")
def create_local_hobbies_adventure_plan(
    payload: LocalHobbiesAdventureInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_hobbies_adventure_agent.create_plan(
        LocalHobbiesAdventureRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            hobby_or_activity=payload.hobbyOrActivity,
            experience_level=payload.experienceLevel,
            adventure_goal=payload.adventureGoal,
            available_gear=payload.availableGear,
            budget_level=payload.budgetLevel,
            budget_notes=payload.budgetNotes,
            location_context_if_user_provided=payload.locationContextIfUserProvided,
            time_available=payload.timeAvailable,
            group_size=payload.groupSize,
            transportation_context=payload.transportationContext,
            risk_tolerance=payload.riskTolerance,
            safety_or_accessibility_notes=payload.safetyOrAccessibilityNotes,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/personal-knowledge-memory-organizer/local-plan")
def create_local_personal_knowledge_memory_organizer_plan(
    payload: LocalPersonalKnowledgeMemoryOrganizerInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_personal_knowledge_memory_organizer_agent.create_plan(
        LocalPersonalKnowledgeMemoryOrganizerRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            knowledge_area=payload.knowledgeArea,
            source_notes_or_summary=payload.sourceNotesOrSummary,
            organization_goal=payload.organizationGoal,
            categories_or_tags=payload.categoriesOrTags,
            projects_or_life_areas=payload.projectsOrLifeAreas,
            review_frequency=payload.reviewFrequency,
            priority_level=payload.priorityLevel,
            retention_goal=payload.retentionGoal,
            decision_or_memory_context=payload.decisionOrMemoryContext,
            constraints_or_notes=payload.constraintsOrNotes,
        )
    ), payload)


@app.post("/agents/life-dashboard-coordinator/local-plan")
def create_local_life_dashboard_coordinator_plan(
    payload: LocalLifeDashboardCoordinatorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_life_dashboard_coordinator_agent.create_plan(
        LocalLifeDashboardCoordinatorRequest(
            request=payload.request,
            prompt_text=payload.promptText,
            output_type=payload.outputType,
            life_areas=payload.lifeAreas,
            current_goals=payload.currentGoals,
            current_projects=payload.currentProjects,
            urgent_items=payload.urgentItems,
            time_horizon=payload.timeHorizon,
            available_time=payload.availableTime,
            energy_level=payload.energyLevel,
            constraints_or_notes=payload.constraintsOrNotes,
            priority_preference=payload.priorityPreference,
            domains_to_coordinate=payload.domainsToCoordinate,
            existing_agent_outputs_or_notes=payload.existingAgentOutputsOrNotes,
            decision_context=payload.decisionContext,
            weekly_focus=payload.weeklyFocus,
            risk_or_stress_flags=payload.riskOrStressFlags,
            desired_dashboard_style=payload.desiredDashboardStyle,
        )
    ), payload)


@app.post("/agents/everyday-life/local-plan")
def create_local_everyday_life_plan(
    payload: LocalEverydayLifeInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_everyday_life_agent.create_plan(
        LocalEverydayLifeRequest(
            life_area=payload.lifeArea,
            situation=payload.situation,
            goals=payload.goals,
            constraints=payload.constraints,
            schedule_notes=payload.scheduleNotes,
            household_notes=payload.householdNotes,
            errands=payload.errands,
            people_involved=payload.peopleInvolved,
            resources=payload.resources,
            energy_notes=payload.energyNotes,
            budget_notes=payload.budgetNotes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/online-presence/local-plan")
def create_local_online_presence_plan(
    payload: LocalOnlinePresenceInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_online_presence_agent.create_plan(
        LocalOnlinePresenceRequest(
            profile_name=payload.profileName,
            platforms=payload.platforms,
            current_bio=payload.currentBio,
            goals=payload.goals,
            target_audience=payload.targetAudience,
            tone=payload.tone,
            strengths=payload.strengths,
            projects=payload.projects,
            content_ideas=payload.contentIdeas,
            constraints=payload.constraints,
            reputation_concerns=payload.reputationConcerns,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/security-safety/local-review")
def create_local_security_safety_review(
    payload: LocalSecuritySafetyInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_security_safety_agent.create_review(
        LocalSecuritySafetyRequest(
            review_name=payload.reviewName,
            situation=payload.situation,
            assets_or_accounts=payload.assetsOrAccounts,
            concerns=payload.concerns,
            current_controls=payload.currentControls,
            constraints=payload.constraints,
            risk_tolerance=payload.riskTolerance,
            environment_notes=payload.environmentNotes,
            incident_notes=payload.incidentNotes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/creator/local-plan")
def create_local_creator_plan(
    payload: LocalCreatorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_creator_agent.create_plan(
        LocalCreatorRequest(
            creator_name=payload.creatorName,
            platforms=payload.platforms,
            niche=payload.niche,
            audience=payload.audience,
            content_idea=payload.contentIdea,
            goals=payload.goals,
            tone=payload.tone,
            format_notes=payload.formatNotes,
            production_resources=payload.productionResources,
            constraints=payload.constraints,
            existing_content_notes=payload.existingContentNotes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/school-robotics/local-plan")
def create_local_school_robotics_plan(
    payload: LocalSchoolRoboticsInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_school_robotics_agent.create_plan(
        LocalSchoolRoboticsRequest(
            student_name=payload.studentName,
            school_name=payload.schoolName,
            program_name=payload.programName,
            term_or_timeline=payload.termOrTimeline,
            academic_goal=payload.academicGoal,
            robotics_focus=payload.roboticsFocus,
            courses=payload.courses,
            professors_or_labs=payload.professorsOrLabs,
            projects=payload.projects,
            constraints=payload.constraints,
            resources=payload.resources,
            current_preparation=payload.currentPreparation,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/career/local-plan")
def create_local_career_plan(
    payload: LocalCareerInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_career_agent.create_plan(
        LocalCareerRequest(
            profile_name=payload.profileName,
            career_goal=payload.careerGoal,
            target_roles=payload.targetRoles,
            target_industries=payload.targetIndustries,
            current_experience=payload.currentExperience,
            education_notes=payload.educationNotes,
            skills=payload.skills,
            projects=payload.projects,
            resume_notes=payload.resumeNotes,
            job_search_notes=payload.jobSearchNotes,
            networking_notes=payload.networkingNotes,
            constraints=payload.constraints,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/finance-budget/local-plan")
def create_local_finance_budget_plan(
    payload: LocalFinanceBudgetInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_finance_budget_agent.create_plan(
        LocalFinanceBudgetRequest(
            profile_name=payload.profileName,
            financial_goal=payload.financialGoal,
            income_notes=payload.incomeNotes,
            expense_notes=payload.expenseNotes,
            debt_notes=payload.debtNotes,
            loan_notes=payload.loanNotes,
            rent_housing_notes=payload.rentHousingNotes,
            move_cost_notes=payload.moveCostNotes,
            savings_notes=payload.savingsNotes,
            spending_notes=payload.spendingNotes,
            constraints=payload.constraints,
            priorities=payload.priorities,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/housing-move-travel/local-plan")
def create_local_housing_move_travel_plan(
    payload: LocalHousingMoveTravelInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_housing_move_travel_agent.create_plan(
        LocalHousingMoveTravelRequest(
            plan_name=payload.planName,
            destination=payload.destination,
            housing_goal=payload.housingGoal,
            timeline=payload.timeline,
            budget_notes=payload.budgetNotes,
            housing_options=payload.housingOptions,
            move_items=payload.moveItems,
            transportation_notes=payload.transportationNotes,
            commute_notes=payload.commuteNotes,
            utility_setup_notes=payload.utilitySetupNotes,
            constraints=payload.constraints,
            priorities=payload.priorities,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/projects-portfolio/local-plan")
def create_local_projects_portfolio_plan(
    payload: LocalProjectsPortfolioInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_projects_portfolio_agent.create_plan(
        LocalProjectsPortfolioRequest(
            profile_name=payload.profileName,
            portfolio_goal=payload.portfolioGoal,
            target_audience=payload.targetAudience,
            target_roles=payload.targetRoles,
            project_notes=payload.projectNotes,
            skills=payload.skills,
            proof_artifacts=payload.proofArtifacts,
            current_status=payload.currentStatus,
            constraints=payload.constraints,
            priorities=payload.priorities,
            timeline=payload.timeline,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/learning-study/local-plan")
def create_local_learning_study_plan(
    payload: LocalLearningStudyInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_learning_study_agent.create_plan(
        LocalLearningStudyRequest(
            learner_name=payload.learnerName,
            learning_goal=payload.learningGoal,
            topics=payload.topics,
            current_level=payload.currentLevel,
            timeline=payload.timeline,
            available_time=payload.availableTime,
            resources=payload.resources,
            weak_areas=payload.weakAreas,
            preferred_methods=payload.preferredMethods,
            constraints=payload.constraints,
            motivation_notes=payload.motivationNotes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/social-networking/local-plan")
def create_local_social_networking_plan(
    payload: LocalSocialNetworkingInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_social_networking_agent.create_plan(
        LocalSocialNetworkingRequest(
            profile_name=payload.profileName,
            social_goal=payload.socialGoal,
            setting=payload.setting,
            people_context=payload.peopleContext,
            event_notes=payload.eventNotes,
            conversation_topics=payload.conversationTopics,
            networking_goals=payload.networkingGoals,
            presentation_notes=payload.presentationNotes,
            constraints=payload.constraints,
            comfort_level=payload.comfortLevel,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/personal-admin/local-plan")
def create_local_personal_admin_plan(
    payload: LocalPersonalAdminInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_personal_admin_agent.create_plan(
        LocalPersonalAdminRequest(
            profile_name=payload.profileName,
            admin_goal=payload.adminGoal,
            document_types=payload.documentTypes,
            deadlines=payload.deadlines,
            requirements=payload.requirements,
            current_status=payload.currentStatus,
            constraints=payload.constraints,
            people_or_offices_involved=payload.peopleOrOfficesInvolved,
            notes=payload.notes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/vehicle-devices-gear/local-plan")
def create_local_vehicle_devices_gear_plan(
    payload: LocalVehicleDevicesGearInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_vehicle_devices_gear_agent.create_plan(
        LocalVehicleDevicesGearRequest(
            profile_name=payload.profileName,
            gear_goal=payload.gearGoal,
            vehicle_notes=payload.vehicleNotes,
            device_notes=payload.deviceNotes,
            drone_scooter_notes=payload.droneScooterNotes,
            inventory_items=payload.inventoryItems,
            maintenance_concerns=payload.maintenanceConcerns,
            troubleshooting_notes=payload.troubleshootingNotes,
            packing_notes=payload.packingNotes,
            constraints=payload.constraints,
            priorities=payload.priorities,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/life-direction/local-plan")
def create_local_life_direction_plan(
    payload: LocalLifeDirectionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_life_direction_agent.create_plan(
        LocalLifeDirectionRequest(
            profile_name=payload.profileName,
            life_question=payload.lifeQuestion,
            current_season=payload.currentSeason,
            values=payload.values,
            long_term_goals=payload.longTermGoals,
            current_priorities=payload.currentPriorities,
            tensions_or_tradeoffs=payload.tensionsOrTradeoffs,
            constraints=payload.constraints,
            areas_to_improve=payload.areasToImprove,
            strengths=payload.strengths,
            non_negotiables=payload.nonNegotiables,
            reflection_notes=payload.reflectionNotes,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/relationships/local-plan")
def create_local_relationships_plan(
    payload: LocalRelationshipsInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_relationships_agent.create_plan(
        LocalRelationshipsRequest(
            profile_name=payload.profileName,
            relationship_goal=payload.relationshipGoal,
            relationship_type=payload.relationshipType,
            people_context=payload.peopleContext,
            situation_notes=payload.situationNotes,
            communication_goals=payload.communicationGoals,
            concerns=payload.concerns,
            boundaries=payload.boundaries,
            desired_tone=payload.desiredTone,
            constraints=payload.constraints,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


@app.post("/agents/emotional-reflection/local-reflect")
def create_local_emotional_reflection_plan(
    payload: LocalEmotionalReflectionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return _local_response_with_web_context(local_emotional_reflection_agent.create_plan(
        LocalEmotionalReflectionRequest(
            profile_name=payload.profileName,
            reflection_goal=payload.reflectionGoal,
            current_mood_notes=payload.currentMoodNotes,
            stressors=payload.stressors,
            energy_notes=payload.energyNotes,
            recent_wins=payload.recentWins,
            current_challenges=payload.currentChallenges,
            patterns_noticed=payload.patternsNoticed,
            support_options=payload.supportOptions,
            constraints=payload.constraints,
            desired_output_type=payload.desiredOutputType,
        )
    ), payload)


_UNIFIED_ASSISTANT_AGENT_DISPATCH: dict[str, tuple[type[LocalResponseAgentInputBase], Any]] = {
    "local_research_agent": (LocalResearchBriefInput, create_local_research_brief),
    "file_data_agent": (FileDataSummaryInput, create_file_data_summary),
    "local_planning_agent": (LocalPlanningInput, create_local_plan),
    "local_drafting_agent": (LocalDraftingInput, create_local_draft),
    "local_review_agent": (LocalReviewInput, create_local_review),
    "local_decision_agent": (LocalDecisionInput, create_local_decision),
    "local_troubleshooting_agent": (LocalTroubleshootingInput, create_local_troubleshooting_triage),
    "local_summarization_agent": (LocalSummarizationInput, create_local_summarization),
    "local_extraction_agent": (LocalExtractionInput, create_local_extraction),
    "local_classification_agent": (LocalClassificationInput, create_local_classification),
    "local_transformation_agent": (LocalTransformationInput, create_local_transformation),
    "local_business_agent": (LocalBusinessInput, create_local_business_brief),
    "local_health_fitness_agent": (LocalHealthFitnessInput, create_local_health_fitness_plan),
    "local_food_cooking_grocery": (LocalFoodCookingGroceryInput, create_local_food_cooking_grocery_plan),
    "local_home_room_living_space": (LocalHomeRoomLivingSpaceInput, create_local_home_room_living_space_plan),
    "local_legal_immigration_official_matters": (LocalLegalImmigrationOfficialInput, create_local_legal_immigration_official_plan),
    "local_emergency_preparedness": (LocalEmergencyPreparednessInput, create_local_emergency_preparedness_plan),
    "local_culture_taste_high_class_lifestyle": (LocalCultureTasteHighClassLifestyleInput, create_local_culture_taste_high_class_lifestyle_plan),
    "local_hobbies_adventure": (LocalHobbiesAdventureInput, create_local_hobbies_adventure_plan),
    "local_personal_knowledge_memory_organizer": (LocalPersonalKnowledgeMemoryOrganizerInput, create_local_personal_knowledge_memory_organizer_plan),
    "local_life_dashboard_cross_agent_coordinator": (LocalLifeDashboardCoordinatorInput, create_local_life_dashboard_coordinator_plan),
    "local_everyday_life_agent": (LocalEverydayLifeInput, create_local_everyday_life_plan),
    "local_online_presence_agent": (LocalOnlinePresenceInput, create_local_online_presence_plan),
    "local_security_safety_agent": (LocalSecuritySafetyInput, create_local_security_safety_review),
    "local_creator_agent": (LocalCreatorInput, create_local_creator_plan),
    "local_school_robotics_agent": (LocalSchoolRoboticsInput, create_local_school_robotics_plan),
    "local_career_agent": (LocalCareerInput, create_local_career_plan),
    "local_finance_budget_agent": (LocalFinanceBudgetInput, create_local_finance_budget_plan),
    "local_housing_move_travel_agent": (LocalHousingMoveTravelInput, create_local_housing_move_travel_plan),
    "local_projects_portfolio_agent": (LocalProjectsPortfolioInput, create_local_projects_portfolio_plan),
    "local_learning_study_agent": (LocalLearningStudyInput, create_local_learning_study_plan),
    "local_social_networking_agent": (LocalSocialNetworkingInput, create_local_social_networking_plan),
    "local_personal_admin_agent": (LocalPersonalAdminInput, create_local_personal_admin_plan),
    "local_vehicle_devices_gear_agent": (LocalVehicleDevicesGearInput, create_local_vehicle_devices_gear_plan),
    "local_life_direction_agent": (LocalLifeDirectionInput, create_local_life_direction_plan),
    "local_relationships_agent": (LocalRelationshipsInput, create_local_relationships_plan),
    "local_emotional_reflection_agent": (LocalEmotionalReflectionInput, create_local_emotional_reflection_plan),
}


@app.post("/api/assistant/analyze-route")
def assistant_analyze_route(
    payload: UnifiedAssistantAnalyzeInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    memory_opt = None
    if payload.memoryEnabled:
        memory_opt = {"retrieve_limit": 4, "private_session": False}
    knowledge_opt = None
    if payload.knowledgeEnabled:
        knowledge_opt = {"mode": "hybrid", "retrieve_limit": 4, "private_session": False}

    prior_ctx = payload.priorAgentContext.model_dump() if payload.priorAgentContext else None
    web_ctx = [w.model_dump() for w in payload.webContext] if payload.webContext else []

    return unified_assistant.analyze(
        request_text=payload.requestText,
        explicit_agent_id=payload.explicitAgentId,
        category_preference=payload.categoryPreference,
        memory_option=memory_opt,
        knowledge_option=knowledge_opt,
        generation_mode=payload.generationMode,
        prior_agent_context=prior_ctx,
        web_context=web_ctx,
        custom_overrides=payload.customOverrides,
    )


@app.post("/api/assistant/execute")
def assistant_execute_agent(
    payload: UnifiedAssistantExecuteInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    agent_id = payload.agentId.strip()
    if agent_id not in _UNIFIED_ASSISTANT_AGENT_DISPATCH:
        raise HTTPException(status_code=400, detail=f"Unknown local response agent ID: {agent_id}")

    input_cls, handler = _UNIFIED_ASSISTANT_AGENT_DISPATCH[agent_id]
    try:
        parsed_payload = input_cls(**payload.payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload for {agent_id}: {exc}") from exc

    return handler(parsed_payload, None)


@app.get("/api/assistant/actions/capabilities")
def get_assistant_action_capabilities(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return assistant_actions.get_capabilities()


@app.post("/api/assistant/actions/detect-intent")
def detect_assistant_action_intent(
    payload: AssistantActionIntentDetectInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return assistant_actions.detect_intent(
        request_text=payload.requestText,
        agent_id=payload.agentId,
    )


@app.post("/api/assistant/actions/prepare")
def prepare_assistant_action(
    payload: AssistantActionPrepareInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_actions.prepare_proposal(
            request_text=payload.requestText,
            action_type=payload.actionType,
            project_name=payload.projectName,
            selected_relative_paths=payload.selectedRelativePaths,
            source_agent_id=payload.sourceAgentId,
            source_response_id=payload.sourceResponseId,
            source_turn_index=payload.sourceTurnIndex,
            report_title=payload.reportTitle,
            custom_notes=payload.customNotes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/assistant/actions/policy-preview")
def preview_assistant_action_policy(
    payload: AssistantActionPolicyPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return assistant_actions.policy_preview(
        action_type=payload.actionType,
        project_name=payload.projectName,
    )


@app.post("/api/assistant/actions/validate-dry-run")
def validate_assistant_action_dry_run(
    payload: AssistantActionValidateDryRunInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_actions.validate_dry_run(
            action_type=payload.actionType,
            project_name=payload.projectName,
            selected_relative_paths=payload.selectedRelativePaths,
            proposal_id=payload.proposalId,
            source_agent_id=payload.sourceAgentId,
            source_response_id=payload.sourceResponseId,
            report_title=payload.reportTitle,
            actor=payload.actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/assistant/actions/project-files")
def list_assistant_project_files(
    projectName: str,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return project_text_reader.list_safe_files(projectName)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.post("/api/assistant/actions/execute-read-only")
def execute_assistant_action_read_only(
    payload: AssistantActionExecuteReadOnlyInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_actions.execute_read_only(
            dry_run_task_id=payload.dryRunTaskId,
            project_name=payload.projectName,
            expected_receipt_id=payload.expectedReceiptId,
            confirmation=payload.confirmation,
            source_agent_id=payload.sourceAgentId,
            source_response_id=payload.sourceResponseId,
            source_turn_index=payload.sourceTurnIndex,
            actor=payload.actor,
        )
    except (ValueError, KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.post("/api/assistant/actions/execute-project-text-read")
def execute_assistant_action_project_text_read(
    payload: AssistantActionExecuteProjectTextReadInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_actions.execute_project_text_read(
            dry_run_task_id=payload.dryRunTaskId,
            project_name=payload.projectName,
            relative_paths=payload.relativePaths,
            expected_receipt_id=payload.expectedReceiptId,
            confirmation=payload.confirmation,
            source_agent_id=payload.sourceAgentId,
            source_response_id=payload.sourceResponseId,
            source_turn_index=payload.sourceTurnIndex,
            actor=payload.actor,
        )
    except (ValueError, KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.post("/api/assistant/actions/execute-report")
def execute_assistant_action_report(
    payload: AssistantActionExecuteReportInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_actions.execute_report(
            dry_run_task_id=payload.dryRunTaskId,
            project_name=payload.projectName,
            title=payload.title,
            content=payload.content,
            expected_receipt_id=payload.expectedReceiptId,
            confirmation=payload.confirmation,
            source_agent_id=payload.sourceAgentId,
            source_response_id=payload.sourceResponseId,
            source_turn_index=payload.sourceTurnIndex,
            actor=payload.actor,
        )
    except (ValueError, KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.get("/api/assistant/actions/task/{task_id}")
def get_assistant_action_task(
    task_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    view = assistant_actions.get_task_action_view(task_id)
    if not view:
        raise HTTPException(status_code=404, detail="Task not found")
    return view


@app.get("/api/action-receipts")
def list_action_receipts(
    taskId: str | None = None,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    return runtime.list_receipts(task_id=taskId)


@app.get("/vm-validation/prep")
def get_vm_validation_prep(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return vm_validation_prep.prep()


@app.get("/vm-validation/prep/runbook")
def get_vm_validation_prep_runbook(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return vm_validation_prep.runbook()

@app.get("/backup/readiness")
def get_backup_readiness(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return backup_readiness.readiness()


@app.get("/backup/readiness/runbook")
def get_backup_readiness_runbook(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return backup_readiness.runbook()

@app.get("/activity/timeline")
def get_activity_timeline(limit: int = 25, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return activity_timeline.timeline(limit)


@app.get("/activity/timeline/{item_id}")
def get_activity_timeline_detail(item_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return activity_timeline.item_detail(item_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/dashboard/surface-health")
def get_dashboard_surface_health(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    service = DashboardSurfaceHealthService(app.routes, dashboard.summary(), dashboard_html())
    return service.surface_health()


@app.get("/dashboard/surface-health/{surface_id}")
def get_dashboard_surface_health_detail(surface_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    service = DashboardSurfaceHealthService(app.routes, dashboard.summary(), dashboard_html())
    try:
        return service.surface_detail(surface_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/projects/profiles")
def dashboard_project_profiles(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for project in projects.list_projects():
        profile = project_profiles.generate_profile(Path(project["path"]), str(project["name"]))
        data = profile.to_dict()
        summaries.append(_dashboard_profile_summary(data))
    return summaries


@app.post("/api/projects/{name}/security-review")
def run_dashboard_project_security_review(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    try:
        result = security_reviews.review_project(Path(project["path"]), project_name=name, mode="read_only")
        security_reviews.write_markdown_report(result)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _security_review_dashboard_summary(result.to_dict())


@app.get("/api/projects/{name}/security-review/latest")
def latest_dashboard_project_security_review(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    safe_project = _safe_report_project_name(name)
    reports_root = DATA_ROOT / "reports"
    if not reports_root.exists():
        return {"projectName": name, "available": False}
    candidates = sorted(
        reports_root.glob(f"security-safety-{safe_project}-*.md"),
        key=lambda path: path.stat().st_mtime if path.is_file() else 0,
        reverse=True,
    )
    for path in candidates:
        resolved = path.resolve()
        if not resolved.is_file() or not resolved.is_relative_to(reports_root.resolve()):
            continue
        stat = resolved.stat()
        return {
            "projectName": name,
            "available": True,
            "reportId": resolved.name,
            "reportPath": str(resolved),
            "sizeBytes": stat.st_size,
        }
    return {"projectName": name, "available": False}


@app.get("/api/setup/lan/status")
def lan_setup_status_endpoint(_: None = Depends(require_loopback_request)) -> dict[str, object]:
    return lan_setup_status()


@app.get("/api/setup/first-run/status")
def first_run_setup_status_endpoint(_: None = Depends(require_loopback_request)) -> dict[str, object]:
    return dashboard.first_run_wizard_summary()


@app.get("/api/safety/summary")
def safety_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.safety_summary()


@app.get("/api/settings/summary")
def settings_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.settings_summary()


@app.get("/api/tasks/active")
def active_dashboard_tasks(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return task_control.active_tasks()


@app.get("/api/tasks/stop/status")
def task_stop_status(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return task_control.stop_status()


@app.post("/api/tasks/{task_id}/stop")
def stop_dashboard_task(task_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return task_control.stop_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/reports")
def list_dashboard_reports(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return dashboard.list_reports()


@app.get("/api/reports/{report_id:path}")
def get_dashboard_report(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return dashboard.read_report(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/evidence/reports")
def list_evidence_reports(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return evidence_reports.index_reports()


@app.get("/evidence/reports/{report_id}/metadata")
def get_evidence_report_metadata(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return evidence_reports.get_report_metadata(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/evidence/reports/{report_id}")
def get_evidence_report_detail(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return evidence_reports.get_report_detail(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/agents/manifest-health")
def get_agent_manifest_health(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return agent_manifest_health.manifest_health()


@app.get("/agents/manifest-health/{manifest_id}")
def get_agent_manifest_detail(manifest_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return agent_manifest_health.manifest_detail(manifest_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/docs/index")
def get_docs_index(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return docs_center.index_docs()


@app.get("/docs/{doc_id}/metadata")
def get_doc_metadata(doc_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return docs_center.get_doc_metadata(doc_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/docs/{doc_id}")
def get_doc_detail(doc_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return docs_center.get_doc_detail(doc_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc




def _raise_knowledge_http_error(exc: Exception) -> None:
    if isinstance(exc, KnowledgeSemanticUnavailableError):
        raise HTTPException(status_code=503, detail={
            "error": "semantic_unavailable", "errorCode": exc.code,
            "requested": True, "used": False, "blocked": False,
            "blockReason": None, "requestedMode": "semantic",
            "actualMode": "unavailable", "retrievalMode": "unavailable",
            "semanticAvailable": False, "semanticUsed": False,
            "embeddingProvider": "ollama_local", "embeddingModel": None,
            "embeddingProfileId": None, "embeddingDimensions": None,
            "lexicalCandidateCount": 0, "semanticCandidateCount": 0,
            "candidateChunkCount": 0, "candidateSourceCount": 0,
            "candidateLimitReached": False, "semanticCandidateLimitReached": False,
            "selectedChunkCount": 0, "selectedSourceCount": 0,
            "retrievalId": None, "items": [], "sourceDiversity": [],
            "limitations": [f"Semantic retrieval was unavailable ({exc.code}); lexical results were not substituted."],
        }) from exc
    if isinstance(exc, KnowledgeEmbeddingError):
        provider_codes = {"provider_unavailable", "model_unavailable", "provider_timeout",
                           "provider_redirect_blocked", "invalid_provider_response",
                           "provider_response_too_large", "embedding_dimension_mismatch",
                           "embedding_input_too_large", "no_current_embeddings",
                           "embedding_write_failed"}
        conflict_codes = {"provider_disabled", "embedding_rebuild_in_progress",
                          "embedding_state_changed", "private_session_blocked"}
        status_code = 503 if exc.code in provider_codes else 409 if exc.code in conflict_codes else 422
        raise HTTPException(status_code=status_code, detail=f"knowledge embedding error: {exc.code}") from exc
    if isinstance(exc, KnowledgeRetrievalNotFoundError):
        raise HTTPException(status_code=404, detail="knowledge retrieval not found") from exc
    if isinstance(exc, KnowledgeNotFoundError):
        raise HTTPException(status_code=404, detail="knowledge source or registered project not found") from exc
    if isinstance(exc, KnowledgeConflictError):
        detail: dict[str, object] = {"message": str(exc)}
        if exc.existing_source_id:
            detail["existingSourceId"] = exc.existing_source_id
        raise HTTPException(status_code=409, detail=detail) from exc
    if isinstance(exc, KnowledgeSecretError):
        raise HTTPException(status_code=422, detail="knowledge content rejected: credential_or_secret_material") from exc
    if isinstance(exc, KnowledgeValidationError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc


@app.get("/api/knowledge/summary")
def knowledge_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    summary = knowledge_service.summary()
    summary.update(knowledge_retrieval_service.status())
    summary.update(knowledge_embedding_service.status())
    return summary


@app.get("/api/knowledge/embeddings/status")
def knowledge_embedding_status(
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return knowledge_embedding_service.status()


@app.post("/api/knowledge/embeddings/probe")
def probe_knowledge_embeddings(
    payload: KnowledgeEmbeddingProbeInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.probe(
            payload.modelName, private_session=payload.privateSession
        )
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/embeddings/configure")
def configure_knowledge_embeddings(
    payload: KnowledgeEmbeddingConfigureInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.configure(
            payload.modelName, payload.confirmation, payload.actor
        )
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/embeddings/disable")
def disable_knowledge_embeddings(
    payload: KnowledgeEmbeddingDisableInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.disable(payload.confirmation, payload.actor)
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/embeddings/clear")
def clear_knowledge_embeddings(
    payload: KnowledgeEmbeddingClearInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.clear(
            payload.scope, payload.sourceId, payload.confirmation, payload.actor
        )
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/embeddings/rebuild-preview")
def preview_knowledge_embedding_rebuild(
    payload: KnowledgeEmbeddingRebuildPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.rebuild_preview(
            source_id=payload.sourceId, include_sensitive=payload.includeSensitive,
            only_missing=payload.onlyMissing, limit=payload.limit, cursor=payload.cursor,
            private_session=payload.privateSession,
        )
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/embeddings/rebuild")
def rebuild_knowledge_embeddings(
    payload: KnowledgeEmbeddingRebuildInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_embedding_service.rebuild(
            source_id=payload.sourceId, include_sensitive=payload.includeSensitive,
            only_missing=payload.onlyMissing, limit=payload.limit, cursor=payload.cursor,
            confirmation=payload.confirmation, actor=payload.actor,
            private_session=payload.privateSession,
        )
    except KnowledgeEmbeddingError as exc:
        _raise_knowledge_http_error(exc)

@app.post("/api/knowledge/retrieval-preview")
def preview_knowledge_retrieval(
    payload: KnowledgeRetrievalPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_retrieval_service.retrieve(
            KnowledgeRetrievalRequest(
                query=payload.query,
                agent_id=payload.agentId,
                project_name=payload.projectName,
                private_session=payload.privateSession,
                include_sensitive=payload.includeSensitive,
                max_items=payload.maxItems,
                purpose="manual_preview",
                mode=payload.mode,
            )
        )
    except (KnowledgeValidationError, KnowledgeSemanticUnavailableError) as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/retrievals")
def list_knowledge_retrievals(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    agentId: str | None = None,
    projectName: str | None = None,
    purpose: str | None = None,
    retrievalMode: str | None = None,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return knowledge_retrieval_service.list_retrievals(
            limit=limit,
            offset=offset,
            agent_id=agentId,
            project_name=projectName,
            purpose=purpose,
            retrieval_mode=retrievalMode,
        )
    except KnowledgeValidationError as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/retrievals/{retrieval_id}")
def get_knowledge_retrieval(
    retrieval_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_retrieval_service.get_retrieval(retrieval_id)
    except (KnowledgeValidationError, KnowledgeRetrievalNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/sources")
def list_knowledge_sources(
    status: str | None = None,
    sourceType: str | None = None,
    scopeType: str | None = None,
    scopeValue: str | None = None,
    sensitivity: str | None = None,
    projectName: str | None = None,
    query: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return knowledge_service.list_sources(
            status=status, source_type=sourceType, scope_type=scopeType,
            scope_value=scopeValue, sensitivity=sensitivity,
            project_name=projectName, query=query, limit=limit, offset=offset,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/sources/{source_id}")
def get_knowledge_source(
    source_id: str, _: None = Depends(require_dashboard_lan_access)
) -> dict[str, object]:
    try:
        return knowledge_service.get_source(source_id)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/sources/{source_id}/chunks")
def get_knowledge_chunks(
    source_id: str, _: None = Depends(require_dashboard_lan_access)
) -> list[dict[str, object]]:
    try:
        return knowledge_service.list_chunks(source_id)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.get("/api/knowledge/sources/{source_id}/events")
def get_knowledge_events(
    source_id: str, _: None = Depends(require_dashboard_lan_access)
) -> list[dict[str, object]]:
    try:
        return knowledge_service.list_events(source_id)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/preview/paste")
def preview_pasted_knowledge(
    payload: KnowledgePastePreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.preview_paste(
            title=payload.title, content=payload.content,
            scope_type=payload.scopeType, scope_value=payload.scopeValue,
            sensitivity=payload.sensitivity, media_type=payload.mediaType,
            tags=payload.tags, private_session=payload.privateSession,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/preview/project-file")
def preview_project_file_knowledge(
    payload: KnowledgeProjectFilePreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.preview_project_file(
            project_name=payload.projectName, relative_path=payload.relativePath,
            sensitivity=payload.sensitivity, tags=payload.tags,
            private_session=payload.privateSession,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/paste")
def import_pasted_knowledge(
    payload: KnowledgePasteImportInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.import_paste(
            title=payload.title, content=payload.content,
            scope_type=payload.scopeType, scope_value=payload.scopeValue,
            sensitivity=payload.sensitivity, media_type=payload.mediaType,
            tags=payload.tags, expected_content_hash=payload.expectedContentHash,
            confirmation=payload.confirmation, private_session=payload.privateSession,
            actor=payload.actor,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/project-file")
def import_project_file_knowledge(
    payload: KnowledgeProjectFileImportInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.import_project_file(
            project_name=payload.projectName, relative_path=payload.relativePath,
            sensitivity=payload.sensitivity, tags=payload.tags,
            expected_content_hash=payload.expectedContentHash,
            expected_size_bytes=payload.expectedSizeBytes,
            expected_modified_at=payload.expectedModifiedAt,
            confirmation=payload.confirmation, private_session=payload.privateSession,
            actor=payload.actor,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.patch("/api/knowledge/sources/{source_id}")
def edit_knowledge_source(
    source_id: str, payload: KnowledgeMetadataEditInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    raw = payload.model_dump(exclude_unset=True)
    actor = raw.pop("actor", "local_user")
    field_map = {
        "title": "title", "tags": "tags", "sensitivity": "sensitivity",
        "scopeType": "scope_type", "scopeValue": "scope_value",
    }
    try:
        return knowledge_service.edit_metadata(
            source_id, {field_map[key]: value for key, value in raw.items()}, actor=actor
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/{source_id}/replace-content")
def replace_knowledge_content(
    source_id: str, payload: KnowledgeReplaceContentInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_service.replace_pasted_content(
            source_id, payload.content, actor=payload.actor
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/{source_id}/refresh-preview")
def preview_knowledge_refresh(
    source_id: str, payload: KnowledgeRefreshPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.refresh_preview(source_id)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/{source_id}/refresh")
def refresh_knowledge_source(
    source_id: str, payload: KnowledgeRefreshInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_ingestion.refresh(
            source_id, expected_content_hash=payload.expectedContentHash,
            expected_size_bytes=payload.expectedSizeBytes,
            expected_modified_at=payload.expectedModifiedAt,
            confirmation=payload.confirmation, actor=payload.actor,
        )
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/{source_id}/disable")
def disable_knowledge_source(
    source_id: str, payload: KnowledgeActorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_service.disable(source_id, actor=payload.actor)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.post("/api/knowledge/sources/{source_id}/enable")
def enable_knowledge_source(
    source_id: str, payload: KnowledgeActorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return knowledge_service.enable(source_id, actor=payload.actor)
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)


@app.delete("/api/knowledge/sources/{source_id}")
def delete_knowledge_source(
    source_id: str, _: None = Depends(require_dashboard_lan_access)
) -> dict[str, object]:
    try:
        return knowledge_service.delete(source_id, actor="local_user")
    except (KnowledgeValidationError, KnowledgeConflictError, KnowledgeNotFoundError) as exc:
        _raise_knowledge_http_error(exc)

def _raise_memory_http_error(exc: Exception) -> None:
    if isinstance(exc, MemoryNotFoundError):
        raise HTTPException(status_code=404, detail="memory not found") from exc
    if isinstance(exc, MemoryRetrievalNotFoundError):
        raise HTTPException(status_code=404, detail="memory retrieval not found") from exc
    if isinstance(exc, MemoryConflictError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, MemorySecretError):
        raise HTTPException(
            status_code=422,
            detail="memory content rejected: credential_or_secret_material",
        ) from exc
    if isinstance(exc, MemoryValidationError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc

def _raise_feedback_http_error(exc: Exception) -> None:
    if isinstance(exc, FeedbackNotFoundError):
        raise HTTPException(status_code=404, detail="feedback not found") from exc
    if isinstance(exc, FeedbackConflictError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, FeedbackValidationError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc



@app.get("/api/feedback/summary")
def feedback_summary(
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return feedback_service.summary()


@app.get("/api/feedback")
def list_feedback(
    agentId: str | None = None,
    rating: str | None = None,
    issueTag: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return feedback_service.list(
            agent_id=agentId,
            rating=rating,
            issue_tag=issueTag,
            limit=limit,
            offset=offset,
        )
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.get("/api/feedback/{feedback_id}")
def get_feedback(
    feedback_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return feedback_service.get(feedback_id)
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.get("/api/feedback/{feedback_id}/events")
def get_feedback_events(
    feedback_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return feedback_service.events(feedback_id)
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.post("/api/feedback")
def create_feedback(
    payload: FeedbackCreateInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return feedback_service.create(
            response_id=payload.responseId,
            agent_id=payload.agentId,
            rating=payload.rating,
            issue_tags=payload.issueTags,
            note=payload.note,
            private_session=payload.privateSession,
            actor=payload.actor,
        )
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.patch("/api/feedback/{feedback_id}")
def update_feedback(
    feedback_id: str,
    payload: FeedbackUpdateInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    raw = payload.model_dump(exclude_unset=True)
    actor = raw.pop("actor", "local_user")
    updates: dict[str, object] = {}
    if "rating" in raw:
        updates["rating"] = raw["rating"]
    if "issueTags" in raw:
        updates["issue_tags"] = raw["issueTags"]
    if "note" in raw:
        updates["note"] = raw["note"]
    try:
        return feedback_service.update(feedback_id, updates, actor=actor)
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.delete("/api/feedback/{feedback_id}")
def delete_feedback(
    feedback_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return feedback_service.delete(feedback_id, actor="local_user")
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)


@app.post("/api/feedback/{feedback_id}/preference-proposal")
def create_feedback_preference_proposal(
    feedback_id: str,
    payload: FeedbackPreferenceProposalInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return feedback_service.create_preference_proposal(
            feedback_id,
            content=payload.content,
            scope_type=payload.scopeType,
            project_name=payload.projectName,
            confidence=payload.confidence,
            sensitivity=payload.sensitivity,
            expires_at=payload.expiresAt,
            actor=payload.actor,
        )
    except (FeedbackValidationError, FeedbackConflictError, FeedbackNotFoundError) as exc:
        _raise_feedback_http_error(exc)
@app.get("/api/memory/summary")
def memory_summary(
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    summary = memory_service.summary()
    summary.update(memory_retrieval_service.status())
    return summary




@app.post("/api/memory/context-preview")
def preview_memory_context(
    payload: MemoryContextPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    project_name = payload.projectName.strip() if payload.projectName and payload.projectName.strip() else None
    agent_id = payload.agentId.strip() if payload.agentId and payload.agentId.strip() else None
    if agent_id and not local_response_agent_metadata(agent_id).get("found"):
        raise HTTPException(
            status_code=422,
            detail="agentId must reference an existing local response agent",
        )
    context = MemoryUseContext(
        private_session=payload.privateSession,
        project_name=project_name,
        agent_id=agent_id,
    )
    policy = memory_service.apply_private_session_policy(context)
    memories = memory_service.list_active_memories(context, limit=payload.limit)
    return {
        "context": {
            "privateSession": context.private_session,
            "projectName": context.project_name,
            "agentId": context.agent_id,
        },
        "policy": policy,
        "count": len(memories),
        "memories": memories,
        "limitations": [
            "This is a manual context preview.",
            "No response agent was invoked.",
            "No memory was injected into an agent.",
            "No relevance ranking was performed.",
            "No automatic proposal or persistence occurred.",
            "All-agent retrieval remains available only through explicit per-request controls.",
        ],
    }

@app.post("/api/memory/retrieval-preview")
def preview_memory_retrieval(
    payload: MemoryRetrievalPreviewInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_retrieval_service.retrieve(
            MemoryRetrievalRequest(
                query=payload.query,
                agent_id=payload.agentId,
                project_name=payload.projectName,
                private_session=payload.privateSession,
                include_sensitive=payload.includeSensitive,
                max_items=payload.maxItems,
                purpose="manual_preview",
            )
        )
    except MemoryValidationError as exc:
        _raise_memory_http_error(exc)


@app.get("/api/memory/retrievals")
def list_memory_retrievals(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    agentId: str | None = None,
    projectName: str | None = None,
    purpose: str | None = None,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return memory_retrieval_service.list_retrievals(
            limit=limit,
            offset=offset,
            agent_id=agentId,
            project_name=projectName,
            purpose=purpose,
        )
    except MemoryValidationError as exc:
        _raise_memory_http_error(exc)


@app.get("/api/memory/retrievals/{retrieval_id}")
def get_memory_retrieval(
    retrieval_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_retrieval_service.get_retrieval(retrieval_id)
    except (MemoryValidationError, MemoryRetrievalNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.get("/api/memories")
def list_memories(
    status: str | None = None,
    memoryType: str | None = None,
    query: str | None = None,
    scopeType: str | None = None,
    scopeValue: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    try:
        return memory_service.list_memories(
            status=status,
            memory_type=memoryType,
            query=query,
            scope_type=scopeType,
            scope_value=scopeValue,
            limit=limit,
            offset=offset,
        )
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.get("/api/memories/{memory_id}")
def get_memory(
    memory_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.get_memory(memory_id)
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)




@app.get("/api/memories/{memory_id}/events")
def get_memory_events(
    memory_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    events_for_memory = memory_service.list_memory_events(memory_id)
    if events_for_memory:
        return events_for_memory
    try:
        memory_service.get_memory(memory_id)
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="memory and event history not found") from exc
    return []

@app.post("/api/memories/proposals")
def create_memory_proposal(
    payload: MemoryProposalInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    if payload.sourceType == "feedback_proposal":
        raise HTTPException(
            status_code=422,
            detail="feedback proposals must be created from stored feedback",
        )
    try:
        return memory_service.create_proposal(
            memory_type=payload.memoryType,
            content=payload.content,
            scope_type=payload.scopeType,
            scope_value=payload.scopeValue,
            source_type=payload.sourceType,
            source_agent_id=payload.sourceAgentId,
            source_reference=payload.sourceReference,
            proposal_reason=payload.proposalReason,
            confidence=payload.confidence,
            sensitivity=payload.sensitivity,
            expires_at=payload.expiresAt,
            actor=payload.actor,
        )
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.patch("/api/memories/{memory_id}")
def edit_memory(
    memory_id: str,
    payload: MemoryEditInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    raw_updates = payload.model_dump(exclude_unset=True)
    actor = raw_updates.pop("actor", "local_user")
    updates = {
        _MEMORY_EDIT_FIELD_MAP[field]: value
        for field, value in raw_updates.items()
    }
    try:
        return memory_service.edit(memory_id, updates, actor=actor)
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.post("/api/memories/{memory_id}/approve")
def approve_memory(
    memory_id: str,
    payload: MemoryApprovalInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.approve(memory_id, approved_by=payload.approvedBy)
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.post("/api/memories/{memory_id}/reject")
def reject_memory(
    memory_id: str,
    payload: MemoryRejectionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.reject(
            memory_id,
            rejected_by=payload.rejectedBy,
            rejection_reason=payload.rejectionReason,
        )
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.post("/api/memories/{memory_id}/disable")
def disable_memory(
    memory_id: str,
    payload: MemoryActorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.disable(memory_id, actor=payload.actor)
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.post("/api/memories/{memory_id}/enable")
def enable_memory(
    memory_id: str,
    payload: MemoryActorInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.enable(memory_id, actor=payload.actor)
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)


@app.delete("/api/memories/{memory_id}")
def delete_memory(
    memory_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return memory_service.delete(memory_id, actor="local_user")
    except (MemoryValidationError, MemoryConflictError, MemoryNotFoundError) as exc:
        _raise_memory_http_error(exc)
@app.get("/projects")
def list_projects() -> list[dict[str, str]]:
    return projects.list_projects()


@app.post("/projects")
def add_project(payload: ProjectInput) -> dict[str, str]:
    try:
        return projects.add_project(payload.name, Path(payload.path))
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{name}")
def get_project(name: str) -> dict[str, str]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@app.get("/projects/{name}/profile")
def get_project_profile(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    profile = project_profiles.generate_profile(Path(project["path"]), name)
    if profile.blocked_reasons:
        raise HTTPException(status_code=400, detail="; ".join(profile.blocked_reasons))
    return profile.to_dict()


@app.post("/projects/{name}/profile/refresh")
def refresh_project_profile(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return get_project_profile(name)


@app.get("/projects/{name}/inspect")
def inspect_registered_project(name: str) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    inspection = inspect_project(Path(project["path"]))
    report_path = DATA_ROOT / "reports" / f"{name}.md"
    write_markdown_report(inspection, report_path)
    inspection["reportPath"] = str(report_path)
    return inspection


@app.post("/actions/validate")
def validate_action(payload: ActionInput) -> dict[str, str]:
    receipt = runtime.validate(
        ActionRequest(
            agent_id=payload.agentId,
            action_type=payload.actionType,
            target=payload.target,
            task_id=payload.taskId,
            tool_id=payload.toolId,
            risk_level=payload.riskLevel,
        )
    )
    return receipt.__dict__


@app.post("/tasks")
def create_task(payload: TaskInput) -> dict[str, object]:
    return tasks.create_task(
        project_name=payload.projectName,
        agent_id=payload.agentId,
        task_type=payload.taskType,
        autonomy_level=payload.autonomyLevel,
        dry_run=payload.dryRun,
        write_capable=payload.writeCapable,
        proposed_actions=[action.model_dump() for action in payload.proposedActions],
        risk_plan=payload.riskPlan,
    )


@app.get("/tasks")
def list_tasks() -> list[dict[str, object]]:
    return tasks.list_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, object]:
    task = tasks.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return tasks.cancel_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/events")
def list_events() -> list[dict[str, object]]:
    return events.list_events()


@app.get("/tasks/{task_id}/events")
def list_task_events(task_id: str) -> list[dict[str, object]]:
    return events.list_events(task_id)


@app.get("/approvals")
def list_approvals() -> list[dict[str, object]]:
    return approvals.list_approvals()


@app.get("/approvals/{approval_id}")
def get_approval(approval_id: str) -> dict[str, object]:
    approval = approvals.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="approval not found")
    return approval


@app.post("/approvals/{approval_id}/approve")
def approve_approval(approval_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return approvals.approve(approval_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/approvals/{approval_id}/reject")
def reject_approval(approval_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return approvals.reject(approval_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/diagnostics/export")
def export_diagnostics() -> dict[str, object]:
    return diagnostics.export()


@app.get("/diagnostics/bundle")
def get_redacted_diagnostics_bundle(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return redacted_diagnostics.generate_bundle()


@app.post("/diagnostics/bundle/report")
def write_redacted_diagnostics_bundle_report(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return redacted_diagnostics.write_reports()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/diagnostics/bundle/latest")
def get_latest_redacted_diagnostics_bundle(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return redacted_diagnostics.get_latest_report_metadata()


@app.post("/reports/validate")
def validate_report(payload: ReportValidationInput) -> dict[str, object]:
    missing = missing_implementation_report_sections(payload.text)
    return {"valid": not missing, "missingSections": missing}


@app.post("/security/reviews")
def create_security_review(payload: SecurityReviewInput, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project_name = payload.projectName or payload.project_name
    project_path = payload.projectPath or payload.project_path
    if project_name:
        project = projects.get_project(project_name)
        if not project:
            raise HTTPException(status_code=404, detail="project not found")
        project_path = project["path"]
    elif not project_path:
        project_name = "Jarvis"
        project_path = str(WORKSPACE_ROOT)
    try:
        result = security_reviews.review_project(Path(project_path), project_name=project_name, mode=payload.mode)
        security_reviews.write_markdown_report(result)
        return result.to_dict()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/security/reviews/{review_id:path}")
def get_security_review(review_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, str]:
    try:
        return security_reviews.read_markdown_report(review_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/validation/runbooks")
def list_validation_runbooks(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return validation_agent.list_runbooks()


@app.get("/readiness/snapshot")
def get_readiness_snapshot(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return readiness_snapshots.generate_snapshot()


@app.post("/readiness/snapshot/report")
def write_readiness_snapshot_report(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return readiness_snapshots.write_markdown_report()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/readiness/snapshot/latest")
def get_latest_readiness_snapshot(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return readiness_snapshots.get_latest_snapshot_metadata()


@app.get("/validation/runbooks/{runbook_id}")
def get_validation_runbook(runbook_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.get_runbook(runbook_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs")
def create_validation_run(payload: ValidationRunInput, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    runbook_id = payload.runbookId or payload.runbook_id
    if not runbook_id:
        raise HTTPException(status_code=400, detail="runbookId is required")
    try:
        return validation_agent.create_run(runbook_id, payload.targetEnvironment or payload.target_environment)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/validation/runs")
def list_validation_runs(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return validation_agent.list_runs()


@app.get("/validation/runs/{run_id}")
def get_validation_run(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.get_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/steps/{step_id}")
def update_validation_step_result(
    run_id: str,
    step_id: str,
    payload: ValidationStepResultInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return validation_agent.update_step_result(run_id, step_id, payload.status, payload.notes, payload.evidence)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/complete")
def complete_validation_run(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.complete_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/report")
def write_validation_report(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, str]:
    try:
        return validation_agent.write_markdown_report(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _dashboard_profile_summary(profile: dict[str, object]) -> dict[str, object]:
    public_docs = profile.get("publicReadinessDocsPresent", {})
    security_docs = profile.get("securityDocsPresent", {})
    boundary = profile.get("boundary", {})
    boundary_dict = boundary if isinstance(boundary, dict) else {}
    return {
        "projectName": profile.get("projectName"),
        "projectType": profile.get("projectType"),
        "detectedLanguages": profile.get("detectedLanguages", []),
        "detectedFrameworks": profile.get("detectedFrameworks", []),
        "packageManager": profile.get("packageManager"),
        "preferredCheckOrder": profile.get("preferredCheckOrder", []),
        "gitClean": profile.get("gitClean"),
        "docsPresence": {
            "publicReadiness": public_docs,
            "security": security_docs,
        },
        "futureConnectorsPlaceholderOnly": profile.get("futureConnectorsPlaceholderOnly"),
        "recommendedMode": profile.get("recommendedMode"),
        "warningCount": len(profile.get("warnings", []) if isinstance(profile.get("warnings"), list) else []),
        "blockedReasonCount": len(profile.get("blockedReasons", []) if isinstance(profile.get("blockedReasons"), list) else []),
        "boundaryStatus": {
            "rootValidated": profile.get("rootValidated"),
            "protectedPatternsActive": bool(profile.get("protectedPatterns")),
            "runtimeSkipDirsActive": bool(profile.get("runtimeSkipDirs")),
            "blockedReasonCount": len(profile.get("blockedReasons", []) if isinstance(profile.get("blockedReasons"), list) else []),
            "warningCount": len(profile.get("warnings", []) if isinstance(profile.get("warnings"), list) else []),
            "rootStatus": (boundary_dict.get("root") or {}).get("status") if isinstance(boundary_dict.get("root"), dict) else None,
        },
    }


def _security_review_dashboard_summary(review: dict[str, object]) -> dict[str, object]:
    findings = review.get("findings", [])
    findings_list = findings if isinstance(findings, list) else []
    by_severity = {"high": 0, "medium": 0, "low": 0}
    for finding in findings_list:
        if isinstance(finding, dict):
            severity = str(finding.get("severity", "low"))
            by_severity[severity] = by_severity.get(severity, 0) + 1
    metadata = review.get("metadata", {})
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    return {
        "projectName": metadata_dict.get("projectName"),
        "agentId": metadata_dict.get("agentId"),
        "reviewMode": metadata_dict.get("reviewMode"),
        "verdict": review.get("verdict"),
        "findingCount": len(findings_list),
        "findingsBySeverity": by_severity,
        "reportId": review.get("reportId"),
        "reportPath": review.get("reportPath"),
    }


def _safe_report_project_name(project_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", project_name.strip()).strip("-") or "project"


@app.post("/codex/plans")
def create_codex_plan(
    payload: CodexPlanRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return codex_plans.create_plan(
        CodexPlanInput(
            task_id=payload.taskId,
            project_name=payload.projectName,
            agent_id=payload.agentId,
            tool_id=payload.toolId,
            action_type=payload.actionType,
            task_goal=payload.taskGoal,
            exact_scope=payload.exactScope,
            non_goals=payload.nonGoals,
            allowed_files=payload.allowedFiles,
            test_commands=payload.testCommands,
            risk_plan=payload.riskPlan,
            sandbox_mode=payload.sandboxMode,
            prompt_path=payload.promptPath,
            output_path=payload.outputPath,
            conservative=payload.conservative,
            execution_mode=payload.executionMode,
        )
    )


@app.get("/codex/plans")
def list_codex_plans(
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    return codex_plans.list_plans()


@app.get("/codex/plans/{plan_id}")
def get_codex_plan(
    plan_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    plan = codex_plans.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="codex plan not found")
    return plan


@app.post("/codex/plans/{plan_id}/cancel")
def cancel_codex_plan(
    plan_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return codex_plans.cancel_plan(plan_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/approve-for-future-execution")
def approve_codex_plan_for_future_execution(
    plan_id: str,
    payload: ApprovalResolutionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return codex_plans.approve_for_future_execution(plan_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/reject")
def reject_codex_plan(
    plan_id: str,
    payload: ApprovalResolutionInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return codex_plans.reject_plan(plan_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/execute")
def execute_codex_plan(
    plan_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return codex_execution.execute_plan(plan_id)


@app.get("/api/codex/execution/active")
@app.get("/codex/execution/active")
def get_active_codex_execution(
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    active = codex_execution.execution_tracker.get_active()
    return {
        "active": active is not None,
        "execution": active,
    }


@app.post("/api/codex/execution/cancel")
@app.post("/codex/execution/cancel")
def cancel_active_codex_execution(
    payload: CodexExecutionCancelInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    success, message, info = codex_execution.execution_tracker.cancel_active(
        confirmation=payload.confirmation,
        expected_execution_id=payload.expectedExecutionId,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "success": True,
        "message": message,
        "execution": info,
    }


# ==========================================
# Assistant Controlled Coding Endpoints
# ==========================================


@app.get("/api/assistant/coding/capabilities")
def get_assistant_coding_capabilities(
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return assistant_coding.get_coding_capabilities()


@app.post("/api/assistant/coding/prepare")
def prepare_assistant_coding_plan(
    payload: AssistantCodingPrepareRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.prepare_coding_plan(
            AssistantCodingPrepareInput(
                project_name=payload.projectName,
                allowed_files=payload.allowedFiles,
                task_goal=payload.taskGoal,
                exact_scope=payload.exactScope,
                non_goals=payload.nonGoals,
                source_response_id=payload.sourceResponseId,
                source_turn_index=payload.sourceTurnIndex,
                actor=payload.actor,
            )
        )
    except (ValueError, FileNotFoundError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to prepare conservative coding plan.")


@app.post("/api/assistant/coding/approve")
def approve_assistant_coding_plan(
    payload: AssistantCodingApproveRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.approve_coding_plan(
            plan_id=payload.planId,
            confirmation=payload.confirmation,
            actor=payload.actor,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to approve conservative coding plan.")


@app.post("/api/assistant/coding/reject")
def reject_assistant_coding_plan(
    payload: AssistantCodingRejectRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.reject_coding_plan(
            plan_id=payload.planId,
            actor=payload.actor,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to reject conservative coding plan.")


@app.post("/api/assistant/coding/execute")
def execute_assistant_coding_plan(
    payload: AssistantCodingExecuteRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.execute_coding_plan(
            plan_id=payload.planId,
            project_name=payload.projectName,
            confirmation=payload.confirmation,
            actor=payload.actor,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to execute conservative coding plan.")


@app.get("/api/assistant/coding/plan/{plan_id}")
def get_assistant_coding_plan(
    plan_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.get_plan_summary(plan_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/assistant/coding/execution/{execution_id}")
def get_assistant_coding_execution(
    execution_id: str,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return assistant_coding.get_execution_summary(execution_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ==========================================
# Assistant Productivity Layer Endpoints
# ==========================================


@app.get("/api/assistant/productivity/agents")
def get_productivity_agents(
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    return get_command_center_agents()


@app.get("/api/assistant/productivity/playbooks")
def get_productivity_playbooks(
    _: None = Depends(require_dashboard_lan_access),
) -> list[dict[str, object]]:
    return get_builtin_playbooks()


@app.post("/api/assistant/productivity/readiness")
def evaluate_productivity_readiness(
    payload: AssistantReadinessRequest,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    return evaluate_request_readiness(
        text=payload.text,
        selected_agent_id=payload.selectedAgentId,
        context_kit_chars=payload.contextKitChars,
        has_reviewed_sources=payload.hasReviewedSources,
        source_count=payload.sourceCount,
        selected_project=payload.selectedProject,
    )
