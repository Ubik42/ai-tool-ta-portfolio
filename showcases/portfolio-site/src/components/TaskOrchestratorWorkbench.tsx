import { useMemo, useState } from "react";
import {
  Activity,
  Archive,
  Cable,
  ClipboardCheck,
  Download,
  GitCompare,
  GitBranch,
  KeyRound,
  ListChecks,
  Network,
  PackageCheck,
  RotateCcw,
  Rocket,
  ShieldAlert,
  ShieldCheck,
  Waypoints,
} from "lucide-react";
import {
  dependencyImpactScenarioOptions,
  defaultDependencyImpactScenarioId,
  getDefaultTaskOrchestratorReport,
  filterDiscoveredTools,
  type TaskChecklistStatus,
  type TaskDiscoveryDiagnosticSeverity,
  type TaskExecutionEventKind,
  type TaskExecutionEventStatus,
  type TaskImpactAssetKind,
  type TaskImpactPublishAction,
  type TaskImpactReceiptState,
  type TaskLifecycleStatus,
  type TaskOrchestratorGate,
  type TaskPlatformReceiptState,
  type TaskReviewerAcceptanceState,
  type TaskToolAvailability,
  type TaskToolDiscoveryFilters,
} from "../data/taskOrchestrator";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

const taskGateLabels: Record<TaskOrchestratorGate, string> = {
  Ready: "Ready",
  Review: "Review",
  Blocked: "Blocked",
};

const compactIdentifier = (value: string, lead = 42, tail = 18) => {
  if (value.length <= lead + tail + 3) {
    return value;
  }
  return `${value.slice(0, lead)}...${value.slice(-tail)}`;
};

const compactEvidenceRefs = (refs: string[], visible = 3) => {
  const shownRefs = refs.slice(0, visible).map((ref) => compactIdentifier(ref, 36, 14));
  const hiddenCount = refs.length - shownRefs.length;
  return `${shownRefs.join(" / ")}${hiddenCount > 0 ? ` / +${hiddenCount} refs` : ""}`;
};

const lifecycleStatusLabels: Record<TaskLifecycleStatus, string> = {
  done: "Done",
  active: "Active",
  queued: "Queued",
  blocked: "Blocked",
};

const checklistStatusLabels: Record<TaskChecklistStatus, string> = {
  pass: "Pass",
  review: "Review",
  block: "Block",
};

const eventKindLabels: Record<TaskExecutionEventKind, string> = {
  start: "Start",
  finish: "Finish",
  review_gate: "Review",
  retry: "Retry",
  skip: "Skip",
};

const eventStatusLabels: Record<TaskExecutionEventStatus, string> = {
  done: "Done",
  running: "Running",
  review: "Review",
  blocked: "Blocked",
  queued: "Queued",
};

const availabilityLabels: Record<TaskToolAvailability, string> = {
  available: "Available",
  review_only: "Review Only",
  version_mismatch: "Version Mismatch",
  missing: "Missing",
};

const diagnosticSeverityLabels: Record<TaskDiscoveryDiagnosticSeverity, string> = {
  info: "Info",
  review: "Review",
  block: "Block",
};

const acceptanceStateLabels: Record<TaskReviewerAcceptanceState, string> = {
  accepted: "Accepted",
  pending: "Pending",
  rejected: "Rejected",
  deferred: "Deferred",
};

const receiptStateLabels: Record<TaskPlatformReceiptState, string> = {
  issued: "Issued",
  held_for_review: "Held",
  blocked: "Blocked",
};

const impactAssetKindLabels: Record<TaskImpactAssetKind, string> = {
  source_mesh: "Source Mesh",
  material: "Material",
  texture_set: "Texture Set",
  validation_rule: "Validation Rule",
  engine_package: "Engine Package",
};

const impactActionLabels: Record<TaskImpactPublishAction, string> = {
  safe_publish: "Safe Publish",
  hold: "Hold",
  rerun_check: "Rerun Check",
  rollback_candidate: "Rollback Candidate",
};

const impactReceiptStateLabels: Record<TaskImpactReceiptState, string> = {
  accepted: "Accepted",
  pending: "Pending",
  waiting_dependency: "Waiting Dependency",
};

const replayStepStatusLabels = {
  pass: "Pass",
  review: "Review",
  skipped: "Skipped",
} as const;

const regressionSignalLabels = {
  improved: "Improved",
  stable: "Stable",
  regressed: "Regressed",
  review: "Review",
} as const;

const contractAssertionStatusLabels = {
  pass: "Pass",
  review: "Review",
  fail: "Fail",
} as const;

const syncActionLabels = {
  create_draft: "Create Draft",
  hold_for_review: "Hold",
  skip_blocked: "Skip Blocked",
} as const;

const recoverySeverityLabels = {
  review: "Review",
  blocked: "Blocked",
} as const;

const handoffDiffStatusLabels = {
  unchanged: "Unchanged",
  changed: "Changed",
  added: "Added",
  held: "Held",
} as const;

const approvalCheckStatusLabels = {
  pass: "Pass",
  review: "Review",
  block: "Block",
} as const;

const retryEntryStateLabels = {
  retry_ready: "Retry Ready",
  waiting_owner: "Waiting Owner",
  blocked: "Blocked",
} as const;

const sandboxReceiptStateLabels = {
  signed: "Signed",
  held: "Held",
  rejected: "Rejected",
} as const;

const smokeCheckStatusLabels = {
  pass: "Pass",
  review: "Review",
  fail: "Fail",
} as const;

const rollbackReceiptStateLabels = {
  verified: "Verified",
  waiting_owner: "Waiting Owner",
  blocked: "Blocked",
} as const;

const credentialProbeStatusLabels = {
  pass: "Pass",
  review: "Review",
  fail: "Fail",
} as const;

const credentialStateLabels = {
  absent_public: "Absent Public",
  scoped_placeholder: "Scoped Alias",
  owner_required: "Owner Required",
  blocked_secret: "Blocked Secret",
} as const;

const retentionStateLabels = {
  retained: "Retained",
  review: "Review",
  purge_required: "Purge",
} as const;

const releaseLaneStateLabels = {
  ready: "Ready",
  review: "Review",
  blocked: "Blocked",
} as const;

const failureInjectionStateLabels = {
  contained: "Contained",
  owner_review: "Owner Review",
  blocked: "Blocked",
} as const;

const lineageStateLabels = {
  linked: "Linked",
  review: "Review",
  orphaned: "Orphaned",
} as const;

const packetDiffStatusLabels = {
  added: "Added",
  changed: "Changed",
  unchanged: "Unchanged",
  review: "Review",
} as const;

const liveReadinessStateLabels = {
  ready: "Ready",
  owner_review: "Owner Review",
  blocked: "Blocked",
} as const;

const approvalCloseoutStateLabels = {
  closed: "Closed",
  requested: "Requested",
  blocked: "Blocked",
} as const;

const mutationReplayStateLabels = {
  rehearsed: "Rehearsed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const cutoverChecklistStateLabels = {
  ready: "Ready",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const postCutoverReceiptStateLabels = {
  healthy: "Healthy",
  watch: "Watch",
  blocked: "Blocked",
} as const;

const emergencyStopStateLabels = {
  verified: "Verified",
  armed: "Armed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const privateReceiptBridgeStateLabels = {
  mapped: "Mapped",
  redacted: "Redacted",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const cutoverSignoffDiffStateLabels = {
  accepted: "Accepted",
  changed: "Changed",
  requested: "Requested",
  blocked: "Blocked",
} as const;

const shadowReplayStateLabels = {
  shadow_pass: "Shadow Pass",
  watch: "Watch",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const productionDriftAuditStateLabels = {
  in_sync: "In Sync",
  drift: "Drift",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerSlaMonitorStateLabels = {
  within_sla: "Within SLA",
  due_soon: "Due Soon",
  overdue: "Overdue",
  blocked: "Blocked",
} as const;

const releaseFreezeReplayStateLabels = {
  frozen: "Frozen",
  dry_run: "Dry Run",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const rollbackAdjudicatorStateLabels = {
  approved: "Approved",
  disputed: "Disputed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const receiptDisputeReplayStateLabels = {
  resolved: "Resolved",
  counterclaim: "Counterclaim",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const auditExportDiffStateLabels = {
  unchanged: "Unchanged",
  added: "Added",
  changed: "Changed",
  blocked: "Blocked",
} as const;

const rolloutWavePlannerStateLabels = {
  ready: "Ready",
  watch: "Watch",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const incidentReplayNotebookStateLabels = {
  replayed: "Replayed",
  open_question: "Open Question",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerExceptionLedgerStateLabels = {
  accepted: "Accepted",
  requested: "Requested",
  expired: "Expired",
  blocked: "Blocked",
} as const;

const rollbackBudgetSimulatorStateLabels = {
  within_budget: "Within Budget",
  near_limit: "Near Limit",
  over_budget: "Over Budget",
  blocked: "Blocked",
} as const;

const releaseConfidenceHeatmapStateLabels = {
  high: "High",
  medium: "Medium",
  low: "Low",
  blocked: "Blocked",
} as const;

const evidenceAgingPolicyStateLabels = {
  fresh: "Fresh",
  due_soon: "Due Soon",
  expired: "Expired",
  blocked: "Blocked",
} as const;

const releaseRollbackRehearsalStateLabels = {
  passed: "Passed",
  watch: "Watch",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerQuorumSimulatorStateLabels = {
  accepted: "Accepted",
  requested: "Requested",
  missing: "Missing",
  blocked: "Blocked",
} as const;

const staleEvidenceAutoRefreshQueueStateLabels = {
  refreshed: "Refreshed",
  queued: "Queued",
  owner_required: "Owner Required",
  blocked: "Blocked",
} as const;

const releaseDecisionBoardStateLabels = {
  approved: "Approved",
  conditional: "Conditional",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const ownerSlaEscalationQueueStateLabels = {
  within_sla: "Within SLA",
  due_today: "Due Today",
  escalated: "Escalated",
  blocked: "Blocked",
} as const;

const evidenceRetentionPurgeRehearsalStateLabels = {
  retained: "Retained",
  purge_queued: "Purge Queued",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseEvidenceCompactorStateLabels = {
  compacted: "Compacted",
  kept: "Kept",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const reviewerPacketLockfileStateLabels = {
  locked: "Locked",
  changed: "Changed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const productionReadinessExceptionCloseoutStateLabels = {
  closed: "Closed",
  needs_owner: "Needs Owner",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const lockedPacketDiffViewerStateLabels = {
  unchanged: "Unchanged",
  changed: "Changed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const exceptionBurnDownDashboardStateLabels = {
  closed: "Closed",
  needs_owner: "Needs Owner",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const reviewerAcceptanceReplayStateLabels = {
  accepted: "Accepted",
  replay_required: "Replay Required",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const acceptedPacketFreezeStateLabels = {
  frozen: "Frozen",
  pending_diff: "Pending Diff",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const exceptionOwnerResponseImporterStateLabels = {
  imported: "Imported",
  waiting_owner: "Waiting Owner",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const releaseReadinessReplayDiffStateLabels = {
  unchanged_ready: "Ready",
  changed_review: "Changed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const frozenPacketPromotionGateStateLabels = {
  promoted: "Promoted",
  blocked_by_diff: "Diff Blocked",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerResponseSlaReconciliationStateLabels = {
  reconciled: "Reconciled",
  due_today: "Due Today",
  overdue: "Overdue",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const readinessAcceptanceLedgerStateLabels = {
  accepted: "Accepted",
  needs_review: "Needs Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const promotionRollbackPreviewStateLabels = {
  preview_ready: "Preview Ready",
  diff_blocked: "Diff Blocked",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const slaExceptionWaiverLedgerStateLabels = {
  waiver_not_needed: "No Waiver",
  waiver_requested: "Waiver Requested",
  waiver_deferred: "Deferred",
  blocked: "Blocked",
} as const;

const candidatePacketReleaseNoteStateLabels = {
  included: "Included",
  needs_review: "Needs Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseNoteReviewerApprovalLoopStateLabels = {
  approved: "Approved",
  changes_requested: "Changes",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const waiverExpiryMonitorStateLabels = {
  clear: "Clear",
  expires_soon: "Expires Soon",
  expired: "Expired",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const rollbackRehearsalBundleDiffStateLabels = {
  bundle_matched: "Matched",
  review_diff: "Review Diff",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const approvalEvidenceSealStateLabels = {
  sealed: "Sealed",
  changes_open: "Changes Open",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const waiverRenewalSimulatorStateLabels = {
  renewal_not_needed: "No Renewal",
  renewal_requested: "Requested",
  renewal_deferred: "Deferred",
  blocked: "Blocked",
} as const;

const rollbackDrillIncidentHandoffStateLabels = {
  handoff_closed: "Closed",
  incident_open: "Incident Open",
  owner_handoff: "Owner Handoff",
  blocked: "Blocked",
} as const;

const sealedApprovalReplayStateLabels = {
  replayed: "Replayed",
  replay_required: "Replay Required",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const waiverExpiryBurnDownStateLabels = {
  burned_down: "Burned Down",
  renewal_open: "Renewal Open",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const incidentClosureAcceptancePacketStateLabels = {
  accepted: "Accepted",
  acceptance_open: "Acceptance Open",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const closureAcceptanceReplayStateLabels = {
  replayed: "Replayed",
  acceptance_required: "Acceptance Required",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const waiverOwnerResponseImporterStateLabels = {
  imported: "Imported",
  waiting_owner: "Waiting Owner",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const incidentSlaScoreboardStateLabels = {
  within_sla: "Within SLA",
  due_today: "Due Today",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const incidentClosureDiffViewerStateLabels = {
  matched: "Matched",
  changed_review: "Changed Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const waiverSlaReconciliationStateLabels = {
  reconciled: "Reconciled",
  due_today: "Due Today",
  deferred: "Deferred",
  blocked: "Blocked",
} as const;

const releaseOperationsAcceptanceLedgerStateLabels = {
  accepted: "Accepted",
  ops_review: "Ops Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const operationsPacketSignoffDiffStateLabels = {
  signed_off: "Signed Off",
  diff_review: "Diff Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseTrainReadinessBoardStateLabels = {
  train_ready: "Train Ready",
  train_review: "Train Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerEscalationCloseoutStateLabels = {
  closed: "Closed",
  escalated: "Escalated",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseTrainReplayReceiptStateLabels = {
  replayed: "Replayed",
  variance_review: "Variance",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerCloseoutAgingAuditStateLabels = {
  fresh: "Fresh",
  aging_review: "Aging",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const publishRehearsalVarianceReportStateLabels = {
  variance_clear: "Clear",
  variance_review: "Variance",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseManagerDailyDigestStateLabels = {
  ready_digest: "Ready Digest",
  attention: "Attention",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const lateOwnerRiskForecastStateLabels = {
  low_risk: "Low Risk",
  rising_risk: "Rising",
  late_owner: "Late Owner",
  blocked: "Blocked",
} as const;

const packageAcceptanceFreezeDiffStateLabels = {
  freeze_matched: "Matched",
  freeze_changed: "Changed",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseAcceptanceWaiverSummaryStateLabels = {
  waiver_not_needed: "No Waiver",
  waiver_review: "Waiver Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const freezeExceptionClosureBoardStateLabels = {
  closure_ready: "Closure Ready",
  closure_review: "Closure Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const publishGoNoGoPacketStateLabels = {
  go: "Go",
  conditional_go: "Conditional",
  no_go_owner_hold: "No-Go Owner",
  blocked: "Blocked",
} as const;

const publishDecisionReceiptReplayStateLabels = {
  receipt_replayed: "Replayed",
  replay_review: "Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const postReleaseWatchWindowBoardStateLabels = {
  watch_clear: "Watch Clear",
  watch_review: "Watch Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const rollbackReadinessDeltaStateLabels = {
  rollback_ready: "Rollback Ready",
  rollback_review: "Rollback Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseCloseoutReceiptSealStateLabels = {
  receipt_sealed: "Sealed",
  seal_review: "Seal Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const watchEscalationReplayStateLabels = {
  escalation_replayed: "Replayed",
  escalation_review: "Escalation Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const rollbackDrillCloseoutPacketStateLabels = {
  closeout_ready: "Closeout Ready",
  closeout_review: "Closeout Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const closeoutAcceptanceReplayStateLabels = {
  acceptance_replayed: "Replayed",
  acceptance_review: "Acceptance Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const escalationAgingBoardStateLabels = {
  aging_clear: "Aging Clear",
  aging_review: "Aging Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const finalReleaseArchivePacketStateLabels = {
  archive_ready: "Archive Ready",
  archive_review: "Archive Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveIntegrityAuditStateLabels = {
  integrity_passed: "Integrity Passed",
  integrity_review: "Integrity Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseMemorySearchStateLabels = {
  memory_found: "Memory Found",
  memory_review: "Memory Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archivedPacketRestoreRehearsalStateLabels = {
  restore_ready: "Restore Ready",
  restore_review: "Restore Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveRetentionPolicySimulatorStateLabels = {
  retention_kept: "Retention Kept",
  retention_review: "Retention Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseMemoryDiffTimelineStateLabels = {
  timeline_stable: "Timeline Stable",
  timeline_review: "Timeline Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreApprovalPacketStateLabels = {
  approval_ready: "Approval Ready",
  approval_review: "Approval Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveAccessReviewLedgerStateLabels = {
  access_granted: "Access Granted",
  access_review: "Access Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreIncidentDrillbookStateLabels = {
  drill_ready: "Drill Ready",
  drill_review: "Drill Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseMemoryOwnershipTransferStateLabels = {
  transfer_ready: "Transfer Ready",
  transfer_review: "Transfer Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreReadinessReplayAuditStateLabels = {
  replay_ready: "Replay Ready",
  replay_review: "Replay Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archivePermissionExpiryMonitorStateLabels = {
  permission_valid: "Permission Valid",
  permission_expiring: "Permission Expiring",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseMemoryAuditExportBundleStateLabels = {
  bundle_ready: "Bundle Ready",
  bundle_review: "Bundle Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const auditBundleReviewerSignoffQueueStateLabels = {
  signoff_ready: "Signoff Ready",
  signoff_review: "Signoff Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const permissionRenewalReplaySimulatorStateLabels = {
  renewal_replayed: "Renewal Replayed",
  renewal_review: "Renewal Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreMemoryEvidenceNotarizationStateLabels = {
  notarized: "Notarized",
  notary_review: "Notary Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const releaseMemoryQueryReplayStateLabels = {
  query_replayed: "Query Replayed",
  query_review: "Query Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreApprovalComparisonStateLabels = {
  approval_matched: "Approval Matched",
  approval_review: "Approval Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const auditPacketRetentionRenewalDashboardStateLabels = {
  retention_renewed: "Retention Renewed",
  retention_review: "Retention Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const auditQueryExceptionLedgerStateLabels = {
  exception_closed: "Exception Closed",
  exception_review: "Exception Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const retentionOwnerResponseImporterStateLabels = {
  response_imported: "Response Imported",
  response_review: "Response Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreMemoryPacketHandoffStateLabels = {
  handoff_ready: "Handoff Ready",
  handoff_review: "Handoff Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restorePacketAcceptanceReplayStateLabels = {
  acceptance_replayed: "Acceptance Replayed",
  acceptance_review: "Acceptance Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const handoffOwnerSlaBoardStateLabels = {
  sla_clear: "SLA Clear",
  sla_watch: "SLA Watch",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveRestorationDrillExporterStateLabels = {
  drill_exported: "Drill Exported",
  drill_review: "Drill Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restorationDrillAcceptanceLedgerStateLabels = {
  drill_accepted: "Drill Accepted",
  acceptance_review: "Acceptance Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveDrillOwnerResponseImporterStateLabels = {
  response_imported: "Response Imported",
  response_review: "Response Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreOperationsReadinessDigestStateLabels = {
  digest_ready: "Digest Ready",
  digest_review: "Digest Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreReadinessExceptionCloseoutStateLabels = {
  exception_closed: "Exception Closed",
  closeout_review: "Closeout Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveOpsSlaEscalationQueueStateLabels = {
  escalation_ready: "Escalation Ready",
  escalation_review: "Escalation Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreCommandRehearsalLockStateLabels = {
  command_locked: "Command Locked",
  lock_review: "Lock Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreLockReviewerSignoffQueueStateLabels = {
  signoff_ready: "Signoff Ready",
  signoff_review: "Signoff Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveCommandRollbackRehearseDiffStateLabels = {
  rollback_matched: "Rollback Matched",
  rollback_review: "Rollback Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreExecutionRedlinePacketStateLabels = {
  redline_ready: "Redline Ready",
  redline_review: "Redline Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreRedlineOwnerOverrideSimulatorStateLabels = {
  override_simulated: "Override Simulated",
  override_review: "Override Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveExecutionBlackboxRecorderStateLabels = {
  blackbox_recorded: "Blackbox Recorded",
  record_review: "Record Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreAbortDrillCloseoutLedgerStateLabels = {
  abort_closed: "Abort Closed",
  abort_review: "Abort Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreIncidentReplayNotarizationStateLabels = {
  replay_notarized: "Replay Notarized",
  replay_review: "Replay Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveRestoreExecutionVarianceReportStateLabels = {
  variance_clear: "Variance Clear",
  variance_review: "Variance Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const postAbortOwnerEvidenceReconciliationStateLabels = {
  evidence_reconciled: "Evidence Reconciled",
  evidence_review: "Evidence Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const restoreAcceptanceFinalAttestationStateLabels = {
  attestation_ready: "Attestation Ready",
  attestation_review: "Attestation Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveIncidentDeltaAgingBoardStateLabels = {
  delta_current: "Delta Current",
  delta_aging: "Delta Aging",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const postRestoreOwnerSignoffPacketStateLabels = {
  signoff_packet_ready: "Packet Ready",
  signoff_packet_review: "Packet Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const signoffDisputeReplayStateLabels = {
  dispute_replayed: "Dispute Replayed",
  dispute_review: "Dispute Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveAcceptanceFreezeDiffStateLabels = {
  freeze_matched: "Freeze Matched",
  freeze_review: "Freeze Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerClosureExceptionLedgerStateLabels = {
  exception_closed: "Exception Closed",
  exception_review: "Exception Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const closureEvidenceSealStateLabels = {
  seal_ready: "Seal Ready",
  seal_review: "Seal Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const archiveTerminalPackageDiffStateLabels = {
  terminal_matched: "Terminal Matched",
  terminal_review: "Terminal Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerReopenGuardrailSimulatorStateLabels = {
  guardrail_passed: "Guardrail Passed",
  guardrail_review: "Guardrail Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const sealedClosureReceiptReplayStateLabels = {
  receipt_replayed: "Receipt Replayed",
  receipt_review: "Receipt Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const terminalArchiveRetentionRenewalStateLabels = {
  retention_renewed: "Retention Renewed",
  retention_review: "Retention Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const ownerReopenIncidentDrillbookStateLabels = {
  drillbook_ready: "Drillbook Ready",
  drillbook_review: "Drillbook Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const receiptReplayAgingLockStateLabels = {
  aging_locked: "Aging Locked",
  aging_review: "Aging Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const retentionExceptionBurnDownStateLabels = {
  exception_burned_down: "Exception Burned Down",
  exception_review: "Exception Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

const drillbookAcceptanceLedgerStateLabels = {
  drillbook_accepted: "Drillbook Accepted",
  acceptance_review: "Acceptance Review",
  owner_hold: "Owner Hold",
  blocked: "Blocked",
} as const;

type TaskDccActionId = "fixture" | "discover" | "queue" | "dryRun" | "export";

interface TaskDccAction {
  id: TaskDccActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface TaskDccAssetRow {
  id: string;
  node: string;
  gate: string;
  role: string;
  lod: string;
  materials: number;
  textures: number;
  triangles: number;
  issues: string;
}

interface TaskDccQueueRow {
  id: string;
  asset: string;
  label: string;
  phase: string;
  status: string;
  evidence: string;
}

interface TaskDccReceiptRow {
  id: string;
  asset: string;
  gate: string;
  state: string;
  nextAction: string;
}

interface TaskDccRun {
  action: TaskDccActionId;
  label: string;
  raw: unknown;
  assetCount: number;
  taskCount: number;
  doneCount: number;
  reviewCount: number;
  blockedCount: number;
  gate: string;
  path?: string;
  assets: TaskDccAssetRow[];
  tasks: TaskDccQueueRow[];
  receipts: TaskDccReceiptRow[];
  updatedAt: string;
}

const taskDccActions: TaskDccAction[] = [
  { id: "fixture", label: "Create Fixture", method: "task_orchestrator_create_fixture" },
  { id: "discover", label: "Discover Scene", method: "task_orchestrator_discover_scene" },
  { id: "queue", label: "Build Queue", method: "task_orchestrator_build_queue" },
  { id: "dryRun", label: "Dry Run", method: "task_orchestrator_run_dry_run" },
  { id: "export", label: "Export Report", method: "task_orchestrator_export_report" },
];

export function TaskOrchestratorWorkbench() {
  const [selectedImpactScenarioId, setSelectedImpactScenarioId] = useState(defaultDependencyImpactScenarioId);
  const report = useMemo(
    () => getDefaultTaskOrchestratorReport(selectedImpactScenarioId),
    [selectedImpactScenarioId],
  );
  const [selectedTraceId, setSelectedTraceId] = useState(report.moduleTraces[0].id);
  const [discoveryFilters, setDiscoveryFilters] = useState<TaskToolDiscoveryFilters>(report.toolDiscovery.defaultFilters);
  const [selectedImpactReceiptId, setSelectedImpactReceiptId] = useState("");
  const [simulatedClosedReceiptIds, setSimulatedClosedReceiptIds] = useState<string[]>([]);
  const [dccSnapshot, setDccSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [dccBusyAction, setDccBusyAction] = useState<TaskDccActionId | null>(null);
  const [dccRun, setDccRun] = useState<TaskDccRun | null>(null);
  const [dccError, setDccError] = useState<string | null>(null);
  const selectedTrace = report.moduleTraces.find((trace) => trace.id === selectedTraceId) ?? report.moduleTraces[0];
  const currentEvent =
    report.executionEvents.find((event) => event.id === report.executionSummary.currentEventId) ?? report.executionEvents[0];
  const impact = report.assetDependencyImpact;
  const maxRegressionScore = Math.max(...impact.regressionScoreTrend.points.map((point) => point.regressionScore));
  const pendingImpactReceipts = impact.ownerReceipts.filter((receipt) => receipt.state !== "accepted");
  const pendingImpactReceiptIds = pendingImpactReceipts.map((receipt) => receipt.id);
  const activeSimulatedClosedReceiptIds = simulatedClosedReceiptIds.filter((receiptId) =>
    pendingImpactReceiptIds.includes(receiptId),
  );
  const simulatedClosedSet = new Set(activeSimulatedClosedReceiptIds);
  const simulatedOpenReceipts = pendingImpactReceipts.filter((receipt) => !simulatedClosedSet.has(receipt.id));
  const simulatedOpenReceiptIds = new Set(simulatedOpenReceipts.map((receipt) => receipt.id));
  const simulatedHeldTargets = impact.publishDecisions.filter(
    (decision) =>
      (decision.action === "hold" || decision.action === "rollback_candidate") &&
      decision.requiredEvidence.some((evidenceId) => simulatedOpenReceiptIds.has(evidenceId)),
  );
  const simulatedGate: TaskOrchestratorGate = simulatedOpenReceipts.length === 0 ? "Ready" : "Review";
  const selectedImpactReceipt =
    impact.ownerReceipts.find((receipt) => receipt.id === selectedImpactReceiptId) ??
    impact.ownerReceipts.find((receipt) => receipt.state !== "accepted") ??
    impact.ownerReceipts[0];
  const selectedReceiptSteps = selectedImpactReceipt
    ? impact.pathSteps.filter((step) => step.receiptId === selectedImpactReceipt.id)
    : [];
  const selectedReceiptDecisions = selectedImpactReceipt
    ? impact.publishDecisions.filter((decision) => decision.requiredEvidence.includes(selectedImpactReceipt.id))
    : [];
  const selectedReceiptMatrix = selectedImpactReceipt
    ? impact.decisionMatrix.filter((cell) => cell.receiptId === selectedImpactReceipt.id)
    : [];
  const discoveredTools = useMemo(
    () => filterDiscoveredTools(report.toolRegistry, discoveryFilters),
    [discoveryFilters, report.toolRegistry],
  );
  const discoveredToolIds = useMemo(() => new Set(discoveredTools.map((tool) => tool.id)), [discoveredTools]);
  const visibleDiagnostics = report.toolDiscovery.diagnostics.filter((diagnostic) => discoveredToolIds.has(diagnostic.toolId));
  const visibleLaunchEntries = report.toolDiscovery.launchManifest.entries.filter((entry) => discoveredToolIds.has(entry.toolId));
  const dccConnected = dccSnapshot.available;

  function downloadReport() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${report.taskId}-orchestrator-report.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function updateDiscoveryFilter<Key extends keyof TaskToolDiscoveryFilters>(
    key: Key,
    value: TaskToolDiscoveryFilters[Key],
  ) {
    setDiscoveryFilters((current) => ({ ...current, [key]: value }));
  }

  function toggleSimulatedReceipt(receiptId: string) {
    setSimulatedClosedReceiptIds((current) =>
      current.includes(receiptId) ? current.filter((id) => id !== receiptId) : [...current, receiptId],
    );
  }

  async function runTaskDccAction(action: TaskDccAction) {
    const latest = getBridgeSnapshot();
    setDccSnapshot(latest);

    if (!latest.available) {
      setDccError("Open this module through the Maya AuroraView host to run task orchestration DCC actions.");
      return;
    }

    setDccBusyAction(action.id);
    setDccError(null);

    try {
      const result = await callMayaBridge<unknown>(action.method, {
        include_all: true,
        label: "task-orchestrator-dcc-scene",
      });
      setDccRun(normalizeTaskDccRun(action, result));
      setDccSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setDccError(caught instanceof Error ? caught.message : "Task Orchestrator DCC call failed.");
    } finally {
      setDccBusyAction(null);
    }
  }

  return (
    <div className="task-orchestrator-workbench">
      <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>
          平台层的价值不是再包一层按钮，而是把任务、工具发现、模块执行证据、review gate 和 publish handoff 变成同一个可追踪状态流。
        </p>
      </section>

      <section className="schema-band task-summary-band" aria-label="task orchestrator summary">
        <div>
          <span>Gate</span>
          <strong data-gate={report.gate}>{taskGateLabels[report.gate]}</strong>
        </div>
        <div>
          <span>Modules</span>
          <strong>{report.moduleTraces.length}</strong>
        </div>
        <div>
          <span>Evidence</span>
          <strong>{report.evidencePacket.itemCount}</strong>
        </div>
        <div>
          <span>Registry</span>
          <strong>{report.toolRegistry.length}</strong>
        </div>
      </section>

      <section className="logic-block wide task-dcc-panel">
        <div className="editor-header">
          <div className="section-title">
            <Waypoints size={17} aria-hidden="true" />
            <h3>Maya Batch Queue</h3>
          </div>
          <span className="bridge-state" data-state={dccConnected ? "connected" : "offline"}>
            {dccConnected ? "Connected" : "Preview"}
          </span>
        </div>

        <div className="task-dcc-action-grid" aria-label="Maya task orchestration actions">
          {taskDccActions.map((action) => {
            const busy = dccBusyAction === action.id;

            return (
              <button
                className="bridge-action-button"
                disabled={!dccConnected || dccBusyAction !== null}
                key={action.id}
                onClick={() => runTaskDccAction(action)}
                type="button"
              >
                {action.id === "fixture" ? (
                  <PackageCheck size={15} aria-hidden="true" />
                ) : action.id === "discover" ? (
                  <Network size={15} aria-hidden="true" />
                ) : action.id === "queue" ? (
                  <ListChecks size={15} aria-hidden="true" />
                ) : action.id === "dryRun" ? (
                  <Activity size={15} aria-hidden="true" />
                ) : (
                  <Download size={15} aria-hidden="true" />
                )}
                <span>{busy ? "Running" : action.label}</span>
              </button>
            );
          })}
        </div>

        {dccError ? (
          <div className="dcc-rule-error" role="alert">
            {dccError}
          </div>
        ) : null}

        <div className="task-dcc-summary">
          <div>
            <span>Last Action</span>
            <strong>{dccRun?.label ?? "Not Run"}</strong>
          </div>
          <div>
            <span>Assets</span>
            <strong>{dccRun?.assetCount ?? "-"}</strong>
          </div>
          <div>
            <span>Tasks</span>
            <strong>{dccRun?.taskCount ?? "-"}</strong>
          </div>
          <div>
            <span>Done / Review</span>
            <strong>{dccRun ? `${dccRun.doneCount} / ${dccRun.reviewCount}` : "-"}</strong>
          </div>
          <div>
            <span>Blocked</span>
            <strong>{dccRun?.blockedCount ?? "-"}</strong>
          </div>
          <div>
            <span>Gate</span>
            <strong data-gate={dccRun?.gate ?? "Preview"}>{dccRun?.gate ?? "Preview"}</strong>
          </div>
        </div>

        {dccRun ? (
          <div className="task-dcc-grid">
            <div className="task-dcc-asset-list">
              {dccRun.assets.length > 0 ? (
                dccRun.assets.map((asset) => (
                  <article data-gate={asset.gate} key={asset.id}>
                    <div>
                      <strong>{asset.node}</strong>
                      <span>{asset.gate}</span>
                    </div>
                    <p>{asset.role} / {asset.lod} / {asset.triangles} tris</p>
                    <code>{asset.materials} material(s) / {asset.textures} texture node(s) / {asset.issues}</code>
                  </article>
                ))
              ) : (
                <p className="empty-state">Create a fixture or discover scene assets to populate batch rows.</p>
              )}
            </div>

            <div className="task-dcc-task-list">
              {dccRun.tasks.length > 0 ? (
                dccRun.tasks.slice(0, 10).map((task) => (
                  <article data-status={task.status} key={task.id}>
                    <div>
                      <strong>{task.label}</strong>
                      <span>{task.status}</span>
                    </div>
                    <p>{task.asset} / {task.phase}</p>
                    <code>{task.evidence}</code>
                  </article>
                ))
              ) : (
                <p className="empty-state">Build queue or dry-run to show per-asset task rows.</p>
              )}
            </div>

            <div className="task-dcc-receipt-list">
              {dccRun.receipts.length > 0 ? (
                dccRun.receipts.map((receipt) => (
                  <article data-gate={receipt.gate} key={receipt.id}>
                    <span>{receipt.gate}</span>
                    <strong>{receipt.asset}</strong>
                    <p>{receipt.state}</p>
                    <code>{receipt.nextAction}</code>
                  </article>
                ))
              ) : (
                <div className="task-dcc-output">
                  <span>Output</span>
                  <code>{dccRun.path ?? "No DCC artifact path yet."}</code>
                  <p>Dry-run keeps scene writes at zero and records commands as adapter contracts.</p>
                </div>
              )}
            </div>

            <div className="dcc-rule-json-panel">
              <div className="bridge-result-title">
                <span>{dccRun.path ?? "DCC task payload"}</span>
                <strong>JSON</strong>
              </div>
              <pre>{safeJson(dccRun.raw)}</pre>
            </div>
          </div>
        ) : (
          <p className="empty-state">
            Create a batch fixture, discover scene assets, build a dry-run queue, then export a DCC orchestration report.
          </p>
        )}
      </section>

      <section className="logic-block wide task-control-panel">
        <div className="editor-header">
          <div className="section-title">
            <Network size={17} aria-hidden="true" />
            <h3>Task Package</h3>
          </div>
          <button className="primary-button compact" onClick={downloadReport} type="button">
            <Download size={15} aria-hidden="true" />
            <span>Export Report</span>
          </button>
        </div>
        <div className="task-package-grid">
          <div>
            <span>Task</span>
            <strong>{report.title}</strong>
            <p>{report.taskId}</p>
          </div>
          <div data-gate={report.gate}>
            <span>Summary</span>
            <strong>{report.gate}</strong>
            <p>{report.summary}</p>
          </div>
          <div>
            <span>Evidence Packet</span>
            <strong>{report.evidencePacket.packetId}</strong>
            <p>{report.evidencePacket.packetHash}</p>
          </div>
        </div>
      </section>

      <section className="logic-block task-lifecycle-panel">
        <div className="section-title">
          <GitBranch size={17} aria-hidden="true" />
          <h3>Lifecycle</h3>
        </div>
        <div className="task-lifecycle-list">
          {report.lifecycle.map((step) => (
            <article className="task-lifecycle-row" data-status={step.status} key={step.id}>
              <span>{lifecycleStatusLabels[step.status]}</span>
              <strong>{step.label}</strong>
              <p>{step.owner}</p>
              <code>{step.exitEvidence}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block task-trace-panel">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Module Execution Trace</h3>
        </div>
        <div className="task-trace-tabs" aria-label="module execution traces">
          {report.moduleTraces.map((trace) => (
            <button
              aria-pressed={trace.id === selectedTrace.id}
              key={trace.id}
              onClick={() => setSelectedTraceId(trace.id)}
              type="button"
            >
              <span>{trace.phase}</span>
              <strong>{trace.moduleName}</strong>
              <em>{trace.gate}</em>
            </button>
          ))}
        </div>
        <article className="task-trace-detail" data-gate={selectedTrace.gate}>
          <div>
            <span>Deterministic Signal</span>
            <strong>{selectedTrace.deterministicSignal}</strong>
          </div>
          <div>
            <span>AI Contribution</span>
            <p>{selectedTrace.aiContribution}</p>
          </div>
          <dl>
            <div><dt>Owner</dt><dd>{selectedTrace.owner}</dd></div>
            <div><dt>Status</dt><dd>{selectedTrace.status}</dd></div>
            <div><dt>Evidence</dt><dd>{selectedTrace.evidenceCount}</dd></div>
            <div><dt>Artifact</dt><dd>{selectedTrace.reportArtifact}</dd></div>
          </dl>
          <code>{selectedTrace.publishBlocker}</code>
        </article>
      </section>

      <section className="logic-block wide task-execution-panel">
        <div className="section-title">
          <Activity size={17} aria-hidden="true" />
          <h3>Execution Events</h3>
        </div>
        <div className="task-execution-summary">
          <div>
            <span>Events</span>
            <strong>{report.executionSummary.totalEvents}</strong>
          </div>
          <div>
            <span>Done</span>
            <strong data-status="done">{report.executionSummary.completedEvents}</strong>
          </div>
          <div>
            <span>Review</span>
            <strong data-status="review">{report.executionSummary.reviewEvents}</strong>
          </div>
          <div>
            <span>Current</span>
            <strong>{currentEvent.label}</strong>
          </div>
        </div>
        <div className="task-event-list">
          {report.executionEvents.map((event) => (
            <article className="task-event-row" data-status={event.status} key={event.id}>
              <span>{eventKindLabels[event.kind]}</span>
              <strong>{event.label}</strong>
              <em>{eventStatusLabels[event.status]}</em>
              <p>{event.detail}</p>
              <code>{event.receipt}</code>
              <small>{event.inputHash}{" -> "}{event.outputHash}</small>
            </article>
          ))}
        </div>
        <p className="task-next-action">{report.executionSummary.nextAction}</p>
      </section>

      <section className="logic-block task-dependency-panel">
        <div className="section-title">
          <Waypoints size={17} aria-hidden="true" />
          <h3>Dependency Graph</h3>
        </div>
        <div className="task-dependency-path">
          {report.dependencyGraph.criticalPath.map((node) => (
            <span key={node}>{node}</span>
          ))}
        </div>
        <div className="task-dependency-node-list">
          {report.dependencyGraph.nodes.map((node) => (
            <article className="task-dependency-node" data-gate={node.gate} key={node.id}>
              <span>{node.gate}</span>
              <strong>{node.label}</strong>
              <p>{node.blocker}</p>
              <code>{node.produces.join(" + ")}</code>
            </article>
          ))}
        </div>
        <div className="task-edge-list">
          {report.dependencyGraph.edges.map((edge) => (
            <article className="task-edge-row" data-gate={edge.gate} key={edge.id}>
              <strong>{edge.contract}</strong>
              <span>{edge.gate}</span>
              <p>{edge.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block wide task-impact-panel">
        <div className="section-title">
          <Waypoints size={17} aria-hidden="true" />
          <h3>Asset Dependency Impact</h3>
        </div>
        <div className="task-impact-scenarios" role="tablist" aria-label="dependency impact scenarios">
          {dependencyImpactScenarioOptions.map((scenario) => (
            <button
              aria-pressed={selectedImpactScenarioId === scenario.datasetId}
              className="task-impact-scenario"
              key={scenario.datasetId}
              onClick={() => {
                setSelectedImpactScenarioId(scenario.datasetId);
                setSelectedImpactReceiptId("");
                setSimulatedClosedReceiptIds([]);
              }}
              type="button"
            >
              <strong>{scenario.name}</strong>
              <span>{scenario.gateHint}</span>
              <small>
                {scenario.assetCount} assets / {scenario.pathCount} paths / {scenario.receiptCount} receipts
              </small>
              <code>{scenario.publicPath}</code>
            </button>
          ))}
        </div>
        <div className="source-list">
          <code>{impact.reportVersion}</code>
          <code>{impact.impactId}</code>
          <code>{impact.dataset.datasetVersion}</code>
          <code>{impact.dataset.datasetId}</code>
          <code>{impact.dataset.scenarioCount} scenario(s)</code>
          <code>{impact.packageId}</code>
          <code>{impact.dataset.publicPath}</code>
        </div>
        <div className="task-impact-summary" data-gate={impact.gate}>
          <div>
            <span>Gate</span>
            <strong>{impact.gate}</strong>
          </div>
          <div>
            <span>Assets</span>
            <strong>{impact.summary.affectedAssets}</strong>
          </div>
          <div>
            <span>Paths</span>
            <strong>{impact.summary.impactPaths}</strong>
          </div>
          <div>
            <span>Steps</span>
            <strong>{impact.summary.pathSteps}</strong>
          </div>
          <div>
            <span>Held</span>
            <strong data-action="hold">{impact.summary.heldPublishes}</strong>
          </div>
          <div>
            <span>Safe</span>
            <strong data-action="safe_publish">{impact.summary.safePublishes}</strong>
          </div>
          <div>
            <span>Pending</span>
            <strong data-state="pending">{impact.summary.pendingReceipts}</strong>
          </div>
          <div>
            <span>Max Risk</span>
            <strong>{impact.summary.maxRiskScore}</strong>
          </div>
          <div>
            <span>Matrix</span>
            <strong>{impact.summary.matrixCells}</strong>
          </div>
        </div>

        <div className="task-impact-dataset">
          <div>
            <span>Scenario</span>
            <strong>{impact.dataset.scenarioName}</strong>
            <p>{impact.sourceChange}</p>
          </div>
          <div>
            <span>Baseline</span>
            <code>{impact.dataset.baselinePackageId}</code>
          </div>
          <div>
            <span>Candidate</span>
            <code>{impact.dataset.currentPackageId}</code>
          </div>
          <div>
            <span>Source Run</span>
            <code>{impact.sourceRunId}</code>
          </div>
        </div>

        <div className="task-impact-root">
          <div>
            <span>Source Change</span>
            <p>{impact.sourceChange}</p>
          </div>
          <div>
            <span>AI Draft</span>
            <p>{impact.aiDraft}</p>
          </div>
          <code>{impact.summary.nextAction}</code>
        </div>

        <div className="task-impact-comparison">
          <div className="task-impact-comparison-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Scenario Comparison</h3>
            </div>
            <p>{impact.scenarioComparison.headline}</p>
          </div>
          <div className="source-list">
            <code>{impact.scenarioComparison.reportVersion}</code>
            <code>{impact.scenarioComparison.currentScenarioId}</code>
            <code>{impact.scenarioComparison.compareScenarioId}</code>
          </div>
          <div className="task-impact-comparison-table" role="table" aria-label="impact scenario comparison">
            <div role="row">
              <span>Metric</span>
              <span>Current</span>
              <span>Compare</span>
              <span>Delta</span>
            </div>
            {impact.scenarioComparison.metrics.map((metric) => (
              <div key={metric.id} role="row">
                <strong>{metric.label}</strong>
                <span>{metric.currentValue}</span>
                <span>{metric.compareValue}</span>
                <em data-delta={metric.delta === 0 ? "flat" : metric.delta > 0 ? "up" : "down"}>
                  {metric.delta > 0 ? "+" : ""}{metric.delta} {metric.unit}
                </em>
              </div>
            ))}
          </div>
          <div className="task-impact-comparison-notes">
            <div>
              <span>Reviewer Use</span>
              <p>{impact.scenarioComparison.reviewerUse}</p>
            </div>
            <ul>
              {impact.scenarioComparison.keyDifferences.map((difference) => (
                <li key={difference}>{difference}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="task-impact-authoring">
          <div className="task-impact-authoring-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Fixture Authoring Draft</h3>
            </div>
            <div>
              <span>{impact.fixtureAuthoringDraft.authoringState}</span>
              <strong>{impact.fixtureAuthoringDraft.draftId}</strong>
              <code>{impact.fixtureAuthoringDraft.targetPublicPath}</code>
            </div>
          </div>
          <div className="task-impact-authoring-counts">
            <div><span>Assets</span><strong>{impact.fixtureAuthoringDraft.previewCounts.assetNodes}</strong></div>
            <div><span>Paths</span><strong>{impact.fixtureAuthoringDraft.previewCounts.impactPaths}</strong></div>
            <div><span>Steps</span><strong>{impact.fixtureAuthoringDraft.previewCounts.pathSteps}</strong></div>
            <div><span>Decisions</span><strong>{impact.fixtureAuthoringDraft.previewCounts.publishDecisions}</strong></div>
            <div><span>Receipts</span><strong>{impact.fixtureAuthoringDraft.previewCounts.ownerReceipts}</strong></div>
            <div><span>Matrix</span><strong>{impact.fixtureAuthoringDraft.previewCounts.decisionMatrixCells}</strong></div>
          </div>
          <div className="task-impact-authoring-grid">
            <div className="task-impact-field-list">
              <span>Required Fields</span>
              {impact.fixtureAuthoringDraft.requiredFields.map((field) => (
                <code key={field}>{field}</code>
              ))}
            </div>
            <div className="task-impact-checklist">
              <span>Validation Checklist</span>
              {impact.fixtureAuthoringDraft.validationChecklist.map((item) => (
                <article data-status={item.status} key={item.id}>
                  <strong>{item.label}</strong>
                  <em>{item.status}</em>
                  <p>{item.note}</p>
                </article>
              ))}
            </div>
            <div className="task-impact-guardrails">
              <span>Guardrails</span>
              {impact.fixtureAuthoringDraft.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
          </div>
          <code>{impact.fixtureAuthoringDraft.targetDatasetId}</code>
        </div>

        <div className="task-impact-closure-sim">
          <div className="task-impact-closure-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Receipt Closure Simulation</h3>
            </div>
            <code>{impact.receiptClosureSimulation.simulationId}</code>
          </div>
          <div className="task-impact-closure-summary">
            <div><span>Before Gate</span><strong>{impact.receiptClosureSimulation.before.gate}</strong></div>
            <div><span>Before Held</span><strong>{impact.receiptClosureSimulation.before.heldPublishes}</strong></div>
            <div><span>Before Pending</span><strong>{impact.receiptClosureSimulation.before.pendingReceipts}</strong></div>
            <div><span>After Gate</span><strong>{impact.receiptClosureSimulation.after.gate}</strong></div>
            <div><span>Publishable</span><strong>{impact.receiptClosureSimulation.after.publishableTargets}</strong></div>
          </div>
          <div className="task-impact-closure-controls" aria-label="simulated receipt closures">
            {pendingImpactReceipts.map((receipt) => (
              <label data-checked={simulatedClosedSet.has(receipt.id)} key={receipt.id}>
                <input
                  checked={simulatedClosedSet.has(receipt.id)}
                  onChange={() => toggleSimulatedReceipt(receipt.id)}
                  type="checkbox"
                />
                <span>{impactReceiptStateLabels[receipt.state]}</span>
                <strong>{receipt.owner}</strong>
                <small>{receipt.id}</small>
              </label>
            ))}
          </div>
          <div className="task-impact-closure-result" data-gate={simulatedGate}>
            <div><span>Simulated Gate</span><strong>{simulatedGate}</strong></div>
            <div><span>Open Receipts</span><strong>{simulatedOpenReceipts.length}</strong></div>
            <div><span>Held Targets</span><strong>{simulatedHeldTargets.length}</strong></div>
            <div><span>Closed Receipts</span><strong>{activeSimulatedClosedReceiptIds.length}</strong></div>
          </div>
          <div className="task-impact-outcome-list">
            {impact.receiptClosureSimulation.targetOutcomes.map((outcome) => (
              <article data-action={outcome.beforeAction} key={outcome.target}>
                <span>{impactActionLabels[outcome.beforeAction]}</span>
                <strong>{outcome.target}</strong>
                <p>{outcome.note}</p>
                <code>{outcome.simulatedAction}</code>
                <small>{outcome.closedReceiptIds.length > 0 ? outcome.closedReceiptIds.join(" / ") : "no receipt closure"}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-residuals">
            {impact.receiptClosureSimulation.residualRisks.map((risk) => (
              <p key={risk}>{risk}</p>
            ))}
          </div>
        </div>

        <div className="task-impact-variant-gen">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitBranch size={17} aria-hidden="true" />
              <h3>Batch Fixture Variant Generator</h3>
            </div>
            <div>
              <span>{impact.batchVariantGenerator.reportVersion}</span>
              <strong>{impact.batchVariantGenerator.generatorId}</strong>
              <code>{impact.batchVariantGenerator.targetPublicPath}</code>
            </div>
          </div>
          <p>{impact.batchVariantGenerator.strategy}</p>
          <div className="task-impact-r8-summary">
            <div><span>Variants</span><strong>{impact.batchVariantGenerator.summary.variantCount}</strong></div>
            <div><span>Ready</span><strong data-gate="Ready">{impact.batchVariantGenerator.summary.readyVariants}</strong></div>
            <div><span>Review</span><strong data-gate="Review">{impact.batchVariantGenerator.summary.reviewVariants}</strong></div>
            <div><span>Blocked</span><strong data-gate="Blocked">{impact.batchVariantGenerator.summary.blockedVariants}</strong></div>
            <div><span>Max Risk</span><strong>{impact.batchVariantGenerator.summary.maxExpectedRiskScore}</strong></div>
          </div>
          <div className="task-impact-variant-list">
            {impact.batchVariantGenerator.variants.map((variant) => (
              <article data-gate={variant.gate} key={variant.variantId}>
                <div className="task-impact-r8-title">
                  <span>{variant.gate}</span>
                  <strong>{variant.label}</strong>
                  <em>{variant.mutationKind}</em>
                </div>
                <p>{variant.whyHighValue}</p>
                <dl>
                  <div><dt>Assets</dt><dd>{variant.expectedAffectedAssets}</dd></div>
                  <div><dt>Paths</dt><dd>{variant.expectedImpactPaths}</dd></div>
                  <div><dt>Held</dt><dd>{variant.expectedHeldPublishes}</dd></div>
                  <div><dt>Pending</dt><dd>{variant.expectedPendingReceipts}</dd></div>
                  <div><dt>Risk</dt><dd>{variant.expectedMaxRiskScore}</dd></div>
                </dl>
                <code>{variant.seedReceipts.join(" / ")}</code>
                <small>{variant.derivedScenarioPatch.join(" | ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Selection Rules</span>
              {impact.batchVariantGenerator.selectionRules.map((rule) => (
                <p key={rule}>{rule}</p>
              ))}
            </div>
            <div>
              <span>Rejection Rules</span>
              {impact.batchVariantGenerator.rejectionRules.map((rule) => (
                <p key={rule}>{rule}</p>
              ))}
            </div>
          </div>
          <code>{impact.batchVariantGenerator.summary.nextAction}</code>
        </div>

        <div className="task-impact-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Adapter Replay Dry-run</h3>
            </div>
            <div>
              <span>{impact.adapterReplayDryRun.reportVersion}</span>
              <strong>{impact.adapterReplayDryRun.adapterName}</strong>
              <code>{impact.adapterReplayDryRun.replayId}</code>
            </div>
          </div>
          <code>{impact.adapterReplayDryRun.command}</code>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.adapterReplayDryRun.summary.gate}>{impact.adapterReplayDryRun.summary.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.adapterReplayDryRun.summary.totalSteps}</strong></div>
            <div><span>Pass</span><strong data-status="pass">{impact.adapterReplayDryRun.summary.passedSteps}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.adapterReplayDryRun.summary.reviewSteps}</strong></div>
            <div><span>Skipped</span><strong>{impact.adapterReplayDryRun.summary.skippedSteps}</strong></div>
            <div><span>Mutation</span><strong>{String(impact.adapterReplayDryRun.mutationAllowed)}</strong></div>
          </div>
          <div className="task-impact-replay-steps">
            {impact.adapterReplayDryRun.steps.map((step) => (
              <article data-status={step.status} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{replayStepStatusLabels[step.status]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.detail}</p>
                <code>{step.inputHash} {"->"} {step.outputHash}</code>
                <small>{step.durationMs} ms</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Input Fixtures</span>
              {impact.adapterReplayDryRun.inputFixtures.map((fixture) => (
                <p key={fixture}>{fixture}</p>
              ))}
            </div>
            <div>
              <span>Guardrails</span>
              {impact.adapterReplayDryRun.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
          </div>
          <code>{impact.adapterReplayDryRun.summary.nextAction}</code>
        </div>

        <div className="task-impact-regression">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Regression Score Trend</h3>
            </div>
            <div>
              <span>{impact.regressionScoreTrend.reportVersion}</span>
              <strong>{impact.regressionScoreTrend.currentRunId}</strong>
              <code>{impact.regressionScoreTrend.trendId}</code>
            </div>
          </div>
          <div className="task-impact-regression-summary" data-gate={impact.regressionScoreTrend.gate}>
            <div><span>Baseline</span><strong>{impact.regressionScoreTrend.baselineRunId}</strong></div>
            <div><span>Current</span><strong>{impact.regressionScoreTrend.currentRunId}</strong></div>
            <div><span>Gate</span><strong>{impact.regressionScoreTrend.gate}</strong></div>
            <div><span>Score Delta</span><strong>{impact.regressionScoreTrend.scoreDelta}</strong></div>
          </div>
          <div className="task-impact-trend-list">
            {impact.regressionScoreTrend.points.map((point) => (
              <article data-gate={point.gate} key={point.runId}>
                <div className="task-impact-r8-title">
                  <span>{point.gate}</span>
                  <strong>{point.label}</strong>
                  <em>{point.regressionScore}</em>
                </div>
                <div className="task-impact-score-bar" aria-label={`${point.regressionScore} regression score`}>
                  <span style={{ width: `${Math.round((point.regressionScore / maxRegressionScore) * 100)}%` }} />
                </div>
                <p>{point.scenarioId}</p>
                <code>{point.runId}</code>
                <small>
                  {point.affectedAssets} assets / {point.heldPublishes} held / {point.pendingReceipts} pending / risk {point.maxRiskScore}
                </small>
              </article>
            ))}
          </div>
          <div className="task-impact-signal-list">
            {impact.regressionScoreTrend.signals.map((signal) => (
              <article data-status={signal.status} key={signal.id}>
                <span>{regressionSignalLabels[signal.status]}</span>
                <strong>{signal.label}</strong>
                <p>{signal.detail}</p>
              </article>
            ))}
          </div>
          <code>{impact.regressionScoreTrend.nextAction}</code>
        </div>

        <div className="task-impact-contract">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Adapter Contract Replay</h3>
            </div>
            <div>
              <span>{impact.adapterContractReplay.reportVersion}</span>
              <strong>{impact.adapterContractReplay.adapterName}</strong>
              <code>{impact.adapterContractReplay.contractId}</code>
            </div>
          </div>
          <code>{impact.adapterContractReplay.command}</code>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.adapterContractReplay.summary.gate}>{impact.adapterContractReplay.summary.gate}</strong></div>
            <div><span>Assertions</span><strong>{impact.adapterContractReplay.summary.totalAssertions}</strong></div>
            <div><span>Pass</span><strong data-status="pass">{impact.adapterContractReplay.summary.passedAssertions}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.adapterContractReplay.summary.reviewAssertions}</strong></div>
            <div><span>Fail</span><strong data-status="fail">{impact.adapterContractReplay.summary.failedAssertions}</strong></div>
            <div><span>Mutation</span><strong>{String(impact.adapterContractReplay.mutationAllowed)}</strong></div>
          </div>
          <div className="task-impact-contract-io">
            <article>
              <span>Input Contract</span>
              <strong>{impact.adapterContractReplay.inputContract.batchVariantPath}</strong>
              <code>{impact.adapterContractReplay.inputContract.fixturePath}</code>
              <small>{impact.adapterContractReplay.inputContract.requiredEnv.join(" / ")}</small>
            </article>
            <article>
              <span>Output Contract</span>
              <strong>{impact.adapterContractReplay.outputContract.syncPayloadPath}</strong>
              <code>{impact.adapterContractReplay.outputContract.receiptDraftPath}</code>
              <small>{impact.adapterContractReplay.outputContract.expectedStatuses.join(" / ")}</small>
            </article>
          </div>
          <div className="task-impact-contract-assertions">
            {impact.adapterContractReplay.assertions.map((assertion) => (
              <article data-status={assertion.status} key={assertion.id}>
                <div className="task-impact-r8-title">
                  <span>{contractAssertionStatusLabels[assertion.status]}</span>
                  <strong>{assertion.label}</strong>
                  <em>{assertion.gate}</em>
                </div>
                <p>{assertion.evidence}</p>
                <code>{assertion.expected}</code>
                <small>{assertion.actual}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Required Artifacts</span>
              {impact.adapterContractReplay.inputContract.requiredArtifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
            <div>
              <span>Guardrails</span>
              {impact.adapterContractReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
          </div>
          <code>{impact.adapterContractReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-sync">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Network size={17} aria-hidden="true" />
              <h3>External Receipt Sync Mock</h3>
            </div>
            <div>
              <span>{impact.externalReceiptSyncMock.reportVersion}</span>
              <strong>{impact.externalReceiptSyncMock.endpoint}</strong>
              <code>{impact.externalReceiptSyncMock.syncId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.externalReceiptSyncMock.queue.gate}>{impact.externalReceiptSyncMock.queue.gate}</strong></div>
            <div><span>Payloads</span><strong>{impact.externalReceiptSyncMock.queue.totalPayloads}</strong></div>
            <div><span>Create</span><strong data-status="pass">{impact.externalReceiptSyncMock.queue.createDraft}</strong></div>
            <div><span>Hold</span><strong data-status="review">{impact.externalReceiptSyncMock.queue.holdForReview}</strong></div>
            <div><span>Skip</span><strong data-status="fail">{impact.externalReceiptSyncMock.queue.skipBlocked}</strong></div>
            <div><span>Mutation</span><strong>{String(impact.externalReceiptSyncMock.mutationAllowed)}</strong></div>
          </div>
          <div className="task-impact-sync-payloads">
            {impact.externalReceiptSyncMock.payloads.map((payload) => (
              <article data-action={payload.syncAction} key={payload.payloadId}>
                <div className="task-impact-r8-title">
                  <span>{syncActionLabels[payload.syncAction]}</span>
                  <strong>{payload.sourceVariantId}</strong>
                  <em>{payload.gate}</em>
                </div>
                <p>{payload.previewComment}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{payload.owner}</dd></div>
                  <div><dt>Target</dt><dd>{payload.targetSystem}</dd></div>
                  <div><dt>State</dt><dd>{payload.receiptState}</dd></div>
                </dl>
                <code>{payload.checksum}</code>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Artifacts</span>
              {impact.externalReceiptSyncMock.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
            <div>
              <span>Guardrails</span>
              {impact.externalReceiptSyncMock.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
          </div>
          <code>{impact.externalReceiptSyncMock.queue.nextAction}</code>
        </div>

        <div className="task-impact-recovery">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Replay Failure Recovery</h3>
            </div>
            <div>
              <span>{impact.replayFailureRecovery.reportVersion}</span>
              <strong>{impact.replayFailureRecovery.gate}</strong>
              <code>{impact.replayFailureRecovery.recoveryId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.replayFailureRecovery.gate}>{impact.replayFailureRecovery.gate}</strong></div>
            <div><span>Incidents</span><strong>{impact.replayFailureRecovery.summary.totalIncidents}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.replayFailureRecovery.summary.blockedIncidents}</strong></div>
            <div><span>Retryable</span><strong data-status="review">{impact.replayFailureRecovery.summary.retryableIncidents}</strong></div>
            <div><span>Recovered</span><strong data-status="pass">{impact.replayFailureRecovery.summary.recoveredIncidents}</strong></div>
          </div>
          <div className="task-impact-recovery-incidents">
            {impact.replayFailureRecovery.incidents.map((incident) => (
              <article data-severity={incident.severity} key={incident.id}>
                <div className="task-impact-r8-title">
                  <span>{recoverySeverityLabels[incident.severity]}</span>
                  <strong>{incident.failureMode}</strong>
                  <em>{incident.sourceVariantId}</em>
                </div>
                <p>{incident.symptom}</p>
                <small>{incident.recoveryAction}</small>
                <code>{incident.retryCommand}</code>
                <small>{incident.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Recovery Plan</span>
              {impact.replayFailureRecovery.recoveryPlan.map((step) => (
                <p key={step}>{step}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.replayFailureRecovery.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.replayFailureRecovery.summary.nextAction}</code>
        </div>

        <div className="task-impact-handoff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Production Handoff Diff</h3>
            </div>
            <div>
              <span>{impact.productionHandoffDiff.reportVersion}</span>
              <strong>{impact.productionHandoffDiff.gate}</strong>
              <code>{impact.productionHandoffDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionHandoffDiff.gate}>{impact.productionHandoffDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.productionHandoffDiff.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-gate="Ready">{impact.productionHandoffDiff.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-gate="Review">{impact.productionHandoffDiff.summary.reviewRows}</strong></div>
            <div><span>Held</span><strong data-status="fail">{impact.productionHandoffDiff.summary.blockedRows}</strong></div>
            <div><span>Changed</span><strong>{impact.productionHandoffDiff.summary.changedFields}</strong></div>
          </div>
          <div className="task-impact-handoff-rows">
            {impact.productionHandoffDiff.rows.map((row) => (
              <article data-status={row.status} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{handoffDiffStatusLabels[row.status]}</span>
                  <strong>{row.field}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.reviewerNote}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Target</dt><dd>{row.targetSystem}</dd></div>
                  <div><dt>Before</dt><dd>{row.before}</dd></div>
                  <div><dt>After</dt><dd>{row.after}</dd></div>
                </dl>
                <code>{row.sourceVariantId}</code>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Signoff Required</span>
              {impact.productionHandoffDiff.signoffRequired.map((owner) => (
                <p key={owner}>{owner}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.productionHandoffDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionHandoffDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-approval">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Adapter Owner Approval Packet</h3>
            </div>
            <div>
              <span>{impact.adapterOwnerApprovalPacket.reportVersion}</span>
              <strong>{impact.adapterOwnerApprovalPacket.approvalState}</strong>
              <code>{impact.adapterOwnerApprovalPacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.adapterOwnerApprovalPacket.gate}>{impact.adapterOwnerApprovalPacket.gate}</strong></div>
            <div><span>Checks</span><strong>{impact.adapterOwnerApprovalPacket.summary.totalChecks}</strong></div>
            <div><span>Pass</span><strong data-status="pass">{impact.adapterOwnerApprovalPacket.summary.passedChecks}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.adapterOwnerApprovalPacket.summary.reviewChecks}</strong></div>
            <div><span>Block</span><strong data-status="fail">{impact.adapterOwnerApprovalPacket.summary.blockedChecks}</strong></div>
            <div><span>Approvals</span><strong>{impact.adapterOwnerApprovalPacket.summary.acceptedApprovals}/{impact.adapterOwnerApprovalPacket.summary.requiredApprovals}</strong></div>
          </div>
          <div className="task-impact-approval-checks">
            {impact.adapterOwnerApprovalPacket.checks.map((check) => (
              <article data-status={check.status} key={check.id}>
                <div className="task-impact-r8-title">
                  <span>{approvalCheckStatusLabels[check.status]}</span>
                  <strong>{check.label}</strong>
                  <em>{check.owner}</em>
                </div>
                <p>{check.decisionNeeded}</p>
                <code>{check.evidence}</code>
                <small>{check.required ? "required" : "optional"}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-approval-owners">
            {impact.adapterOwnerApprovalPacket.requestedApprovals.map((approval) => (
              <article data-state={approval.state} key={`${approval.owner}-${approval.scope}`}>
                <span>{approval.state}</span>
                <strong>{approval.owner}</strong>
                <p>{approval.scope}</p>
                <code>{approval.due}</code>
                <small>{approval.note}</small>
              </article>
            ))}
          </div>
          <code>{impact.adapterOwnerApprovalPacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-retry-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Held Payload Retry Ledger</h3>
            </div>
            <div>
              <span>{impact.heldPayloadRetryLedger.reportVersion}</span>
              <strong>{impact.heldPayloadRetryLedger.gate}</strong>
              <code>{impact.heldPayloadRetryLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.heldPayloadRetryLedger.gate}>{impact.heldPayloadRetryLedger.gate}</strong></div>
            <div><span>Entries</span><strong>{impact.heldPayloadRetryLedger.summary.totalEntries}</strong></div>
            <div><span>Retry Ready</span><strong data-status="pass">{impact.heldPayloadRetryLedger.summary.retryReady}</strong></div>
            <div><span>Waiting</span><strong data-status="review">{impact.heldPayloadRetryLedger.summary.waitingOwner}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.heldPayloadRetryLedger.summary.blocked}</strong></div>
          </div>
          <div className="task-impact-retry-entries">
            {impact.heldPayloadRetryLedger.entries.map((entry) => (
              <article data-state={entry.state} key={entry.id}>
                <div className="task-impact-r8-title">
                  <span>{retryEntryStateLabels[entry.state]}</span>
                  <strong>{entry.owner}</strong>
                  <em>{entry.sourceVariantId}</em>
                </div>
                <p>{entry.nextCheck}</p>
                <small>{entry.lastFailureMode} / attempt {entry.attempt}</small>
                <code>{entry.retryCommand}</code>
                <small>{entry.requiredApprovalIds.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Artifacts</span>
              {impact.heldPayloadRetryLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
            <div>
              <span>Evidence Threads</span>
              {impact.heldPayloadRetryLedger.entries.map((entry) => (
                <p key={entry.id}>{entry.evidence.join(" / ")}</p>
              ))}
            </div>
          </div>
          <code>{impact.heldPayloadRetryLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-signed-sandbox">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Signed Receipt Sandbox</h3>
            </div>
            <div>
              <span>{impact.signedReceiptSandbox.reportVersion}</span>
              <strong>{impact.signedReceiptSandbox.gate}</strong>
              <code>{impact.signedReceiptSandbox.sandboxId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.signedReceiptSandbox.gate}>{impact.signedReceiptSandbox.gate}</strong></div>
            <div><span>Receipts</span><strong>{impact.signedReceiptSandbox.summary.totalReceipts}</strong></div>
            <div><span>Signed</span><strong data-status="pass">{impact.signedReceiptSandbox.summary.signedReceipts}</strong></div>
            <div><span>Held</span><strong data-status="review">{impact.signedReceiptSandbox.summary.heldReceipts}</strong></div>
            <div><span>Rejected</span><strong data-status="fail">{impact.signedReceiptSandbox.summary.rejectedReceipts}</strong></div>
            <div><span>Replayable</span><strong>{impact.signedReceiptSandbox.summary.replayableReceipts}</strong></div>
          </div>
          <div className="task-impact-sandbox-receipts">
            {impact.signedReceiptSandbox.receipts.map((receipt) => (
              <article data-state={receipt.state} key={receipt.id}>
                <div className="task-impact-r8-title">
                  <span>{sandboxReceiptStateLabels[receipt.state]}</span>
                  <strong>{receipt.scope}</strong>
                  <em>{receipt.gate}</em>
                </div>
                <p>{receipt.note}</p>
                <dl>
                  <div><dt>Signer</dt><dd>{receipt.signer}</dd></div>
                  <div><dt>Write Mode</dt><dd>{receipt.writeMode}</dd></div>
                  <div><dt>Replay</dt><dd>{receipt.replayAllowed ? "allowed" : "held"}</dd></div>
                </dl>
                <code>{receipt.signatureHash}</code>
                <small>{receipt.linkedApprovalIds.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.signedReceiptSandbox.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.signedReceiptSandbox.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.signedReceiptSandbox.summary.nextAction}</code>
        </div>

        <div className="task-impact-smoke-harness">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Cable size={17} aria-hidden="true" />
              <h3>Production Adapter Smoke Harness</h3>
            </div>
            <div>
              <span>{impact.productionAdapterSmokeHarness.reportVersion}</span>
              <strong>{impact.productionAdapterSmokeHarness.adapterName}</strong>
              <code>{impact.productionAdapterSmokeHarness.harnessId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionAdapterSmokeHarness.gate}>{impact.productionAdapterSmokeHarness.gate}</strong></div>
            <div><span>Checks</span><strong>{impact.productionAdapterSmokeHarness.summary.totalChecks}</strong></div>
            <div><span>Pass</span><strong data-status="pass">{impact.productionAdapterSmokeHarness.summary.passedChecks}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.productionAdapterSmokeHarness.summary.reviewChecks}</strong></div>
            <div><span>Fail</span><strong data-status="fail">{impact.productionAdapterSmokeHarness.summary.failedChecks}</strong></div>
            <div><span>Writes</span><strong>{impact.productionAdapterSmokeHarness.summary.writeAttempts}</strong></div>
          </div>
          <div className="task-impact-smoke-checks">
            {impact.productionAdapterSmokeHarness.checks.map((check) => (
              <article data-status={check.status} key={check.id}>
                <div className="task-impact-r8-title">
                  <span>{smokeCheckStatusLabels[check.status]}</span>
                  <strong>{check.label}</strong>
                  <em>{check.method}</em>
                </div>
                <p>{check.observed}</p>
                <dl>
                  <div><dt>Target</dt><dd>{check.target}</dd></div>
                  <div><dt>Expected</dt><dd>{check.expected}</dd></div>
                </dl>
                <small>{check.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Command Preview</span>
              <p>{impact.productionAdapterSmokeHarness.commandPreview}</p>
            </div>
            <div>
              <span>Guardrails</span>
              {impact.productionAdapterSmokeHarness.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionAdapterSmokeHarness.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-verification">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Rollback Receipt Verification</h3>
            </div>
            <div>
              <span>{impact.rollbackReceiptVerification.reportVersion}</span>
              <strong>{impact.rollbackReceiptVerification.gate}</strong>
              <code>{impact.rollbackReceiptVerification.verificationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackReceiptVerification.gate}>{impact.rollbackReceiptVerification.gate}</strong></div>
            <div><span>Rollbacks</span><strong>{impact.rollbackReceiptVerification.summary.totalRollbacks}</strong></div>
            <div><span>Verified</span><strong data-status="pass">{impact.rollbackReceiptVerification.summary.verifiedRollbacks}</strong></div>
            <div><span>Waiting</span><strong data-status="review">{impact.rollbackReceiptVerification.summary.waitingOwner}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.rollbackReceiptVerification.summary.blockedRollbacks}</strong></div>
          </div>
          <div className="task-impact-rollback-entries">
            {impact.rollbackReceiptVerification.entries.map((entry) => (
              <article data-state={entry.state} key={entry.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackReceiptStateLabels[entry.state]}</span>
                  <strong>{entry.owner}</strong>
                  <em>{entry.gate}</em>
                </div>
                <p>{entry.proof}</p>
                <dl>
                  <div><dt>Trigger</dt><dd>{entry.trigger}</dd></div>
                  <div><dt>Restore</dt><dd>{entry.restorationTarget}</dd></div>
                </dl>
                <code>{entry.rollbackReceiptId}</code>
                <small>{entry.nextAction}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackReceiptVerification.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackReceiptVerification.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackReceiptVerification.summary.nextAction}</code>
        </div>

        <div className="task-impact-credential-drill">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <KeyRound size={17} aria-hidden="true" />
              <h3>Credential Boundary Drill</h3>
            </div>
            <div>
              <span>{impact.credentialBoundaryDrill.reportVersion}</span>
              <strong>{impact.credentialBoundaryDrill.gate}</strong>
              <code>{impact.credentialBoundaryDrill.drillId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.credentialBoundaryDrill.gate}>{impact.credentialBoundaryDrill.gate}</strong></div>
            <div><span>Probes</span><strong>{impact.credentialBoundaryDrill.summary.totalProbes}</strong></div>
            <div><span>Pass</span><strong data-status="pass">{impact.credentialBoundaryDrill.summary.passedProbes}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.credentialBoundaryDrill.summary.reviewProbes}</strong></div>
            <div><span>Fail</span><strong data-status="fail">{impact.credentialBoundaryDrill.summary.failedProbes}</strong></div>
            <div><span>Leaks</span><strong data-status="fail">{impact.credentialBoundaryDrill.summary.leakedSecrets}</strong></div>
          </div>
          <div className="task-impact-credential-probes">
            {impact.credentialBoundaryDrill.probes.map((probe) => (
              <article data-status={probe.status} key={probe.id}>
                <div className="task-impact-r8-title">
                  <span>{credentialProbeStatusLabels[probe.status]}</span>
                  <strong>{probe.label}</strong>
                  <em>{probe.gate}</em>
                </div>
                <p>{probe.observed}</p>
                <dl>
                  <div><dt>State</dt><dd>{credentialStateLabels[probe.credentialState]}</dd></div>
                  <div><dt>Scope</dt><dd>{probe.scope}</dd></div>
                  <div><dt>Owner</dt><dd>{probe.owner}</dd></div>
                </dl>
                <code>{probe.expected}</code>
                <small>{probe.nextAction} / {probe.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.credentialBoundaryDrill.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.credentialBoundaryDrill.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.credentialBoundaryDrill.summary.nextAction}</code>
        </div>

        <div className="task-impact-retention-audit">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Receipt Retention Audit</h3>
            </div>
            <div>
              <span>{impact.receiptRetentionAudit.reportVersion}</span>
              <strong>{impact.receiptRetentionAudit.gate}</strong>
              <code>{impact.receiptRetentionAudit.auditId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.receiptRetentionAudit.gate}>{impact.receiptRetentionAudit.gate}</strong></div>
            <div><span>Records</span><strong>{impact.receiptRetentionAudit.summary.totalRecords}</strong></div>
            <div><span>Retained</span><strong data-status="pass">{impact.receiptRetentionAudit.summary.retainedRecords}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.receiptRetentionAudit.summary.reviewRecords}</strong></div>
            <div><span>Purge</span><strong data-status="fail">{impact.receiptRetentionAudit.summary.purgeRequired}</strong></div>
            <div><span>Days</span><strong>{impact.receiptRetentionAudit.summary.minRetentionDays}-{impact.receiptRetentionAudit.summary.maxRetentionDays}</strong></div>
          </div>
          <div className="task-impact-retention-records">
            {impact.receiptRetentionAudit.records.map((record) => (
              <article data-state={record.state} key={record.id}>
                <div className="task-impact-r8-title">
                  <span>{retentionStateLabels[record.state]}</span>
                  <strong>{record.receiptType}</strong>
                  <em>{record.gate}</em>
                </div>
                <p>{record.reason}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{record.owner}</dd></div>
                  <div><dt>Expires</dt><dd>{record.expiresAt}</dd></div>
                  <div><dt>Days</dt><dd>{record.retentionDays}</dd></div>
                  <div><dt>Storage</dt><dd>{record.storage}</dd></div>
                </dl>
                <code>{record.receiptId}</code>
                <small>{record.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.receiptRetentionAudit.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.receiptRetentionAudit.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.receiptRetentionAudit.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-drill">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Cross-Module Release Drill</h3>
            </div>
            <div>
              <span>{impact.crossModuleReleaseDrill.reportVersion}</span>
              <strong>{impact.crossModuleReleaseDrill.gate}</strong>
              <code>{impact.crossModuleReleaseDrill.drillId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.crossModuleReleaseDrill.gate}>{impact.crossModuleReleaseDrill.gate}</strong></div>
            <div><span>Lanes</span><strong>{impact.crossModuleReleaseDrill.summary.totalLanes}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.crossModuleReleaseDrill.summary.readyLanes}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.crossModuleReleaseDrill.summary.reviewLanes}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.crossModuleReleaseDrill.summary.blockedLanes}</strong></div>
            <div><span>Candidates</span><strong>{impact.crossModuleReleaseDrill.summary.releaseCandidates}</strong></div>
          </div>
          <div className="task-impact-release-lanes">
            {impact.crossModuleReleaseDrill.lanes.map((lane) => (
              <article data-state={lane.state} key={lane.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseLaneStateLabels[lane.state]}</span>
                  <strong>{lane.label}</strong>
                  <em>{lane.gate}</em>
                </div>
                <p>{lane.releaseAction}</p>
                <dl>
                  <div><dt>Module</dt><dd>{lane.moduleId}</dd></div>
                  <div><dt>Owner</dt><dd>{lane.owner}</dd></div>
                  <div><dt>Blockers</dt><dd>{lane.blockingReceiptIds.length}</dd></div>
                </dl>
                <code>{lane.drillCommand}</code>
                <small>{lane.blockingReceiptIds.length > 0 ? lane.blockingReceiptIds.join(" / ") : "no blockers"} / {lane.nextAction}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.crossModuleReleaseDrill.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.crossModuleReleaseDrill.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.crossModuleReleaseDrill.summary.nextAction}</code>
        </div>

        <div className="task-impact-failure-matrix">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Adapter Failure Injection Matrix</h3>
            </div>
            <div>
              <span>{impact.adapterFailureInjectionMatrix.reportVersion}</span>
              <strong>{impact.adapterFailureInjectionMatrix.gate}</strong>
              <code>{impact.adapterFailureInjectionMatrix.matrixId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.adapterFailureInjectionMatrix.gate}>{impact.adapterFailureInjectionMatrix.gate}</strong></div>
            <div><span>Cases</span><strong>{impact.adapterFailureInjectionMatrix.summary.totalCases}</strong></div>
            <div><span>Contained</span><strong data-status="pass">{impact.adapterFailureInjectionMatrix.summary.containedCases}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.adapterFailureInjectionMatrix.summary.reviewCases}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.adapterFailureInjectionMatrix.summary.blockedCases}</strong></div>
            <div><span>Rollback</span><strong>{impact.adapterFailureInjectionMatrix.summary.rollbackLinkedCases}</strong></div>
          </div>
          <div className="task-impact-failure-cases">
            {impact.adapterFailureInjectionMatrix.cases.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{failureInjectionStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.trigger}</p>
                <dl>
                  <div><dt>Mode</dt><dd>{item.failureMode}</dd></div>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Retry</dt><dd>{item.retryPolicy}</dd></div>
                </dl>
                <code>{item.expectedContainment}</code>
                <small>{item.observedRecovery} / {item.rollbackReceiptId}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.adapterFailureInjectionMatrix.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.adapterFailureInjectionMatrix.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.adapterFailureInjectionMatrix.summary.nextAction}</code>
        </div>

        <div className="task-impact-lineage-graph">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitBranch size={17} aria-hidden="true" />
              <h3>Receipt Lineage Graph</h3>
            </div>
            <div>
              <span>{impact.receiptLineageGraph.reportVersion}</span>
              <strong>{impact.receiptLineageGraph.gate}</strong>
              <code>{impact.receiptLineageGraph.graphId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.receiptLineageGraph.gate}>{impact.receiptLineageGraph.gate}</strong></div>
            <div><span>Nodes</span><strong>{impact.receiptLineageGraph.summary.totalNodes}</strong></div>
            <div><span>Linked</span><strong data-status="pass">{impact.receiptLineageGraph.summary.linkedNodes}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.receiptLineageGraph.summary.reviewNodes}</strong></div>
            <div><span>Orphaned</span><strong data-status="fail">{impact.receiptLineageGraph.summary.orphanedNodes}</strong></div>
            <div><span>Depth</span><strong>{impact.receiptLineageGraph.summary.maxDepth}</strong></div>
          </div>
          <div className="task-impact-lineage-nodes">
            {impact.receiptLineageGraph.nodes.map((node) => (
              <article data-state={node.state} key={node.id}>
                <div className="task-impact-r8-title">
                  <span>{lineageStateLabels[node.state]}</span>
                  <strong>{node.label}</strong>
                  <em>{node.gate}</em>
                </div>
                <p>{node.nextAction}</p>
                <dl>
                  <div><dt>Source</dt><dd>{node.source}</dd></div>
                  <div><dt>Owner</dt><dd>{node.owner}</dd></div>
                  <div><dt>Upstream</dt><dd>{node.upstreamIds.length}</dd></div>
                  <div><dt>Downstream</dt><dd>{node.downstreamIds.length}</dd></div>
                </dl>
                <code>{node.receiptId}</code>
                <small>{node.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.receiptLineageGraph.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.receiptLineageGraph.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.receiptLineageGraph.summary.nextAction}</code>
        </div>

        <div className="task-impact-reviewer-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Reviewer Packet Diff</h3>
            </div>
            <div>
              <span>{impact.reviewerPacketDiff.reportVersion}</span>
              <strong>{impact.reviewerPacketDiff.gate}</strong>
              <code>{impact.reviewerPacketDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.reviewerPacketDiff.gate}>{impact.reviewerPacketDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.reviewerPacketDiff.summary.totalRows}</strong></div>
            <div><span>Added</span><strong data-status="pass">{impact.reviewerPacketDiff.summary.addedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.reviewerPacketDiff.summary.changedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.reviewerPacketDiff.summary.reviewRows}</strong></div>
            <div><span>Same</span><strong>{impact.reviewerPacketDiff.summary.unchangedRows}</strong></div>
          </div>
          <div className="task-impact-reviewer-diff-rows">
            {impact.reviewerPacketDiff.rows.map((row) => (
              <article data-status={row.status} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{packetDiffStatusLabels[row.status]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.reviewReason}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Before</dt><dd>{row.before}</dd></div>
                  <div><dt>After</dt><dd>{row.after}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.reviewerPacketDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.reviewerPacketDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.reviewerPacketDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-readiness-simulator">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Live Adapter Readiness Simulator</h3>
            </div>
            <div>
              <span>{impact.liveAdapterReadinessSimulator.reportVersion}</span>
              <strong>{impact.liveAdapterReadinessSimulator.gate}</strong>
              <code>{impact.liveAdapterReadinessSimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.liveAdapterReadinessSimulator.gate}>{impact.liveAdapterReadinessSimulator.gate}</strong></div>
            <div><span>Checks</span><strong>{impact.liveAdapterReadinessSimulator.summary.totalChecks}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.liveAdapterReadinessSimulator.summary.readyChecks}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.liveAdapterReadinessSimulator.summary.reviewChecks}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.liveAdapterReadinessSimulator.summary.blockedChecks}</strong></div>
            <div><span>Writes</span><strong>{impact.liveAdapterReadinessSimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-readiness-checks">
            {impact.liveAdapterReadinessSimulator.checks.map((check) => (
              <article data-state={check.state} key={check.id}>
                <div className="task-impact-r8-title">
                  <span>{liveReadinessStateLabels[check.state]}</span>
                  <strong>{check.label}</strong>
                  <em>{check.gate}</em>
                </div>
                <p>{check.readinessSignal}</p>
                <dl>
                  <div><dt>Area</dt><dd>{check.adapterArea}</dd></div>
                  <div><dt>Owner</dt><dd>{check.owner}</dd></div>
                  <div><dt>Blocker</dt><dd>{check.blocker}</dd></div>
                </dl>
                <code>{check.simulatedInput}</code>
                <small>{check.nextAction} / {check.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.liveAdapterReadinessSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.liveAdapterReadinessSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.liveAdapterReadinessSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-approval-closeout">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Owner Approval Closeout</h3>
            </div>
            <div>
              <span>{impact.ownerApprovalCloseout.reportVersion}</span>
              <strong>{impact.ownerApprovalCloseout.gate}</strong>
              <code>{impact.ownerApprovalCloseout.closeoutId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerApprovalCloseout.gate}>{impact.ownerApprovalCloseout.gate}</strong></div>
            <div><span>Approvals</span><strong>{impact.ownerApprovalCloseout.summary.totalApprovals}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.ownerApprovalCloseout.summary.closedApprovals}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.ownerApprovalCloseout.summary.requestedApprovals}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.ownerApprovalCloseout.summary.blockedApprovals}</strong></div>
            <div><span>Required</span><strong>{impact.ownerApprovalCloseout.summary.requiredApprovals}</strong></div>
          </div>
          <div className="task-impact-approval-closeouts">
            {impact.ownerApprovalCloseout.approvals.map((approval) => (
              <article data-state={approval.state} key={approval.id}>
                <div className="task-impact-r8-title">
                  <span>{approvalCloseoutStateLabels[approval.state]}</span>
                  <strong>{approval.label}</strong>
                  <em>{approval.gate}</em>
                </div>
                <p>{approval.residualRisk}</p>
                <dl>
                  <div><dt>Scope</dt><dd>{approval.scope}</dd></div>
                  <div><dt>Owner</dt><dd>{approval.owner}</dd></div>
                </dl>
                <code>{approval.closeCommand}</code>
                <small>{approval.nextAction} / {approval.closeoutEvidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerApprovalCloseout.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerApprovalCloseout.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerApprovalCloseout.summary.nextAction}</code>
        </div>

        <div className="task-impact-mutation-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Mutation Replay Rehearsal</h3>
            </div>
            <div>
              <span>{impact.mutationReplayRehearsal.reportVersion}</span>
              <strong>{impact.mutationReplayRehearsal.gate}</strong>
              <code>{impact.mutationReplayRehearsal.rehearsalId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.mutationReplayRehearsal.gate}>{impact.mutationReplayRehearsal.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.mutationReplayRehearsal.summary.totalSteps}</strong></div>
            <div><span>Rehearsed</span><strong data-status="pass">{impact.mutationReplayRehearsal.summary.rehearsedSteps}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.mutationReplayRehearsal.summary.ownerHoldSteps}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.mutationReplayRehearsal.summary.blockedSteps}</strong></div>
            <div><span>Writes</span><strong>{impact.mutationReplayRehearsal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-mutation-steps">
            {impact.mutationReplayRehearsal.steps.map((step) => (
              <article data-state={step.state} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{mutationReplayStateLabels[step.state]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.observedResult}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{step.lane}</dd></div>
                  <div><dt>Owner</dt><dd>{step.owner}</dd></div>
                  <div><dt>Receipt</dt><dd>{step.expectedReceipt}</dd></div>
                </dl>
                <code>{step.dryRunCommand}</code>
                <small>{step.writeIntent} / {step.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.mutationReplayRehearsal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.mutationReplayRehearsal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.mutationReplayRehearsal.summary.nextAction}</code>
        </div>

        <div className="task-impact-cutover-checklist">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Production Adapter Cutover Checklist</h3>
            </div>
            <div>
              <span>{impact.productionAdapterCutoverChecklist.reportVersion}</span>
              <strong>{impact.productionAdapterCutoverChecklist.gate}</strong>
              <code>{impact.productionAdapterCutoverChecklist.checklistId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionAdapterCutoverChecklist.gate}>{impact.productionAdapterCutoverChecklist.gate}</strong></div>
            <div><span>Items</span><strong>{impact.productionAdapterCutoverChecklist.summary.totalItems}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.productionAdapterCutoverChecklist.summary.readyItems}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.productionAdapterCutoverChecklist.summary.ownerHoldItems}</strong></div>
            <div><span>Blocked</span><strong data-status="fail">{impact.productionAdapterCutoverChecklist.summary.blockedItems}</strong></div>
            <div><span>Dry Writes</span><strong>{impact.productionAdapterCutoverChecklist.summary.dryRunWrites}</strong></div>
          </div>
          <div className="task-impact-cutover-items">
            {impact.productionAdapterCutoverChecklist.items.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{cutoverChecklistStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.decisionSignal}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{item.cutoverLane}</dd></div>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Hold</dt><dd>{item.holdReason}</dd></div>
                </dl>
                <code>{item.precondition}</code>
                <small>{item.nextAction} / {item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.productionAdapterCutoverChecklist.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.productionAdapterCutoverChecklist.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionAdapterCutoverChecklist.summary.nextAction}</code>
        </div>

        <div className="task-impact-post-cutover-monitor">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Post-Cutover Receipt Monitor</h3>
            </div>
            <div>
              <span>{impact.postCutoverReceiptMonitor.reportVersion}</span>
              <strong>{impact.postCutoverReceiptMonitor.gate}</strong>
              <code>{impact.postCutoverReceiptMonitor.monitorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.postCutoverReceiptMonitor.gate}>{impact.postCutoverReceiptMonitor.gate}</strong></div>
            <div><span>Streams</span><strong>{impact.postCutoverReceiptMonitor.summary.totalStreams}</strong></div>
            <div><span>Healthy</span><strong data-status="pass">{impact.postCutoverReceiptMonitor.summary.healthyStreams}</strong></div>
            <div><span>Watch</span><strong data-status="review">{impact.postCutoverReceiptMonitor.summary.watchStreams}</strong></div>
            <div><span>Missing</span><strong data-status="fail">{impact.postCutoverReceiptMonitor.summary.missingReceipts}</strong></div>
            <div><span>Writes</span><strong>{impact.postCutoverReceiptMonitor.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-post-cutover-streams">
            {impact.postCutoverReceiptMonitor.streams.map((stream) => (
              <article data-state={stream.state} key={stream.id}>
                <div className="task-impact-r8-title">
                  <span>{postCutoverReceiptStateLabels[stream.state]}</span>
                  <strong>{stream.label}</strong>
                  <em>{stream.gate}</em>
                </div>
                <p>{stream.observedSignal}</p>
                <dl>
                  <div><dt>Stream</dt><dd>{stream.receiptStream}</dd></div>
                  <div><dt>Owner</dt><dd>{stream.owner}</dd></div>
                  <div><dt>Sampled</dt><dd>{stream.sampledReceipts}</dd></div>
                  <div><dt>Missing</dt><dd>{stream.missingReceiptCount}</dd></div>
                </dl>
                <code>{stream.expectedCadence}</code>
                <small>{stream.nextAction} / {stream.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.postCutoverReceiptMonitor.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.postCutoverReceiptMonitor.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.postCutoverReceiptMonitor.summary.nextAction}</code>
        </div>

        <div className="task-impact-emergency-stop">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Emergency Stop Drill</h3>
            </div>
            <div>
              <span>{impact.emergencyStopDrill.reportVersion}</span>
              <strong>{impact.emergencyStopDrill.gate}</strong>
              <code>{impact.emergencyStopDrill.drillId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.emergencyStopDrill.gate}>{impact.emergencyStopDrill.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.emergencyStopDrill.summary.totalSteps}</strong></div>
            <div><span>Verified</span><strong data-status="pass">{impact.emergencyStopDrill.summary.verifiedSteps}</strong></div>
            <div><span>Armed</span><strong data-status="review">{impact.emergencyStopDrill.summary.armedSteps}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.emergencyStopDrill.summary.ownerHoldSteps}</strong></div>
            <div><span>Max Latency</span><strong>{impact.emergencyStopDrill.summary.maxStopLatencyMs}ms</strong></div>
          </div>
          <div className="task-impact-emergency-steps">
            {impact.emergencyStopDrill.steps.map((step) => (
              <article data-state={step.state} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{emergencyStopStateLabels[step.state]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.restoreEvidence}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{step.stopLane}</dd></div>
                  <div><dt>Owner</dt><dd>{step.owner}</dd></div>
                  <div><dt>Latency</dt><dd>{step.latencyMs}ms</dd></div>
                </dl>
                <code>{step.stopCommand}</code>
                <small>{step.trigger} / {step.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.emergencyStopDrill.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.emergencyStopDrill.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.emergencyStopDrill.summary.nextAction}</code>
        </div>

        <div className="task-impact-private-bridge">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <KeyRound size={17} aria-hidden="true" />
              <h3>Private Owner Receipt Bridge</h3>
            </div>
            <div>
              <span>{impact.privateOwnerReceiptBridge.reportVersion}</span>
              <strong>{impact.privateOwnerReceiptBridge.gate}</strong>
              <code>{impact.privateOwnerReceiptBridge.bridgeId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.privateOwnerReceiptBridge.gate}>{impact.privateOwnerReceiptBridge.gate}</strong></div>
            <div><span>Links</span><strong>{impact.privateOwnerReceiptBridge.summary.totalLinks}</strong></div>
            <div><span>Mapped</span><strong data-status="pass">{impact.privateOwnerReceiptBridge.summary.mappedLinks}</strong></div>
            <div><span>Redacted</span><strong data-status="review">{impact.privateOwnerReceiptBridge.summary.redactedLinks}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.privateOwnerReceiptBridge.summary.ownerHoldLinks}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.privateOwnerReceiptBridge.summary.privateValuesExposed}</strong></div>
          </div>
          <div className="task-impact-private-bridge-links">
            {impact.privateOwnerReceiptBridge.links.map((link) => (
              <article data-state={link.state} key={link.id}>
                <div className="task-impact-r8-title">
                  <span>{privateReceiptBridgeStateLabels[link.state]}</span>
                  <strong>{link.label}</strong>
                  <em>{link.gate}</em>
                </div>
                <p>{link.bridgeSignal}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{link.owner}</dd></div>
                  <div><dt>Private Alias</dt><dd>{link.privateReceiptAlias}</dd></div>
                  <div><dt>Public Ref</dt><dd>{link.publicReceiptRef}</dd></div>
                </dl>
                <code>{link.redactionPolicy}</code>
                <small>{link.nextAction} / {link.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.privateOwnerReceiptBridge.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.privateOwnerReceiptBridge.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.privateOwnerReceiptBridge.summary.nextAction}</code>
        </div>

        <div className="task-impact-signoff-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Cutover Signoff Diff</h3>
            </div>
            <div>
              <span>{impact.cutoverSignoffDiff.reportVersion}</span>
              <strong>{impact.cutoverSignoffDiff.gate}</strong>
              <code>{impact.cutoverSignoffDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.cutoverSignoffDiff.gate}>{impact.cutoverSignoffDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.cutoverSignoffDiff.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.cutoverSignoffDiff.summary.acceptedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.cutoverSignoffDiff.summary.changedRows}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.cutoverSignoffDiff.summary.requestedRows}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.cutoverSignoffDiff.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-signoff-diff-rows">
            {impact.cutoverSignoffDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{cutoverSignoffDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffReason}</p>
                <dl>
                  <div><dt>Scope</dt><dd>{row.signoffScope}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Before</dt><dd>{row.before}</dd></div>
                  <div><dt>After</dt><dd>{row.after}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.cutoverSignoffDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.cutoverSignoffDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.cutoverSignoffDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-shadow-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Waypoints size={17} aria-hidden="true" />
              <h3>Production Route Shadow Replay</h3>
            </div>
            <div>
              <span>{impact.productionRouteShadowReplay.reportVersion}</span>
              <strong>{impact.productionRouteShadowReplay.gate}</strong>
              <code>{impact.productionRouteShadowReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionRouteShadowReplay.gate}>{impact.productionRouteShadowReplay.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.productionRouteShadowReplay.summary.totalSteps}</strong></div>
            <div><span>Shadow Pass</span><strong data-status="pass">{impact.productionRouteShadowReplay.summary.shadowPassSteps}</strong></div>
            <div><span>Watch</span><strong data-status="review">{impact.productionRouteShadowReplay.summary.watchSteps}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.productionRouteShadowReplay.summary.ownerHoldSteps}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.productionRouteShadowReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-shadow-steps">
            {impact.productionRouteShadowReplay.steps.map((step) => (
              <article data-state={step.state} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{shadowReplayStateLabels[step.state]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.observedSignal}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{step.routeLane}</dd></div>
                  <div><dt>Owner</dt><dd>{step.owner}</dd></div>
                  <div><dt>Mirrored</dt><dd>{step.mirroredReceiptCount}</dd></div>
                </dl>
                <code>{step.shadowCommand}</code>
                <small>{step.nextAction} / {step.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.productionRouteShadowReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.productionRouteShadowReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionRouteShadowReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-drift-audit">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Production Drift Audit</h3>
            </div>
            <div>
              <span>{impact.productionDriftAudit.reportVersion}</span>
              <strong>{impact.productionDriftAudit.gate}</strong>
              <code>{impact.productionDriftAudit.auditId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionDriftAudit.gate}>{impact.productionDriftAudit.gate}</strong></div>
            <div><span>Checks</span><strong>{impact.productionDriftAudit.summary.totalChecks}</strong></div>
            <div><span>In Sync</span><strong data-status="pass">{impact.productionDriftAudit.summary.inSyncChecks}</strong></div>
            <div><span>Drift</span><strong data-status="review">{impact.productionDriftAudit.summary.driftChecks}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.productionDriftAudit.summary.ownerHoldChecks}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.productionDriftAudit.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-drift-checks">
            {impact.productionDriftAudit.checks.map((check) => (
              <article data-state={check.state} key={check.id}>
                <div className="task-impact-r8-title">
                  <span>{productionDriftAuditStateLabels[check.state]}</span>
                  <strong>{check.label}</strong>
                  <em>{check.gate}</em>
                </div>
                <p>{check.driftReason}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{check.owner}</dd></div>
                  <div><dt>Signal</dt><dd>{check.sourceSignal}</dd></div>
                  <div><dt>Expected</dt><dd>{check.expectedState}</dd></div>
                  <div><dt>Observed</dt><dd>{check.observedState}</dd></div>
                </dl>
                <code>{check.nextAction}</code>
                <small>{check.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.productionDriftAudit.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.productionDriftAudit.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionDriftAudit.summary.nextAction}</code>
        </div>

        <div className="task-impact-sla-monitor">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Owner SLA Monitor</h3>
            </div>
            <div>
              <span>{impact.ownerSlaMonitor.reportVersion}</span>
              <strong>{impact.ownerSlaMonitor.gate}</strong>
              <code>{impact.ownerSlaMonitor.monitorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerSlaMonitor.gate}>{impact.ownerSlaMonitor.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerSlaMonitor.summary.totalRows}</strong></div>
            <div><span>Within</span><strong data-status="pass">{impact.ownerSlaMonitor.summary.withinSlaRows}</strong></div>
            <div><span>Due Soon</span><strong data-status="review">{impact.ownerSlaMonitor.summary.dueSoonRows}</strong></div>
            <div><span>Overdue</span><strong data-status="review">{impact.ownerSlaMonitor.summary.overdueRows}</strong></div>
            <div><span>Max Age</span><strong>{impact.ownerSlaMonitor.summary.maxAgeHours}h</strong></div>
          </div>
          <div className="task-impact-sla-rows">
            {impact.ownerSlaMonitor.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerSlaMonitorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.businessRisk}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Receipt</dt><dd>{row.receiptRef}</dd></div>
                  <div><dt>Age</dt><dd>{row.ageHours}h</dd></div>
                  <div><dt>SLA</dt><dd>{row.slaHours}h</dd></div>
                </dl>
                <code>{row.escalation}</code>
                <small>{row.nextAction} / {row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerSlaMonitor.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerSlaMonitor.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerSlaMonitor.summary.nextAction}</code>
        </div>

        <div className="task-impact-freeze-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Release Freeze Replay</h3>
            </div>
            <div>
              <span>{impact.releaseFreezeReplay.reportVersion}</span>
              <strong>{impact.releaseFreezeReplay.gate}</strong>
              <code>{impact.releaseFreezeReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseFreezeReplay.gate}>{impact.releaseFreezeReplay.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.releaseFreezeReplay.summary.totalSteps}</strong></div>
            <div><span>Frozen</span><strong data-status="pass">{impact.releaseFreezeReplay.summary.frozenSteps}</strong></div>
            <div><span>Dry Run</span><strong data-status="pass">{impact.releaseFreezeReplay.summary.dryRunSteps}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseFreezeReplay.summary.ownerHoldSteps}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.releaseFreezeReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-freeze-steps">
            {impact.releaseFreezeReplay.steps.map((step) => (
              <article data-state={step.state} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseFreezeReplayStateLabels[step.state]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.observedEffect}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{step.freezeLane}</dd></div>
                  <div><dt>Owner</dt><dd>{step.owner}</dd></div>
                  <div><dt>Expected</dt><dd>{step.expectedEffect}</dd></div>
                </dl>
                <code>{step.replayCommand}</code>
                <small>{step.nextAction} / {step.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseFreezeReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseFreezeReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseFreezeReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-adjudicator">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Adapter Rollback Adjudicator</h3>
            </div>
            <div>
              <span>{impact.adapterRollbackAdjudicator.reportVersion}</span>
              <strong>{impact.adapterRollbackAdjudicator.gate}</strong>
              <code>{impact.adapterRollbackAdjudicator.adjudicatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.adapterRollbackAdjudicator.gate}>{impact.adapterRollbackAdjudicator.gate}</strong></div>
            <div><span>Decisions</span><strong>{impact.adapterRollbackAdjudicator.summary.totalDecisions}</strong></div>
            <div><span>Approved</span><strong data-status="pass">{impact.adapterRollbackAdjudicator.summary.approvedDecisions}</strong></div>
            <div><span>Disputed</span><strong data-status="review">{impact.adapterRollbackAdjudicator.summary.disputedDecisions}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.adapterRollbackAdjudicator.summary.ownerHoldDecisions}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.adapterRollbackAdjudicator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rollback-decisions">
            {impact.adapterRollbackAdjudicator.decisions.map((decision) => (
              <article data-state={decision.state} key={decision.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackAdjudicatorStateLabels[decision.state]}</span>
                  <strong>{decision.label}</strong>
                  <em>{decision.gate}</em>
                </div>
                <p>{decision.decisionReason}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{decision.rollbackLane}</dd></div>
                  <div><dt>Owner</dt><dd>{decision.owner}</dd></div>
                  <div><dt>Trigger</dt><dd>{decision.triggerEvidence}</dd></div>
                  <div><dt>Action</dt><dd>{decision.adjudicatedAction}</dd></div>
                </dl>
                <code>{decision.nextAction}</code>
                <small>{decision.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.adapterRollbackAdjudicator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.adapterRollbackAdjudicator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.adapterRollbackAdjudicator.summary.nextAction}</code>
        </div>

        <div className="task-impact-dispute-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitBranch size={17} aria-hidden="true" />
              <h3>Receipt Dispute Replay</h3>
            </div>
            <div>
              <span>{impact.receiptDisputeReplay.reportVersion}</span>
              <strong>{impact.receiptDisputeReplay.gate}</strong>
              <code>{impact.receiptDisputeReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.receiptDisputeReplay.gate}>{impact.receiptDisputeReplay.gate}</strong></div>
            <div><span>Cases</span><strong>{impact.receiptDisputeReplay.summary.totalCases}</strong></div>
            <div><span>Resolved</span><strong data-status="pass">{impact.receiptDisputeReplay.summary.resolvedCases}</strong></div>
            <div><span>Counterclaim</span><strong data-status="review">{impact.receiptDisputeReplay.summary.counterclaimCases}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.receiptDisputeReplay.summary.ownerHoldCases}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.receiptDisputeReplay.summary.privateValuesExposed}</strong></div>
          </div>
          <div className="task-impact-dispute-cases">
            {impact.receiptDisputeReplay.cases.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{receiptDisputeReplayStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.ruling}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Receipt</dt><dd>{item.receiptRef}</dd></div>
                  <div><dt>Claim</dt><dd>{item.disputedClaim}</dd></div>
                  <div><dt>Replay</dt><dd>{item.replayFinding}</dd></div>
                </dl>
                <code>{item.nextAction}</code>
                <small>{item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.receiptDisputeReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.receiptDisputeReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.receiptDisputeReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-export-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Audit Export Diff</h3>
            </div>
            <div>
              <span>{impact.auditExportDiff.reportVersion}</span>
              <strong>{impact.auditExportDiff.gate}</strong>
              <code>{impact.auditExportDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.auditExportDiff.gate}>{impact.auditExportDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.auditExportDiff.summary.totalRows}</strong></div>
            <div><span>Unchanged</span><strong data-status="pass">{impact.auditExportDiff.summary.unchangedRows}</strong></div>
            <div><span>Added</span><strong data-status="review">{impact.auditExportDiff.summary.addedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.auditExportDiff.summary.changedRows}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.auditExportDiff.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-export-rows">
            {impact.auditExportDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{auditExportDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffReason}</p>
                <dl>
                  <div><dt>Path</dt><dd>{row.exportPath}</dd></div>
                  <div><dt>Before</dt><dd>{row.before}</dd></div>
                  <div><dt>After</dt><dd>{row.after}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.auditExportDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.auditExportDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.auditExportDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollout-planner">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Rollout Wave Planner</h3>
            </div>
            <div>
              <span>{impact.rolloutWavePlanner.reportVersion}</span>
              <strong>{impact.rolloutWavePlanner.gate}</strong>
              <code>{impact.rolloutWavePlanner.plannerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rolloutWavePlanner.gate}>{impact.rolloutWavePlanner.gate}</strong></div>
            <div><span>Waves</span><strong>{impact.rolloutWavePlanner.summary.totalWaves}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.rolloutWavePlanner.summary.readyWaves}</strong></div>
            <div><span>Watch</span><strong data-status="review">{impact.rolloutWavePlanner.summary.watchWaves}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.rolloutWavePlanner.summary.ownerHoldWaves}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.rolloutWavePlanner.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rollout-waves">
            {impact.rolloutWavePlanner.waves.map((wave) => (
              <article data-state={wave.state} key={wave.id}>
                <div className="task-impact-r8-title">
                  <span>{rolloutWavePlannerStateLabels[wave.state]}</span>
                  <strong>{wave.label}</strong>
                  <em>{wave.gate}</em>
                </div>
                <p>{wave.releaseAction}</p>
                <dl>
                  <div><dt>Wave</dt><dd>{wave.wave}</dd></div>
                  <div><dt>Owner</dt><dd>{wave.owner}</dd></div>
                  <div><dt>Scope</dt><dd>{wave.scope}</dd></div>
                  <div><dt>Risk</dt><dd>{wave.riskBudget}</dd></div>
                </dl>
                <code>{wave.nextAction}</code>
                <small>{wave.entryCriteria} / {wave.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rolloutWavePlanner.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rolloutWavePlanner.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rolloutWavePlanner.summary.nextAction}</code>
        </div>

        <div className="task-impact-incident-notebook">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Incident Replay Notebook</h3>
            </div>
            <div>
              <span>{impact.incidentReplayNotebook.reportVersion}</span>
              <strong>{impact.incidentReplayNotebook.gate}</strong>
              <code>{impact.incidentReplayNotebook.notebookId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.incidentReplayNotebook.gate}>{impact.incidentReplayNotebook.gate}</strong></div>
            <div><span>Cases</span><strong>{impact.incidentReplayNotebook.summary.totalCases}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.incidentReplayNotebook.summary.replayedCases}</strong></div>
            <div><span>Open</span><strong data-status="review">{impact.incidentReplayNotebook.summary.openQuestionCases}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.incidentReplayNotebook.summary.ownerHoldCases}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.incidentReplayNotebook.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-incident-cases">
            {impact.incidentReplayNotebook.cases.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{incidentReplayNotebookStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.outcome}</p>
                <dl>
                  <div><dt>Incident</dt><dd>{item.incidentRef}</dd></div>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Trigger</dt><dd>{item.trigger}</dd></div>
                  <div><dt>Replay</dt><dd>{item.replayCommand}</dd></div>
                </dl>
                <code>{item.nextAction}</code>
                <small>{item.rootCauseHypothesis} / {item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.incidentReplayNotebook.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.incidentReplayNotebook.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.incidentReplayNotebook.summary.nextAction}</code>
        </div>

        <div className="task-impact-exception-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Owner Exception Ledger</h3>
            </div>
            <div>
              <span>{impact.ownerExceptionLedger.reportVersion}</span>
              <strong>{impact.ownerExceptionLedger.gate}</strong>
              <code>{impact.ownerExceptionLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerExceptionLedger.gate}>{impact.ownerExceptionLedger.gate}</strong></div>
            <div><span>Exceptions</span><strong>{impact.ownerExceptionLedger.summary.totalExceptions}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.ownerExceptionLedger.summary.acceptedExceptions}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.ownerExceptionLedger.summary.requestedExceptions}</strong></div>
            <div><span>Expired</span><strong data-status="review">{impact.ownerExceptionLedger.summary.expiredExceptions}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.ownerExceptionLedger.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-exception-entries">
            {impact.ownerExceptionLedger.entries.map((entry) => (
              <article data-state={entry.state} key={entry.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerExceptionLedgerStateLabels[entry.state]}</span>
                  <strong>{entry.label}</strong>
                  <em>{entry.gate}</em>
                </div>
                <p>{entry.reason}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{entry.owner}</dd></div>
                  <div><dt>Scope</dt><dd>{entry.exceptionScope}</dd></div>
                  <div><dt>Expires</dt><dd>{entry.expiresAt}</dd></div>
                  <div><dt>Allowed</dt><dd>{entry.allowedAction}</dd></div>
                </dl>
                <code>{entry.nextAction}</code>
                <small>{entry.publicRef} / {entry.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerExceptionLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerExceptionLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerExceptionLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-budget">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Rollback Budget Simulator</h3>
            </div>
            <div>
              <span>{impact.rollbackBudgetSimulator.reportVersion}</span>
              <strong>{impact.rollbackBudgetSimulator.gate}</strong>
              <code>{impact.rollbackBudgetSimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackBudgetSimulator.gate}>{impact.rollbackBudgetSimulator.gate}</strong></div>
            <div><span>Lines</span><strong>{impact.rollbackBudgetSimulator.summary.totalLines}</strong></div>
            <div><span>Within</span><strong data-status="pass">{impact.rollbackBudgetSimulator.summary.withinBudgetLines}</strong></div>
            <div><span>Near</span><strong data-status="review">{impact.rollbackBudgetSimulator.summary.nearLimitLines}</strong></div>
            <div><span>Over</span><strong data-status="review">{impact.rollbackBudgetSimulator.summary.overBudgetLines}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.rollbackBudgetSimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-budget-lines">
            {impact.rollbackBudgetSimulator.lines.map((line) => (
              <article data-state={line.state} key={line.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackBudgetSimulatorStateLabels[line.state]}</span>
                  <strong>{line.label}</strong>
                  <em>{line.gate}</em>
                </div>
                <p>{line.riskDriver}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{line.owner}</dd></div>
                  <div><dt>Scope</dt><dd>{line.rollbackScope}</dd></div>
                  <div><dt>Budget</dt><dd>{line.budgetLimit}</dd></div>
                  <div><dt>Cost</dt><dd>{line.estimatedCost}</dd></div>
                  <div><dt>Remain</dt><dd>{line.remainingBudget}</dd></div>
                  <div><dt>Allowed</dt><dd>{line.allowedAction}</dd></div>
                </dl>
                <code>{line.nextAction}</code>
                <small>{line.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackBudgetSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackBudgetSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackBudgetSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-confidence-heatmap">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Release Confidence Heatmap</h3>
            </div>
            <div>
              <span>{impact.releaseConfidenceHeatmap.reportVersion}</span>
              <strong>{impact.releaseConfidenceHeatmap.gate}</strong>
              <code>{impact.releaseConfidenceHeatmap.heatmapId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseConfidenceHeatmap.gate}>{impact.releaseConfidenceHeatmap.gate}</strong></div>
            <div><span>Cells</span><strong>{impact.releaseConfidenceHeatmap.summary.totalCells}</strong></div>
            <div><span>High</span><strong data-status="pass">{impact.releaseConfidenceHeatmap.summary.highCells}</strong></div>
            <div><span>Medium</span><strong data-status="review">{impact.releaseConfidenceHeatmap.summary.mediumCells}</strong></div>
            <div><span>Low</span><strong data-status="review">{impact.releaseConfidenceHeatmap.summary.lowCells}</strong></div>
            <div><span>Min</span><strong>{impact.releaseConfidenceHeatmap.summary.minConfidenceScore}</strong></div>
          </div>
          <div className="task-impact-confidence-cells">
            {impact.releaseConfidenceHeatmap.cells.map((cell) => (
              <article data-state={cell.state} key={cell.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseConfidenceHeatmapStateLabels[cell.state]}</span>
                  <strong>{cell.label}</strong>
                  <em>{cell.gate}</em>
                </div>
                <p>{cell.confidenceReason}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{cell.lane}</dd></div>
                  <div><dt>Signal</dt><dd>{cell.signal}</dd></div>
                  <div><dt>Score</dt><dd>{cell.confidenceScore}</dd></div>
                  <div><dt>Owner</dt><dd>{cell.owner}</dd></div>
                  <div><dt>Action</dt><dd>{cell.recommendedAction}</dd></div>
                </dl>
                <code>{cell.nextAction}</code>
                <small>{cell.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseConfidenceHeatmap.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseConfidenceHeatmap.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseConfidenceHeatmap.summary.nextAction}</code>
        </div>

        <div className="task-impact-aging-policy">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Evidence Aging Policy</h3>
            </div>
            <div>
              <span>{impact.evidenceAgingPolicy.reportVersion}</span>
              <strong>{impact.evidenceAgingPolicy.gate}</strong>
              <code>{impact.evidenceAgingPolicy.policyId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.evidenceAgingPolicy.gate}>{impact.evidenceAgingPolicy.gate}</strong></div>
            <div><span>Records</span><strong>{impact.evidenceAgingPolicy.summary.totalRecords}</strong></div>
            <div><span>Fresh</span><strong data-status="pass">{impact.evidenceAgingPolicy.summary.freshRecords}</strong></div>
            <div><span>Due Soon</span><strong data-status="review">{impact.evidenceAgingPolicy.summary.dueSoonRecords}</strong></div>
            <div><span>Expired</span><strong data-status="review">{impact.evidenceAgingPolicy.summary.expiredRecords}</strong></div>
            <div><span>Max Age</span><strong>{impact.evidenceAgingPolicy.summary.maxAgeHours}h</strong></div>
          </div>
          <div className="task-impact-aging-records">
            {impact.evidenceAgingPolicy.records.map((record) => (
              <article data-state={record.state} key={record.id}>
                <div className="task-impact-r8-title">
                  <span>{evidenceAgingPolicyStateLabels[record.state]}</span>
                  <strong>{record.label}</strong>
                  <em>{record.gate}</em>
                </div>
                <p>{record.staleRisk}</p>
                <dl>
                  <div><dt>Evidence</dt><dd>{record.evidenceRef}</dd></div>
                  <div><dt>Owner</dt><dd>{record.owner}</dd></div>
                  <div><dt>Age</dt><dd>{record.ageHours}h</dd></div>
                  <div><dt>Expires</dt><dd>{record.expiresAt}</dd></div>
                  <div><dt>Policy</dt><dd>{record.refreshPolicy}</dd></div>
                </dl>
                <code>{record.nextAction}</code>
                <small>{record.generatedAt} / {record.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.evidenceAgingPolicy.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.evidenceAgingPolicy.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.evidenceAgingPolicy.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-rehearsal">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitBranch size={17} aria-hidden="true" />
              <h3>Release Rollback Rehearsal</h3>
            </div>
            <div>
              <span>{impact.releaseRollbackRehearsal.reportVersion}</span>
              <strong>{impact.releaseRollbackRehearsal.gate}</strong>
              <code>{impact.releaseRollbackRehearsal.rehearsalId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseRollbackRehearsal.gate}>{impact.releaseRollbackRehearsal.gate}</strong></div>
            <div><span>Steps</span><strong>{impact.releaseRollbackRehearsal.summary.totalSteps}</strong></div>
            <div><span>Passed</span><strong data-status="pass">{impact.releaseRollbackRehearsal.summary.passedSteps}</strong></div>
            <div><span>Watch</span><strong data-status="review">{impact.releaseRollbackRehearsal.summary.watchSteps}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseRollbackRehearsal.summary.ownerHoldSteps}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.releaseRollbackRehearsal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rehearsal-steps">
            {impact.releaseRollbackRehearsal.steps.map((step) => (
              <article data-state={step.state} key={step.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseRollbackRehearsalStateLabels[step.state]}</span>
                  <strong>{step.label}</strong>
                  <em>{step.gate}</em>
                </div>
                <p>{step.rollbackAction}</p>
                <dl>
                  <div><dt>Phase</dt><dd>{step.phase}</dd></div>
                  <div><dt>Owner</dt><dd>{step.owner}</dd></div>
                  <div><dt>Precondition</dt><dd>{step.precondition}</dd></div>
                  <div><dt>Receipt</dt><dd>{step.expectedReceipt}</dd></div>
                </dl>
                <code>{step.nextAction}</code>
                <small>{step.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseRollbackRehearsal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseRollbackRehearsal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseRollbackRehearsal.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-quorum">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Owner Quorum Simulator</h3>
            </div>
            <div>
              <span>{impact.ownerQuorumSimulator.reportVersion}</span>
              <strong>{impact.ownerQuorumSimulator.gate}</strong>
              <code>{impact.ownerQuorumSimulator.quorumId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerQuorumSimulator.gate}>{impact.ownerQuorumSimulator.gate}</strong></div>
            <div><span>Votes</span><strong>{impact.ownerQuorumSimulator.summary.totalVotes}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.ownerQuorumSimulator.summary.acceptedVotes}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.ownerQuorumSimulator.summary.requestedVotes}</strong></div>
            <div><span>Missing</span><strong data-status="review">{impact.ownerQuorumSimulator.summary.missingVotes}</strong></div>
            <div><span>Quorum</span><strong>{impact.ownerQuorumSimulator.summary.quorumAccepted}/{impact.ownerQuorumSimulator.summary.quorumNeeded}</strong></div>
          </div>
          <div className="task-impact-quorum-votes">
            {impact.ownerQuorumSimulator.votes.map((vote) => (
              <article data-state={vote.state} key={vote.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerQuorumSimulatorStateLabels[vote.state]}</span>
                  <strong>{vote.label}</strong>
                  <em>{vote.gate}</em>
                </div>
                <p>{vote.signal}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{vote.owner}</dd></div>
                  <div><dt>Role</dt><dd>{vote.role}</dd></div>
                  <div><dt>Required</dt><dd>{vote.required ? "yes" : "no"}</dd></div>
                  <div><dt>Decision</dt><dd>{vote.decisionRef}</dd></div>
                </dl>
                <code>{vote.nextAction}</code>
                <small>{vote.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerQuorumSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerQuorumSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerQuorumSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-stale-refresh">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Cable size={17} aria-hidden="true" />
              <h3>Stale Evidence Auto-Refresh Queue</h3>
            </div>
            <div>
              <span>{impact.staleEvidenceAutoRefreshQueue.reportVersion}</span>
              <strong>{impact.staleEvidenceAutoRefreshQueue.gate}</strong>
              <code>{impact.staleEvidenceAutoRefreshQueue.queueId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.staleEvidenceAutoRefreshQueue.gate}>{impact.staleEvidenceAutoRefreshQueue.gate}</strong></div>
            <div><span>Jobs</span><strong>{impact.staleEvidenceAutoRefreshQueue.summary.totalJobs}</strong></div>
            <div><span>Refreshed</span><strong data-status="pass">{impact.staleEvidenceAutoRefreshQueue.summary.refreshedJobs}</strong></div>
            <div><span>Queued</span><strong data-status="review">{impact.staleEvidenceAutoRefreshQueue.summary.queuedJobs}</strong></div>
            <div><span>Owner</span><strong data-status="review">{impact.staleEvidenceAutoRefreshQueue.summary.ownerRequiredJobs}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.staleEvidenceAutoRefreshQueue.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-refresh-jobs">
            {impact.staleEvidenceAutoRefreshQueue.jobs.map((job) => (
              <article data-state={job.state} key={job.id}>
                <div className="task-impact-r8-title">
                  <span>{staleEvidenceAutoRefreshQueueStateLabels[job.state]}</span>
                  <strong>{job.label}</strong>
                  <em>{job.gate}</em>
                </div>
                <p>{job.reason}</p>
                <dl>
                  <div><dt>Evidence</dt><dd>{job.evidenceRef}</dd></div>
                  <div><dt>Adapter</dt><dd>{job.refreshAdapter}</dd></div>
                  <div><dt>Owner</dt><dd>{job.owner}</dd></div>
                  <div><dt>Scheduled</dt><dd>{job.scheduledAt}</dd></div>
                </dl>
                <code>{job.nextAction}</code>
                <small>{job.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.staleEvidenceAutoRefreshQueue.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.staleEvidenceAutoRefreshQueue.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.staleEvidenceAutoRefreshQueue.summary.nextAction}</code>
        </div>

        <div className="task-impact-decision-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Release Decision Board</h3>
            </div>
            <div>
              <span>{impact.releaseDecisionBoard.reportVersion}</span>
              <strong>{impact.releaseDecisionBoard.gate}</strong>
              <code>{impact.releaseDecisionBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseDecisionBoard.gate}>{impact.releaseDecisionBoard.gate}</strong></div>
            <div><span>Lanes</span><strong>{impact.releaseDecisionBoard.summary.totalLanes}</strong></div>
            <div><span>Approved</span><strong data-status="pass">{impact.releaseDecisionBoard.summary.approvedLanes}</strong></div>
            <div><span>Conditional</span><strong data-status="review">{impact.releaseDecisionBoard.summary.conditionalLanes}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.releaseDecisionBoard.summary.deferredLanes}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.releaseDecisionBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-decision-lanes">
            {impact.releaseDecisionBoard.lanes.map((lane) => (
              <article data-state={lane.state} key={lane.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseDecisionBoardStateLabels[lane.state]}</span>
                  <strong>{lane.label}</strong>
                  <em>{lane.gate}</em>
                </div>
                <p>{lane.decisionReason}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{lane.lane}</dd></div>
                  <div><dt>Decision</dt><dd>{lane.releaseDecision}</dd></div>
                  <div><dt>Owner</dt><dd>{lane.requiredOwnerState}</dd></div>
                  <div><dt>Evidence</dt><dd>{lane.requiredEvidenceState}</dd></div>
                </dl>
                <code>{lane.nextAction}</code>
                <small>{lane.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseDecisionBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseDecisionBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseDecisionBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-sla-escalation">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Owner SLA Escalation Queue</h3>
            </div>
            <div>
              <span>{impact.ownerSlaEscalationQueue.reportVersion}</span>
              <strong>{impact.ownerSlaEscalationQueue.gate}</strong>
              <code>{impact.ownerSlaEscalationQueue.queueId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerSlaEscalationQueue.gate}>{impact.ownerSlaEscalationQueue.gate}</strong></div>
            <div><span>Items</span><strong>{impact.ownerSlaEscalationQueue.summary.totalItems}</strong></div>
            <div><span>Within</span><strong data-status="pass">{impact.ownerSlaEscalationQueue.summary.withinSlaItems}</strong></div>
            <div><span>Due</span><strong data-status="review">{impact.ownerSlaEscalationQueue.summary.dueTodayItems}</strong></div>
            <div><span>Escalated</span><strong data-status="review">{impact.ownerSlaEscalationQueue.summary.escalatedItems}</strong></div>
            <div><span>Max Age</span><strong>{impact.ownerSlaEscalationQueue.summary.maxElapsedHours}h</strong></div>
          </div>
          <div className="task-impact-sla-items">
            {impact.ownerSlaEscalationQueue.items.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerSlaEscalationQueueStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.blocker}</p>
                <dl>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Role</dt><dd>{item.role}</dd></div>
                  <div><dt>Due</dt><dd>{item.dueAt}</dd></div>
                  <div><dt>Elapsed</dt><dd>{item.elapsedHours}h</dd></div>
                  <div><dt>Escalate</dt><dd>{item.escalationPath}</dd></div>
                </dl>
                <code>{item.nextAction}</code>
                <small>{item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerSlaEscalationQueue.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerSlaEscalationQueue.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerSlaEscalationQueue.summary.nextAction}</code>
        </div>

        <div className="task-impact-retention-purge">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Evidence Retention Purge Rehearsal</h3>
            </div>
            <div>
              <span>{impact.evidenceRetentionPurgeRehearsal.reportVersion}</span>
              <strong>{impact.evidenceRetentionPurgeRehearsal.gate}</strong>
              <code>{impact.evidenceRetentionPurgeRehearsal.rehearsalId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.evidenceRetentionPurgeRehearsal.gate}>{impact.evidenceRetentionPurgeRehearsal.gate}</strong></div>
            <div><span>Records</span><strong>{impact.evidenceRetentionPurgeRehearsal.summary.totalRecords}</strong></div>
            <div><span>Retained</span><strong data-status="pass">{impact.evidenceRetentionPurgeRehearsal.summary.retainedRecords}</strong></div>
            <div><span>Purge</span><strong data-status="review">{impact.evidenceRetentionPurgeRehearsal.summary.purgeQueuedRecords}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.evidenceRetentionPurgeRehearsal.summary.ownerHoldRecords}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.evidenceRetentionPurgeRehearsal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-purge-records">
            {impact.evidenceRetentionPurgeRehearsal.records.map((record) => (
              <article data-state={record.state} key={record.id}>
                <div className="task-impact-r8-title">
                  <span>{evidenceRetentionPurgeRehearsalStateLabels[record.state]}</span>
                  <strong>{record.label}</strong>
                  <em>{record.gate}</em>
                </div>
                <p>{record.purgeAction}</p>
                <dl>
                  <div><dt>Evidence</dt><dd>{record.evidenceRef}</dd></div>
                  <div><dt>Class</dt><dd>{record.retentionClass}</dd></div>
                  <div><dt>Owner</dt><dd>{record.owner}</dd></div>
                  <div><dt>Until</dt><dd>{record.retentionUntil}</dd></div>
                </dl>
                <code>{record.nextAction}</code>
                <small>{record.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.evidenceRetentionPurgeRehearsal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.evidenceRetentionPurgeRehearsal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.evidenceRetentionPurgeRehearsal.summary.nextAction}</code>
        </div>

        <div className="task-impact-evidence-compactor">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Release Evidence Compactor</h3>
            </div>
            <div>
              <span>{impact.releaseEvidenceCompactor.reportVersion}</span>
              <strong>{impact.releaseEvidenceCompactor.gate}</strong>
              <code>{impact.releaseEvidenceCompactor.compactorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseEvidenceCompactor.gate}>{impact.releaseEvidenceCompactor.gate}</strong></div>
            <div><span>Bundles</span><strong>{impact.releaseEvidenceCompactor.summary.totalBundles}</strong></div>
            <div><span>Compacted</span><strong data-status="pass">{impact.releaseEvidenceCompactor.summary.compactedBundles}</strong></div>
            <div><span>Kept</span><strong data-status="review">{impact.releaseEvidenceCompactor.summary.keptBundles}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseEvidenceCompactor.summary.ownerHoldBundles}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.releaseEvidenceCompactor.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-compactor-bundles">
            {impact.releaseEvidenceCompactor.bundles.map((bundle) => (
              <article data-state={bundle.state} key={bundle.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseEvidenceCompactorStateLabels[bundle.state]}</span>
                  <strong>{bundle.label}</strong>
                  <em>{bundle.gate}</em>
                </div>
                <p>{bundle.compactionRule}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{bundle.sourceLane}</dd></div>
                  <div><dt>Original</dt><dd>{bundle.originalArtifacts}</dd></div>
                  <div><dt>Compact</dt><dd>{bundle.compactedArtifacts}</dd></div>
                  <div><dt>Owner</dt><dd>{bundle.owner}</dd></div>
                </dl>
                <code>{bundle.nextAction}</code>
                <small>{bundle.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseEvidenceCompactor.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseEvidenceCompactor.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseEvidenceCompactor.summary.nextAction}</code>
        </div>

        <div className="task-impact-packet-lockfile">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Reviewer Packet Lockfile</h3>
            </div>
            <div>
              <span>{impact.reviewerPacketLockfile.reportVersion}</span>
              <strong>{impact.reviewerPacketLockfile.gate}</strong>
              <code>{impact.reviewerPacketLockfile.lockfileId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.reviewerPacketLockfile.gate}>{impact.reviewerPacketLockfile.gate}</strong></div>
            <div><span>Entries</span><strong>{impact.reviewerPacketLockfile.summary.totalEntries}</strong></div>
            <div><span>Locked</span><strong data-status="pass">{impact.reviewerPacketLockfile.summary.lockedEntries}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.reviewerPacketLockfile.summary.changedEntries}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.reviewerPacketLockfile.summary.ownerHoldEntries}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.reviewerPacketLockfile.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-lockfile-entries">
            {impact.reviewerPacketLockfile.entries.map((entry) => (
              <article data-state={entry.state} key={entry.id}>
                <div className="task-impact-r8-title">
                  <span>{reviewerPacketLockfileStateLabels[entry.state]}</span>
                  <strong>{entry.label}</strong>
                  <em>{entry.gate}</em>
                </div>
                <p>{entry.lockReason}</p>
                <dl>
                  <div><dt>Path</dt><dd>{entry.path}</dd></div>
                  <div><dt>Version</dt><dd>{entry.version}</dd></div>
                  <div><dt>Owner</dt><dd>{entry.owner}</dd></div>
                  <div><dt>Hash</dt><dd>{entry.checksum}</dd></div>
                </dl>
                <code>{entry.nextAction}</code>
                <small>{entry.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.reviewerPacketLockfile.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.reviewerPacketLockfile.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.reviewerPacketLockfile.summary.nextAction}</code>
        </div>

        <div className="task-impact-exception-closeout">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Production Readiness Exception Closeout</h3>
            </div>
            <div>
              <span>{impact.productionReadinessExceptionCloseout.reportVersion}</span>
              <strong>{impact.productionReadinessExceptionCloseout.gate}</strong>
              <code>{impact.productionReadinessExceptionCloseout.closeoutId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.productionReadinessExceptionCloseout.gate}>{impact.productionReadinessExceptionCloseout.gate}</strong></div>
            <div><span>Cases</span><strong>{impact.productionReadinessExceptionCloseout.summary.totalCases}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.productionReadinessExceptionCloseout.summary.closedCases}</strong></div>
            <div><span>Owner</span><strong data-status="review">{impact.productionReadinessExceptionCloseout.summary.needsOwnerCases}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.productionReadinessExceptionCloseout.summary.deferredCases}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.productionReadinessExceptionCloseout.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closeout-cases">
            {impact.productionReadinessExceptionCloseout.cases.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{productionReadinessExceptionCloseoutStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.productionReadinessEffect}</p>
                <dl>
                  <div><dt>Exception</dt><dd>{item.exceptionRef}</dd></div>
                  <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                  <div><dt>Rule</dt><dd>{item.closeoutRule}</dd></div>
                  <div><dt>Evidence</dt><dd>{item.requiredEvidence}</dd></div>
                </dl>
                <code>{item.nextAction}</code>
                <small>{item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.productionReadinessExceptionCloseout.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.productionReadinessExceptionCloseout.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.productionReadinessExceptionCloseout.summary.nextAction}</code>
        </div>

        <div className="task-impact-packet-diff-viewer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Locked Packet Diff Viewer</h3>
            </div>
            <div>
              <span>{impact.lockedPacketDiffViewer.reportVersion}</span>
              <strong>{impact.lockedPacketDiffViewer.gate}</strong>
              <code>{impact.lockedPacketDiffViewer.viewerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.lockedPacketDiffViewer.gate}>{impact.lockedPacketDiffViewer.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.lockedPacketDiffViewer.summary.totalRows}</strong></div>
            <div><span>Unchanged</span><strong data-status="pass">{impact.lockedPacketDiffViewer.summary.unchangedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.lockedPacketDiffViewer.summary.changedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.lockedPacketDiffViewer.summary.ownerHoldRows}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.lockedPacketDiffViewer.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-packet-diff-rows">
            {impact.lockedPacketDiffViewer.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{lockedPacketDiffViewerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffReason}</p>
                <dl>
                  <div><dt>Entry</dt><dd>{row.lockedEntryId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Before</dt><dd>{row.beforeVersion}</dd></div>
                  <div><dt>After</dt><dd>{row.afterVersion}</dd></div>
                  <div><dt>Before Hash</dt><dd>{row.beforeChecksum}</dd></div>
                  <div><dt>After Hash</dt><dd>{row.afterChecksum}</dd></div>
                </dl>
                <code>{row.reviewerAction}</code>
                <small>{row.path} / {row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.lockedPacketDiffViewer.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.lockedPacketDiffViewer.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.lockedPacketDiffViewer.summary.nextAction}</code>
        </div>

        <div className="task-impact-exception-burndown">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Exception Burn-Down Dashboard</h3>
            </div>
            <div>
              <span>{impact.exceptionBurnDownDashboard.reportVersion}</span>
              <strong>{impact.exceptionBurnDownDashboard.gate}</strong>
              <code>{impact.exceptionBurnDownDashboard.dashboardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.exceptionBurnDownDashboard.gate}>{impact.exceptionBurnDownDashboard.gate}</strong></div>
            <div><span>Exceptions</span><strong>{impact.exceptionBurnDownDashboard.summary.totalExceptions}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.exceptionBurnDownDashboard.summary.closedExceptions}</strong></div>
            <div><span>Remaining</span><strong data-status="review">{impact.exceptionBurnDownDashboard.summary.remainingExceptions}</strong></div>
            <div><span>Owner</span><strong data-status="review">{impact.exceptionBurnDownDashboard.summary.needsOwnerExceptions}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.exceptionBurnDownDashboard.summary.deferredExceptions}</strong></div>
          </div>
          <div className="task-impact-burndown-trend">
            {impact.exceptionBurnDownDashboard.trend.map((point) => (
              <article key={point.label}>
                <span>{point.label}</span>
                <strong>{point.remainingExceptions}</strong>
                <p>{point.closedExceptions} closed / {point.needsOwnerExceptions} owner / {point.deferredExceptions} deferred</p>
              </article>
            ))}
          </div>
          <div className="task-impact-burndown-lanes">
            {impact.exceptionBurnDownDashboard.lanes.map((lane) => (
              <article data-state={lane.state} key={lane.id}>
                <div className="task-impact-r8-title">
                  <span>{exceptionBurnDownDashboardStateLabels[lane.state]}</span>
                  <strong>{lane.label}</strong>
                  <em>{lane.gate}</em>
                </div>
                <p>{lane.burnDownSignal}</p>
                <dl>
                  <div><dt>Exception</dt><dd>{lane.exceptionRef}</dd></div>
                  <div><dt>Owner</dt><dd>{lane.owner}</dd></div>
                  <div><dt>Due</dt><dd>{lane.dueAt}</dd></div>
                  <div><dt>Remaining</dt><dd>{lane.remainingWork}</dd></div>
                </dl>
                <code>{lane.nextAction}</code>
                <small>{lane.requiredEvidence} / {lane.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.exceptionBurnDownDashboard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.exceptionBurnDownDashboard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.exceptionBurnDownDashboard.summary.nextAction}</code>
        </div>

        <div className="task-impact-acceptance-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Reviewer Acceptance Replay</h3>
            </div>
            <div>
              <span>{impact.reviewerAcceptanceReplay.reportVersion}</span>
              <strong>{impact.reviewerAcceptanceReplay.gate}</strong>
              <code>{impact.reviewerAcceptanceReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.reviewerAcceptanceReplay.gate}>{impact.reviewerAcceptanceReplay.gate}</strong></div>
            <div><span>Replays</span><strong>{impact.reviewerAcceptanceReplay.summary.totalReplays}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.reviewerAcceptanceReplay.summary.acceptedReplays}</strong></div>
            <div><span>Replay Req</span><strong data-status="review">{impact.reviewerAcceptanceReplay.summary.replayRequiredReplays}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.reviewerAcceptanceReplay.summary.ownerHoldReplays}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.reviewerAcceptanceReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-acceptance-replays">
            {impact.reviewerAcceptanceReplay.items.map((item) => (
              <article data-state={item.state} key={item.id}>
                <div className="task-impact-r8-title">
                  <span>{reviewerAcceptanceReplayStateLabels[item.state]}</span>
                  <strong>{item.label}</strong>
                  <em>{item.gate}</em>
                </div>
                <p>{item.replayResult}</p>
                <dl>
                  <div><dt>Entry</dt><dd>{item.packetEntryId}</dd></div>
                  <div><dt>Reviewer</dt><dd>{item.reviewer}</dd></div>
                  <div><dt>Source</dt><dd>{item.acceptanceSource}</dd></div>
                  <div><dt>Input</dt><dd>{item.requiredInput}</dd></div>
                </dl>
                <code>{item.nextAction}</code>
                <small>{item.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.reviewerAcceptanceReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.reviewerAcceptanceReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.reviewerAcceptanceReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-accepted-freeze">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Accepted Packet Freeze</h3>
            </div>
            <div>
              <span>{impact.acceptedPacketFreeze.reportVersion}</span>
              <strong>{impact.acceptedPacketFreeze.gate}</strong>
              <code>{impact.acceptedPacketFreeze.freezeId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.acceptedPacketFreeze.gate}>{impact.acceptedPacketFreeze.gate}</strong></div>
            <div><span>Entries</span><strong>{impact.acceptedPacketFreeze.summary.totalEntries}</strong></div>
            <div><span>Frozen</span><strong data-status="pass">{impact.acceptedPacketFreeze.summary.frozenEntries}</strong></div>
            <div><span>Pending</span><strong data-status="review">{impact.acceptedPacketFreeze.summary.pendingDiffEntries}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.acceptedPacketFreeze.summary.ownerHoldEntries}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.acceptedPacketFreeze.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-freeze-entries">
            {impact.acceptedPacketFreeze.entries.map((entry) => (
              <article data-state={entry.state} key={entry.id}>
                <div className="task-impact-r8-title">
                  <span>{acceptedPacketFreezeStateLabels[entry.state]}</span>
                  <strong>{entry.label}</strong>
                  <em>{entry.gate}</em>
                </div>
                <p>{entry.freezeResult}</p>
                <dl>
                  <div><dt>Entry</dt><dd>{entry.packetEntryId}</dd></div>
                  <div><dt>Owner</dt><dd>{entry.owner}</dd></div>
                  <div><dt>Scope</dt><dd>{entry.freezeScope}</dd></div>
                  <div><dt>Rule</dt><dd>{entry.freezeRule}</dd></div>
                  <div><dt>Checksum</dt><dd>{entry.acceptedChecksum}</dd></div>
                </dl>
                <code>{entry.nextAction}</code>
                <small>{entry.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.acceptedPacketFreeze.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.acceptedPacketFreeze.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.acceptedPacketFreeze.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-response-importer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Cable size={17} aria-hidden="true" />
              <h3>Exception Owner Response Importer</h3>
            </div>
            <div>
              <span>{impact.exceptionOwnerResponseImporter.reportVersion}</span>
              <strong>{impact.exceptionOwnerResponseImporter.gate}</strong>
              <code>{impact.exceptionOwnerResponseImporter.importerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.exceptionOwnerResponseImporter.gate}>{impact.exceptionOwnerResponseImporter.gate}</strong></div>
            <div><span>Responses</span><strong>{impact.exceptionOwnerResponseImporter.summary.totalResponses}</strong></div>
            <div><span>Imported</span><strong data-status="pass">{impact.exceptionOwnerResponseImporter.summary.importedResponses}</strong></div>
            <div><span>Waiting</span><strong data-status="review">{impact.exceptionOwnerResponseImporter.summary.waitingOwnerResponses}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.exceptionOwnerResponseImporter.summary.deferredResponses}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.exceptionOwnerResponseImporter.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-owner-responses">
            {impact.exceptionOwnerResponseImporter.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{exceptionOwnerResponseImporterStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.importResult}</p>
                <dl>
                  <div><dt>Lane</dt><dd>{row.exceptionLaneId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Source</dt><dd>{row.responseSource}</dd></div>
                  <div><dt>Rule</dt><dd>{row.importRule}</dd></div>
                  <div><dt>Evidence</dt><dd>{row.requiredEvidence}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.exceptionOwnerResponseImporter.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.exceptionOwnerResponseImporter.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.exceptionOwnerResponseImporter.summary.nextAction}</code>
        </div>

        <div className="task-impact-readiness-replay-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Release Readiness Replay Diff</h3>
            </div>
            <div>
              <span>{impact.releaseReadinessReplayDiff.reportVersion}</span>
              <strong>{impact.releaseReadinessReplayDiff.gate}</strong>
              <code>{impact.releaseReadinessReplayDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseReadinessReplayDiff.gate}>{impact.releaseReadinessReplayDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseReadinessReplayDiff.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.releaseReadinessReplayDiff.summary.unchangedReadyRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.releaseReadinessReplayDiff.summary.changedReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseReadinessReplayDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.releaseReadinessReplayDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-readiness-diff-rows">
            {impact.releaseReadinessReplayDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseReadinessReplayDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.readinessEffect}</p>
                <dl>
                  <div><dt>Source</dt><dd>{row.sourceId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Gate</dt><dd>{row.beforeGate}{" -> "}{row.afterGate}</dd></div>
                  <div><dt>Reason</dt><dd>{row.diffReason}</dd></div>
                  <div><dt>Action</dt><dd>{row.requiredAction}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseReadinessReplayDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseReadinessReplayDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseReadinessReplayDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-promotion-gate">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Frozen Packet Promotion Gate</h3>
            </div>
            <div>
              <span>{impact.frozenPacketPromotionGate.reportVersion}</span>
              <strong>{impact.frozenPacketPromotionGate.gate}</strong>
              <code>{impact.frozenPacketPromotionGate.gateId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.frozenPacketPromotionGate.gate}>{impact.frozenPacketPromotionGate.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.frozenPacketPromotionGate.summary.totalRows}</strong></div>
            <div><span>Promoted</span><strong data-status="pass">{impact.frozenPacketPromotionGate.summary.promotedRows}</strong></div>
            <div><span>Diff Blocked</span><strong data-status="review">{impact.frozenPacketPromotionGate.summary.diffBlockedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.frozenPacketPromotionGate.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.frozenPacketPromotionGate.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-promotion-rows">
            {impact.frozenPacketPromotionGate.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{frozenPacketPromotionGateStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.promotionResult}</p>
                <dl>
                  <div><dt>Entry</dt><dd>{row.packetEntryId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.promotionLane}</dd></div>
                  <div><dt>Rule</dt><dd>{row.promotionRule}</dd></div>
                  <div><dt>Source</dt><dd>{row.sourceReadinessRowId}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.frozenPacketPromotionGate.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.frozenPacketPromotionGate.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.frozenPacketPromotionGate.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-sla-reconciliation">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Owner Response SLA Reconciliation</h3>
            </div>
            <div>
              <span>{impact.ownerResponseSlaReconciliation.reportVersion}</span>
              <strong>{impact.ownerResponseSlaReconciliation.gate}</strong>
              <code>{impact.ownerResponseSlaReconciliation.reconciliationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerResponseSlaReconciliation.gate}>{impact.ownerResponseSlaReconciliation.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerResponseSlaReconciliation.summary.totalRows}</strong></div>
            <div><span>Reconciled</span><strong data-status="pass">{impact.ownerResponseSlaReconciliation.summary.reconciledRows}</strong></div>
            <div><span>Overdue</span><strong data-status="review">{impact.ownerResponseSlaReconciliation.summary.overdueRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.ownerResponseSlaReconciliation.summary.deferredRows}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.ownerResponseSlaReconciliation.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-owner-sla-rows">
            {impact.ownerResponseSlaReconciliation.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerResponseSlaReconciliationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.releaseEffect}</p>
                <dl>
                  <div><dt>Response</dt><dd>{row.sourceResponseId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Due</dt><dd>{row.dueAt}</dd></div>
                  <div><dt>Reconciled</dt><dd>{row.reconciledAt ?? "pending"}</dd></div>
                  <div><dt>Signal</dt><dd>{row.slaSignal}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerResponseSlaReconciliation.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerResponseSlaReconciliation.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerResponseSlaReconciliation.summary.nextAction}</code>
        </div>

        <div className="task-impact-readiness-acceptance-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Readiness Acceptance Ledger</h3>
            </div>
            <div>
              <span>{impact.readinessAcceptanceLedger.reportVersion}</span>
              <strong>{impact.readinessAcceptanceLedger.gate}</strong>
              <code>{impact.readinessAcceptanceLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.readinessAcceptanceLedger.gate}>{impact.readinessAcceptanceLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.readinessAcceptanceLedger.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.readinessAcceptanceLedger.summary.acceptedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.readinessAcceptanceLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.readinessAcceptanceLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong data-status="fail">{impact.readinessAcceptanceLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-readiness-ledger-rows">
            {impact.readinessAcceptanceLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{readinessAcceptanceLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceResult}</p>
                <dl>
                  <div><dt>Promotion</dt><dd>{row.promotionRowId}</dd></div>
                  <div><dt>SLA</dt><dd>{row.slaRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Rule</dt><dd>{row.acceptanceRule}</dd></div>
                  <div><dt>Evidence</dt><dd>{row.requiredEvidence.join(" / ")}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.readinessAcceptanceLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.readinessAcceptanceLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.readinessAcceptanceLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-preview">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Promotion Rollback Preview</h3>
            </div>
            <div>
              <span>{impact.promotionRollbackPreview.reportVersion}</span>
              <strong>{impact.promotionRollbackPreview.gate}</strong>
              <code>{impact.promotionRollbackPreview.previewId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.promotionRollbackPreview.gate}>{impact.promotionRollbackPreview.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.promotionRollbackPreview.summary.totalRows}</strong></div>
            <div><span>Preview</span><strong data-status="pass">{impact.promotionRollbackPreview.summary.previewReadyRows}</strong></div>
            <div><span>Diff Blocked</span><strong data-status="review">{impact.promotionRollbackPreview.summary.diffBlockedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.promotionRollbackPreview.summary.ownerHoldRows}</strong></div>
            <div><span>Cost</span><strong>{impact.promotionRollbackPreview.summary.estimatedRollbackCost}</strong></div>
          </div>
          <div className="task-impact-rollback-preview-rows">
            {impact.promotionRollbackPreview.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{promotionRollbackPreviewStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.rollbackEffect}</p>
                <dl>
                  <div><dt>Acceptance</dt><dd>{row.sourceAcceptanceRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Target</dt><dd>{row.rollbackTarget}</dd></div>
                  <div><dt>Rule</dt><dd>{row.rollbackRule}</dd></div>
                  <div><dt>Cost</dt><dd>{row.estimatedCost}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.promotionRollbackPreview.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.promotionRollbackPreview.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.promotionRollbackPreview.summary.nextAction}</code>
        </div>

        <div className="task-impact-sla-waiver-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>SLA Exception Waiver Ledger</h3>
            </div>
            <div>
              <span>{impact.slaExceptionWaiverLedger.reportVersion}</span>
              <strong>{impact.slaExceptionWaiverLedger.gate}</strong>
              <code>{impact.slaExceptionWaiverLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.slaExceptionWaiverLedger.gate}>{impact.slaExceptionWaiverLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.slaExceptionWaiverLedger.summary.totalRows}</strong></div>
            <div><span>No Waiver</span><strong data-status="pass">{impact.slaExceptionWaiverLedger.summary.notNeededRows}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.slaExceptionWaiverLedger.summary.requestedRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.slaExceptionWaiverLedger.summary.deferredRows}</strong></div>
            <div><span>Exposed</span><strong data-status="fail">{impact.slaExceptionWaiverLedger.summary.privateFieldsExposed}</strong></div>
          </div>
          <div className="task-impact-sla-waiver-rows">
            {impact.slaExceptionWaiverLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{slaExceptionWaiverLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.waiverEffect}</p>
                <dl>
                  <div><dt>SLA</dt><dd>{row.sourceSlaRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Scope</dt><dd>{row.waiverScope}</dd></div>
                  <div><dt>Rule</dt><dd>{row.waiverRule}</dd></div>
                  <div><dt>Expires</dt><dd>{row.expiresAt ?? "none"}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.slaExceptionWaiverLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.slaExceptionWaiverLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.slaExceptionWaiverLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-note">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Candidate Packet Release Note</h3>
            </div>
            <div>
              <span>{impact.candidatePacketReleaseNote.reportVersion}</span>
              <strong>{impact.candidatePacketReleaseNote.gate}</strong>
              <code>{impact.candidatePacketReleaseNote.noteId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.candidatePacketReleaseNote.gate}>{impact.candidatePacketReleaseNote.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.candidatePacketReleaseNote.summary.totalRows}</strong></div>
            <div><span>Included</span><strong data-status="pass">{impact.candidatePacketReleaseNote.summary.includedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.candidatePacketReleaseNote.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.candidatePacketReleaseNote.summary.ownerHoldRows}</strong></div>
            <div><span>Draft Fields</span><strong>{impact.candidatePacketReleaseNote.summary.aiDraftFields}</strong></div>
          </div>
          <div className="task-impact-release-note-rows">
            {impact.candidatePacketReleaseNote.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{candidatePacketReleaseNoteStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.releaseNoteDraft}</p>
                <dl>
                  <div><dt>Section</dt><dd>{row.noteSection}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Rollback</dt><dd>{row.rollbackPreviewRowId}</dd></div>
                  <div><dt>Waiver</dt><dd>{row.waiverRowId}</dd></div>
                  <div><dt>Redaction</dt><dd>{row.redactionPolicy}</dd></div>
                </dl>
                <code>{row.deterministicBasis}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.candidatePacketReleaseNote.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.candidatePacketReleaseNote.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.candidatePacketReleaseNote.summary.nextAction}</code>
        </div>

        <div className="task-impact-reviewer-approval-loop">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Release Note Reviewer Approval Loop</h3>
            </div>
            <div>
              <span>{impact.releaseNoteReviewerApprovalLoop.reportVersion}</span>
              <strong>{impact.releaseNoteReviewerApprovalLoop.gate}</strong>
              <code>{impact.releaseNoteReviewerApprovalLoop.loopId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseNoteReviewerApprovalLoop.gate}>{impact.releaseNoteReviewerApprovalLoop.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseNoteReviewerApprovalLoop.summary.totalRows}</strong></div>
            <div><span>Approved</span><strong data-status="pass">{impact.releaseNoteReviewerApprovalLoop.summary.approvedRows}</strong></div>
            <div><span>Changes</span><strong data-status="review">{impact.releaseNoteReviewerApprovalLoop.summary.changesRequestedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseNoteReviewerApprovalLoop.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseNoteReviewerApprovalLoop.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-approval-loop-rows">
            {impact.releaseNoteReviewerApprovalLoop.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseNoteReviewerApprovalLoopStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.approvalResult}</p>
                <dl>
                  <div><dt>Release Note</dt><dd>{row.sourceReleaseNoteRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Rule</dt><dd>{row.approvalRule}</dd></div>
                </dl>
                <code>{row.reviewerCommentDraft}</code>
                <small>{row.requiredEvidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseNoteReviewerApprovalLoop.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseNoteReviewerApprovalLoop.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseNoteReviewerApprovalLoop.summary.nextAction}</code>
        </div>

        <div className="task-impact-waiver-expiry-monitor">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Waiver Expiry Monitor</h3>
            </div>
            <div>
              <span>{impact.waiverExpiryMonitor.reportVersion}</span>
              <strong>{impact.waiverExpiryMonitor.gate}</strong>
              <code>{impact.waiverExpiryMonitor.monitorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.waiverExpiryMonitor.gate}>{impact.waiverExpiryMonitor.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.waiverExpiryMonitor.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.waiverExpiryMonitor.summary.clearRows}</strong></div>
            <div><span>Expiring</span><strong data-status="review">{impact.waiverExpiryMonitor.summary.expiringRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.waiverExpiryMonitor.summary.deferredRows}</strong></div>
            <div><span>Expired</span><strong data-status="fail">{impact.waiverExpiryMonitor.summary.expiredRows}</strong></div>
          </div>
          <div className="task-impact-waiver-expiry-rows">
            {impact.waiverExpiryMonitor.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{waiverExpiryMonitorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.releaseEffect}</p>
                <dl>
                  <div><dt>Waiver Row</dt><dd>{row.sourceWaiverRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Expires</dt><dd>{row.expiresAt ?? "none"}</dd></div>
                  <div><dt>Signal</dt><dd>{row.monitorSignal}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.waiverExpiryMonitor.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.waiverExpiryMonitor.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.waiverExpiryMonitor.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-bundle-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Rollback Rehearsal Bundle Diff</h3>
            </div>
            <div>
              <span>{impact.rollbackRehearsalBundleDiff.reportVersion}</span>
              <strong>{impact.rollbackRehearsalBundleDiff.gate}</strong>
              <code>{impact.rollbackRehearsalBundleDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackRehearsalBundleDiff.gate}>{impact.rollbackRehearsalBundleDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.rollbackRehearsalBundleDiff.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.rollbackRehearsalBundleDiff.summary.matchedRows}</strong></div>
            <div><span>Diffs</span><strong data-status="review">{impact.rollbackRehearsalBundleDiff.summary.reviewDiffRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.rollbackRehearsalBundleDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.rollbackRehearsalBundleDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rollback-bundle-rows">
            {impact.rollbackRehearsalBundleDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackRehearsalBundleDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.rehearsalEffect}</p>
                <dl>
                  <div><dt>Rollback</dt><dd>{row.sourceRollbackRowId}</dd></div>
                  <div><dt>Approval</dt><dd>{row.approvalRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Before</dt><dd>{row.beforeBundle}</dd></div>
                  <div><dt>After</dt><dd>{row.afterBundle}</dd></div>
                </dl>
                <code>{row.diffReason}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackRehearsalBundleDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackRehearsalBundleDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackRehearsalBundleDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-approval-evidence-seal">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Approval Evidence Seal</h3>
            </div>
            <div>
              <span>{impact.approvalEvidenceSeal.reportVersion}</span>
              <strong>{impact.approvalEvidenceSeal.gate}</strong>
              <code>{impact.approvalEvidenceSeal.sealId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.approvalEvidenceSeal.gate}>{impact.approvalEvidenceSeal.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.approvalEvidenceSeal.summary.totalRows}</strong></div>
            <div><span>Sealed</span><strong data-status="pass">{impact.approvalEvidenceSeal.summary.sealedRows}</strong></div>
            <div><span>Open</span><strong data-status="review">{impact.approvalEvidenceSeal.summary.openChangeRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.approvalEvidenceSeal.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.approvalEvidenceSeal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-approval-seal-rows">
            {impact.approvalEvidenceSeal.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{approvalEvidenceSealStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.sealResult}</p>
                <dl>
                  <div><dt>Approval</dt><dd>{row.sourceApprovalRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Scope</dt><dd>{row.checksumScope}</dd></div>
                  <div><dt>Sealed</dt><dd>{row.sealedAt ?? "none"}</dd></div>
                </dl>
                <code>{row.sealKey}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.approvalEvidenceSeal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.approvalEvidenceSeal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.approvalEvidenceSeal.summary.nextAction}</code>
        </div>

        <div className="task-impact-waiver-renewal-simulator">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Waiver Renewal Simulator</h3>
            </div>
            <div>
              <span>{impact.waiverRenewalSimulator.reportVersion}</span>
              <strong>{impact.waiverRenewalSimulator.gate}</strong>
              <code>{impact.waiverRenewalSimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.waiverRenewalSimulator.gate}>{impact.waiverRenewalSimulator.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.waiverRenewalSimulator.summary.totalRows}</strong></div>
            <div><span>No Renewal</span><strong data-status="pass">{impact.waiverRenewalSimulator.summary.noRenewalRows}</strong></div>
            <div><span>Requested</span><strong data-status="review">{impact.waiverRenewalSimulator.summary.requestedRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.waiverRenewalSimulator.summary.deferredRows}</strong></div>
            <div><span>Writes</span><strong>{impact.waiverRenewalSimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-waiver-renewal-rows">
            {impact.waiverRenewalSimulator.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{waiverRenewalSimulatorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.renewalEffect}</p>
                <dl>
                  <div><dt>Expiry Row</dt><dd>{row.sourceExpiryRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Requested Until</dt><dd>{row.requestedUntil ?? "none"}</dd></div>
                  <div><dt>Rule</dt><dd>{row.renewalRule}</dd></div>
                </dl>
                <code>{row.nextAction}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.waiverRenewalSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.waiverRenewalSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.waiverRenewalSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-incident-handoff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Rollback Drill Incident Handoff</h3>
            </div>
            <div>
              <span>{impact.rollbackDrillIncidentHandoff.reportVersion}</span>
              <strong>{impact.rollbackDrillIncidentHandoff.gate}</strong>
              <code>{impact.rollbackDrillIncidentHandoff.handoffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackDrillIncidentHandoff.gate}>{impact.rollbackDrillIncidentHandoff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.rollbackDrillIncidentHandoff.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.rollbackDrillIncidentHandoff.summary.closedRows}</strong></div>
            <div><span>Open</span><strong data-status="review">{impact.rollbackDrillIncidentHandoff.summary.openIncidentRows}</strong></div>
            <div><span>Owner</span><strong data-status="review">{impact.rollbackDrillIncidentHandoff.summary.ownerHandoffRows}</strong></div>
            <div><span>Writes</span><strong>{impact.rollbackDrillIncidentHandoff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-incident-handoff-rows">
            {impact.rollbackDrillIncidentHandoff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackDrillIncidentHandoffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.handoffResult}</p>
                <dl>
                  <div><dt>Bundle</dt><dd>{row.sourceBundleRowId}</dd></div>
                  <div><dt>Seal</dt><dd>{row.sealRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Channel</dt><dd>{row.incidentChannel}</dd></div>
                  <div><dt>Escalation</dt><dd>{row.escalationOwner}</dd></div>
                </dl>
                <code>{row.handoffRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackDrillIncidentHandoff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackDrillIncidentHandoff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackDrillIncidentHandoff.summary.nextAction}</code>
        </div>

        <div className="task-impact-sealed-approval-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitBranch size={17} aria-hidden="true" />
              <h3>Sealed Approval Replay</h3>
            </div>
            <div>
              <span>{impact.sealedApprovalReplay.reportVersion}</span>
              <strong>{impact.sealedApprovalReplay.gate}</strong>
              <code>{impact.sealedApprovalReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.sealedApprovalReplay.gate}>{impact.sealedApprovalReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.sealedApprovalReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.sealedApprovalReplay.summary.replayedRows}</strong></div>
            <div><span>Required</span><strong data-status="review">{impact.sealedApprovalReplay.summary.replayRequiredRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.sealedApprovalReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.sealedApprovalReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-sealed-replay-rows">
            {impact.sealedApprovalReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{sealedApprovalReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayResult}</p>
                <dl>
                  <div><dt>Seal Row</dt><dd>{row.sourceSealRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Scope</dt><dd>{row.replayScope}</dd></div>
                </dl>
                <code>{row.replayKey}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.sealedApprovalReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.sealedApprovalReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.sealedApprovalReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-waiver-expiry-burndown">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Waiver Expiry Burn-down</h3>
            </div>
            <div>
              <span>{impact.waiverExpiryBurnDown.reportVersion}</span>
              <strong>{impact.waiverExpiryBurnDown.gate}</strong>
              <code>{impact.waiverExpiryBurnDown.burnDownId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.waiverExpiryBurnDown.gate}>{impact.waiverExpiryBurnDown.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.waiverExpiryBurnDown.summary.totalRows}</strong></div>
            <div><span>Burned</span><strong data-status="pass">{impact.waiverExpiryBurnDown.summary.burnedDownRows}</strong></div>
            <div><span>Open</span><strong data-status="review">{impact.waiverExpiryBurnDown.summary.renewalOpenRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.waiverExpiryBurnDown.summary.deferredRows}</strong></div>
            <div><span>Writes</span><strong>{impact.waiverExpiryBurnDown.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-waiver-burndown-rows">
            {impact.waiverExpiryBurnDown.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{waiverExpiryBurnDownStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.releaseEffect}</p>
                <dl>
                  <div><dt>Renewal Row</dt><dd>{row.sourceRenewalRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Requested Until</dt><dd>{row.requestedUntil ?? "none"}</dd></div>
                  <div><dt>Risk</dt><dd>{row.remainingRisk}</dd></div>
                </dl>
                <code>{row.burnDownSignal}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.waiverExpiryBurnDown.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.waiverExpiryBurnDown.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.waiverExpiryBurnDown.summary.nextAction}</code>
        </div>

        <div className="task-impact-incident-closure-packet">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Incident Closure Acceptance Packet</h3>
            </div>
            <div>
              <span>{impact.incidentClosureAcceptancePacket.reportVersion}</span>
              <strong>{impact.incidentClosureAcceptancePacket.gate}</strong>
              <code>{impact.incidentClosureAcceptancePacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.incidentClosureAcceptancePacket.gate}>{impact.incidentClosureAcceptancePacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.incidentClosureAcceptancePacket.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.incidentClosureAcceptancePacket.summary.acceptedRows}</strong></div>
            <div><span>Open</span><strong data-status="review">{impact.incidentClosureAcceptancePacket.summary.openAcceptanceRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.incidentClosureAcceptancePacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.incidentClosureAcceptancePacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closure-packet-rows">
            {impact.incidentClosureAcceptancePacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{incidentClosureAcceptancePacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceResult}</p>
                <dl>
                  <div><dt>Handoff</dt><dd>{row.sourceHandoffRowId}</dd></div>
                  <div><dt>Replay</dt><dd>{row.replayRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Scope</dt><dd>{row.packetScope}</dd></div>
                </dl>
                <code>{row.acceptanceRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.incidentClosureAcceptancePacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.incidentClosureAcceptancePacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.incidentClosureAcceptancePacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-closure-acceptance-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Closure Acceptance Replay</h3>
            </div>
            <div>
              <span>{impact.closureAcceptanceReplay.reportVersion}</span>
              <strong>{impact.closureAcceptanceReplay.gate}</strong>
              <code>{impact.closureAcceptanceReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.closureAcceptanceReplay.gate}>{impact.closureAcceptanceReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.closureAcceptanceReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.closureAcceptanceReplay.summary.replayedRows}</strong></div>
            <div><span>Required</span><strong data-status="review">{impact.closureAcceptanceReplay.summary.acceptanceRequiredRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.closureAcceptanceReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.closureAcceptanceReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closure-replay-rows">
            {impact.closureAcceptanceReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{closureAcceptanceReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayResult}</p>
                <dl>
                  <div><dt>Packet</dt><dd>{row.sourcePacketRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Scope</dt><dd>{row.replayScope}</dd></div>
                </dl>
                <code>{row.replayKey}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.closureAcceptanceReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.closureAcceptanceReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.closureAcceptanceReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-waiver-response-importer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Cable size={17} aria-hidden="true" />
              <h3>Waiver Owner Response Importer</h3>
            </div>
            <div>
              <span>{impact.waiverOwnerResponseImporter.reportVersion}</span>
              <strong>{impact.waiverOwnerResponseImporter.gate}</strong>
              <code>{impact.waiverOwnerResponseImporter.importerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.waiverOwnerResponseImporter.gate}>{impact.waiverOwnerResponseImporter.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.waiverOwnerResponseImporter.summary.totalRows}</strong></div>
            <div><span>Imported</span><strong data-status="pass">{impact.waiverOwnerResponseImporter.summary.importedRows}</strong></div>
            <div><span>Waiting</span><strong data-status="review">{impact.waiverOwnerResponseImporter.summary.waitingOwnerRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.waiverOwnerResponseImporter.summary.deferredRows}</strong></div>
            <div><span>Writes</span><strong>{impact.waiverOwnerResponseImporter.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-waiver-response-rows">
            {impact.waiverOwnerResponseImporter.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{waiverOwnerResponseImporterStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.importResult}</p>
                <dl>
                  <div><dt>Burn-down</dt><dd>{row.sourceBurnDownRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Source</dt><dd>{row.responseSource}</dd></div>
                  <div><dt>Required</dt><dd>{row.requiredEvidence}</dd></div>
                </dl>
                <code>{row.importRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.waiverOwnerResponseImporter.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.waiverOwnerResponseImporter.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.waiverOwnerResponseImporter.summary.nextAction}</code>
        </div>

        <div className="task-impact-incident-sla-scoreboard">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Incident SLA Scoreboard</h3>
            </div>
            <div>
              <span>{impact.incidentSlaScoreboard.reportVersion}</span>
              <strong>{impact.incidentSlaScoreboard.gate}</strong>
              <code>{impact.incidentSlaScoreboard.scoreboardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.incidentSlaScoreboard.gate}>{impact.incidentSlaScoreboard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.incidentSlaScoreboard.summary.totalRows}</strong></div>
            <div><span>Within SLA</span><strong data-status="pass">{impact.incidentSlaScoreboard.summary.withinSlaRows}</strong></div>
            <div><span>Due Today</span><strong data-status="review">{impact.incidentSlaScoreboard.summary.dueTodayRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.incidentSlaScoreboard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.incidentSlaScoreboard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-incident-sla-rows">
            {impact.incidentSlaScoreboard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{incidentSlaScoreboardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.scoreboardResult}</p>
                <dl>
                  <div><dt>Packet</dt><dd>{row.sourcePacketRowId}</dd></div>
                  <div><dt>Response</dt><dd>{row.responseRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>SLA</dt><dd>{row.slaTarget}</dd></div>
                  <div><dt>Escalation</dt><dd>{row.escalationOwner}</dd></div>
                </dl>
                <code>{row.scoreboardRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.incidentSlaScoreboard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.incidentSlaScoreboard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.incidentSlaScoreboard.summary.nextAction}</code>
        </div>

        <div className="task-impact-incident-closure-diff-viewer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Incident Closure Diff Viewer</h3>
            </div>
            <div>
              <span>{impact.incidentClosureDiffViewer.reportVersion}</span>
              <strong>{impact.incidentClosureDiffViewer.gate}</strong>
              <code>{impact.incidentClosureDiffViewer.viewerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.incidentClosureDiffViewer.gate}>{impact.incidentClosureDiffViewer.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.incidentClosureDiffViewer.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.incidentClosureDiffViewer.summary.matchedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.incidentClosureDiffViewer.summary.changedReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.incidentClosureDiffViewer.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.incidentClosureDiffViewer.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closure-diff-rows">
            {impact.incidentClosureDiffViewer.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{incidentClosureDiffViewerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffResult}</p>
                <dl>
                  <div><dt>Replay</dt><dd>{row.sourceReplayRowId}</dd></div>
                  <div><dt>SLA</dt><dd>{row.scoreboardRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Before</dt><dd>{row.beforeClosureState}</dd></div>
                  <div><dt>After</dt><dd>{row.afterClosureState}</dd></div>
                </dl>
                <code>{row.diffBasis}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.incidentClosureDiffViewer.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.incidentClosureDiffViewer.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.incidentClosureDiffViewer.summary.nextAction}</code>
        </div>

        <div className="task-impact-waiver-sla-reconciliation">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Cable size={17} aria-hidden="true" />
              <h3>Waiver SLA Reconciliation</h3>
            </div>
            <div>
              <span>{impact.waiverSlaReconciliation.reportVersion}</span>
              <strong>{impact.waiverSlaReconciliation.gate}</strong>
              <code>{impact.waiverSlaReconciliation.reconciliationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.waiverSlaReconciliation.gate}>{impact.waiverSlaReconciliation.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.waiverSlaReconciliation.summary.totalRows}</strong></div>
            <div><span>Reconciled</span><strong data-status="pass">{impact.waiverSlaReconciliation.summary.reconciledRows}</strong></div>
            <div><span>Due Today</span><strong data-status="review">{impact.waiverSlaReconciliation.summary.dueTodayRows}</strong></div>
            <div><span>Deferred</span><strong data-status="review">{impact.waiverSlaReconciliation.summary.deferredRows}</strong></div>
            <div><span>Writes</span><strong>{impact.waiverSlaReconciliation.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-waiver-sla-rows">
            {impact.waiverSlaReconciliation.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{waiverSlaReconciliationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.reconciliationResult}</p>
                <dl>
                  <div><dt>Response</dt><dd>{row.sourceResponseRowId}</dd></div>
                  <div><dt>SLA</dt><dd>{row.scoreboardRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Waiver</dt><dd>{row.waiverSignal}</dd></div>
                  <div><dt>Due Owner</dt><dd>{row.dueOwner}</dd></div>
                </dl>
                <code>{row.reconciliationRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.waiverSlaReconciliation.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.waiverSlaReconciliation.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.waiverSlaReconciliation.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-operations-acceptance-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Release Operations Acceptance Ledger</h3>
            </div>
            <div>
              <span>{impact.releaseOperationsAcceptanceLedger.reportVersion}</span>
              <strong>{impact.releaseOperationsAcceptanceLedger.gate}</strong>
              <code>{impact.releaseOperationsAcceptanceLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseOperationsAcceptanceLedger.gate}>{impact.releaseOperationsAcceptanceLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseOperationsAcceptanceLedger.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.releaseOperationsAcceptanceLedger.summary.acceptedRows}</strong></div>
            <div><span>Ops Review</span><strong data-status="review">{impact.releaseOperationsAcceptanceLedger.summary.opsReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseOperationsAcceptanceLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseOperationsAcceptanceLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-release-ops-rows">
            {impact.releaseOperationsAcceptanceLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseOperationsAcceptanceLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceResult}</p>
                <dl>
                  <div><dt>Diff</dt><dd>{row.sourceDiffRowId}</dd></div>
                  <div><dt>SLA</dt><dd>{row.sourceReconciliationRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.operationLane}</dd></div>
                  <div><dt>Effect</dt><dd>{row.releaseEffect}</dd></div>
                </dl>
                <code>{row.acceptanceRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseOperationsAcceptanceLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseOperationsAcceptanceLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseOperationsAcceptanceLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-operations-packet-signoff-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Operations Packet Signoff Diff</h3>
            </div>
            <div>
              <span>{impact.operationsPacketSignoffDiff.reportVersion}</span>
              <strong>{impact.operationsPacketSignoffDiff.gate}</strong>
              <code>{impact.operationsPacketSignoffDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.operationsPacketSignoffDiff.gate}>{impact.operationsPacketSignoffDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.operationsPacketSignoffDiff.summary.totalRows}</strong></div>
            <div><span>Signed Off</span><strong data-status="pass">{impact.operationsPacketSignoffDiff.summary.signedOffRows}</strong></div>
            <div><span>Diff Review</span><strong data-status="review">{impact.operationsPacketSignoffDiff.summary.diffReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.operationsPacketSignoffDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.operationsPacketSignoffDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-ops-signoff-rows">
            {impact.operationsPacketSignoffDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{operationsPacketSignoffDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffResult}</p>
                <dl>
                  <div><dt>Ops Row</dt><dd>{row.sourceOperationsRowId}</dd></div>
                  <div><dt>Decision</dt><dd>{row.sourceDecisionLaneId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.packetLane}</dd></div>
                  <div><dt>Effect</dt><dd>{row.releaseEffect}</dd></div>
                </dl>
                <code>{row.signoffBasis}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.operationsPacketSignoffDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.operationsPacketSignoffDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.operationsPacketSignoffDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-train-readiness-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Release Train Readiness Board</h3>
            </div>
            <div>
              <span>{impact.releaseTrainReadinessBoard.reportVersion}</span>
              <strong>{impact.releaseTrainReadinessBoard.gate}</strong>
              <code>{impact.releaseTrainReadinessBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseTrainReadinessBoard.gate}>{impact.releaseTrainReadinessBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseTrainReadinessBoard.summary.totalRows}</strong></div>
            <div><span>Train Ready</span><strong data-status="pass">{impact.releaseTrainReadinessBoard.summary.trainReadyRows}</strong></div>
            <div><span>Train Review</span><strong data-status="review">{impact.releaseTrainReadinessBoard.summary.trainReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseTrainReadinessBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseTrainReadinessBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-train-readiness-rows">
            {impact.releaseTrainReadinessBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseTrainReadinessBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.trainEffect}</p>
                <dl>
                  <div><dt>Signoff</dt><dd>{row.sourceSignoffRowId}</dd></div>
                  <div><dt>Decision</dt><dd>{row.sourceDecisionLaneId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Train</dt><dd>{row.trainLane}</dd></div>
                  <div><dt>Signal</dt><dd>{row.readinessSignal}</dd></div>
                </dl>
                <code>{row.entryRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseTrainReadinessBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseTrainReadinessBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseTrainReadinessBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-escalation-closeout">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Owner Escalation Closeout</h3>
            </div>
            <div>
              <span>{impact.ownerEscalationCloseout.reportVersion}</span>
              <strong>{impact.ownerEscalationCloseout.gate}</strong>
              <code>{impact.ownerEscalationCloseout.closeoutId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerEscalationCloseout.gate}>{impact.ownerEscalationCloseout.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerEscalationCloseout.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.ownerEscalationCloseout.summary.closedRows}</strong></div>
            <div><span>Escalated</span><strong data-status="review">{impact.ownerEscalationCloseout.summary.escalatedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.ownerEscalationCloseout.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.ownerEscalationCloseout.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-owner-closeout-rows">
            {impact.ownerEscalationCloseout.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerEscalationCloseoutStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.closeoutResult}</p>
                <dl>
                  <div><dt>Readiness</dt><dd>{row.sourceReadinessRowId}</dd></div>
                  <div><dt>SLA</dt><dd>{row.sourceSlaItemId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Escalation</dt><dd>{row.escalationState}</dd></div>
                  <div><dt>Effect</dt><dd>{row.releaseEffect}</dd></div>
                </dl>
                <code>{row.closeoutRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerEscalationCloseout.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerEscalationCloseout.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerEscalationCloseout.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-train-replay-receipt">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Release Train Replay Receipt</h3>
            </div>
            <div>
              <span>{impact.releaseTrainReplayReceipt.reportVersion}</span>
              <strong>{impact.releaseTrainReplayReceipt.gate}</strong>
              <code>{impact.releaseTrainReplayReceipt.receiptId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseTrainReplayReceipt.gate}>{impact.releaseTrainReplayReceipt.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseTrainReplayReceipt.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.releaseTrainReplayReceipt.summary.replayedRows}</strong></div>
            <div><span>Variance</span><strong data-status="review">{impact.releaseTrainReplayReceipt.summary.varianceReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseTrainReplayReceipt.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseTrainReplayReceipt.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-train-replay-rows">
            {impact.releaseTrainReplayReceipt.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseTrainReplayReceiptStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayResult}</p>
                <dl>
                  <div><dt>Readiness</dt><dd>{row.sourceReadinessRowId}</dd></div>
                  <div><dt>Closeout</dt><dd>{row.sourceCloseoutRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Train</dt><dd>{row.trainLane}</dd></div>
                  <div><dt>Effect</dt><dd>{row.releaseEffect}</dd></div>
                </dl>
                <code>{row.receiptRule}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseTrainReplayReceipt.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseTrainReplayReceipt.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseTrainReplayReceipt.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-closeout-aging-audit">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Owner Closeout Aging Audit</h3>
            </div>
            <div>
              <span>{impact.ownerCloseoutAgingAudit.reportVersion}</span>
              <strong>{impact.ownerCloseoutAgingAudit.gate}</strong>
              <code>{impact.ownerCloseoutAgingAudit.auditId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerCloseoutAgingAudit.gate}>{impact.ownerCloseoutAgingAudit.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerCloseoutAgingAudit.summary.totalRows}</strong></div>
            <div><span>Fresh</span><strong data-status="pass">{impact.ownerCloseoutAgingAudit.summary.freshRows}</strong></div>
            <div><span>Aging</span><strong data-status="review">{impact.ownerCloseoutAgingAudit.summary.agingReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.ownerCloseoutAgingAudit.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.ownerCloseoutAgingAudit.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closeout-aging-rows">
            {impact.ownerCloseoutAgingAudit.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerCloseoutAgingAuditStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.auditResult}</p>
                <dl>
                  <div><dt>Closeout</dt><dd>{row.sourceCloseoutRowId}</dd></div>
                  <div><dt>Replay</dt><dd>{row.sourceReplayRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Age</dt><dd>{row.daysOpen}d</dd></div>
                  <div><dt>Bucket</dt><dd>{row.agingBucket}</dd></div>
                </dl>
                <code>{row.agingSignal}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerCloseoutAgingAudit.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerCloseoutAgingAudit.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerCloseoutAgingAudit.summary.nextAction}</code>
        </div>

        <div className="task-impact-publish-rehearsal-variance-report">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Publish Rehearsal Variance Report</h3>
            </div>
            <div>
              <span>{impact.publishRehearsalVarianceReport.reportVersion}</span>
              <strong>{impact.publishRehearsalVarianceReport.gate}</strong>
              <code>{impact.publishRehearsalVarianceReport.varianceId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.publishRehearsalVarianceReport.gate}>{impact.publishRehearsalVarianceReport.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.publishRehearsalVarianceReport.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.publishRehearsalVarianceReport.summary.varianceClearRows}</strong></div>
            <div><span>Variance</span><strong data-status="review">{impact.publishRehearsalVarianceReport.summary.varianceReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.publishRehearsalVarianceReport.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.publishRehearsalVarianceReport.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-publish-variance-rows">
            {impact.publishRehearsalVarianceReport.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{publishRehearsalVarianceReportStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.varianceSignal}</p>
                <dl>
                  <div><dt>Replay</dt><dd>{row.sourceReplayRowId}</dd></div>
                  <div><dt>Aging</dt><dd>{row.sourceAgingRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Expected</dt><dd>{row.expectedOutcome}</dd></div>
                  <div><dt>Actual</dt><dd>{row.actualOutcome}</dd></div>
                </dl>
                <code>{row.releaseEffect}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.publishRehearsalVarianceReport.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.publishRehearsalVarianceReport.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.publishRehearsalVarianceReport.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-manager-daily-digest">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Release Manager Daily Digest</h3>
            </div>
            <div>
              <span>{impact.releaseManagerDailyDigest.reportVersion}</span>
              <strong>{impact.releaseManagerDailyDigest.gate}</strong>
              <code>{impact.releaseManagerDailyDigest.digestId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseManagerDailyDigest.gate}>{impact.releaseManagerDailyDigest.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseManagerDailyDigest.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.releaseManagerDailyDigest.summary.readyDigestRows}</strong></div>
            <div><span>Attention</span><strong data-status="review">{impact.releaseManagerDailyDigest.summary.attentionRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseManagerDailyDigest.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseManagerDailyDigest.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-manager-digest-rows">
            {impact.releaseManagerDailyDigest.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseManagerDailyDigestStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.managerSummary}</p>
                <dl>
                  <div><dt>Variance</dt><dd>{row.sourceVarianceRowId}</dd></div>
                  <div><dt>Replay</dt><dd>{row.sourceReplayRowId}</dd></div>
                  <div><dt>Aging</dt><dd>{row.sourceAgingRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Priority</dt><dd>{row.priority}</dd></div>
                </dl>
                <code>{row.reviewQuestion}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseManagerDailyDigest.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseManagerDailyDigest.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseManagerDailyDigest.summary.nextAction}</code>
        </div>

        <div className="task-impact-late-owner-risk-forecast">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Late Owner Risk Forecast</h3>
            </div>
            <div>
              <span>{impact.lateOwnerRiskForecast.reportVersion}</span>
              <strong>{impact.lateOwnerRiskForecast.gate}</strong>
              <code>{impact.lateOwnerRiskForecast.forecastId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.lateOwnerRiskForecast.gate}>{impact.lateOwnerRiskForecast.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.lateOwnerRiskForecast.summary.totalRows}</strong></div>
            <div><span>Low</span><strong data-status="pass">{impact.lateOwnerRiskForecast.summary.lowRiskRows}</strong></div>
            <div><span>Rising</span><strong data-status="review">{impact.lateOwnerRiskForecast.summary.risingRiskRows}</strong></div>
            <div><span>Late</span><strong data-status="review">{impact.lateOwnerRiskForecast.summary.lateOwnerRows}</strong></div>
            <div><span>Max Risk</span><strong>{impact.lateOwnerRiskForecast.summary.maxRiskScore}</strong></div>
          </div>
          <div className="task-impact-owner-risk-rows">
            {impact.lateOwnerRiskForecast.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{lateOwnerRiskForecastStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.riskSignal}</p>
                <dl>
                  <div><dt>Aging</dt><dd>{row.sourceAgingRowId}</dd></div>
                  <div><dt>Digest</dt><dd>{row.sourceDigestRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Age</dt><dd>{row.daysOpen}d</dd></div>
                  <div><dt>Score</dt><dd>{row.riskScore}</dd></div>
                </dl>
                <code>{row.mitigation}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.lateOwnerRiskForecast.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.lateOwnerRiskForecast.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.lateOwnerRiskForecast.summary.nextAction}</code>
        </div>

        <div className="task-impact-package-acceptance-freeze-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Package Acceptance Freeze Diff</h3>
            </div>
            <div>
              <span>{impact.packageAcceptanceFreezeDiff.reportVersion}</span>
              <strong>{impact.packageAcceptanceFreezeDiff.gate}</strong>
              <code>{impact.packageAcceptanceFreezeDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.packageAcceptanceFreezeDiff.gate}>{impact.packageAcceptanceFreezeDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.packageAcceptanceFreezeDiff.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.packageAcceptanceFreezeDiff.summary.freezeMatchedRows}</strong></div>
            <div><span>Changed</span><strong data-status="review">{impact.packageAcceptanceFreezeDiff.summary.freezeChangedRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.packageAcceptanceFreezeDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.packageAcceptanceFreezeDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-acceptance-freeze-rows">
            {impact.packageAcceptanceFreezeDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{packageAcceptanceFreezeDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffSignal}</p>
                <dl>
                  <div><dt>Variance</dt><dd>{row.sourceVarianceRowId}</dd></div>
                  <div><dt>Digest</dt><dd>{row.sourceDigestRowId}</dd></div>
                  <div><dt>Forecast</dt><dd>{row.sourceForecastRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.packageLane}</dd></div>
                </dl>
                <code>{row.acceptanceEffect}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.packageAcceptanceFreezeDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.packageAcceptanceFreezeDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.packageAcceptanceFreezeDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-waiver-summary">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Release Acceptance Waiver Summary</h3>
            </div>
            <div>
              <span>{impact.releaseAcceptanceWaiverSummary.reportVersion}</span>
              <strong>{impact.releaseAcceptanceWaiverSummary.gate}</strong>
              <code>{impact.releaseAcceptanceWaiverSummary.summaryId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseAcceptanceWaiverSummary.gate}>{impact.releaseAcceptanceWaiverSummary.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseAcceptanceWaiverSummary.summary.totalRows}</strong></div>
            <div><span>No Waiver</span><strong data-status="pass">{impact.releaseAcceptanceWaiverSummary.summary.waiverNotNeededRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseAcceptanceWaiverSummary.summary.waiverReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseAcceptanceWaiverSummary.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseAcceptanceWaiverSummary.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-waiver-summary-rows">
            {impact.releaseAcceptanceWaiverSummary.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseAcceptanceWaiverSummaryStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.waiverReason}</p>
                <dl>
                  <div><dt>Freeze</dt><dd>{row.sourceFreezeRowId}</dd></div>
                  <div><dt>Forecast</dt><dd>{row.sourceForecastRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.packageLane}</dd></div>
                  <div><dt>Policy</dt><dd>{row.waiverPolicy}</dd></div>
                </dl>
                <code>{row.acceptanceEffect}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseAcceptanceWaiverSummary.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseAcceptanceWaiverSummary.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseAcceptanceWaiverSummary.summary.nextAction}</code>
        </div>

        <div className="task-impact-freeze-exception-closure-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Freeze Exception Closure Board</h3>
            </div>
            <div>
              <span>{impact.freezeExceptionClosureBoard.reportVersion}</span>
              <strong>{impact.freezeExceptionClosureBoard.gate}</strong>
              <code>{impact.freezeExceptionClosureBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.freezeExceptionClosureBoard.gate}>{impact.freezeExceptionClosureBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.freezeExceptionClosureBoard.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.freezeExceptionClosureBoard.summary.closureReadyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.freezeExceptionClosureBoard.summary.closureReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.freezeExceptionClosureBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.freezeExceptionClosureBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-freeze-closure-rows">
            {impact.freezeExceptionClosureBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{freezeExceptionClosureBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.exceptionSignal}</p>
                <dl>
                  <div><dt>Waiver</dt><dd>{row.sourceWaiverRowId}</dd></div>
                  <div><dt>Freeze</dt><dd>{row.sourceFreezeRowId}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.closureLane}</dd></div>
                  <div><dt>Disposition</dt><dd>{row.closureDisposition}</dd></div>
                </dl>
                <code>{row.closureEffect}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.freezeExceptionClosureBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.freezeExceptionClosureBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.freezeExceptionClosureBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-go-no-go-packet">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Publish Go/No-Go Packet</h3>
            </div>
            <div>
              <span>{impact.publishGoNoGoPacket.reportVersion}</span>
              <strong>{impact.publishGoNoGoPacket.gate}</strong>
              <code>{impact.publishGoNoGoPacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.publishGoNoGoPacket.gate}>{impact.publishGoNoGoPacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.publishGoNoGoPacket.summary.totalRows}</strong></div>
            <div><span>Go</span><strong data-status="pass">{impact.publishGoNoGoPacket.summary.goRows}</strong></div>
            <div><span>Conditional</span><strong data-status="review">{impact.publishGoNoGoPacket.summary.conditionalGoRows}</strong></div>
            <div><span>No-Go</span><strong data-status="review">{impact.publishGoNoGoPacket.summary.noGoOwnerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.publishGoNoGoPacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-go-no-go-rows">
            {impact.publishGoNoGoPacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{publishGoNoGoPacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.decisionReason}</p>
                <dl>
                  <div><dt>Digest</dt><dd>{row.sourceDigestRowId}</dd></div>
                  <div><dt>Freeze</dt><dd>{row.sourceFreezeRowId}</dd></div>
                  <div><dt>Waiver</dt><dd>{row.sourceWaiverRowId}</dd></div>
                  <div><dt>Closure</dt><dd>{row.sourceClosureRowId}</dd></div>
                  <div><dt>Decision</dt><dd>{row.decision}</dd></div>
                </dl>
                <code>{row.goNoGoEffect}</code>
                <small>{row.evidence.join(" / ")}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.publishGoNoGoPacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.publishGoNoGoPacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.publishGoNoGoPacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-decision-receipt-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Publish Decision Receipt Replay</h3>
            </div>
            <div>
              <span>{impact.publishDecisionReceiptReplay.reportVersion}</span>
              <strong>{impact.publishDecisionReceiptReplay.gate}</strong>
              <code>{impact.publishDecisionReceiptReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.publishDecisionReceiptReplay.gate}>{impact.publishDecisionReceiptReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.publishDecisionReceiptReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.publishDecisionReceiptReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.publishDecisionReceiptReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.publishDecisionReceiptReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.publishDecisionReceiptReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-decision-replay-rows">
            {impact.publishDecisionReceiptReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{publishDecisionReceiptReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replaySignal}</p>
                <dl>
                  <div><dt>Go/No-Go</dt><dd title={row.sourceGoNoGoRowId}>{compactIdentifier(row.sourceGoNoGoRowId)}</dd></div>
                  <div><dt>Receipt</dt><dd>{row.receiptRef}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.releaseLane}</dd></div>
                  <div><dt>Finding</dt><dd>{row.replayFinding}</dd></div>
                </dl>
                <code>{row.replayEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.publishDecisionReceiptReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.publishDecisionReceiptReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.publishDecisionReceiptReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-post-release-watch-window">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Post-Release Watch Window Board</h3>
            </div>
            <div>
              <span>{impact.postReleaseWatchWindowBoard.reportVersion}</span>
              <strong>{impact.postReleaseWatchWindowBoard.gate}</strong>
              <code>{impact.postReleaseWatchWindowBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.postReleaseWatchWindowBoard.gate}>{impact.postReleaseWatchWindowBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.postReleaseWatchWindowBoard.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.postReleaseWatchWindowBoard.summary.watchClearRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.postReleaseWatchWindowBoard.summary.watchReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.postReleaseWatchWindowBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.postReleaseWatchWindowBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-watch-window-rows">
            {impact.postReleaseWatchWindowBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{postReleaseWatchWindowBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.observedSignal}</p>
                <dl>
                  <div><dt>Replay</dt><dd title={row.sourceReceiptReplayRowId}>{compactIdentifier(row.sourceReceiptReplayRowId)}</dd></div>
                  <div><dt>Go/No-Go</dt><dd title={row.sourceGoNoGoRowId}>{compactIdentifier(row.sourceGoNoGoRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Window</dt><dd>{row.watchWindow}</dd></div>
                  <div><dt>Disposition</dt><dd>{row.watchDisposition}</dd></div>
                </dl>
                <code>{row.releaseEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.postReleaseWatchWindowBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.postReleaseWatchWindowBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.postReleaseWatchWindowBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-readiness-delta">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Rollback Readiness Delta</h3>
            </div>
            <div>
              <span>{impact.rollbackReadinessDelta.reportVersion}</span>
              <strong>{impact.rollbackReadinessDelta.gate}</strong>
              <code>{impact.rollbackReadinessDelta.deltaId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackReadinessDelta.gate}>{impact.rollbackReadinessDelta.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.rollbackReadinessDelta.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.rollbackReadinessDelta.summary.rollbackReadyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.rollbackReadinessDelta.summary.rollbackReviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.rollbackReadinessDelta.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.rollbackReadinessDelta.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rollback-delta-rows">
            {impact.rollbackReadinessDelta.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackReadinessDeltaStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.deltaSignal}</p>
                <dl>
                  <div><dt>Watch</dt><dd title={row.sourceWatchRowId}>{compactIdentifier(row.sourceWatchRowId)}</dd></div>
                  <div><dt>Replay</dt><dd title={row.sourceReceiptReplayRowId}>{compactIdentifier(row.sourceReceiptReplayRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.rollbackLane}</dd></div>
                  <div><dt>Before</dt><dd>{row.beforeReadiness}</dd></div>
                  <div><dt>After</dt><dd>{row.afterReadiness}</dd></div>
                </dl>
                <code>{row.rollbackEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackReadinessDelta.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackReadinessDelta.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackReadinessDelta.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-closeout-seal">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Release Closeout Receipt Seal</h3>
            </div>
            <div>
              <span>{impact.releaseCloseoutReceiptSeal.reportVersion}</span>
              <strong>{impact.releaseCloseoutReceiptSeal.gate}</strong>
              <code>{impact.releaseCloseoutReceiptSeal.sealId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseCloseoutReceiptSeal.gate}>{impact.releaseCloseoutReceiptSeal.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseCloseoutReceiptSeal.summary.totalRows}</strong></div>
            <div><span>Sealed</span><strong data-status="pass">{impact.releaseCloseoutReceiptSeal.summary.sealedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseCloseoutReceiptSeal.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseCloseoutReceiptSeal.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseCloseoutReceiptSeal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closeout-seal-rows">
            {impact.releaseCloseoutReceiptSeal.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseCloseoutReceiptSealStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.sealRule}</p>
                <dl>
                  <div><dt>Rollback</dt><dd title={row.sourceRollbackDeltaRowId}>{compactIdentifier(row.sourceRollbackDeltaRowId)}</dd></div>
                  <div><dt>Watch</dt><dd title={row.sourceWatchRowId}>{compactIdentifier(row.sourceWatchRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.closeoutLane}</dd></div>
                  <div><dt>Seal</dt><dd>{row.sealRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.sealResult}</dd></div>
                </dl>
                <code>{row.closeoutEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseCloseoutReceiptSeal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseCloseoutReceiptSeal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseCloseoutReceiptSeal.summary.nextAction}</code>
        </div>

        <div className="task-impact-watch-escalation-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Watch Escalation Replay</h3>
            </div>
            <div>
              <span>{impact.watchEscalationReplay.reportVersion}</span>
              <strong>{impact.watchEscalationReplay.gate}</strong>
              <code>{impact.watchEscalationReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.watchEscalationReplay.gate}>{impact.watchEscalationReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.watchEscalationReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.watchEscalationReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.watchEscalationReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.watchEscalationReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.watchEscalationReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-escalation-replay-rows">
            {impact.watchEscalationReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{watchEscalationReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayRule}</p>
                <dl>
                  <div><dt>Seal</dt><dd title={row.sourceSealRowId}>{compactIdentifier(row.sourceSealRowId)}</dd></div>
                  <div><dt>Watch</dt><dd title={row.sourceWatchRowId}>{compactIdentifier(row.sourceWatchRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.escalationLane}</dd></div>
                  <div><dt>Escalation</dt><dd>{row.escalationRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.replayResult}</dd></div>
                </dl>
                <code>{row.escalationEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.watchEscalationReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.watchEscalationReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.watchEscalationReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-rollback-drill-closeout">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Rollback Drill Closeout Packet</h3>
            </div>
            <div>
              <span>{impact.rollbackDrillCloseoutPacket.reportVersion}</span>
              <strong>{impact.rollbackDrillCloseoutPacket.gate}</strong>
              <code>{impact.rollbackDrillCloseoutPacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.rollbackDrillCloseoutPacket.gate}>{impact.rollbackDrillCloseoutPacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.rollbackDrillCloseoutPacket.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.rollbackDrillCloseoutPacket.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.rollbackDrillCloseoutPacket.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.rollbackDrillCloseoutPacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.rollbackDrillCloseoutPacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-rollback-closeout-rows">
            {impact.rollbackDrillCloseoutPacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{rollbackDrillCloseoutPacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.closeoutRule}</p>
                <dl>
                  <div><dt>Escalation</dt><dd title={row.sourceEscalationRowId}>{compactIdentifier(row.sourceEscalationRowId)}</dd></div>
                  <div><dt>Rollback</dt><dd title={row.sourceRollbackDeltaRowId}>{compactIdentifier(row.sourceRollbackDeltaRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.closeoutLane}</dd></div>
                  <div><dt>Packet</dt><dd>{row.packetRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.closeoutResult}</dd></div>
                </dl>
                <code>{row.releaseEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.rollbackDrillCloseoutPacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.rollbackDrillCloseoutPacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.rollbackDrillCloseoutPacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-closeout-acceptance-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Closeout Acceptance Replay</h3>
            </div>
            <div>
              <span>{impact.closeoutAcceptanceReplay.reportVersion}</span>
              <strong>{impact.closeoutAcceptanceReplay.gate}</strong>
              <code>{impact.closeoutAcceptanceReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.closeoutAcceptanceReplay.gate}>{impact.closeoutAcceptanceReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.closeoutAcceptanceReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.closeoutAcceptanceReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.closeoutAcceptanceReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.closeoutAcceptanceReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.closeoutAcceptanceReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-acceptance-replay-rows">
            {impact.closeoutAcceptanceReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{closeoutAcceptanceReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayRule}</p>
                <dl>
                  <div><dt>Closeout</dt><dd title={row.sourceCloseoutPacketRowId}>{compactIdentifier(row.sourceCloseoutPacketRowId)}</dd></div>
                  <div><dt>Seal</dt><dd title={row.sourceSealRowId}>{compactIdentifier(row.sourceSealRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.acceptanceLane}</dd></div>
                  <div><dt>Acceptance</dt><dd>{row.acceptanceRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.replayResult}</dd></div>
                </dl>
                <code>{row.acceptanceEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.closeoutAcceptanceReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.closeoutAcceptanceReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.closeoutAcceptanceReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-escalation-aging-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Escalation Aging Board</h3>
            </div>
            <div>
              <span>{impact.escalationAgingBoard.reportVersion}</span>
              <strong>{impact.escalationAgingBoard.gate}</strong>
              <code>{impact.escalationAgingBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.escalationAgingBoard.gate}>{impact.escalationAgingBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.escalationAgingBoard.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.escalationAgingBoard.summary.clearRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.escalationAgingBoard.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.escalationAgingBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.escalationAgingBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-escalation-aging-rows">
            {impact.escalationAgingBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{escalationAgingBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.agingRule}</p>
                <dl>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceRowId}>{compactIdentifier(row.sourceAcceptanceRowId)}</dd></div>
                  <div><dt>Escalation</dt><dd title={row.sourceEscalationRowId}>{compactIdentifier(row.sourceEscalationRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.agingLane}</dd></div>
                  <div><dt>Bucket</dt><dd>{row.agingBucket}</dd></div>
                  <div><dt>Result</dt><dd>{row.agingResult}</dd></div>
                </dl>
                <code>{row.escalationEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.escalationAgingBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.escalationAgingBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.escalationAgingBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-final-release-archive">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Final Release Archive Packet</h3>
            </div>
            <div>
              <span>{impact.finalReleaseArchivePacket.reportVersion}</span>
              <strong>{impact.finalReleaseArchivePacket.gate}</strong>
              <code>{impact.finalReleaseArchivePacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.finalReleaseArchivePacket.gate}>{impact.finalReleaseArchivePacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.finalReleaseArchivePacket.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.finalReleaseArchivePacket.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.finalReleaseArchivePacket.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.finalReleaseArchivePacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.finalReleaseArchivePacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-final-archive-rows">
            {impact.finalReleaseArchivePacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{finalReleaseArchivePacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.archiveRule}</p>
                <dl>
                  <div><dt>Aging</dt><dd title={row.sourceAgingRowId}>{compactIdentifier(row.sourceAgingRowId)}</dd></div>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceRowId}>{compactIdentifier(row.sourceAcceptanceRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.archiveLane}</dd></div>
                  <div><dt>Archive</dt><dd>{row.archiveRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.archiveResult}</dd></div>
                </dl>
                <code>{row.releaseEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.finalReleaseArchivePacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.finalReleaseArchivePacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.finalReleaseArchivePacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-integrity-audit">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Archive Integrity Audit</h3>
            </div>
            <div>
              <span>{impact.archiveIntegrityAudit.reportVersion}</span>
              <strong>{impact.archiveIntegrityAudit.gate}</strong>
              <code>{impact.archiveIntegrityAudit.auditId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveIntegrityAudit.gate}>{impact.archiveIntegrityAudit.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveIntegrityAudit.summary.totalRows}</strong></div>
            <div><span>Passed</span><strong data-status="pass">{impact.archiveIntegrityAudit.summary.passedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveIntegrityAudit.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveIntegrityAudit.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveIntegrityAudit.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-integrity-rows">
            {impact.archiveIntegrityAudit.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveIntegrityAuditStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.integrityRule}</p>
                <dl>
                  <div><dt>Archive</dt><dd title={row.sourceArchiveRowId}>{compactIdentifier(row.sourceArchiveRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.auditLane}</dd></div>
                  <div><dt>Integrity</dt><dd>{row.integrityRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.integrityResult}</dd></div>
                </dl>
                <code>{row.archiveEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveIntegrityAudit.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveIntegrityAudit.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveIntegrityAudit.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-memory-search">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Network size={17} aria-hidden="true" />
              <h3>Release Memory Search</h3>
            </div>
            <div>
              <span>{impact.releaseMemorySearch.reportVersion}</span>
              <strong>{impact.releaseMemorySearch.gate}</strong>
              <code>{impact.releaseMemorySearch.searchId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseMemorySearch.gate}>{impact.releaseMemorySearch.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseMemorySearch.summary.totalRows}</strong></div>
            <div><span>Found</span><strong data-status="pass">{impact.releaseMemorySearch.summary.foundRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseMemorySearch.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseMemorySearch.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseMemorySearch.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-release-memory-rows">
            {impact.releaseMemorySearch.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseMemorySearchStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.searchRule}</p>
                <dl>
                  <div><dt>Integrity</dt><dd title={row.sourceIntegrityRowId}>{compactIdentifier(row.sourceIntegrityRowId)}</dd></div>
                  <div><dt>Archive</dt><dd title={row.sourceArchiveRowId}>{compactIdentifier(row.sourceArchiveRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.queryLane}</dd></div>
                  <div><dt>Query</dt><dd>{row.memoryQuery}</dd></div>
                  <div><dt>Result</dt><dd>{row.searchResult}</dd></div>
                </dl>
                <code>{row.retrievalEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseMemorySearch.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseMemorySearch.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseMemorySearch.summary.nextAction}</code>
        </div>

        <div className="task-impact-archived-packet-restore">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Archived Packet Restore Rehearsal</h3>
            </div>
            <div>
              <span>{impact.archivedPacketRestoreRehearsal.reportVersion}</span>
              <strong>{impact.archivedPacketRestoreRehearsal.gate}</strong>
              <code>{impact.archivedPacketRestoreRehearsal.rehearsalId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archivedPacketRestoreRehearsal.gate}>{impact.archivedPacketRestoreRehearsal.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archivedPacketRestoreRehearsal.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.archivedPacketRestoreRehearsal.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archivedPacketRestoreRehearsal.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archivedPacketRestoreRehearsal.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archivedPacketRestoreRehearsal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archived-restore-rows">
            {impact.archivedPacketRestoreRehearsal.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archivedPacketRestoreRehearsalStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.restoreRule}</p>
                <dl>
                  <div><dt>Memory</dt><dd title={row.sourceMemoryRowId}>{compactIdentifier(row.sourceMemoryRowId)}</dd></div>
                  <div><dt>Integrity</dt><dd title={row.sourceIntegrityRowId}>{compactIdentifier(row.sourceIntegrityRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.restoreLane}</dd></div>
                  <div><dt>Restore</dt><dd>{row.restoreRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.restoreResult}</dd></div>
                </dl>
                <code>{row.productionEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archivedPacketRestoreRehearsal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archivedPacketRestoreRehearsal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archivedPacketRestoreRehearsal.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-retention-policy">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Archive Retention Policy Simulator</h3>
            </div>
            <div>
              <span>{impact.archiveRetentionPolicySimulator.reportVersion}</span>
              <strong>{impact.archiveRetentionPolicySimulator.gate}</strong>
              <code>{impact.archiveRetentionPolicySimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveRetentionPolicySimulator.gate}>{impact.archiveRetentionPolicySimulator.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveRetentionPolicySimulator.summary.totalRows}</strong></div>
            <div><span>Kept</span><strong data-status="pass">{impact.archiveRetentionPolicySimulator.summary.keptRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveRetentionPolicySimulator.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveRetentionPolicySimulator.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveRetentionPolicySimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-retention-rows">
            {impact.archiveRetentionPolicySimulator.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveRetentionPolicySimulatorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.retentionRule}</p>
                <dl>
                  <div><dt>Restore</dt><dd title={row.sourceRestoreRowId}>{compactIdentifier(row.sourceRestoreRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.retentionLane}</dd></div>
                  <div><dt>Policy</dt><dd>{row.retentionPolicy}</dd></div>
                  <div><dt>Retention</dt><dd>{row.retentionRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.retentionResult}</dd></div>
                </dl>
                <code>{row.archiveEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveRetentionPolicySimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveRetentionPolicySimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveRetentionPolicySimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-memory-timeline">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Release Memory Diff Timeline</h3>
            </div>
            <div>
              <span>{impact.releaseMemoryDiffTimeline.reportVersion}</span>
              <strong>{impact.releaseMemoryDiffTimeline.gate}</strong>
              <code>{impact.releaseMemoryDiffTimeline.timelineId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseMemoryDiffTimeline.gate}>{impact.releaseMemoryDiffTimeline.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseMemoryDiffTimeline.summary.totalRows}</strong></div>
            <div><span>Stable</span><strong data-status="pass">{impact.releaseMemoryDiffTimeline.summary.stableRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseMemoryDiffTimeline.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseMemoryDiffTimeline.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseMemoryDiffTimeline.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-memory-timeline-rows">
            {impact.releaseMemoryDiffTimeline.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseMemoryDiffTimelineStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.timelineRule}</p>
                <dl>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRowId}>{compactIdentifier(row.sourceRetentionRowId)}</dd></div>
                  <div><dt>Memory</dt><dd title={row.sourceMemoryRowId}>{compactIdentifier(row.sourceMemoryRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.timelineLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.diffWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.timelineResult}</dd></div>
                </dl>
                <code>{row.memoryEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseMemoryDiffTimeline.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseMemoryDiffTimeline.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseMemoryDiffTimeline.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-approval-packet">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Restore Approval Packet</h3>
            </div>
            <div>
              <span>{impact.restoreApprovalPacket.reportVersion}</span>
              <strong>{impact.restoreApprovalPacket.gate}</strong>
              <code>{impact.restoreApprovalPacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreApprovalPacket.gate}>{impact.restoreApprovalPacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreApprovalPacket.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreApprovalPacket.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreApprovalPacket.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreApprovalPacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreApprovalPacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-approval-rows">
            {impact.restoreApprovalPacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreApprovalPacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.approvalRule}</p>
                <dl>
                  <div><dt>Timeline</dt><dd title={row.sourceTimelineRowId}>{compactIdentifier(row.sourceTimelineRowId)}</dd></div>
                  <div><dt>Restore</dt><dd title={row.sourceRestoreRowId}>{compactIdentifier(row.sourceRestoreRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.approvalLane}</dd></div>
                  <div><dt>Approval</dt><dd>{row.approvalRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.approvalResult}</dd></div>
                </dl>
                <code>{row.releaseEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreApprovalPacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreApprovalPacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreApprovalPacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-access-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <KeyRound size={17} aria-hidden="true" />
              <h3>Archive Access Review Ledger</h3>
            </div>
            <div>
              <span>{impact.archiveAccessReviewLedger.reportVersion}</span>
              <strong>{impact.archiveAccessReviewLedger.gate}</strong>
              <code>{impact.archiveAccessReviewLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveAccessReviewLedger.gate}>{impact.archiveAccessReviewLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveAccessReviewLedger.summary.totalRows}</strong></div>
            <div><span>Granted</span><strong data-status="pass">{impact.archiveAccessReviewLedger.summary.grantedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveAccessReviewLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveAccessReviewLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveAccessReviewLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-access-rows">
            {impact.archiveAccessReviewLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveAccessReviewLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.accessRule}</p>
                <dl>
                  <div><dt>Approval</dt><dd title={row.sourceApprovalRowId}>{compactIdentifier(row.sourceApprovalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.accessLane}</dd></div>
                  <div><dt>Requester</dt><dd>{row.requesterRole}</dd></div>
                  <div><dt>Access</dt><dd>{row.accessRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.accessResult}</dd></div>
                </dl>
                <code>{row.auditEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveAccessReviewLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveAccessReviewLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveAccessReviewLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-incident-drillbook">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Restore Incident Drillbook</h3>
            </div>
            <div>
              <span>{impact.restoreIncidentDrillbook.reportVersion}</span>
              <strong>{impact.restoreIncidentDrillbook.gate}</strong>
              <code>{impact.restoreIncidentDrillbook.drillbookId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreIncidentDrillbook.gate}>{impact.restoreIncidentDrillbook.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreIncidentDrillbook.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreIncidentDrillbook.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreIncidentDrillbook.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreIncidentDrillbook.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreIncidentDrillbook.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-drillbook-rows">
            {impact.restoreIncidentDrillbook.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreIncidentDrillbookStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.drillRule}</p>
                <dl>
                  <div><dt>Access</dt><dd title={row.sourceAccessRowId}>{compactIdentifier(row.sourceAccessRowId)}</dd></div>
                  <div><dt>Approval</dt><dd title={row.sourceApprovalRowId}>{compactIdentifier(row.sourceApprovalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.drillLane}</dd></div>
                  <div><dt>Incident</dt><dd>{row.incidentRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.drillResult}</dd></div>
                </dl>
                <code>{row.responseEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreIncidentDrillbook.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreIncidentDrillbook.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreIncidentDrillbook.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-memory-ownership-transfer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Waypoints size={17} aria-hidden="true" />
              <h3>Release Memory Ownership Transfer</h3>
            </div>
            <div>
              <span>{impact.releaseMemoryOwnershipTransfer.reportVersion}</span>
              <strong>{impact.releaseMemoryOwnershipTransfer.gate}</strong>
              <code>{impact.releaseMemoryOwnershipTransfer.transferId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseMemoryOwnershipTransfer.gate}>{impact.releaseMemoryOwnershipTransfer.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseMemoryOwnershipTransfer.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.releaseMemoryOwnershipTransfer.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseMemoryOwnershipTransfer.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseMemoryOwnershipTransfer.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseMemoryOwnershipTransfer.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-memory-ownership-rows">
            {impact.releaseMemoryOwnershipTransfer.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseMemoryOwnershipTransferStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.transferRule}</p>
                <dl>
                  <div><dt>Drill</dt><dd title={row.sourceDrillRowId}>{compactIdentifier(row.sourceDrillRowId)}</dd></div>
                  <div><dt>Access</dt><dd title={row.sourceAccessRowId}>{compactIdentifier(row.sourceAccessRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>New Owner</dt><dd>{row.newOwner}</dd></div>
                  <div><dt>Transfer</dt><dd>{row.transferRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.transferResult}</dd></div>
                </dl>
                <code>{row.ownershipEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseMemoryOwnershipTransfer.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseMemoryOwnershipTransfer.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseMemoryOwnershipTransfer.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-readiness-audit">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Restore Readiness Replay Audit</h3>
            </div>
            <div>
              <span>{impact.restoreReadinessReplayAudit.reportVersion}</span>
              <strong>{impact.restoreReadinessReplayAudit.gate}</strong>
              <code>{impact.restoreReadinessReplayAudit.auditId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreReadinessReplayAudit.gate}>{impact.restoreReadinessReplayAudit.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreReadinessReplayAudit.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreReadinessReplayAudit.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreReadinessReplayAudit.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreReadinessReplayAudit.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreReadinessReplayAudit.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-readiness-audit-rows">
            {impact.restoreReadinessReplayAudit.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreReadinessReplayAuditStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayRule}</p>
                <dl>
                  <div><dt>Transfer</dt><dd title={row.sourceTransferRowId}>{compactIdentifier(row.sourceTransferRowId)}</dd></div>
                  <div><dt>Drill</dt><dd title={row.sourceDrillRowId}>{compactIdentifier(row.sourceDrillRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.replayLane}</dd></div>
                  <div><dt>Replay</dt><dd>{row.replayRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.replayResult}</dd></div>
                </dl>
                <code>{row.auditEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreReadinessReplayAudit.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreReadinessReplayAudit.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreReadinessReplayAudit.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-permission-expiry">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Archive Permission Expiry Monitor</h3>
            </div>
            <div>
              <span>{impact.archivePermissionExpiryMonitor.reportVersion}</span>
              <strong>{impact.archivePermissionExpiryMonitor.gate}</strong>
              <code>{impact.archivePermissionExpiryMonitor.monitorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archivePermissionExpiryMonitor.gate}>{impact.archivePermissionExpiryMonitor.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archivePermissionExpiryMonitor.summary.totalRows}</strong></div>
            <div><span>Valid</span><strong data-status="pass">{impact.archivePermissionExpiryMonitor.summary.validRows}</strong></div>
            <div><span>Expiring</span><strong data-status="review">{impact.archivePermissionExpiryMonitor.summary.expiringRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archivePermissionExpiryMonitor.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archivePermissionExpiryMonitor.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-permission-expiry-rows">
            {impact.archivePermissionExpiryMonitor.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archivePermissionExpiryMonitorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.permissionRule}</p>
                <dl>
                  <div><dt>Replay</dt><dd title={row.sourceReplayRowId}>{compactIdentifier(row.sourceReplayRowId)}</dd></div>
                  <div><dt>Access</dt><dd title={row.sourceAccessRowId}>{compactIdentifier(row.sourceAccessRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.permissionLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.expiryWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.permissionResult}</dd></div>
                </dl>
                <code>{row.expiryEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archivePermissionExpiryMonitor.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archivePermissionExpiryMonitor.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archivePermissionExpiryMonitor.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-memory-audit-bundle">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Release Memory Audit Export Bundle</h3>
            </div>
            <div>
              <span>{impact.releaseMemoryAuditExportBundle.reportVersion}</span>
              <strong>{impact.releaseMemoryAuditExportBundle.gate}</strong>
              <code>{impact.releaseMemoryAuditExportBundle.bundleId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseMemoryAuditExportBundle.gate}>{impact.releaseMemoryAuditExportBundle.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseMemoryAuditExportBundle.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.releaseMemoryAuditExportBundle.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseMemoryAuditExportBundle.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseMemoryAuditExportBundle.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseMemoryAuditExportBundle.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-audit-bundle-rows">
            {impact.releaseMemoryAuditExportBundle.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseMemoryAuditExportBundleStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.bundleRule}</p>
                <dl>
                  <div><dt>Permission</dt><dd title={row.sourcePermissionRowId}>{compactIdentifier(row.sourcePermissionRowId)}</dd></div>
                  <div><dt>Transfer</dt><dd title={row.sourceTransferRowId}>{compactIdentifier(row.sourceTransferRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.bundleLane}</dd></div>
                  <div><dt>Format</dt><dd>{row.exportFormat}</dd></div>
                  <div><dt>Result</dt><dd>{row.bundleResult}</dd></div>
                </dl>
                <code>{row.packageEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseMemoryAuditExportBundle.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseMemoryAuditExportBundle.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseMemoryAuditExportBundle.summary.nextAction}</code>
        </div>

        <div className="task-impact-audit-signoff-queue">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Audit Bundle Reviewer Signoff Queue</h3>
            </div>
            <div>
              <span>{impact.auditBundleReviewerSignoffQueue.reportVersion}</span>
              <strong>{impact.auditBundleReviewerSignoffQueue.gate}</strong>
              <code>{impact.auditBundleReviewerSignoffQueue.queueId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.auditBundleReviewerSignoffQueue.gate}>{impact.auditBundleReviewerSignoffQueue.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.auditBundleReviewerSignoffQueue.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.auditBundleReviewerSignoffQueue.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.auditBundleReviewerSignoffQueue.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.auditBundleReviewerSignoffQueue.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.auditBundleReviewerSignoffQueue.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-audit-signoff-rows">
            {impact.auditBundleReviewerSignoffQueue.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{auditBundleReviewerSignoffQueueStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.signoffRule}</p>
                <dl>
                  <div><dt>Bundle</dt><dd title={row.sourceBundleRowId}>{compactIdentifier(row.sourceBundleRowId)}</dd></div>
                  <div><dt>Permission</dt><dd title={row.sourcePermissionRowId}>{compactIdentifier(row.sourcePermissionRowId)}</dd></div>
                  <div><dt>Reviewer</dt><dd>{row.reviewer}</dd></div>
                  <div><dt>Lane</dt><dd>{row.queueLane}</dd></div>
                  <div><dt>Queue</dt><dd>{row.queueRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.signoffResult}</dd></div>
                </dl>
                <code>{row.reviewerEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.auditBundleReviewerSignoffQueue.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.auditBundleReviewerSignoffQueue.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.auditBundleReviewerSignoffQueue.summary.nextAction}</code>
        </div>

        <div className="task-impact-permission-renewal-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Permission Renewal Replay Simulator</h3>
            </div>
            <div>
              <span>{impact.permissionRenewalReplaySimulator.reportVersion}</span>
              <strong>{impact.permissionRenewalReplaySimulator.gate}</strong>
              <code>{impact.permissionRenewalReplaySimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.permissionRenewalReplaySimulator.gate}>{impact.permissionRenewalReplaySimulator.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.permissionRenewalReplaySimulator.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.permissionRenewalReplaySimulator.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.permissionRenewalReplaySimulator.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.permissionRenewalReplaySimulator.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.permissionRenewalReplaySimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-renewal-replay-rows">
            {impact.permissionRenewalReplaySimulator.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{permissionRenewalReplaySimulatorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.renewalRule}</p>
                <dl>
                  <div><dt>Signoff</dt><dd title={row.sourceSignoffRowId}>{compactIdentifier(row.sourceSignoffRowId)}</dd></div>
                  <div><dt>Permission</dt><dd title={row.sourcePermissionRowId}>{compactIdentifier(row.sourcePermissionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.renewalLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.renewalWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.renewalResult}</dd></div>
                </dl>
                <code>{row.simulatorEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.permissionRenewalReplaySimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.permissionRenewalReplaySimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.permissionRenewalReplaySimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-memory-notarization">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Restore Memory Evidence Notarization</h3>
            </div>
            <div>
              <span>{impact.restoreMemoryEvidenceNotarization.reportVersion}</span>
              <strong>{impact.restoreMemoryEvidenceNotarization.gate}</strong>
              <code>{impact.restoreMemoryEvidenceNotarization.notarizationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreMemoryEvidenceNotarization.gate}>{impact.restoreMemoryEvidenceNotarization.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreMemoryEvidenceNotarization.summary.totalRows}</strong></div>
            <div><span>Notarized</span><strong data-status="pass">{impact.restoreMemoryEvidenceNotarization.summary.notarizedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreMemoryEvidenceNotarization.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreMemoryEvidenceNotarization.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreMemoryEvidenceNotarization.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-memory-notary-rows">
            {impact.restoreMemoryEvidenceNotarization.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreMemoryEvidenceNotarizationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.notaryRule}</p>
                <dl>
                  <div><dt>Renewal</dt><dd title={row.sourceRenewalRowId}>{compactIdentifier(row.sourceRenewalRowId)}</dd></div>
                  <div><dt>Replay</dt><dd title={row.sourceReplayRowId}>{compactIdentifier(row.sourceReplayRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.notaryLane}</dd></div>
                  <div><dt>Digest</dt><dd>{row.digestAlgorithm}</dd></div>
                  <div><dt>Result</dt><dd>{row.notaryResult}</dd></div>
                </dl>
                <code>{row.evidenceEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreMemoryEvidenceNotarization.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreMemoryEvidenceNotarization.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreMemoryEvidenceNotarization.summary.nextAction}</code>
        </div>

        <div className="task-impact-release-memory-query-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Network size={17} aria-hidden="true" />
              <h3>Release Memory Query Replay</h3>
            </div>
            <div>
              <span>{impact.releaseMemoryQueryReplay.reportVersion}</span>
              <strong>{impact.releaseMemoryQueryReplay.gate}</strong>
              <code>{impact.releaseMemoryQueryReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.releaseMemoryQueryReplay.gate}>{impact.releaseMemoryQueryReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.releaseMemoryQueryReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.releaseMemoryQueryReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.releaseMemoryQueryReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.releaseMemoryQueryReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.releaseMemoryQueryReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-memory-query-replay-rows">
            {impact.releaseMemoryQueryReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{releaseMemoryQueryReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.queryRule}</p>
                <dl>
                  <div><dt>Notary</dt><dd title={row.sourceNotaryRowId}>{compactIdentifier(row.sourceNotaryRowId)}</dd></div>
                  <div><dt>Memory</dt><dd title={row.sourceMemoryRowId}>{compactIdentifier(row.sourceMemoryRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.queryLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.queryScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.queryResult}</dd></div>
                </dl>
                <code>{row.replayEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.releaseMemoryQueryReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.releaseMemoryQueryReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.releaseMemoryQueryReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-approval-comparison">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Restore Approval Comparison</h3>
            </div>
            <div>
              <span>{impact.restoreApprovalComparison.reportVersion}</span>
              <strong>{impact.restoreApprovalComparison.gate}</strong>
              <code>{impact.restoreApprovalComparison.comparisonId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreApprovalComparison.gate}>{impact.restoreApprovalComparison.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreApprovalComparison.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.restoreApprovalComparison.summary.matchedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreApprovalComparison.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreApprovalComparison.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreApprovalComparison.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-comparison-rows">
            {impact.restoreApprovalComparison.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreApprovalComparisonStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.comparisonRule}</p>
                <dl>
                  <div><dt>Query</dt><dd title={row.sourceQueryRowId}>{compactIdentifier(row.sourceQueryRowId)}</dd></div>
                  <div><dt>Approval</dt><dd title={row.sourceApprovalRowId}>{compactIdentifier(row.sourceApprovalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.comparisonLane}</dd></div>
                  <div><dt>Delta</dt><dd>{row.deltaSummary}</dd></div>
                  <div><dt>Result</dt><dd>{row.comparisonResult}</dd></div>
                </dl>
                <code>{row.comparisonEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreApprovalComparison.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreApprovalComparison.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreApprovalComparison.summary.nextAction}</code>
        </div>

        <div className="task-impact-audit-retention-renewal-dashboard">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Audit Packet Retention Renewal Dashboard</h3>
            </div>
            <div>
              <span>{impact.auditPacketRetentionRenewalDashboard.reportVersion}</span>
              <strong>{impact.auditPacketRetentionRenewalDashboard.gate}</strong>
              <code>{impact.auditPacketRetentionRenewalDashboard.dashboardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.auditPacketRetentionRenewalDashboard.gate}>{impact.auditPacketRetentionRenewalDashboard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.auditPacketRetentionRenewalDashboard.summary.totalRows}</strong></div>
            <div><span>Renewed</span><strong data-status="pass">{impact.auditPacketRetentionRenewalDashboard.summary.renewedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.auditPacketRetentionRenewalDashboard.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.auditPacketRetentionRenewalDashboard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.auditPacketRetentionRenewalDashboard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-retention-renewal-rows">
            {impact.auditPacketRetentionRenewalDashboard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{auditPacketRetentionRenewalDashboardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.dashboardRule}</p>
                <dl>
                  <div><dt>Compare</dt><dd title={row.sourceComparisonRowId}>{compactIdentifier(row.sourceComparisonRowId)}</dd></div>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRowId}>{compactIdentifier(row.sourceRetentionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.dashboardLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.retentionWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.dashboardResult}</dd></div>
                </dl>
                <code>{row.renewalEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.auditPacketRetentionRenewalDashboard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.auditPacketRetentionRenewalDashboard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.auditPacketRetentionRenewalDashboard.summary.nextAction}</code>
        </div>

        <div className="task-impact-audit-query-exception-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Audit Query Exception Ledger</h3>
            </div>
            <div>
              <span>{impact.auditQueryExceptionLedger.reportVersion}</span>
              <strong>{impact.auditQueryExceptionLedger.gate}</strong>
              <code>{impact.auditQueryExceptionLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.auditQueryExceptionLedger.gate}>{impact.auditQueryExceptionLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.auditQueryExceptionLedger.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.auditQueryExceptionLedger.summary.closedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.auditQueryExceptionLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.auditQueryExceptionLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.auditQueryExceptionLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-query-exception-rows">
            {impact.auditQueryExceptionLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{auditQueryExceptionLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.ledgerRule}</p>
                <dl>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRenewalRowId}>{compactIdentifier(row.sourceRetentionRenewalRowId)}</dd></div>
                  <div><dt>Query</dt><dd title={row.sourceQueryRowId}>{compactIdentifier(row.sourceQueryRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.exceptionLane}</dd></div>
                  <div><dt>Type</dt><dd>{row.exceptionType}</dd></div>
                  <div><dt>Result</dt><dd>{row.ledgerResult}</dd></div>
                </dl>
                <code>{row.exceptionEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.auditQueryExceptionLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.auditQueryExceptionLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.auditQueryExceptionLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-retention-owner-response-importer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Download size={17} aria-hidden="true" />
              <h3>Retention Owner Response Importer</h3>
            </div>
            <div>
              <span>{impact.retentionOwnerResponseImporter.reportVersion}</span>
              <strong>{impact.retentionOwnerResponseImporter.gate}</strong>
              <code>{impact.retentionOwnerResponseImporter.importerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.retentionOwnerResponseImporter.gate}>{impact.retentionOwnerResponseImporter.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.retentionOwnerResponseImporter.summary.totalRows}</strong></div>
            <div><span>Imported</span><strong data-status="pass">{impact.retentionOwnerResponseImporter.summary.importedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.retentionOwnerResponseImporter.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.retentionOwnerResponseImporter.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.retentionOwnerResponseImporter.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-retention-response-rows">
            {impact.retentionOwnerResponseImporter.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{retentionOwnerResponseImporterStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.responseRule}</p>
                <dl>
                  <div><dt>Exception</dt><dd title={row.sourceExceptionRowId}>{compactIdentifier(row.sourceExceptionRowId)}</dd></div>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRenewalRowId}>{compactIdentifier(row.sourceRetentionRenewalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.responseLane}</dd></div>
                  <div><dt>Source</dt><dd>{row.responseSource}</dd></div>
                  <div><dt>Result</dt><dd>{row.responseResult}</dd></div>
                </dl>
                <code>{row.importEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.retentionOwnerResponseImporter.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.retentionOwnerResponseImporter.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.retentionOwnerResponseImporter.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-memory-packet-handoff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>Restore Memory Packet Handoff</h3>
            </div>
            <div>
              <span>{impact.restoreMemoryPacketHandoff.reportVersion}</span>
              <strong>{impact.restoreMemoryPacketHandoff.gate}</strong>
              <code>{impact.restoreMemoryPacketHandoff.handoffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreMemoryPacketHandoff.gate}>{impact.restoreMemoryPacketHandoff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreMemoryPacketHandoff.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreMemoryPacketHandoff.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreMemoryPacketHandoff.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreMemoryPacketHandoff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreMemoryPacketHandoff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-memory-handoff-rows">
            {impact.restoreMemoryPacketHandoff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreMemoryPacketHandoffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.handoffRule}</p>
                <dl>
                  <div><dt>Response</dt><dd title={row.sourceResponseRowId}>{compactIdentifier(row.sourceResponseRowId)}</dd></div>
                  <div><dt>Approval</dt><dd title={row.sourceApprovalComparisonRowId}>{compactIdentifier(row.sourceApprovalComparisonRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.handoffLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.packetScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.handoffResult}</dd></div>
                </dl>
                <code>{row.handoffEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreMemoryPacketHandoff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreMemoryPacketHandoff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreMemoryPacketHandoff.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-packet-acceptance-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Restore Packet Acceptance Replay</h3>
            </div>
            <div>
              <span>{impact.restorePacketAcceptanceReplay.reportVersion}</span>
              <strong>{impact.restorePacketAcceptanceReplay.gate}</strong>
              <code>{impact.restorePacketAcceptanceReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restorePacketAcceptanceReplay.gate}>{impact.restorePacketAcceptanceReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restorePacketAcceptanceReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.restorePacketAcceptanceReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restorePacketAcceptanceReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restorePacketAcceptanceReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restorePacketAcceptanceReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-acceptance-rows">
            {impact.restorePacketAcceptanceReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restorePacketAcceptanceReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceRule}</p>
                <dl>
                  <div><dt>Handoff</dt><dd title={row.sourceHandoffRowId}>{compactIdentifier(row.sourceHandoffRowId)}</dd></div>
                  <div><dt>Replay</dt><dd title={row.sourceAcceptanceReplayId}>{compactIdentifier(row.sourceAcceptanceReplayId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.acceptanceLane}</dd></div>
                  <div><dt>Ref</dt><dd>{row.acceptanceRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.acceptanceResult}</dd></div>
                </dl>
                <code>{row.replayEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restorePacketAcceptanceReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restorePacketAcceptanceReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restorePacketAcceptanceReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-handoff-owner-sla-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Handoff Owner SLA Board</h3>
            </div>
            <div>
              <span>{impact.handoffOwnerSlaBoard.reportVersion}</span>
              <strong>{impact.handoffOwnerSlaBoard.gate}</strong>
              <code>{impact.handoffOwnerSlaBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.handoffOwnerSlaBoard.gate}>{impact.handoffOwnerSlaBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.handoffOwnerSlaBoard.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.handoffOwnerSlaBoard.summary.clearRows}</strong></div>
            <div><span>Watch</span><strong data-status="review">{impact.handoffOwnerSlaBoard.summary.watchRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.handoffOwnerSlaBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.handoffOwnerSlaBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-handoff-sla-rows">
            {impact.handoffOwnerSlaBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{handoffOwnerSlaBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.slaRule}</p>
                <dl>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceRowId}>{compactIdentifier(row.sourceAcceptanceRowId)}</dd></div>
                  <div><dt>Response</dt><dd title={row.sourceResponseRowId}>{compactIdentifier(row.sourceResponseRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.slaLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.slaWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.slaResult}</dd></div>
                </dl>
                <code>{row.slaEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.handoffOwnerSlaBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.handoffOwnerSlaBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.handoffOwnerSlaBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-restoration-drill-exporter">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Archive Restoration Drill Exporter</h3>
            </div>
            <div>
              <span>{impact.archiveRestorationDrillExporter.reportVersion}</span>
              <strong>{impact.archiveRestorationDrillExporter.gate}</strong>
              <code>{impact.archiveRestorationDrillExporter.exporterId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveRestorationDrillExporter.gate}>{impact.archiveRestorationDrillExporter.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveRestorationDrillExporter.summary.totalRows}</strong></div>
            <div><span>Exported</span><strong data-status="pass">{impact.archiveRestorationDrillExporter.summary.exportedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveRestorationDrillExporter.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveRestorationDrillExporter.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveRestorationDrillExporter.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restoration-drill-rows">
            {impact.archiveRestorationDrillExporter.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveRestorationDrillExporterStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.drillRule}</p>
                <dl>
                  <div><dt>SLA</dt><dd title={row.sourceSlaRowId}>{compactIdentifier(row.sourceSlaRowId)}</dd></div>
                  <div><dt>Rehearsal</dt><dd title={row.sourceRestoreRehearsalRowId}>{compactIdentifier(row.sourceRestoreRehearsalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.drillLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.exportScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.drillResult}</dd></div>
                </dl>
                <code>{row.exportEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveRestorationDrillExporter.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveRestorationDrillExporter.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveRestorationDrillExporter.summary.nextAction}</code>
        </div>

        <div className="task-impact-restoration-drill-acceptance-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Restoration Drill Acceptance Ledger</h3>
            </div>
            <div>
              <span>{impact.restorationDrillAcceptanceLedger.reportVersion}</span>
              <strong>{impact.restorationDrillAcceptanceLedger.gate}</strong>
              <code>{impact.restorationDrillAcceptanceLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restorationDrillAcceptanceLedger.gate}>{impact.restorationDrillAcceptanceLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restorationDrillAcceptanceLedger.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.restorationDrillAcceptanceLedger.summary.acceptedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restorationDrillAcceptanceLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restorationDrillAcceptanceLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restorationDrillAcceptanceLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restoration-acceptance-rows">
            {impact.restorationDrillAcceptanceLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restorationDrillAcceptanceLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceRule}</p>
                <dl>
                  <div><dt>Drill Export</dt><dd title={row.sourceDrillExportRowId}>{compactIdentifier(row.sourceDrillExportRowId)}</dd></div>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceReplayId}>{compactIdentifier(row.sourceAcceptanceReplayId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.acceptanceLane}</dd></div>
                  <div><dt>Ref</dt><dd>{row.acceptanceRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.acceptanceResult}</dd></div>
                </dl>
                <code>{row.ledgerEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restorationDrillAcceptanceLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restorationDrillAcceptanceLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restorationDrillAcceptanceLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-drill-owner-response-importer">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Download size={17} aria-hidden="true" />
              <h3>Archive Drill Owner Response Importer</h3>
            </div>
            <div>
              <span>{impact.archiveDrillOwnerResponseImporter.reportVersion}</span>
              <strong>{impact.archiveDrillOwnerResponseImporter.gate}</strong>
              <code>{impact.archiveDrillOwnerResponseImporter.importerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveDrillOwnerResponseImporter.gate}>{impact.archiveDrillOwnerResponseImporter.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveDrillOwnerResponseImporter.summary.totalRows}</strong></div>
            <div><span>Imported</span><strong data-status="pass">{impact.archiveDrillOwnerResponseImporter.summary.importedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveDrillOwnerResponseImporter.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveDrillOwnerResponseImporter.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveDrillOwnerResponseImporter.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-drill-response-rows">
            {impact.archiveDrillOwnerResponseImporter.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveDrillOwnerResponseImporterStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.responseRule}</p>
                <dl>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceRowId}>{compactIdentifier(row.sourceAcceptanceRowId)}</dd></div>
                  <div><dt>Response</dt><dd title={row.sourceResponseRowId}>{compactIdentifier(row.sourceResponseRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.responseLane}</dd></div>
                  <div><dt>Source</dt><dd>{row.responseSource}</dd></div>
                  <div><dt>Result</dt><dd>{row.responseResult}</dd></div>
                </dl>
                <code>{row.importEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveDrillOwnerResponseImporter.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveDrillOwnerResponseImporter.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveDrillOwnerResponseImporter.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-operations-readiness-digest">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Activity size={17} aria-hidden="true" />
              <h3>Restore Operations Readiness Digest</h3>
            </div>
            <div>
              <span>{impact.restoreOperationsReadinessDigest.reportVersion}</span>
              <strong>{impact.restoreOperationsReadinessDigest.gate}</strong>
              <code>{impact.restoreOperationsReadinessDigest.digestId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreOperationsReadinessDigest.gate}>{impact.restoreOperationsReadinessDigest.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreOperationsReadinessDigest.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreOperationsReadinessDigest.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreOperationsReadinessDigest.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreOperationsReadinessDigest.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreOperationsReadinessDigest.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-ops-digest-rows">
            {impact.restoreOperationsReadinessDigest.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreOperationsReadinessDigestStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.digestRule}</p>
                <dl>
                  <div><dt>Response</dt><dd title={row.sourceResponseRowId}>{compactIdentifier(row.sourceResponseRowId)}</dd></div>
                  <div><dt>SLA</dt><dd title={row.sourceSlaRowId}>{compactIdentifier(row.sourceSlaRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.digestLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.digestScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.digestResult}</dd></div>
                </dl>
                <code>{row.opsEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreOperationsReadinessDigest.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreOperationsReadinessDigest.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreOperationsReadinessDigest.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-readiness-exception-closeout">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Restore Readiness Exception Closeout</h3>
            </div>
            <div>
              <span>{impact.restoreReadinessExceptionCloseout.reportVersion}</span>
              <strong>{impact.restoreReadinessExceptionCloseout.gate}</strong>
              <code>{impact.restoreReadinessExceptionCloseout.closeoutId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreReadinessExceptionCloseout.gate}>{impact.restoreReadinessExceptionCloseout.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreReadinessExceptionCloseout.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.restoreReadinessExceptionCloseout.summary.closedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreReadinessExceptionCloseout.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreReadinessExceptionCloseout.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreReadinessExceptionCloseout.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-exception-closeout-rows">
            {impact.restoreReadinessExceptionCloseout.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreReadinessExceptionCloseoutStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.closeoutRule}</p>
                <dl>
                  <div><dt>Digest</dt><dd title={row.sourceDigestRowId}>{compactIdentifier(row.sourceDigestRowId)}</dd></div>
                  <div><dt>Exception</dt><dd title={row.sourceExceptionRowId}>{compactIdentifier(row.sourceExceptionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.closeoutLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.closeoutScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.closeoutResult}</dd></div>
                </dl>
                <code>{row.closeoutEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreReadinessExceptionCloseout.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreReadinessExceptionCloseout.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreReadinessExceptionCloseout.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-ops-sla-escalation-queue">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Rocket size={17} aria-hidden="true" />
              <h3>Archive Ops SLA Escalation Queue</h3>
            </div>
            <div>
              <span>{impact.archiveOpsSlaEscalationQueue.reportVersion}</span>
              <strong>{impact.archiveOpsSlaEscalationQueue.gate}</strong>
              <code>{impact.archiveOpsSlaEscalationQueue.queueId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveOpsSlaEscalationQueue.gate}>{impact.archiveOpsSlaEscalationQueue.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveOpsSlaEscalationQueue.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.archiveOpsSlaEscalationQueue.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveOpsSlaEscalationQueue.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveOpsSlaEscalationQueue.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveOpsSlaEscalationQueue.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-ops-escalation-rows">
            {impact.archiveOpsSlaEscalationQueue.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveOpsSlaEscalationQueueStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.escalationRule}</p>
                <dl>
                  <div><dt>Closeout</dt><dd title={row.sourceCloseoutRowId}>{compactIdentifier(row.sourceCloseoutRowId)}</dd></div>
                  <div><dt>SLA</dt><dd title={row.sourceSlaRowId}>{compactIdentifier(row.sourceSlaRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.escalationLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.escalationWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.escalationResult}</dd></div>
                </dl>
                <code>{row.queueEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveOpsSlaEscalationQueue.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveOpsSlaEscalationQueue.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveOpsSlaEscalationQueue.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-command-rehearsal-lock">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <KeyRound size={17} aria-hidden="true" />
              <h3>Restore Command Rehearsal Lock</h3>
            </div>
            <div>
              <span>{impact.restoreCommandRehearsalLock.reportVersion}</span>
              <strong>{impact.restoreCommandRehearsalLock.gate}</strong>
              <code>{impact.restoreCommandRehearsalLock.lockId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreCommandRehearsalLock.gate}>{impact.restoreCommandRehearsalLock.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreCommandRehearsalLock.summary.totalRows}</strong></div>
            <div><span>Locked</span><strong data-status="pass">{impact.restoreCommandRehearsalLock.summary.lockedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreCommandRehearsalLock.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreCommandRehearsalLock.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreCommandRehearsalLock.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-command-lock-rows">
            {impact.restoreCommandRehearsalLock.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreCommandRehearsalLockStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.commandRule}</p>
                <dl>
                  <div><dt>Escalation</dt><dd title={row.sourceEscalationRowId}>{compactIdentifier(row.sourceEscalationRowId)}</dd></div>
                  <div><dt>Rehearsal</dt><dd title={row.sourceRestoreRehearsalRowId}>{compactIdentifier(row.sourceRestoreRehearsalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.commandLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.commandScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.commandResult}</dd></div>
                </dl>
                <code>{row.lockEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreCommandRehearsalLock.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreCommandRehearsalLock.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreCommandRehearsalLock.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-lock-reviewer-signoff-queue">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Restore Lock Reviewer Signoff Queue</h3>
            </div>
            <div>
              <span>{impact.restoreLockReviewerSignoffQueue.reportVersion}</span>
              <strong>{impact.restoreLockReviewerSignoffQueue.gate}</strong>
              <code>{impact.restoreLockReviewerSignoffQueue.queueId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreLockReviewerSignoffQueue.gate}>{impact.restoreLockReviewerSignoffQueue.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreLockReviewerSignoffQueue.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreLockReviewerSignoffQueue.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreLockReviewerSignoffQueue.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreLockReviewerSignoffQueue.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreLockReviewerSignoffQueue.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-lock-signoff-rows">
            {impact.restoreLockReviewerSignoffQueue.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreLockReviewerSignoffQueueStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.signoffRule}</p>
                <dl>
                  <div><dt>Command Lock</dt><dd title={row.sourceCommandLockRowId}>{compactIdentifier(row.sourceCommandLockRowId)}</dd></div>
                  <div><dt>Audit Signoff</dt><dd title={row.sourceAuditSignoffRowId}>{compactIdentifier(row.sourceAuditSignoffRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.signoffLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.signoffScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.signoffResult}</dd></div>
                </dl>
                <code>{row.signoffEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreLockReviewerSignoffQueue.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreLockReviewerSignoffQueue.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreLockReviewerSignoffQueue.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-command-rollback-rehearse-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Archive Command Rollback Rehearse Diff</h3>
            </div>
            <div>
              <span>{impact.archiveCommandRollbackRehearseDiff.reportVersion}</span>
              <strong>{impact.archiveCommandRollbackRehearseDiff.gate}</strong>
              <code>{impact.archiveCommandRollbackRehearseDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveCommandRollbackRehearseDiff.gate}>{impact.archiveCommandRollbackRehearseDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveCommandRollbackRehearseDiff.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.archiveCommandRollbackRehearseDiff.summary.matchedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveCommandRollbackRehearseDiff.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveCommandRollbackRehearseDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveCommandRollbackRehearseDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-command-rollback-rows">
            {impact.archiveCommandRollbackRehearseDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveCommandRollbackRehearseDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.rollbackRule}</p>
                <dl>
                  <div><dt>Signoff</dt><dd title={row.sourceSignoffRowId}>{compactIdentifier(row.sourceSignoffRowId)}</dd></div>
                  <div><dt>Rollback Diff</dt><dd title={row.sourceRollbackDiffRowId}>{compactIdentifier(row.sourceRollbackDiffRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.rollbackLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.rollbackScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.rollbackResult}</dd></div>
                </dl>
                <code>{row.rollbackEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveCommandRollbackRehearseDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveCommandRollbackRehearseDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveCommandRollbackRehearseDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-execution-redline-packet">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Restore Execution Redline Packet</h3>
            </div>
            <div>
              <span>{impact.restoreExecutionRedlinePacket.reportVersion}</span>
              <strong>{impact.restoreExecutionRedlinePacket.gate}</strong>
              <code>{impact.restoreExecutionRedlinePacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreExecutionRedlinePacket.gate}>{impact.restoreExecutionRedlinePacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreExecutionRedlinePacket.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreExecutionRedlinePacket.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreExecutionRedlinePacket.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreExecutionRedlinePacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreExecutionRedlinePacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-redline-packet-rows">
            {impact.restoreExecutionRedlinePacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreExecutionRedlinePacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.redlineRule}</p>
                <dl>
                  <div><dt>Rollback Diff</dt><dd title={row.sourceRollbackDiffRowId}>{compactIdentifier(row.sourceRollbackDiffRowId)}</dd></div>
                  <div><dt>Approval</dt><dd title={row.sourceRestoreApprovalRowId}>{compactIdentifier(row.sourceRestoreApprovalRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.redlineLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.redlineScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.redlineResult}</dd></div>
                </dl>
                <code>{row.redlineEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreExecutionRedlinePacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreExecutionRedlinePacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreExecutionRedlinePacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-redline-owner-override-simulator">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Restore Redline Owner Override Simulator</h3>
            </div>
            <div>
              <span>{impact.restoreRedlineOwnerOverrideSimulator.reportVersion}</span>
              <strong>{impact.restoreRedlineOwnerOverrideSimulator.gate}</strong>
              <code>{impact.restoreRedlineOwnerOverrideSimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreRedlineOwnerOverrideSimulator.gate}>{impact.restoreRedlineOwnerOverrideSimulator.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreRedlineOwnerOverrideSimulator.summary.totalRows}</strong></div>
            <div><span>Simulated</span><strong data-status="pass">{impact.restoreRedlineOwnerOverrideSimulator.summary.simulatedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreRedlineOwnerOverrideSimulator.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreRedlineOwnerOverrideSimulator.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreRedlineOwnerOverrideSimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-redline-override-rows">
            {impact.restoreRedlineOwnerOverrideSimulator.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreRedlineOwnerOverrideSimulatorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.overrideRule}</p>
                <dl>
                  <div><dt>Redline</dt><dd title={row.sourceRedlineRowId}>{compactIdentifier(row.sourceRedlineRowId)}</dd></div>
                  <div><dt>Owner Response</dt><dd title={row.sourceOwnerResponseRowId}>{compactIdentifier(row.sourceOwnerResponseRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.overrideLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.overrideScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.overrideResult}</dd></div>
                </dl>
                <code>{row.overrideEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreRedlineOwnerOverrideSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreRedlineOwnerOverrideSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreRedlineOwnerOverrideSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-execution-blackbox-recorder">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Archive Execution Blackbox Recorder</h3>
            </div>
            <div>
              <span>{impact.archiveExecutionBlackboxRecorder.reportVersion}</span>
              <strong>{impact.archiveExecutionBlackboxRecorder.gate}</strong>
              <code>{impact.archiveExecutionBlackboxRecorder.recorderId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveExecutionBlackboxRecorder.gate}>{impact.archiveExecutionBlackboxRecorder.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveExecutionBlackboxRecorder.summary.totalRows}</strong></div>
            <div><span>Recorded</span><strong data-status="pass">{impact.archiveExecutionBlackboxRecorder.summary.recordedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveExecutionBlackboxRecorder.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveExecutionBlackboxRecorder.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveExecutionBlackboxRecorder.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-blackbox-record-rows">
            {impact.archiveExecutionBlackboxRecorder.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveExecutionBlackboxRecorderStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.recordRule}</p>
                <dl>
                  <div><dt>Override</dt><dd title={row.sourceOverrideRowId}>{compactIdentifier(row.sourceOverrideRowId)}</dd></div>
                  <div><dt>Command Lock</dt><dd title={row.sourceCommandLockRowId}>{compactIdentifier(row.sourceCommandLockRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.recordLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.recordScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.recordResult}</dd></div>
                </dl>
                <code>{row.recordEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveExecutionBlackboxRecorder.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveExecutionBlackboxRecorder.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveExecutionBlackboxRecorder.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-abort-drill-closeout-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Restore Abort Drill Closeout Ledger</h3>
            </div>
            <div>
              <span>{impact.restoreAbortDrillCloseoutLedger.reportVersion}</span>
              <strong>{impact.restoreAbortDrillCloseoutLedger.gate}</strong>
              <code>{impact.restoreAbortDrillCloseoutLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreAbortDrillCloseoutLedger.gate}>{impact.restoreAbortDrillCloseoutLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreAbortDrillCloseoutLedger.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.restoreAbortDrillCloseoutLedger.summary.closedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreAbortDrillCloseoutLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreAbortDrillCloseoutLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreAbortDrillCloseoutLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-abort-closeout-rows">
            {impact.restoreAbortDrillCloseoutLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreAbortDrillCloseoutLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.abortRule}</p>
                <dl>
                  <div><dt>Blackbox</dt><dd title={row.sourceBlackboxRowId}>{compactIdentifier(row.sourceBlackboxRowId)}</dd></div>
                  <div><dt>Drillbook</dt><dd title={row.sourceIncidentDrillRowId}>{compactIdentifier(row.sourceIncidentDrillRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.abortLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.abortScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.abortResult}</dd></div>
                </dl>
                <code>{row.abortEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreAbortDrillCloseoutLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreAbortDrillCloseoutLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreAbortDrillCloseoutLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-incident-replay-notarization">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Restore Incident Replay Notarization</h3>
            </div>
            <div>
              <span>{impact.restoreIncidentReplayNotarization.reportVersion}</span>
              <strong>{impact.restoreIncidentReplayNotarization.gate}</strong>
              <code>{impact.restoreIncidentReplayNotarization.notarizationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreIncidentReplayNotarization.gate}>{impact.restoreIncidentReplayNotarization.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreIncidentReplayNotarization.summary.totalRows}</strong></div>
            <div><span>Notarized</span><strong data-status="pass">{impact.restoreIncidentReplayNotarization.summary.notarizedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreIncidentReplayNotarization.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreIncidentReplayNotarization.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreIncidentReplayNotarization.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-incident-notary-rows">
            {impact.restoreIncidentReplayNotarization.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreIncidentReplayNotarizationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.notaryRule}</p>
                <dl>
                  <div><dt>Abort</dt><dd title={row.sourceAbortCloseoutRowId}>{compactIdentifier(row.sourceAbortCloseoutRowId)}</dd></div>
                  <div><dt>Memory Notary</dt><dd title={row.sourceNotarizationRowId}>{compactIdentifier(row.sourceNotarizationRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.notaryLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.notaryScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.notaryResult}</dd></div>
                </dl>
                <code>{row.notaryEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreIncidentReplayNotarization.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreIncidentReplayNotarization.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreIncidentReplayNotarization.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-restore-execution-variance-report">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Archive Restore Execution Variance Report</h3>
            </div>
            <div>
              <span>{impact.archiveRestoreExecutionVarianceReport.reportVersion}</span>
              <strong>{impact.archiveRestoreExecutionVarianceReport.gate}</strong>
              <code>{impact.archiveRestoreExecutionVarianceReport.reportId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveRestoreExecutionVarianceReport.gate}>{impact.archiveRestoreExecutionVarianceReport.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveRestoreExecutionVarianceReport.summary.totalRows}</strong></div>
            <div><span>Clear</span><strong data-status="pass">{impact.archiveRestoreExecutionVarianceReport.summary.clearRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveRestoreExecutionVarianceReport.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveRestoreExecutionVarianceReport.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveRestoreExecutionVarianceReport.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-restore-variance-rows">
            {impact.archiveRestoreExecutionVarianceReport.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveRestoreExecutionVarianceReportStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.varianceRule}</p>
                <dl>
                  <div><dt>Replay Notary</dt><dd title={row.sourceNotarizationRowId}>{compactIdentifier(row.sourceNotarizationRowId)}</dd></div>
                  <div><dt>Blackbox</dt><dd title={row.sourceBlackboxRowId}>{compactIdentifier(row.sourceBlackboxRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.varianceLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.varianceScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.varianceResult}</dd></div>
                </dl>
                <code>{row.varianceEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveRestoreExecutionVarianceReport.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveRestoreExecutionVarianceReport.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveRestoreExecutionVarianceReport.summary.nextAction}</code>
        </div>

        <div className="task-impact-post-abort-owner-evidence-reconciliation">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Post-Abort Owner Evidence Reconciliation</h3>
            </div>
            <div>
              <span>{impact.postAbortOwnerEvidenceReconciliation.reportVersion}</span>
              <strong>{impact.postAbortOwnerEvidenceReconciliation.gate}</strong>
              <code>{impact.postAbortOwnerEvidenceReconciliation.reconciliationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.postAbortOwnerEvidenceReconciliation.gate}>{impact.postAbortOwnerEvidenceReconciliation.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.postAbortOwnerEvidenceReconciliation.summary.totalRows}</strong></div>
            <div><span>Reconciled</span><strong data-status="pass">{impact.postAbortOwnerEvidenceReconciliation.summary.reconciledRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.postAbortOwnerEvidenceReconciliation.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.postAbortOwnerEvidenceReconciliation.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.postAbortOwnerEvidenceReconciliation.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-post-abort-reconciliation-rows">
            {impact.postAbortOwnerEvidenceReconciliation.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{postAbortOwnerEvidenceReconciliationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.reconciliationRule}</p>
                <dl>
                  <div><dt>Variance</dt><dd title={row.sourceVarianceRowId}>{compactIdentifier(row.sourceVarianceRowId)}</dd></div>
                  <div><dt>Owner Response</dt><dd title={row.sourceOwnerResponseRowId}>{compactIdentifier(row.sourceOwnerResponseRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.reconciliationLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.reconciliationScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.reconciliationResult}</dd></div>
                </dl>
                <code>{row.reconciliationEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.postAbortOwnerEvidenceReconciliation.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.postAbortOwnerEvidenceReconciliation.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.postAbortOwnerEvidenceReconciliation.summary.nextAction}</code>
        </div>

        <div className="task-impact-restore-acceptance-final-attestation">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Restore Acceptance Final Attestation</h3>
            </div>
            <div>
              <span>{impact.restoreAcceptanceFinalAttestation.reportVersion}</span>
              <strong>{impact.restoreAcceptanceFinalAttestation.gate}</strong>
              <code>{impact.restoreAcceptanceFinalAttestation.attestationId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.restoreAcceptanceFinalAttestation.gate}>{impact.restoreAcceptanceFinalAttestation.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.restoreAcceptanceFinalAttestation.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.restoreAcceptanceFinalAttestation.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.restoreAcceptanceFinalAttestation.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.restoreAcceptanceFinalAttestation.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.restoreAcceptanceFinalAttestation.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-restore-final-attestation-rows">
            {impact.restoreAcceptanceFinalAttestation.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{restoreAcceptanceFinalAttestationStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.attestationRule}</p>
                <dl>
                  <div><dt>Reconciliation</dt><dd title={row.sourceReconciliationRowId}>{compactIdentifier(row.sourceReconciliationRowId)}</dd></div>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceReplayRowId}>{compactIdentifier(row.sourceAcceptanceReplayRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.attestationLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.attestationScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.attestationResult}</dd></div>
                </dl>
                <code>{row.attestationEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.restoreAcceptanceFinalAttestation.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.restoreAcceptanceFinalAttestation.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.restoreAcceptanceFinalAttestation.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-incident-delta-aging-board">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Archive Incident Delta Aging Board</h3>
            </div>
            <div>
              <span>{impact.archiveIncidentDeltaAgingBoard.reportVersion}</span>
              <strong>{impact.archiveIncidentDeltaAgingBoard.gate}</strong>
              <code>{impact.archiveIncidentDeltaAgingBoard.boardId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveIncidentDeltaAgingBoard.gate}>{impact.archiveIncidentDeltaAgingBoard.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveIncidentDeltaAgingBoard.summary.totalRows}</strong></div>
            <div><span>Current</span><strong data-status="pass">{impact.archiveIncidentDeltaAgingBoard.summary.currentRows}</strong></div>
            <div><span>Aging</span><strong data-status="review">{impact.archiveIncidentDeltaAgingBoard.summary.agingRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveIncidentDeltaAgingBoard.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveIncidentDeltaAgingBoard.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-delta-aging-rows">
            {impact.archiveIncidentDeltaAgingBoard.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveIncidentDeltaAgingBoardStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.agingRule}</p>
                <dl>
                  <div><dt>Attestation</dt><dd title={row.sourceAttestationRowId}>{compactIdentifier(row.sourceAttestationRowId)}</dd></div>
                  <div><dt>Incident Replay</dt><dd title={row.sourceIncidentReplayRowId}>{compactIdentifier(row.sourceIncidentReplayRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Bucket</dt><dd>{row.deltaAgeBucket}</dd></div>
                  <div><dt>Lane</dt><dd>{row.agingLane}</dd></div>
                  <div><dt>Result</dt><dd>{row.agingResult}</dd></div>
                </dl>
                <code>{row.agingEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveIncidentDeltaAgingBoard.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveIncidentDeltaAgingBoard.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveIncidentDeltaAgingBoard.summary.nextAction}</code>
        </div>

        <div className="task-impact-post-restore-owner-signoff-packet">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Post-Restore Owner Signoff Packet</h3>
            </div>
            <div>
              <span>{impact.postRestoreOwnerSignoffPacket.reportVersion}</span>
              <strong>{impact.postRestoreOwnerSignoffPacket.gate}</strong>
              <code>{impact.postRestoreOwnerSignoffPacket.packetId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.postRestoreOwnerSignoffPacket.gate}>{impact.postRestoreOwnerSignoffPacket.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.postRestoreOwnerSignoffPacket.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.postRestoreOwnerSignoffPacket.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.postRestoreOwnerSignoffPacket.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.postRestoreOwnerSignoffPacket.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.postRestoreOwnerSignoffPacket.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-post-restore-signoff-rows">
            {impact.postRestoreOwnerSignoffPacket.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{postRestoreOwnerSignoffPacketStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.signoffRule}</p>
                <dl>
                  <div><dt>Delta Aging</dt><dd title={row.sourceDeltaAgingRowId}>{compactIdentifier(row.sourceDeltaAgingRowId)}</dd></div>
                  <div><dt>Owner Response</dt><dd title={row.sourceOwnerResponseRowId}>{compactIdentifier(row.sourceOwnerResponseRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.signoffLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.signoffScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.signoffResult}</dd></div>
                </dl>
                <code>{row.signoffEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.postRestoreOwnerSignoffPacket.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.postRestoreOwnerSignoffPacket.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.postRestoreOwnerSignoffPacket.summary.nextAction}</code>
        </div>

        <div className="task-impact-signoff-dispute-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Signoff Dispute Replay</h3>
            </div>
            <div>
              <span>{impact.signoffDisputeReplay.reportVersion}</span>
              <strong>{impact.signoffDisputeReplay.gate}</strong>
              <code>{impact.signoffDisputeReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.signoffDisputeReplay.gate}>{impact.signoffDisputeReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.signoffDisputeReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.signoffDisputeReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.signoffDisputeReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.signoffDisputeReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.signoffDisputeReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-signoff-dispute-rows">
            {impact.signoffDisputeReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{signoffDisputeReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayRule}</p>
                <dl>
                  <div><dt>Signoff</dt><dd title={row.sourceSignoffRowId}>{compactIdentifier(row.sourceSignoffRowId)}</dd></div>
                  <div><dt>Dispute</dt><dd title={row.sourceDisputeCaseId}>{compactIdentifier(row.sourceDisputeCaseId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.disputeLane}</dd></div>
                  <div><dt>Claim</dt><dd>{row.disputedClaim}</dd></div>
                  <div><dt>Result</dt><dd>{row.replayResult}</dd></div>
                </dl>
                <code>{row.replayEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.signoffDisputeReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.signoffDisputeReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.signoffDisputeReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-acceptance-freeze-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <GitCompare size={17} aria-hidden="true" />
              <h3>Archive Acceptance Freeze Diff</h3>
            </div>
            <div>
              <span>{impact.archiveAcceptanceFreezeDiff.reportVersion}</span>
              <strong>{impact.archiveAcceptanceFreezeDiff.gate}</strong>
              <code>{impact.archiveAcceptanceFreezeDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveAcceptanceFreezeDiff.gate}>{impact.archiveAcceptanceFreezeDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveAcceptanceFreezeDiff.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.archiveAcceptanceFreezeDiff.summary.matchedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveAcceptanceFreezeDiff.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveAcceptanceFreezeDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveAcceptanceFreezeDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-freeze-diff-rows">
            {impact.archiveAcceptanceFreezeDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveAcceptanceFreezeDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffRule}</p>
                <dl>
                  <div><dt>Replay</dt><dd title={row.sourceDisputeReplayRowId}>{compactIdentifier(row.sourceDisputeReplayRowId)}</dd></div>
                  <div><dt>Freeze</dt><dd title={row.sourceAcceptedFreezeEntryId}>{compactIdentifier(row.sourceAcceptedFreezeEntryId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.freezeLane}</dd></div>
                  <div><dt>Checksum</dt><dd>{row.acceptedChecksum}</dd></div>
                  <div><dt>Result</dt><dd>{row.diffResult}</dd></div>
                </dl>
                <code>{row.freezeEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveAcceptanceFreezeDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveAcceptanceFreezeDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveAcceptanceFreezeDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-closure-exception-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Owner Closure Exception Ledger</h3>
            </div>
            <div>
              <span>{impact.ownerClosureExceptionLedger.reportVersion}</span>
              <strong>{impact.ownerClosureExceptionLedger.gate}</strong>
              <code>{impact.ownerClosureExceptionLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerClosureExceptionLedger.gate}>{impact.ownerClosureExceptionLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerClosureExceptionLedger.summary.totalRows}</strong></div>
            <div><span>Closed</span><strong data-status="pass">{impact.ownerClosureExceptionLedger.summary.closedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.ownerClosureExceptionLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.ownerClosureExceptionLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.ownerClosureExceptionLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-owner-closure-exception-rows">
            {impact.ownerClosureExceptionLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerClosureExceptionLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.exceptionRule}</p>
                <dl>
                  <div><dt>Freeze Diff</dt><dd title={row.sourceFreezeDiffRowId}>{compactIdentifier(row.sourceFreezeDiffRowId)}</dd></div>
                  <div><dt>Closeout</dt><dd title={row.sourceCloseoutRowId}>{compactIdentifier(row.sourceCloseoutRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.exceptionLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.exceptionScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.exceptionResult}</dd></div>
                </dl>
                <code>{row.closureEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerClosureExceptionLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerClosureExceptionLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerClosureExceptionLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-closure-evidence-seal">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldCheck size={17} aria-hidden="true" />
              <h3>Closure Evidence Seal</h3>
            </div>
            <div>
              <span>{impact.closureEvidenceSeal.reportVersion}</span>
              <strong>{impact.closureEvidenceSeal.gate}</strong>
              <code>{impact.closureEvidenceSeal.sealId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.closureEvidenceSeal.gate}>{impact.closureEvidenceSeal.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.closureEvidenceSeal.summary.totalRows}</strong></div>
            <div><span>Sealed</span><strong data-status="pass">{impact.closureEvidenceSeal.summary.sealedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.closureEvidenceSeal.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.closureEvidenceSeal.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.closureEvidenceSeal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-closure-seal-rows">
            {impact.closureEvidenceSeal.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{closureEvidenceSealStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.sealRule}</p>
                <dl>
                  <div><dt>Closure</dt><dd title={row.sourceClosureExceptionRowId}>{compactIdentifier(row.sourceClosureExceptionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.sealLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.sealedScope}</dd></div>
                  <div><dt>Seal</dt><dd>{row.sealRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.sealResult}</dd></div>
                </dl>
                <code>{row.sealEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.closureEvidenceSeal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.closureEvidenceSeal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.closureEvidenceSeal.summary.nextAction}</code>
        </div>

        <div className="task-impact-archive-terminal-package-diff">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Archive Terminal Package Diff</h3>
            </div>
            <div>
              <span>{impact.archiveTerminalPackageDiff.reportVersion}</span>
              <strong>{impact.archiveTerminalPackageDiff.gate}</strong>
              <code>{impact.archiveTerminalPackageDiff.diffId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.archiveTerminalPackageDiff.gate}>{impact.archiveTerminalPackageDiff.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.archiveTerminalPackageDiff.summary.totalRows}</strong></div>
            <div><span>Matched</span><strong data-status="pass">{impact.archiveTerminalPackageDiff.summary.matchedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.archiveTerminalPackageDiff.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.archiveTerminalPackageDiff.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.archiveTerminalPackageDiff.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-archive-terminal-diff-rows">
            {impact.archiveTerminalPackageDiff.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{archiveTerminalPackageDiffStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.diffRule}</p>
                <dl>
                  <div><dt>Seal</dt><dd title={row.sourceSealRowId}>{compactIdentifier(row.sourceSealRowId)}</dd></div>
                  <div><dt>Archive</dt><dd title={row.sourceArchiveRowId}>{compactIdentifier(row.sourceArchiveRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.terminalLane}</dd></div>
                  <div><dt>Archive Ref</dt><dd>{row.archiveRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.diffResult}</dd></div>
                </dl>
                <code>{row.terminalEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.archiveTerminalPackageDiff.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.archiveTerminalPackageDiff.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.archiveTerminalPackageDiff.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-reopen-guardrail-simulator">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Owner Reopen Guardrail Simulator</h3>
            </div>
            <div>
              <span>{impact.ownerReopenGuardrailSimulator.reportVersion}</span>
              <strong>{impact.ownerReopenGuardrailSimulator.gate}</strong>
              <code>{impact.ownerReopenGuardrailSimulator.simulatorId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerReopenGuardrailSimulator.gate}>{impact.ownerReopenGuardrailSimulator.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerReopenGuardrailSimulator.summary.totalRows}</strong></div>
            <div><span>Passed</span><strong data-status="pass">{impact.ownerReopenGuardrailSimulator.summary.passedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.ownerReopenGuardrailSimulator.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.ownerReopenGuardrailSimulator.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.ownerReopenGuardrailSimulator.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-owner-reopen-guardrail-rows">
            {impact.ownerReopenGuardrailSimulator.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerReopenGuardrailSimulatorStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.guardrailRule}</p>
                <dl>
                  <div><dt>Terminal</dt><dd title={row.sourceTerminalDiffRowId}>{compactIdentifier(row.sourceTerminalDiffRowId)}</dd></div>
                  <div><dt>Aging</dt><dd title={row.sourceAgingRowId}>{compactIdentifier(row.sourceAgingRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.reopenLane}</dd></div>
                  <div><dt>Request</dt><dd>{row.reopenRequestRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.guardrailResult}</dd></div>
                </dl>
                <code>{row.reopenEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerReopenGuardrailSimulator.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerReopenGuardrailSimulator.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerReopenGuardrailSimulator.summary.nextAction}</code>
        </div>

        <div className="task-impact-sealed-receipt-replay">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <RotateCcw size={17} aria-hidden="true" />
              <h3>Sealed Closure Receipt Replay</h3>
            </div>
            <div>
              <span>{impact.sealedClosureReceiptReplay.reportVersion}</span>
              <strong>{impact.sealedClosureReceiptReplay.gate}</strong>
              <code>{impact.sealedClosureReceiptReplay.replayId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.sealedClosureReceiptReplay.gate}>{impact.sealedClosureReceiptReplay.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.sealedClosureReceiptReplay.summary.totalRows}</strong></div>
            <div><span>Replayed</span><strong data-status="pass">{impact.sealedClosureReceiptReplay.summary.replayedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.sealedClosureReceiptReplay.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.sealedClosureReceiptReplay.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.sealedClosureReceiptReplay.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-sealed-receipt-replay-rows">
            {impact.sealedClosureReceiptReplay.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{sealedClosureReceiptReplayStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.replayRule}</p>
                <dl>
                  <div><dt>Seal</dt><dd title={row.sourceSealRowId}>{compactIdentifier(row.sourceSealRowId)}</dd></div>
                  <div><dt>Receipt</dt><dd title={row.sourceReceiptRowId}>{compactIdentifier(row.sourceReceiptRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.receiptLane}</dd></div>
                  <div><dt>Replay</dt><dd>{row.receiptRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.replayResult}</dd></div>
                </dl>
                <code>{row.receiptEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.sealedClosureReceiptReplay.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.sealedClosureReceiptReplay.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.sealedClosureReceiptReplay.summary.nextAction}</code>
        </div>

        <div className="task-impact-terminal-retention-renewal">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <Archive size={17} aria-hidden="true" />
              <h3>Terminal Archive Retention Renewal</h3>
            </div>
            <div>
              <span>{impact.terminalArchiveRetentionRenewal.reportVersion}</span>
              <strong>{impact.terminalArchiveRetentionRenewal.gate}</strong>
              <code>{impact.terminalArchiveRetentionRenewal.renewalId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.terminalArchiveRetentionRenewal.gate}>{impact.terminalArchiveRetentionRenewal.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.terminalArchiveRetentionRenewal.summary.totalRows}</strong></div>
            <div><span>Renewed</span><strong data-status="pass">{impact.terminalArchiveRetentionRenewal.summary.renewedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.terminalArchiveRetentionRenewal.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.terminalArchiveRetentionRenewal.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.terminalArchiveRetentionRenewal.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-terminal-retention-renewal-rows">
            {impact.terminalArchiveRetentionRenewal.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{terminalArchiveRetentionRenewalStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.renewalRule}</p>
                <dl>
                  <div><dt>Terminal</dt><dd title={row.sourceTerminalDiffRowId}>{compactIdentifier(row.sourceTerminalDiffRowId)}</dd></div>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRowId}>{compactIdentifier(row.sourceRetentionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.retentionLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.retentionWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.renewalResult}</dd></div>
                </dl>
                <code>{row.retentionEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.terminalArchiveRetentionRenewal.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.terminalArchiveRetentionRenewal.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.terminalArchiveRetentionRenewal.summary.nextAction}</code>
        </div>

        <div className="task-impact-owner-reopen-drillbook">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ShieldAlert size={17} aria-hidden="true" />
              <h3>Owner Reopen Incident Drillbook</h3>
            </div>
            <div>
              <span>{impact.ownerReopenIncidentDrillbook.reportVersion}</span>
              <strong>{impact.ownerReopenIncidentDrillbook.gate}</strong>
              <code>{impact.ownerReopenIncidentDrillbook.drillbookId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.ownerReopenIncidentDrillbook.gate}>{impact.ownerReopenIncidentDrillbook.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.ownerReopenIncidentDrillbook.summary.totalRows}</strong></div>
            <div><span>Ready</span><strong data-status="pass">{impact.ownerReopenIncidentDrillbook.summary.readyRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.ownerReopenIncidentDrillbook.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.ownerReopenIncidentDrillbook.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.ownerReopenIncidentDrillbook.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-owner-reopen-drillbook-rows">
            {impact.ownerReopenIncidentDrillbook.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{ownerReopenIncidentDrillbookStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.drillRule}</p>
                <dl>
                  <div><dt>Guardrail</dt><dd title={row.sourceGuardrailRowId}>{compactIdentifier(row.sourceGuardrailRowId)}</dd></div>
                  <div><dt>Drillbook</dt><dd title={row.sourceDrillbookRowId}>{compactIdentifier(row.sourceDrillbookRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.drillLane}</dd></div>
                  <div><dt>Scenario</dt><dd>{row.incidentScenario}</dd></div>
                  <div><dt>Result</dt><dd>{row.drillResult}</dd></div>
                </dl>
                <code>{row.incidentEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.ownerReopenIncidentDrillbook.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.ownerReopenIncidentDrillbook.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.ownerReopenIncidentDrillbook.summary.nextAction}</code>
        </div>

        <div className="task-impact-receipt-aging-lock">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <KeyRound size={17} aria-hidden="true" />
              <h3>Receipt Replay Aging Lock</h3>
            </div>
            <div>
              <span>{impact.receiptReplayAgingLock.reportVersion}</span>
              <strong>{impact.receiptReplayAgingLock.gate}</strong>
              <code>{impact.receiptReplayAgingLock.lockId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.receiptReplayAgingLock.gate}>{impact.receiptReplayAgingLock.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.receiptReplayAgingLock.summary.totalRows}</strong></div>
            <div><span>Locked</span><strong data-status="pass">{impact.receiptReplayAgingLock.summary.lockedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.receiptReplayAgingLock.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.receiptReplayAgingLock.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.receiptReplayAgingLock.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-receipt-aging-lock-rows">
            {impact.receiptReplayAgingLock.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{receiptReplayAgingLockStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.lockRule}</p>
                <dl>
                  <div><dt>Replay</dt><dd title={row.sourceReceiptReplayRowId}>{compactIdentifier(row.sourceReceiptReplayRowId)}</dd></div>
                  <div><dt>Aging</dt><dd title={row.sourceAgingRecordId}>{compactIdentifier(row.sourceAgingRecordId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.lockLane}</dd></div>
                  <div><dt>Window</dt><dd>{row.agingWindow}</dd></div>
                  <div><dt>Result</dt><dd>{row.lockResult}</dd></div>
                </dl>
                <code>{row.lockEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.receiptReplayAgingLock.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.receiptReplayAgingLock.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.receiptReplayAgingLock.summary.nextAction}</code>
        </div>

        <div className="task-impact-retention-exception-burndown">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ClipboardCheck size={17} aria-hidden="true" />
              <h3>Retention Exception Burn-Down</h3>
            </div>
            <div>
              <span>{impact.retentionExceptionBurnDown.reportVersion}</span>
              <strong>{impact.retentionExceptionBurnDown.gate}</strong>
              <code>{impact.retentionExceptionBurnDown.burnDownId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.retentionExceptionBurnDown.gate}>{impact.retentionExceptionBurnDown.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.retentionExceptionBurnDown.summary.totalRows}</strong></div>
            <div><span>Burned Down</span><strong data-status="pass">{impact.retentionExceptionBurnDown.summary.burnedDownRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.retentionExceptionBurnDown.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.retentionExceptionBurnDown.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.retentionExceptionBurnDown.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-retention-exception-burndown-rows">
            {impact.retentionExceptionBurnDown.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{retentionExceptionBurnDownStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.burnDownRule}</p>
                <dl>
                  <div><dt>Retention</dt><dd title={row.sourceRetentionRenewalRowId}>{compactIdentifier(row.sourceRetentionRenewalRowId)}</dd></div>
                  <div><dt>Exception</dt><dd title={row.sourceExceptionRowId}>{compactIdentifier(row.sourceExceptionRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.burnDownLane}</dd></div>
                  <div><dt>Ref</dt><dd>{row.exceptionRef}</dd></div>
                  <div><dt>Result</dt><dd>{row.burnDownResult}</dd></div>
                </dl>
                <code>{row.burnDownEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.retentionExceptionBurnDown.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.retentionExceptionBurnDown.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.retentionExceptionBurnDown.summary.nextAction}</code>
        </div>

        <div className="task-impact-drillbook-acceptance-ledger">
          <div className="task-impact-r8-head">
            <div className="section-title">
              <ListChecks size={17} aria-hidden="true" />
              <h3>Drillbook Acceptance Ledger</h3>
            </div>
            <div>
              <span>{impact.drillbookAcceptanceLedger.reportVersion}</span>
              <strong>{impact.drillbookAcceptanceLedger.gate}</strong>
              <code>{impact.drillbookAcceptanceLedger.ledgerId}</code>
            </div>
          </div>
          <div className="task-impact-r8-summary">
            <div><span>Gate</span><strong data-gate={impact.drillbookAcceptanceLedger.gate}>{impact.drillbookAcceptanceLedger.gate}</strong></div>
            <div><span>Rows</span><strong>{impact.drillbookAcceptanceLedger.summary.totalRows}</strong></div>
            <div><span>Accepted</span><strong data-status="pass">{impact.drillbookAcceptanceLedger.summary.acceptedRows}</strong></div>
            <div><span>Review</span><strong data-status="review">{impact.drillbookAcceptanceLedger.summary.reviewRows}</strong></div>
            <div><span>Owner Hold</span><strong data-status="review">{impact.drillbookAcceptanceLedger.summary.ownerHoldRows}</strong></div>
            <div><span>Writes</span><strong>{impact.drillbookAcceptanceLedger.summary.liveWrites}</strong></div>
          </div>
          <div className="task-impact-drillbook-acceptance-ledger-rows">
            {impact.drillbookAcceptanceLedger.rows.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div className="task-impact-r8-title">
                  <span>{drillbookAcceptanceLedgerStateLabels[row.state]}</span>
                  <strong>{row.label}</strong>
                  <em>{row.gate}</em>
                </div>
                <p>{row.acceptanceRule}</p>
                <dl>
                  <div><dt>Drillbook</dt><dd title={row.sourceIncidentDrillbookRowId}>{compactIdentifier(row.sourceIncidentDrillbookRowId)}</dd></div>
                  <div><dt>Acceptance</dt><dd title={row.sourceAcceptanceRowId}>{compactIdentifier(row.sourceAcceptanceRowId)}</dd></div>
                  <div><dt>Owner</dt><dd>{row.owner}</dd></div>
                  <div><dt>Lane</dt><dd>{row.acceptanceLane}</dd></div>
                  <div><dt>Scope</dt><dd>{row.acceptanceScope}</dd></div>
                  <div><dt>Result</dt><dd>{row.acceptanceResult}</dd></div>
                </dl>
                <code>{row.acceptanceEffect}</code>
                <small title={row.evidence.join(" / ")}>{compactEvidenceRefs(row.evidence)}</small>
              </article>
            ))}
          </div>
          <div className="task-impact-r8-rules">
            <div>
              <span>Guardrails</span>
              {impact.drillbookAcceptanceLedger.guardrails.map((guardrail) => (
                <p key={guardrail}>{guardrail}</p>
              ))}
            </div>
            <div>
              <span>Artifacts</span>
              {impact.drillbookAcceptanceLedger.artifacts.map((artifact) => (
                <p key={artifact}>{artifact}</p>
              ))}
            </div>
          </div>
          <code>{impact.drillbookAcceptanceLedger.summary.nextAction}</code>
        </div>

        <div className="task-impact-flow-map">
          {impact.impactPaths.map((path) => {
            const steps = impact.pathSteps
              .filter((step) => step.pathId === path.id)
              .sort((left, right) => left.order - right.order);
            return (
              <article className="task-impact-flow" data-gate={path.gate} key={path.id}>
                <div className="task-impact-flow-head">
                  <span>{path.gate}</span>
                  <strong>{path.label}</strong>
                  <em>{path.requiredReceiptIds.join(" / ")}</em>
                </div>
                <div className="task-impact-step-list">
                  {steps.map((step) => (
                    <div className="task-impact-step" data-action={step.action} data-gate={step.gate} key={step.id}>
                      <span>{step.order}</span>
                      <strong>{step.moduleName}</strong>
                      <p>{step.evidence}</p>
                      <code>{step.assetId}</code>
                    </div>
                  ))}
                </div>
              </article>
            );
          })}
        </div>

        <div className="task-impact-assets">
          {impact.assetNodes.map((asset) => (
            <article className="task-impact-asset" data-action={asset.publishAction} data-gate={asset.gate} key={asset.id}>
              <div className="task-impact-title">
                <span>{impactAssetKindLabels[asset.kind]}</span>
                <strong>{asset.label}</strong>
                <em>{asset.gate}</em>
              </div>
              <p>{asset.change}</p>
              <dl>
                <div><dt>Owner</dt><dd>{asset.owner}</dd></div>
                <div><dt>Risk</dt><dd>{asset.riskScore}</dd></div>
                <div><dt>Action</dt><dd>{impactActionLabels[asset.publishAction]}</dd></div>
                <div><dt>Hash</dt><dd>{asset.previousHash}{" -> "}{asset.currentHash}</dd></div>
              </dl>
              <code>{asset.downstream.join(" -> ")}</code>
              <small>{asset.evidence}</small>
            </article>
          ))}
        </div>

        <div className="task-impact-paths">
          {impact.impactPaths.map((path) => (
            <article className="task-impact-path" data-gate={path.gate} key={path.id}>
              <span>{path.gate}</span>
              <strong>{path.label}</strong>
              <p>{path.blocker}</p>
              <code>{path.modules.join(" -> ")}</code>
              <small>{path.requiredReceiptIds.join(" / ")}</small>
            </article>
          ))}
        </div>

        <div className="task-impact-matrix" role="table" aria-label="dependency impact decision matrix">
          <div role="row">
            <span>Asset</span>
            <span>Module</span>
            <span>Gate</span>
            <span>Action</span>
            <span>Receipt</span>
            <span>Reason</span>
          </div>
          {impact.decisionMatrix.map((cell) => {
            const asset = impact.assetNodes.find((candidate) => candidate.id === cell.assetId);
            return (
              <div data-action={cell.action} data-gate={cell.gate} key={cell.id} role="row">
                <strong>{asset?.label ?? cell.assetId}</strong>
                <span>{cell.moduleName}</span>
                <em>{cell.gate}</em>
                <code>{impactActionLabels[cell.action]}</code>
                <small>{impactReceiptStateLabels[cell.receiptState]}</small>
                <p>{cell.reason}</p>
              </div>
            );
          })}
        </div>

        <div className="task-impact-review-grid">
          {selectedImpactReceipt && (
            <div className="task-impact-drilldown">
              <div className="task-impact-drilldown-head">
                <div>
                  <span>Receipt Drilldown</span>
                  <strong>{selectedImpactReceipt.id}</strong>
                  <p>{selectedImpactReceipt.scope}</p>
                </div>
                <div>
                  <span>{impactReceiptStateLabels[selectedImpactReceipt.state]}</span>
                  <strong>{selectedImpactReceipt.owner}</strong>
                  <p>{selectedImpactReceipt.gate}</p>
                </div>
              </div>
              <div className="task-impact-receipt-tabs" role="tablist" aria-label="impact owner receipts">
                {impact.ownerReceipts.map((receipt) => (
                  <button
                    aria-pressed={selectedImpactReceipt.id === receipt.id}
                    data-state={receipt.state}
                    key={receipt.id}
                    onClick={() => setSelectedImpactReceiptId(receipt.id)}
                    type="button"
                  >
                    <strong>{receipt.owner}</strong>
                    <span>{impactReceiptStateLabels[receipt.state]}</span>
                    <small>{receipt.id}</small>
                  </button>
                ))}
              </div>
              <div className="task-impact-drilldown-grid">
                <div>
                  <span>Path Steps</span>
                  {selectedReceiptSteps.map((step) => (
                    <article data-gate={step.gate} key={step.id}>
                      <strong>{step.order}. {step.moduleName}</strong>
                      <p>{step.evidence}</p>
                      <code>{step.assetId}</code>
                    </article>
                  ))}
                </div>
                <div>
                  <span>Publish Targets</span>
                  {selectedReceiptDecisions.length > 0 ? (
                    selectedReceiptDecisions.map((decision) => (
                      <article data-gate={decision.gate} key={decision.id}>
                        <strong>{decision.target}</strong>
                        <p>{decision.reason}</p>
                        <code>{impactActionLabels[decision.action]}</code>
                      </article>
                    ))
                  ) : (
                    <article data-gate={selectedImpactReceipt.gate}>
                      <strong>No direct publish target</strong>
                      <p>Receipt is inherited through path steps and matrix cells.</p>
                      <code>{selectedImpactReceipt.id}</code>
                    </article>
                  )}
                </div>
                <div>
                  <span>Matrix Cells</span>
                  {selectedReceiptMatrix.map((cell) => {
                    const asset = impact.assetNodes.find((candidate) => candidate.id === cell.assetId);
                    return (
                      <article data-gate={cell.gate} key={cell.id}>
                        <strong>{asset?.label ?? cell.assetId}</strong>
                        <p>{cell.moduleName}: {cell.reason}</p>
                        <code>{impactActionLabels[cell.action]} / {impactReceiptStateLabels[cell.receiptState]}</code>
                      </article>
                    );
                  })}
                </div>
              </div>
              <code>{selectedImpactReceipt.nextAction}</code>
            </div>
          )}
          <div className="task-impact-decision-list">
            {impact.publishDecisions.map((decision) => (
              <article className="task-impact-decision" data-action={decision.action} data-gate={decision.gate} key={decision.id}>
                <span>{impactActionLabels[decision.action]}</span>
                <strong>{decision.target}</strong>
                <p>{decision.reason}</p>
                <code>{decision.requiredEvidence.join(" / ")}</code>
              </article>
            ))}
          </div>
          <div className="task-impact-receipt-list">
            {impact.ownerReceipts.map((receipt) => (
              <article className="task-impact-receipt" data-state={receipt.state} key={receipt.id}>
                <span>{impactReceiptStateLabels[receipt.state]}</span>
                <strong>{receipt.owner}</strong>
                <p>{receipt.scope}</p>
                <code>{receipt.evidenceIds.join(" / ")}</code>
                <small>{receipt.nextAction}</small>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="logic-block task-diff-panel">
        <div className="section-title">
          <GitCompare size={17} aria-hidden="true" />
          <h3>Run Diff</h3>
        </div>
        <div className="task-diff-summary">
          <div>
            <span>From</span>
            <strong>{report.runDiff.fromRunId}</strong>
          </div>
          <div>
            <span>To</span>
            <strong>{report.runDiff.toRunId}</strong>
          </div>
          <div>
            <span>Changed</span>
            <strong>{report.runDiff.changedModules}</strong>
          </div>
          <div>
            <span>Evidence</span>
            <strong>+{report.runDiff.evidenceDelta}</strong>
          </div>
        </div>
        <p>{report.runDiff.summary}</p>
        <div className="task-diff-table" role="table" aria-label="task run diff">
          <div role="row">
            <span>Module</span>
            <span>Gate</span>
            <span>Evidence</span>
            <span>Action</span>
          </div>
          {report.runDiff.rows.map((row) => (
            <div key={row.id} role="row">
              <strong>{row.moduleName}</strong>
              <code>{row.previousGate}{" -> "}{row.currentGate}</code>
              <span>{row.previousEvidenceCount}{" -> "}{row.currentEvidenceCount}</span>
              <p>{row.action}</p>
            </div>
          ))}
        </div>
        <code>{report.runDiff.blockerDelta}</code>
      </section>

      <section className="logic-block wide task-registry-panel">
        <div className="section-title">
          <ListChecks size={17} aria-hidden="true" />
          <h3>Tool Registry Manifest</h3>
        </div>
        <div className="task-registry-table" role="table" aria-label="tool registry manifest">
          <div role="row">
            <span>Tool</span>
            <span>Owner</span>
            <span>Adapter</span>
            <span>Input</span>
            <span>Output</span>
          </div>
          {report.toolRegistry.map((tool) => (
            <div key={tool.id} role="row">
              <strong>{tool.label}</strong>
              <span>{tool.owner}</span>
              <code>{tool.adapter}</code>
              <code>{tool.inputContract}</code>
              <code>{tool.outputContract}</code>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block wide task-discovery-panel">
        <div className="section-title">
          <Network size={17} aria-hidden="true" />
          <h3>Tool Discovery</h3>
        </div>
        <div className="task-discovery-filters">
          <label className="field-control">
            <span>DCC</span>
            <select
              aria-label="DCC Filter"
              onChange={(event) => updateDiscoveryFilter("dcc", event.currentTarget.value as TaskToolDiscoveryFilters["dcc"])}
              value={discoveryFilters.dcc}
            >
              {report.toolDiscovery.filterOptions.dcc.map((value) => (
                <option key={value} value={value}>{value === "all" ? "All DCC" : value}</option>
              ))}
            </select>
          </label>
          <label className="field-control">
            <span>Domain</span>
            <select
              aria-label="Domain Filter"
              onChange={(event) => updateDiscoveryFilter("domain", event.currentTarget.value as TaskToolDiscoveryFilters["domain"])}
              value={discoveryFilters.domain}
            >
              {report.toolDiscovery.filterOptions.domains.map((value) => (
                <option key={value} value={value}>{value === "all" ? "All Domains" : value}</option>
              ))}
            </select>
          </label>
          <label className="field-control">
            <span>Owner</span>
            <select
              aria-label="Owner Filter"
              onChange={(event) => updateDiscoveryFilter("owner", event.currentTarget.value)}
              value={discoveryFilters.owner}
            >
              {report.toolDiscovery.filterOptions.owners.map((value) => (
                <option key={value} value={value}>{value === "all" ? "All Owners" : value}</option>
              ))}
            </select>
          </label>
          <label className="field-control">
            <span>Input</span>
            <select
              aria-label="Input Contract Filter"
              onChange={(event) => updateDiscoveryFilter("inputContract", event.currentTarget.value)}
              value={discoveryFilters.inputContract}
            >
              {report.toolDiscovery.filterOptions.inputContracts.map((value) => (
                <option key={value} value={value}>{value === "all" ? "All Inputs" : value}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="task-discovery-summary">
          <div>
            <span>Visible</span>
            <strong>{discoveredTools.length}</strong>
          </div>
          <div>
            <span>Available</span>
            <strong data-status="available">{report.toolDiscovery.summary.availableTools}</strong>
          </div>
          <div>
            <span>Review</span>
            <strong data-status="review">{report.toolDiscovery.summary.reviewOnlyTools}</strong>
          </div>
          <div>
            <span>Mismatch</span>
            <strong data-status="version_mismatch">{report.toolDiscovery.summary.versionMismatches}</strong>
          </div>
          <div>
            <span>Missing</span>
            <strong data-status="missing">{report.toolDiscovery.summary.missingTools}</strong>
          </div>
        </div>
        <div className="task-discovery-list">
          {discoveredTools.map((tool) => (
            <article className="task-discovery-card" data-status={tool.availability} key={tool.id}>
              <span>{availabilityLabels[tool.availability]}</span>
              <strong>{tool.label}</strong>
              <p>{tool.boundary}</p>
              <dl>
                <div><dt>Owner</dt><dd>{tool.owner}</dd></div>
                <div><dt>Version</dt><dd>{tool.detectedVersion ?? "not found"} / {tool.minVersion}</dd></div>
                <div><dt>DCC</dt><dd>{tool.dccTargets.join(", ")}</dd></div>
                <div><dt>Domain</dt><dd>{tool.domains.join(", ")}</dd></div>
              </dl>
              <code>{tool.commandTemplate}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block task-discovery-diagnostics-panel">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Discovery Diagnostics</h3>
        </div>
        <div className="task-diagnostic-list">
          {visibleDiagnostics.map((diagnostic) => (
            <article className="task-diagnostic-row" data-severity={diagnostic.severity} key={diagnostic.id}>
              <span>{diagnosticSeverityLabels[diagnostic.severity]}</span>
              <strong>{diagnostic.title}</strong>
              <p>{diagnostic.detail}</p>
              <code>{diagnostic.action}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block task-launch-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Launch Manifest</h3>
        </div>
        <div className="task-launch-summary" data-gate={report.toolDiscovery.launchManifest.gate}>
          <div>
            <span>Manifest</span>
            <strong>{report.toolDiscovery.launchManifest.manifestId}</strong>
          </div>
          <div>
            <span>Gate</span>
            <strong>{report.toolDiscovery.launchManifest.gate}</strong>
          </div>
          <div>
            <span>Dry Run</span>
            <strong>{report.toolDiscovery.launchManifest.dryRun ? "true" : "false"}</strong>
          </div>
        </div>
        <div className="task-launch-list">
          {visibleLaunchEntries.map((entry) => (
            <article className="task-launch-row" data-gate={entry.gate} key={entry.id}>
              <span>{entry.gate}</span>
              <strong>{entry.label}</strong>
              <p>{entry.reason}</p>
              <code>{entry.command} {entry.args.join(" ")}</code>
              <small>{entry.receiptId} / mutationAllowed={String(entry.mutationAllowed)}</small>
            </article>
          ))}
        </div>
        <ul className="task-boundary-list">
          {report.toolDiscovery.launchManifest.boundaryRules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      </section>

      <section className="logic-block wide task-acceptance-panel">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Reviewer Acceptance</h3>
        </div>
        <div className="task-acceptance-summary" data-gate={report.reviewerAcceptance.summary.gate}>
          <div>
            <span>Gate</span>
            <strong>{report.reviewerAcceptance.summary.gate}</strong>
          </div>
          <div>
            <span>Accepted</span>
            <strong data-state="accepted">{report.reviewerAcceptance.summary.accepted}</strong>
          </div>
          <div>
            <span>Pending</span>
            <strong data-state="pending">{report.reviewerAcceptance.summary.pending}</strong>
          </div>
          <div>
            <span>Deferred</span>
            <strong data-state="deferred">{report.reviewerAcceptance.summary.deferred}</strong>
          </div>
          <div>
            <span>Required Pending</span>
            <strong data-state="pending">{report.reviewerAcceptance.summary.requiredPending}</strong>
          </div>
        </div>
        <div className="task-acceptance-list">
          {report.reviewerAcceptance.items.map((item) => (
            <article className="task-acceptance-row" data-state={item.state} key={item.id}>
              <span>{acceptanceStateLabels[item.state]}</span>
              <strong>{item.scope}</strong>
              <em>{item.owner}</em>
              <p>{item.note}</p>
              <code>{item.receiptId} / {item.evidence}</code>
            </article>
          ))}
        </div>
        <p className="task-next-action">{report.reviewerAcceptance.summary.nextAction}</p>
      </section>

      <section className="logic-block task-final-packet-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Final Handoff Packet</h3>
        </div>
        <div className="task-final-packet-card" data-gate={report.finalHandoffPacket.gate}>
          <span>{report.finalHandoffPacket.gate}</span>
          <strong>{report.finalHandoffPacket.packetId}</strong>
          <p>{report.finalHandoffPacket.summary}</p>
          <code>{report.finalHandoffPacket.packetHash}</code>
        </div>
        <div className="task-artifact-list">
          {report.finalHandoffPacket.artifacts.map((artifact) => (
            <article className="task-artifact-row" data-gate={artifact.gate} key={artifact.id}>
              <span>{artifact.type}</span>
              <strong>{artifact.label}</strong>
              <p>{artifact.required ? "Required" : "Optional"}</p>
              <code>{artifact.path}</code>
            </article>
          ))}
        </div>
        <div className="task-blocker-list">
          {report.finalHandoffPacket.blockedReasons.map((reason) => (
            <code key={reason}>{reason}</code>
          ))}
        </div>
      </section>

      <section className="logic-block task-platform-receipt-panel">
        <div className="section-title">
          <Download size={17} aria-hidden="true" />
          <h3>Platform Receipt</h3>
        </div>
        <div className="task-platform-receipt-card" data-state={report.platformReceipt.state}>
          <span>{receiptStateLabels[report.platformReceipt.state]}</span>
          <strong>{report.platformReceipt.receiptId}</strong>
          <p>{report.platformReceipt.recipient} / issued={String(report.platformReceipt.issued)}</p>
          <code>{report.platformReceipt.checksum}</code>
        </div>
        <div className="task-condition-list">
          {report.platformReceipt.conditions.map((condition) => (
            <article className="task-condition-row" data-state={condition.includes("pending") ? "pending" : "accepted"} key={condition}>
              <span>{condition.includes("pending") ? "Review" : "Pass"}</span>
              <p>{condition}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block task-readiness-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Publish Readiness</h3>
        </div>
        <div className="task-readiness-list">
          {report.readinessChecklist.map((item) => (
            <article className="task-readiness-row" data-status={item.status} key={item.id}>
              <span>{checklistStatusLabels[item.status]}</span>
              <strong>{item.label}</strong>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block task-handoff-panel">
        <div className="section-title">
          <Download size={17} aria-hidden="true" />
          <h3>AI Handoff Draft</h3>
        </div>
        <pre>{report.aiHandoffDraft}</pre>
      </section>
    </div>
  );
}

function normalizeTaskDccRun(action: TaskDccAction, raw: unknown): TaskDccRun {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const discovery = asRecord(record?.discovery ?? report?.discovery);
  const queue = asRecord(record?.queue ?? report?.queue);
  const dryRun = asRecord(record?.dry_run ?? report?.dryRun);
  const discoverySummary = asRecord(discovery?.summary);
  const queueSummary = asRecord(queue?.summary);
  const drySummary = asRecord(dryRun?.summary);
  const assets = normalizeTaskDccAssets(discovery?.assets);
  const tasks = normalizeTaskDccTasks(queue?.tasks);
  const receipts = normalizeTaskDccReceipts(dryRun?.receipts);
  const path = readString(record?.path);
  const gate =
    readString(drySummary?.gate) ??
    readString(queueSummary?.gate) ??
    readString(discoverySummary?.gate) ??
    (action.id === "fixture" ? "Ready" : "Preview");

  return {
    action: action.id,
    label: action.label,
    raw,
    assetCount: readNumber(discoverySummary?.asset_count) ?? assets.length,
    taskCount: readNumber(queueSummary?.total) ?? tasks.length,
    doneCount: readNumber(drySummary?.done) ?? readNumber(queueSummary?.done) ?? 0,
    reviewCount: readNumber(drySummary?.review) ?? readNumber(queueSummary?.review) ?? 0,
    blockedCount: readNumber(drySummary?.blocked) ?? readNumber(queueSummary?.blocked) ?? 0,
    gate,
    path: path ?? undefined,
    assets,
    tasks,
    receipts,
    updatedAt: new Date().toLocaleTimeString(),
  };
}

function normalizeTaskDccAssets(value: unknown): TaskDccAssetRow[] {
  return asRecordArray(value).map((item, index) => {
    const review = Array.isArray(item.review) ? item.review.filter((entry) => typeof entry === "string") : [];
    const blockers = Array.isArray(item.blockers) ? item.blockers.filter((entry) => typeof entry === "string") : [];
    const issues = [...blockers, ...review].join(", ") || "clean";

    return {
      id: readString(item.id) ?? `asset-${index + 1}`,
      node: readString(item.node) ?? "<unknown>",
      gate: readString(item.gate) ?? "Review",
      role: readString(item.role) ?? "unknown",
      lod: readString(item.lod) ?? "unknown",
      materials: readNumber(item.material_count) ?? 0,
      textures: readNumber(item.texture_count) ?? 0,
      triangles: readNumber(item.triangles) ?? 0,
      issues,
    };
  });
}

function normalizeTaskDccTasks(value: unknown): TaskDccQueueRow[] {
  return asRecordArray(value).map((item) => ({
    id: readString(item.id) ?? "<unknown>",
    asset: readString(item.asset) ?? "<scene>",
    label: readString(item.label) ?? "<unnamed task>",
    phase: readString(item.phase) ?? "unknown",
    status: readString(item.status) ?? "review",
    evidence: readString(item.evidence) ?? "-",
  }));
}

function normalizeTaskDccReceipts(value: unknown): TaskDccReceiptRow[] {
  return asRecordArray(value).map((item) => ({
    id: readString(item.id) ?? "<unknown>",
    asset: readString(item.asset) ?? "<scene>",
    gate: readString(item.gate) ?? "Review",
    state: readString(item.state) ?? "held_for_review",
    nextAction: readString(item.next_action) ?? readString(item.nextAction) ?? "-",
  }));
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.flatMap((item) => {
    const record = asRecord(item);
    return record ? [record] : [];
  });
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function readNumber(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function safeJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return error instanceof Error ? error.message : "Unable to serialize payload.";
  }
}
