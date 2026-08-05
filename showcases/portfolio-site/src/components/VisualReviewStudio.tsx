import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Bell,
  BarChart3,
  Camera,
  Check,
  CircleSlash,
  ClipboardList,
  Download,
  Eye,
  FileJson,
  GitBranch,
  Images,
  ListFilter,
  ListChecks,
  MessageSquare,
  PackageCheck,
  RefreshCw,
  Send,
  ShieldAlert,
  SlidersHorizontal,
  Sparkles,
  Target,
  UserCheck,
} from "lucide-react";
import {
  applyVisualFixtureEditorState,
  buildAiReviewDraft,
  buildBatchReviewReport,
  buildVisualReviewReport,
  createVisualFixtureEditorPresetState,
  createVisualFixtureEditorState,
  createVisualReviewAuditEvent,
  defaultVisualReviewOptions,
  getSelectedCameras,
  getVisualFixtureEditSummary,
  visualFixtureEditorPresets,
  visualPassPresets,
  visualReviewFixtures,
  type CameraGroupId,
  type FindingSeverity,
  type HandoffDeliveryOverrides,
  type HandoffDeliveryState,
  type PassPresetId,
  type PassStatus,
  type ReviewHandoffPacket,
  type ReviewHandoffSection,
  type ReviewDecisionState,
  type ReviewGate,
  type ReviewQueueItem,
  type ReviewQueueOwner,
  type ReviewQueueState,
  type ReviewQueueStateOverrides,
  type VisualBatchItem,
  type VisualDiffSignal,
  type VisualFixtureEditSummary,
  type VisualFixtureEditorPresetId,
  type VisualFixtureEditorState,
  type VisualPassDrilldown,
  type VisualPassRun,
  type VisualReleaseCriterion,
  type VisualReleaseDecision,
  type VisualReleaseGate,
  type VisualReviewFixture,
  type VisualReviewReport,
  type VisualReviewAuditAction,
  type VisualReviewAuditEvent,
  type VisualReviewOptions,
  type VisualSignalId,
} from "../data/visualReview";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

const gateLabels: Record<ReviewGate, string> = {
  Ready: "Ready",
  Review: "Review",
  Blocked: "Blocked",
};

const severityLabels: Record<FindingSeverity, string> = {
  info: "Info",
  warning: "Review",
  error: "Block",
};

const passStatusLabels: Record<PassStatus, string> = {
  run: "Run",
  skipped: "Skip",
};

const decisionLabels: Record<ReviewDecisionState, string> = {
  pending: "Pending",
  accepted: "Accepted",
  needs_fix: "Needs Fix",
};

const queueOwnerLabels: Record<ReviewQueueOwner, string> = {
  artist: "Artist",
  ta: "TA",
  reviewer: "Reviewer",
};

const queueStateLabels: Record<ReviewQueueState, string> = {
  todo: "Todo",
  blocked: "Blocked",
  ready: "Ready",
};

const deliveryStateLabels: Record<HandoffDeliveryState, string> = {
  not_required: "No Item",
  draft: "Draft",
  sent: "Sent",
  failed: "Failed",
  read: "Read",
  acknowledged: "Ack",
};

const releaseDecisionLabels: Record<VisualReleaseDecision, string> = {
  release_candidate: "Release Candidate",
  hold_for_review: "Hold for Review",
  blocked_from_release: "Blocked",
};

const resolutionOptions = [512, 1024, 1536, 2048];
const queueOwnerOptions = ["all", "artist", "ta", "reviewer"] as const;
const queueGateOptions = ["all", "Blocked", "Review", "Ready"] as const;
type QueueOwnerFilter = (typeof queueOwnerOptions)[number];
type QueueGateFilter = (typeof queueGateOptions)[number];
type VisualWorkflowSectionId = "setup" | "capture" | "triage" | "handoff" | "batch" | "draft";
type VisualWorkflowPresetId = "full" | "review" | "release";

const visualWorkflowSections: {
  id: VisualWorkflowSectionId;
  label: string;
  detail: string;
}[] = [
  { id: "setup", label: "Setup", detail: "Fixture, scenario, import diff, LOD split" },
  { id: "capture", label: "Capture", detail: "Signal thresholds, pass matrix, shot manifest" },
  { id: "triage", label: "Triage", detail: "Findings, owner queue, action state" },
  { id: "handoff", label: "Handoff", detail: "Owner packet, delivery receipt, release gate" },
  { id: "batch", label: "Batch", detail: "Batch runner, item detail, release preview" },
  { id: "draft", label: "Draft", detail: "AI review draft, audit, evidence package" },
];

const visualWorkflowPresets: Record<VisualWorkflowPresetId, VisualWorkflowSectionId[]> = {
  full: ["setup", "capture", "triage", "handoff", "batch", "draft"],
  review: ["setup", "capture", "triage", "draft"],
  release: ["setup", "triage", "handoff", "batch"],
};

const visualWorkflowPresetLabels: Record<VisualWorkflowPresetId, string> = {
  full: "Full Workbench",
  review: "Review Focus",
  release: "Release Focus",
};

type VisualDccActionId = "rig" | "manifest" | "preview" | "export";

interface VisualDccAction {
  id: VisualDccActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface VisualDccPassRow {
  id: string;
  label: string;
  status: string;
  reason: string;
  cameraCount: number;
  imageCount: number;
}

interface VisualDccRun {
  action: VisualDccActionId;
  label: string;
  raw: unknown;
  cameraCount: number;
  meshCount: number;
  runCount: number;
  skippedCount: number;
  imageCount: number;
  plannedCaptures: number;
  gate: string;
  outputDir?: string;
  path?: string;
  passes: VisualDccPassRow[];
  updatedAt: string;
}

const visualDccActions: VisualDccAction[] = [
  { id: "rig", label: "Create Rig", method: "visual_review_create_camera_rig" },
  { id: "manifest", label: "Build Manifest", method: "visual_review_build_pass_manifest" },
  { id: "preview", label: "Preview Capture", method: "visual_review_preview_capture" },
  { id: "export", label: "Export DCC Review", method: "visual_review_export_report" },
];

export function VisualReviewStudio() {
  const [selectedFixtureId, setSelectedFixtureId] = useState(visualReviewFixtures[0].id);
  const [selectedPassId, setSelectedPassId] = useState<PassPresetId>(visualPassPresets[0].id);
  const [selectedSignalId, setSelectedSignalId] = useState<VisualSignalId | undefined>();
  const [selectedBatchItemId, setSelectedBatchItemId] = useState(visualReviewFixtures[0].id);
  const [selectedQueueId, setSelectedQueueId] = useState<string | undefined>();
  const [queueOwnerFilter, setQueueOwnerFilter] = useState<(typeof queueOwnerOptions)[number]>("all");
  const [queueGateFilter, setQueueGateFilter] = useState<(typeof queueGateOptions)[number]>("all");
  const [queueStateOverrides, setQueueStateOverrides] = useState<ReviewQueueStateOverrides>({});
  const [selectedHandoffOwner, setSelectedHandoffOwner] = useState<ReviewQueueOwner>("artist");
  const [handoffDeliveryOverrides, setHandoffDeliveryOverrides] = useState<HandoffDeliveryOverrides>({});
  const [options, setOptions] = useState<VisualReviewOptions>(defaultVisualReviewOptions);
  const [decisionState, setDecisionState] = useState<ReviewDecisionState>("pending");
  const [draftOverride, setDraftOverride] = useState<string | undefined>();
  const [reviewAudit, setReviewAudit] = useState<VisualReviewAuditEvent[]>([]);
  const [fixtureEdits, setFixtureEdits] = useState<Partial<Record<string, VisualFixtureEditorState>>>({});
  const [workflowPresetId, setWorkflowPresetId] = useState<VisualWorkflowPresetId>("full");
  const [openWorkflowSections, setOpenWorkflowSections] = useState<VisualWorkflowSectionId[]>(
    visualWorkflowPresets.full,
  );
  const [dccSnapshot, setDccSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [dccBusyAction, setDccBusyAction] = useState<VisualDccActionId | null>(null);
  const [dccRun, setDccRun] = useState<VisualDccRun | null>(null);
  const [dccError, setDccError] = useState<string | null>(null);

  const sourceFixture = useMemo(
    () => visualReviewFixtures.find((item) => item.id === selectedFixtureId) ?? visualReviewFixtures[0],
    [selectedFixtureId],
  );
  const fixtureEditorState = useMemo(
    () => fixtureEdits[sourceFixture.id] ?? createVisualFixtureEditorState(sourceFixture),
    [fixtureEdits, sourceFixture],
  );
  const fixture = useMemo(
    () => applyVisualFixtureEditorState(sourceFixture, fixtureEditorState),
    [fixtureEditorState, sourceFixture],
  );
  const fixtureEditSummary = useMemo(
    () => getVisualFixtureEditSummary(sourceFixture, fixture),
    [fixture, sourceFixture],
  );
  const editedFixtures = useMemo(
    () => visualReviewFixtures.map((item) => applyVisualFixtureEditorState(
      item,
      fixtureEdits[item.id] ?? createVisualFixtureEditorState(item),
    )),
    [fixtureEdits],
  );
  const fixtureEditSummaries = useMemo(
    () => visualReviewFixtures.reduce<Partial<Record<string, VisualFixtureEditSummary>>>((summaries, item, index) => {
      const editedFixture = editedFixtures[index] ?? item;
      summaries[item.id] = getVisualFixtureEditSummary(item, editedFixture);
      return summaries;
    }, {}),
    [editedFixtures],
  );
  const computedReport = useMemo(
    () => buildVisualReviewReport(
      fixture,
      options,
      decisionState,
      undefined,
      [],
      {},
      {},
      fixtureEditSummary,
    ),
    [decisionState, fixture, fixtureEditSummary, options],
  );
  const report = useMemo(
    () => buildVisualReviewReport(
      fixture,
      options,
      decisionState,
      draftOverride,
      reviewAudit,
      queueStateOverrides,
      handoffDeliveryOverrides,
      fixtureEditSummary,
    ),
    [decisionState, draftOverride, fixture, fixtureEditSummary, handoffDeliveryOverrides, options, queueStateOverrides, reviewAudit],
  );
  const batchReport = useMemo(
    () => buildBatchReviewReport(editedFixtures, options, fixtureEditSummaries),
    [editedFixtures, fixtureEditSummaries, options],
  );
  const selectedPass = useMemo(
    () => report.passDrilldowns.find((item) => item.presetId === selectedPassId) ?? report.passDrilldowns[0]!,
    [report.passDrilldowns, selectedPassId],
  );
  const selectedBatchItem = useMemo(
    () => batchReport.items.find((item) => item.fixtureId === selectedBatchItemId) ?? batchReport.items[0]!,
    [batchReport.items, selectedBatchItemId],
  );
  const filteredQueue = useMemo(
    () => report.reviewQueue.filter((item) => {
      const ownerMatches = queueOwnerFilter === "all" || item.owner === queueOwnerFilter;
      const gateMatches = queueGateFilter === "all" || item.gate === queueGateFilter;
      return ownerMatches && gateMatches;
    }),
    [queueGateFilter, queueOwnerFilter, report.reviewQueue],
  );
  const selectedQueueItem = useMemo(
    () => report.reviewQueue.find((item) => item.id === selectedQueueId) ?? filteredQueue[0] ?? report.reviewQueue[0],
    [filteredQueue, report.reviewQueue, selectedQueueId],
  );
  const selectedHandoffSection = useMemo(
    () => report.handoffPacket.sections.find((section) => section.owner === selectedHandoffOwner) ?? report.handoffPacket.sections[0]!,
    [report.handoffPacket.sections, selectedHandoffOwner],
  );
  const cameras = getSelectedCameras(fixture, options.cameraGroups);
  const runCount = report.passRuns.filter((run) => run.status === "run").length;
  const skippedCount = report.passRuns.length - runCount;
  const openWorkflowSet = useMemo(
    () => new Set(openWorkflowSections),
    [openWorkflowSections],
  );
  const dccConnected = dccSnapshot.available;

  useEffect(() => {
    resetReviewRuntime();
  }, [selectedFixtureId]);

  function resetReviewRuntime() {
    setDecisionState("pending");
    setDraftOverride(undefined);
    setReviewAudit([]);
    setSelectedQueueId(undefined);
    setQueueStateOverrides({});
    setSelectedHandoffOwner("artist");
    setHandoffDeliveryOverrides({});
  }

  function selectFixture(fixtureId: string) {
    setSelectedFixtureId(fixtureId);
    setSelectedBatchItemId(fixtureId);
    setSelectedSignalId(undefined);
    setSelectedQueueId(undefined);
  }

  function updateFixtureEditorField<K extends keyof VisualFixtureEditorState>(
    field: K,
    value: VisualFixtureEditorState[K],
  ) {
    setFixtureEdits((current) => ({
      ...current,
      [sourceFixture.id]: {
        ...fixtureEditorState,
        [field]: value,
      },
    }));
    setSelectedSignalId(undefined);
    resetReviewRuntime();
  }

  function applyFixtureEditorPreset(presetId: VisualFixtureEditorPresetId) {
    if (presetId === "source") {
      resetFixtureEdit();
      return;
    }
    setFixtureEdits((current) => ({
      ...current,
      [sourceFixture.id]: createVisualFixtureEditorPresetState(sourceFixture, presetId),
    }));
    setSelectedSignalId(undefined);
    resetReviewRuntime();
  }

  function resetFixtureEdit() {
    setFixtureEdits((current) => {
      const next = { ...current };
      delete next[sourceFixture.id];
      return next;
    });
    setSelectedSignalId(undefined);
    resetReviewRuntime();
  }

  function applyWorkflowPreset(presetId: VisualWorkflowPresetId) {
    setWorkflowPresetId(presetId);
    setOpenWorkflowSections(visualWorkflowPresets[presetId]);
  }

  function toggleWorkflowSection(sectionId: VisualWorkflowSectionId) {
    setOpenWorkflowSections((current) => {
      const isOpen = current.includes(sectionId);
      const next = isOpen
        ? current.filter((item) => item !== sectionId)
        : [...current, sectionId];
      const sorted = visualWorkflowSections
        .map((section) => section.id)
        .filter((item) => next.includes(item));
      return sorted.length > 0 ? sorted : current;
    });
    setWorkflowPresetId("full");
  }

  function jumpToWorkflowSection(sectionId: VisualWorkflowSectionId) {
    const element = document.getElementById(`visual-workflow-${sectionId}`);
    element?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function selectSignal(signal: VisualDiffSignal) {
    setSelectedSignalId(signal.id);
    setSelectedPassId(signal.relatedPasses[0] ?? visualPassPresets[0].id);
  }

  function selectPass(passId: PassPresetId) {
    setSelectedPassId(passId);
    setSelectedSignalId(undefined);
  }

  function selectQueuePass(passId: PassPresetId) {
    setSelectedPassId(passId);
    setSelectedSignalId(undefined);
  }

  function updateQueueState(item: ReviewQueueItem, state: ReviewQueueState) {
    setQueueStateOverrides((current) => ({ ...current, [item.id]: state }));
    setSelectedQueueId(item.id);
    const action: VisualReviewAuditAction =
      state === "blocked" ? "queue_blocked" : state === "ready" ? "queue_ready" : "queue_todo";
    recordAudit(
      action,
      decisionState,
      decisionState,
      draftOverride ?? computedReport.aiReviewDraft,
      `${item.sourceFindingTitle}: queue state set to ${state}.`,
    );
  }

  function updateHandoffDelivery(owner: ReviewQueueOwner, state: HandoffDeliveryState) {
    const section = report.handoffPacket.sections.find((item) => item.owner === owner);
    if (!section || section.total === 0) {
      return;
    }
    const previous = section.delivery;
    const attempts = getNextDeliveryAttempts(previous.state, state, previous.attempts);
    const lastEvent = `${section.ownerLabel} delivery state set to ${deliveryStateLabels[state]}.`;
    setSelectedHandoffOwner(owner);
    setHandoffDeliveryOverrides((current) => ({
      ...current,
      [owner]: {
        state,
        attempts,
        lastEvent,
      },
    }));
    recordAudit(
      getDeliveryAuditAction(state),
      decisionState,
      decisionState,
      draftOverride ?? computedReport.aiReviewDraft,
      `${section.ownerLabel} handoff delivery changed from ${previous.state} to ${state}.`,
    );
  }

  function recordAudit(
    action: VisualReviewAuditAction,
    fromDecision: ReviewDecisionState,
    toDecision: ReviewDecisionState,
    draft: string,
    note: string,
  ) {
    setReviewAudit((current) => [
      ...current,
      createVisualReviewAuditEvent(
        current.length + 1,
        action,
        fixture,
        report.gate,
        fromDecision,
        toDecision,
        draft,
        note,
      ),
    ]);
  }

  function toggleCameraGroup(group: CameraGroupId) {
    setOptions((current) => {
      const hasGroup = current.cameraGroups.includes(group);
      const nextGroups = hasGroup
        ? current.cameraGroups.filter((item) => item !== group)
        : [...current.cameraGroups, group];

      return {
        ...current,
        cameraGroups: nextGroups.length > 0 ? nextGroups : current.cameraGroups,
      };
    });
  }

  function updateResolution(value: number) {
    setOptions((current) => ({ ...current, width: value, height: value }));
  }

  function resetRun() {
    setOptions(defaultVisualReviewOptions);
    setSelectedPassId(visualPassPresets[0].id);
    setSelectedSignalId(undefined);
    resetReviewRuntime();
  }

  function regenerateDraft() {
    const nextDraft = buildAiReviewDraft(fixture, report.findings, report.gate);
    recordAudit("draft_regenerated", decisionState, "pending", nextDraft, "Regenerated AI review draft from deterministic findings.");
    setDraftOverride(nextDraft);
    setDecisionState("pending");
  }

  function updateDraft(value: string) {
    setDraftOverride(value);
    setDecisionState("pending");
    setReviewAudit((current) => {
      const alreadyRecorded = current.some(
        (event) => event.fixtureId === fixture.id && event.action === "draft_edited",
      );
      if (alreadyRecorded) {
        return current;
      }
      return [
        ...current,
        createVisualReviewAuditEvent(
          current.length + 1,
          "draft_edited",
          fixture,
          report.gate,
          decisionState,
          "pending",
          value,
          "Manual edit recorded from AI draft textarea.",
        ),
      ];
    });
  }

  function markNeedsFix() {
    const draft = draftOverride ?? computedReport.aiReviewDraft;
    recordAudit("needs_fix", decisionState, "needs_fix", draft, "Reviewer marked the current evidence package as needing fixes.");
    setDecisionState("needs_fix");
  }

  function acceptReview() {
    const draft = draftOverride ?? computedReport.aiReviewDraft;
    recordAudit("accepted", decisionState, "accepted", draft, "Reviewer accepted the current review draft as the handoff note.");
    setDecisionState("accepted");
  }

  function downloadReport() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${fixture.id}-visual-review-report.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadBatchReport() {
    const blob = new Blob([JSON.stringify(batchReport, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "visual-review-batch-report.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadHandoffPacket() {
    const blob = new Blob([JSON.stringify(report.handoffPacket, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${fixture.id}-visual-review-handoff.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadReleaseGate() {
    const blob = new Blob([JSON.stringify(report.releaseGate, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${fixture.id}-visual-release-gate.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function runVisualDccAction(action: VisualDccAction) {
    const latest = getBridgeSnapshot();
    setDccSnapshot(latest);

    if (!latest.available) {
      setDccError("Open this module through the Maya AuroraView host to run visual review DCC actions.");
      return;
    }

    setDccBusyAction(action.id);
    setDccError(null);

    try {
      const result = await callMayaBridge<unknown>(action.method, {
        include_all: true,
        camera_groups: options.cameraGroups,
        width: options.width,
        height: options.height,
        label: "visual-review-dcc-scene",
      });
      setDccRun(normalizeVisualDccRun(action, result));
      setDccSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setDccError(caught instanceof Error ? caught.message : "Visual Review DCC call failed.");
    } finally {
      setDccBusyAction(null);
    }
  }

  return (
    <div className="view-grid visual-review-workbench">
      <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>
          视觉评审的核心不是截图，而是固定变量。import diff 定义 A/B 槽，LOD 命名定义可比较对象，
          pass preset 定义材质和可见性，报告再把跳过原因、阈值和人工结论固定下来。
        </p>
      </section>

      <section className="schema-band visual-summary-band" aria-label="visual review summary">
        <div>
          <span>Gate</span>
          <strong data-gate={report.gate}>{gateLabels[report.gate]}</strong>
        </div>
        <div>
          <span>Passes</span>
          <strong>{runCount} run / {skippedCount} skip</strong>
        </div>
        <div>
          <span>Images</span>
          <strong>{report.evidencePackage.imageCount}</strong>
        </div>
        <div>
          <span>Decision</span>
          <strong>{decisionLabels[decisionState]}</strong>
        </div>
      </section>

      <section className="logic-block wide visual-dcc-panel">
        <div className="editor-header">
          <div className="section-title">
            <Camera size={17} aria-hidden="true" />
            <h3>Maya Capture Setup</h3>
          </div>
          <span className="bridge-state" data-state={dccConnected ? "connected" : "offline"}>
            {dccConnected ? "Connected" : "Preview"}
          </span>
        </div>

        <div className="visual-dcc-action-grid" aria-label="Maya visual review actions">
          {visualDccActions.map((action) => {
            const busy = dccBusyAction === action.id;

            return (
              <button
                className="bridge-action-button"
                disabled={!dccConnected || dccBusyAction !== null}
                key={action.id}
                onClick={() => runVisualDccAction(action)}
                type="button"
              >
                {action.id === "rig" ? (
                  <Camera size={15} aria-hidden="true" />
                ) : action.id === "manifest" ? (
                  <ListChecks size={15} aria-hidden="true" />
                ) : action.id === "preview" ? (
                  <Images size={15} aria-hidden="true" />
                ) : (
                  <FileJson size={15} aria-hidden="true" />
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

        <div className="visual-dcc-summary">
          <div>
            <span>Last Action</span>
            <strong>{dccRun?.label ?? "Not Run"}</strong>
          </div>
          <div>
            <span>Cameras</span>
            <strong>{dccRun?.cameraCount ?? "-"}</strong>
          </div>
          <div>
            <span>Meshes</span>
            <strong>{dccRun?.meshCount ?? "-"}</strong>
          </div>
          <div>
            <span>Passes</span>
            <strong>{dccRun ? `${dccRun.runCount} / ${dccRun.skippedCount}` : "-"}</strong>
          </div>
          <div>
            <span>Images</span>
            <strong>{dccRun?.imageCount ?? "-"}</strong>
          </div>
          <div>
            <span>Gate</span>
            <strong data-gate={dccRun?.gate ?? "Preview"}>{dccRun?.gate ?? "Preview"}</strong>
          </div>
        </div>

        {dccRun ? (
          <div className="visual-dcc-grid">
            <div className="visual-dcc-pass-list">
              {dccRun.passes.length > 0 ? (
                dccRun.passes.map((pass) => (
                  <article data-status={pass.status} key={pass.id}>
                    <div>
                      <strong>{pass.label}</strong>
                      <span>{pass.status}</span>
                    </div>
                    <p>{pass.reason}</p>
                    <code>{pass.cameraCount} camera(s) / {pass.imageCount} image(s)</code>
                  </article>
                ))
              ) : (
                <p className="empty-state">Create a rig or build a manifest to populate DCC pass rows.</p>
              )}
            </div>

            <div className="visual-dcc-output">
              <span>Output</span>
              <code>{dccRun.outputDir ?? dccRun.path ?? "No DCC artifact path yet."}</code>
              <p>
                Planned captures: {dccRun.plannedCaptures}. Export saves a JSON report; preview only plans image paths until GUI playblast is enabled.
              </p>
            </div>

            <div className="dcc-rule-json-panel">
              <div className="bridge-result-title">
                <span>{dccRun.path ?? "DCC visual payload"}</span>
                <strong>JSON</strong>
              </div>
              <pre>{safeJson(dccRun.raw)}</pre>
            </div>
          </div>
        ) : (
          <p className="empty-state">
            Create a review camera rig, then build the Maya pass manifest against all scene meshes.
          </p>
        )}
      </section>

      <div className="fixture-tabs visual-fixture-tabs" aria-label="visual review fixtures">
        {visualReviewFixtures.map((item) => (
          <button
            aria-pressed={item.id === fixture.id}
            className="fixture-button"
            key={item.id}
            onClick={() => selectFixture(item.id)}
            type="button"
          >
            <span>{item.name}</span>
            <strong>{item.discoveryMode === "fuzzy_camera_group" ? "Camera_Group" : "cam_*"}</strong>
          </button>
        ))}
      </div>

      <WorkflowNavigator
        activePreset={workflowPresetId}
        openSections={openWorkflowSet}
        report={report}
        onApplyPreset={applyWorkflowPreset}
        onJump={jumpToWorkflowSection}
        onToggle={toggleWorkflowSection}
      />

      <WorkflowSectionGroup
        id="setup"
        isOpen={openWorkflowSet.has("setup")}
        onExpand={() => toggleWorkflowSection("setup")}
      >
        <FixtureEditorPanel
          report={report}
          sourceFixture={sourceFixture}
          state={fixtureEditorState}
          summary={fixtureEditSummary}
          onApplyPreset={applyFixtureEditorPreset}
          onChange={updateFixtureEditorField}
          onReset={resetFixtureEdit}
        />

        <section className="logic-block wide case-study-card">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Case Study Card</h3>
        </div>
        <div className="case-grid">
          <div>
            <span>Problem</span>
            <p>武器迭代评审依赖人工对图，变量太多时看不出是造型、LOD、材质、单位还是截图环境的问题。</p>
          </div>
          <div>
            <span>Core Logic</span>
            <p>基准 A 和变体 B 先做 import diff，再按 LOD0/DT 分桶，5 个 pass 固定材质、可见性和输出命名。</p>
          </div>
          <div>
            <span>AI Boundary</span>
            <p>AI 只把 deterministic finding 写成 review comment 草案，gate 仍由 pass 可运行性和阈值决定。</p>
          </div>
          <div>
            <span>Evidence</span>
            <p>shot manifest、跳过原因、scene backup、HTML overview 和 JSON report 都能直接交给 reviewer 复盘。</p>
          </div>
        </div>
      </section>

      <section className="logic-block wide review-controls">
        <div className="editor-header">
          <div className="section-title">
            <SlidersHorizontal size={17} aria-hidden="true" />
            <h3>Capture Contract</h3>
          </div>
          <div className="mini-toolbar">
            <button className="icon-button compact" onClick={resetRun} type="button">
              <RefreshCw size={16} aria-hidden="true" />
              <span>Reset Run</span>
            </button>
            <button className="primary-button compact" onClick={downloadReport} type="button">
              <Download size={16} aria-hidden="true" />
              <span>Export Report</span>
            </button>
          </div>
        </div>

        <div className="review-control-grid">
          <label className="field-control">
            <span>Resolution</span>
            <select
              value={options.width}
              onChange={(event) => updateResolution(Number(event.currentTarget.value))}
            >
              {resolutionOptions.map((size) => (
                <option key={size} value={size}>{size} x {size}</option>
              ))}
            </select>
          </label>

          <div className="review-toggle-group" aria-label="camera groups">
            <span>Camera Groups</span>
            <div>
              {(["basic", "detail"] as CameraGroupId[]).map((group) => (
                <button
                  aria-pressed={options.cameraGroups.includes(group)}
                  className="toggle-pill"
                  key={group}
                  onClick={() => toggleCameraGroup(group)}
                  type="button"
                >
                  <Camera size={15} aria-hidden="true" />
                  <span>{group}</span>
                </button>
              ))}
            </div>
          </div>

          <label className="check-row">
            <input
              checked={options.saveSceneBackup}
              onChange={(event) => setOptions((current) => ({ ...current, saveSceneBackup: event.currentTarget.checked }))}
              type="checkbox"
            />
            <span>Save WB LOD0 scene backup</span>
          </label>

          <label className="check-row">
            <input
              checked={options.notifyEnabled}
              onChange={(event) => setOptions((current) => ({ ...current, notifyEnabled: event.currentTarget.checked }))}
              type="checkbox"
            />
            <span>Prepare WeCom notification</span>
          </label>
        </div>
      </section>

      <section className="logic-block review-slot-panel">
        <div className="section-title">
          <FileJson size={17} aria-hidden="true" />
          <h3>A / B Import Diff</h3>
        </div>
        <div className="review-slot-grid">
          {[fixture.baseline, fixture.variant].map((slot) => (
            <div className="review-slot" key={slot.label}>
              <span>Slot {slot.label}</span>
              <strong>{slot.name}</strong>
              <p>{slot.sourcePath}</p>
              <dl>
                <div>
                  <dt>Unit</dt>
                  <dd>{slot.unit}</dd>
                </div>
                <div>
                  <dt>Meshes</dt>
                  <dd>{slot.meshes.length}</dd>
                </div>
                <div>
                  <dt>Materials</dt>
                  <dd>{slot.materialCount}</dd>
                </div>
                <div>
                  <dt>Missing Tex</dt>
                  <dd>{slot.unresolvedTextures.length}</dd>
                </div>
              </dl>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block review-slot-panel">
        <div className="section-title">
          <ListChecks size={17} aria-hidden="true" />
          <h3>LOD Buckets</h3>
        </div>
        <div className="lod-split-table" role="table" aria-label="lod split">
          <div role="row">
            <span>Slot</span>
            <span>LOD0</span>
            <span>DT</span>
            <span>Other</span>
          </div>
          {report.lodSplit.map((split) => (
            <div key={split.slot} role="row">
              <strong>{split.slot}</strong>
              <span>{split.LOD0}</span>
              <span>{split.DT}</span>
              <span>{split.other}</span>
            </div>
          ))}
        </div>
        <p className="muted-note">
          LOD0 先匹配，DT 次之，其他 mesh 在 5-pass capture 中隐藏。
        </p>
      </section>
      </WorkflowSectionGroup>

      <WorkflowSectionGroup
        id="capture"
        isOpen={openWorkflowSet.has("capture")}
        onExpand={() => toggleWorkflowSection("capture")}
      >
        <section className="logic-block wide">
        <div className="section-title">
          <BarChart3 size={17} aria-hidden="true" />
          <h3>Signal Thresholds</h3>
        </div>
        <div className="signal-grid">
          {report.diffSignals.map((signal) => (
            <SignalCard
              isSelected={signal.id === selectedSignalId}
              key={signal.id}
              onSelect={selectSignal}
              signal={signal}
            />
          ))}
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Images size={17} aria-hidden="true" />
          <h3>Pass Matrix</h3>
        </div>
        <div className="pass-contract-grid">
          {report.passRuns.map((run) => (
            <PassCard
              isSelected={run.presetId === selectedPass.presetId}
              key={run.presetId}
              onSelect={selectPass}
              run={run}
            />
          ))}
        </div>
      </section>

      <PassDrilldownPanel drilldown={selectedPass} selectedSignalId={selectedSignalId} />

      <section className="logic-block wide">
        <div className="section-title">
          <Eye size={17} aria-hidden="true" />
          <h3>Shot Manifest</h3>
        </div>
        <div className="shot-manifest">
          {report.passRuns.map((run) => (
            <div className="shot-row" data-status={run.status} key={run.presetId}>
              <span>{run.label}</span>
              <strong>{run.imageCount}</strong>
              <code>{run.shotNames.slice(0, 3).join("  ") || run.reason}</code>
            </div>
          ))}
        </div>
        <p className="muted-note">
          Selected cameras: {cameras.join(", ")}
        </p>
      </section>
      </WorkflowSectionGroup>

      <WorkflowSectionGroup
        id="triage"
        isOpen={openWorkflowSet.has("triage")}
        onExpand={() => toggleWorkflowSection("triage")}
      >
        <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Review Findings</h3>
        </div>
        <div className="finding-stack">
          {report.findings.map((finding) => (
            <article className="finding-row" data-severity={finding.severity} key={finding.id}>
              <div>
                <span>{severityLabels[finding.severity]}</span>
                <strong>{finding.title}</strong>
                <p>{finding.detail}</p>
              </div>
              <div>
                <span>{finding.channel}</span>
                <p>{finding.suggestedAction}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <ReviewQueuePanel
        gateFilter={queueGateFilter}
        items={filteredQueue}
        onGateFilterChange={setQueueGateFilter}
        onOwnerFilterChange={setQueueOwnerFilter}
        onSelectItem={setSelectedQueueId}
        onSelectPass={selectQueuePass}
        onUpdateState={updateQueueState}
        ownerFilter={queueOwnerFilter}
        selectedItem={selectedQueueItem}
        summary={report.reviewQueueSummary}
      />
      </WorkflowSectionGroup>

      <WorkflowSectionGroup
        id="handoff"
        isOpen={openWorkflowSet.has("handoff")}
        onExpand={() => toggleWorkflowSection("handoff")}
      >
        <HandoffPacketPanel
          onExport={downloadHandoffPacket}
          onSelectOwner={setSelectedHandoffOwner}
          onUpdateDelivery={updateHandoffDelivery}
          packet={report.handoffPacket}
          selectedSection={selectedHandoffSection}
        />

        <ReleaseGatePanel gate={report.releaseGate} onExport={downloadReleaseGate} />
      </WorkflowSectionGroup>

      <WorkflowSectionGroup
        id="batch"
        isOpen={openWorkflowSet.has("batch")}
        onExpand={() => toggleWorkflowSection("batch")}
      >
        <section className="logic-block wide batch-review-panel">
        <div className="editor-header">
          <div className="section-title">
            <ClipboardList size={17} aria-hidden="true" />
            <h3>Batch Runner Overview</h3>
          </div>
          <button className="icon-button compact" onClick={downloadBatchReport} type="button">
            <Download size={16} aria-hidden="true" />
            <span>Export Batch</span>
          </button>
        </div>
        <div className="batch-summary-row">
          <div>
            <span>Capture</span>
            <strong>{batchReport.success} ok / {batchReport.failed} failed</strong>
          </div>
          <div>
            <span>Ready</span>
            <strong data-gate="Ready">{batchReport.ready}</strong>
          </div>
          <div>
            <span>Review</span>
            <strong data-gate="Review">{batchReport.review}</strong>
          </div>
          <div>
            <span>Blocked</span>
            <strong data-gate="Blocked">{batchReport.blocked}</strong>
          </div>
        </div>
        <div className="batch-table" role="table" aria-label="visual batch runner">
          <div role="row">
            <span>Variant</span>
            <span>Capture</span>
            <span>Gate</span>
            <span>Passes</span>
            <span>Images</span>
            <span>Reason</span>
          </div>
          {batchReport.items.map((item) => (
            <button
              aria-pressed={item.fixtureId === selectedBatchItem.fixtureId}
              className="batch-row"
              data-gate={item.reviewGate}
              key={item.fixtureId}
              onClick={() => selectFixture(item.fixtureId)}
              role="row"
              type="button"
            >
              <strong>{item.name}</strong>
              <span>{item.captureStatus}</span>
              <span>{item.reviewGate}</span>
              <span>{item.passesRun} / {item.passesSkipped}</span>
              <span>{item.imageCount}</span>
              <code>{item.reason}</code>
            </button>
          ))}
        </div>
        <BatchItemDetail item={selectedBatchItem} />
        <div className="batch-notification-preview">
          <MessageSquare size={16} aria-hidden="true" />
          <pre>{batchReport.notificationPreview}</pre>
        </div>
      </section>
      </WorkflowSectionGroup>

      <WorkflowSectionGroup
        id="draft"
        isOpen={openWorkflowSet.has("draft")}
        onExpand={() => toggleWorkflowSection("draft")}
      >
        <section className="logic-block review-ai-panel">
        <div className="editor-header">
          <div className="section-title">
            <Sparkles size={17} aria-hidden="true" />
            <h3>AI Review Draft</h3>
          </div>
          <button className="icon-button compact" onClick={regenerateDraft} type="button">
            <RefreshCw size={16} aria-hidden="true" />
            <span>Regenerate</span>
          </button>
        </div>
        <textarea
          aria-label="AI review draft"
          value={draftOverride ?? computedReport.aiReviewDraft}
          onChange={(event) => updateDraft(event.currentTarget.value)}
        />
        <div className="decision-actions">
          <button
            className="icon-button compact"
            onClick={markNeedsFix}
            type="button"
          >
            <CircleSlash size={16} aria-hidden="true" />
            <span>Needs Fix</span>
          </button>
          <button
            className="primary-button compact"
            onClick={acceptReview}
            type="button"
          >
            <Check size={16} aria-hidden="true" />
            <span>Accept Review</span>
          </button>
        </div>
        <div className="review-audit-list">
          {reviewAudit.length > 0 ? (
            reviewAudit.map((event) => (
              <div className="review-audit-row" key={`${event.revision}-${event.action}`}>
                <span>#{event.revision}</span>
                <strong>{event.action.replace("_", " ")}</strong>
                <em>{`${event.fromDecision} -> ${event.toDecision}`}</em>
                <p>{event.note}</p>
              </div>
            ))
          ) : (
            <p className="muted-note">Review decisions and AI draft edits will be recorded here.</p>
          )}
        </div>
      </section>

      <section className="logic-block review-package-panel">
        <div className="section-title">
          <Bell size={17} aria-hidden="true" />
          <h3>Evidence Package</h3>
        </div>
        <div className="package-grid">
          <div>
            <span>Output Dir</span>
            <code>{report.evidencePackage.outputDir}</code>
          </div>
          <div>
            <span>Scene Backup</span>
            <code>{report.evidencePackage.sceneBackup || "disabled"}</code>
          </div>
          <div>
            <span>HTML Overview</span>
            <code>{report.evidencePackage.htmlOverview}</code>
          </div>
        </div>
        <div className="notification-preview">
          <MessageSquare size={16} aria-hidden="true" />
          <pre>{report.notificationPreview}</pre>
        </div>
      </section>
      </WorkflowSectionGroup>
    </div>
  );
}

function WorkflowNavigator({
  activePreset,
  openSections,
  report,
  onApplyPreset,
  onJump,
  onToggle,
}: {
  activePreset: VisualWorkflowPresetId;
  openSections: Set<VisualWorkflowSectionId>;
  report: VisualReviewReport;
  onApplyPreset: (presetId: VisualWorkflowPresetId) => void;
  onJump: (sectionId: VisualWorkflowSectionId) => void;
  onToggle: (sectionId: VisualWorkflowSectionId) => void;
}) {
  const openCount = visualWorkflowSections.filter((section) => openSections.has(section.id)).length;

  return (
    <section className="logic-block wide workflow-map-panel">
      <div className="editor-header">
        <div className="section-title">
          <ListFilter size={17} aria-hidden="true" />
          <h3>Workflow Map</h3>
        </div>
        <div className="workflow-map-summary">
          <span>{openCount} / {visualWorkflowSections.length} sections open</span>
          <strong data-gate={report.releaseGate.gate}>{report.releaseGate.gate}</strong>
        </div>
      </div>

      <div className="workflow-preset-row" aria-label="workflow focus presets">
        {(["full", "review", "release"] as VisualWorkflowPresetId[]).map((presetId) => (
          <button
            aria-pressed={activePreset === presetId}
            className="toggle-pill"
            key={presetId}
            onClick={() => onApplyPreset(presetId)}
            type="button"
          >
            <GitBranch size={15} aria-hidden="true" />
            <span>{visualWorkflowPresetLabels[presetId]}</span>
          </button>
        ))}
      </div>

      <div className="workflow-map-grid">
        {visualWorkflowSections.map((section) => {
          const isOpen = openSections.has(section.id);
          const gate = getWorkflowSectionGate(section.id, report);
          return (
            <article className="workflow-map-row" data-gate={gate} data-open={isOpen} key={section.id}>
              <button className="workflow-jump-button" onClick={() => onJump(section.id)} type="button">
                <Eye size={15} aria-hidden="true" />
                <span>{section.label}</span>
              </button>
              <div>
                <strong>{gate}</strong>
                <p>{section.detail}</p>
              </div>
              <button
                aria-expanded={isOpen}
                className="icon-button compact"
                onClick={() => onToggle(section.id)}
                type="button"
              >
                {isOpen ? <Check size={15} aria-hidden="true" /> : <CircleSlash size={15} aria-hidden="true" />}
                <span>{isOpen ? "Hide" : "Show"}</span>
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function WorkflowSectionGroup({
  id,
  isOpen,
  onExpand,
  children,
}: {
  id: VisualWorkflowSectionId;
  isOpen: boolean;
  onExpand: () => void;
  children: ReactNode;
}) {
  const section = visualWorkflowSections.find((item) => item.id === id) ?? visualWorkflowSections[0];

  return (
    <div className="visual-section-group wide" data-open={isOpen} id={`visual-workflow-${id}`}>
      {isOpen ? (
        <div className="visual-section-inner">
          {children}
        </div>
      ) : (
        <section className="logic-block wide workflow-collapsed-panel">
          <div className="section-title">
            <ListChecks size={17} aria-hidden="true" />
            <h3>{section.label}</h3>
          </div>
          <p>{section.detail}</p>
          <button className="primary-button compact" onClick={onExpand} type="button">
            <Eye size={15} aria-hidden="true" />
            <span>Show Section</span>
          </button>
        </section>
      )}
    </div>
  );
}

function FixtureEditorPanel({
  sourceFixture,
  state,
  summary,
  report,
  onApplyPreset,
  onChange,
  onReset,
}: {
  sourceFixture: VisualReviewFixture;
  state: VisualFixtureEditorState;
  summary: VisualFixtureEditSummary;
  report: VisualReviewReport;
  onApplyPreset: (presetId: VisualFixtureEditorPresetId) => void;
  onChange: <K extends keyof VisualFixtureEditorState>(field: K, value: VisualFixtureEditorState[K]) => void;
  onReset: () => void;
}) {
  const signalById = new Map(report.diffSignals.map((signal) => [signal.id, signal]));
  const changedLabel = summary.changedFields.length > 0
    ? summary.changedFields.join(", ")
    : "source fixture";

  return (
    <section className="logic-block wide fixture-editor-panel">
      <div className="editor-header">
        <div className="section-title">
          <SlidersHorizontal size={17} aria-hidden="true" />
          <h3>Runtime Fixture Editor</h3>
        </div>
        <button className="icon-button compact" onClick={onReset} type="button">
          <RefreshCw size={16} aria-hidden="true" />
          <span>Reset Fixture</span>
        </button>
      </div>

      <div className="fixture-editor-grid">
        <div className="fixture-editor-card fixture-editor-presets">
          <span>Scenario Presets</span>
          <div>
            {visualFixtureEditorPresets.map((preset) => (
              <button
                aria-pressed={preset.id === "source" ? !summary.changed : undefined}
                className="fixture-preset-button"
                key={preset.id}
                onClick={() => onApplyPreset(preset.id)}
                type="button"
              >
                <strong>{preset.label}</strong>
                <small>{preset.description}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="fixture-editor-card signal-editor-card">
          <span>Signal Tuning</span>
          <MetricEditor
            gate={signalById.get("silhouette")?.gate ?? "Ready"}
            label="Silhouette Delta"
            max={20}
            min={0}
            step={0.1}
            unit="%"
            value={state.silhouetteDeltaPercent}
            onChange={(value) => onChange("silhouetteDeltaPercent", value)}
          />
          <MetricEditor
            gate={signalById.get("bbox")?.gate ?? "Ready"}
            label="Bounding Box Delta"
            max={12}
            min={0}
            step={0.1}
            unit="%"
            value={state.bboxDeltaPercent}
            onChange={(value) => onChange("bboxDeltaPercent", value)}
          />
          <MetricEditor
            gate={signalById.get("material")?.gate ?? "Ready"}
            label="Material Drift"
            max={0.6}
            min={0}
            step={0.01}
            unit="score"
            value={state.materialDriftScore}
            onChange={(value) => onChange("materialDriftScore", value)}
          />
          <MetricEditor
            gate={signalById.get("cameraCoverage")?.gate ?? "Ready"}
            label="Camera Coverage"
            max={100}
            min={50}
            step={1}
            unit="%"
            value={Math.round(state.cameraCoverageScore * 100)}
            onChange={(value) => onChange("cameraCoverageScore", value / 100)}
          />
        </div>

        <div className="fixture-editor-card asset-contract-card">
          <span>Asset Contract</span>
          <div className="fixture-contract-grid">
            <label className="field-control compact-field">
              <span>Variant Unit</span>
              <select
                aria-label="Variant Unit"
                value={state.variantUnit}
                onChange={(event) => onChange("variantUnit", event.currentTarget.value as VisualFixtureEditorState["variantUnit"])}
              >
                {(["cm", "m", "mm"] as VisualFixtureEditorState["variantUnit"][]).map((unit) => (
                  <option key={unit} value={unit}>{unit}</option>
                ))}
              </select>
            </label>
            <IntegerEditor
              label="Variant Material Count"
              max={24}
              min={1}
              value={state.variantMaterialCount}
              onChange={(value) => onChange("variantMaterialCount", value)}
            />
            <IntegerEditor
              label="Missing Textures"
              max={12}
              min={0}
              value={state.unresolvedTextureCount}
              onChange={(value) => onChange("unresolvedTextureCount", value)}
            />
            <IntegerEditor
              label="Variant DT Meshes"
              max={8}
              min={0}
              value={state.variantDtCount}
              onChange={(value) => onChange("variantDtCount", value)}
            />
          </div>
          <textarea
            aria-label="Reviewer Note"
            value={state.reviewerNote}
            onChange={(event) => onChange("reviewerNote", event.currentTarget.value)}
          />
        </div>

        <div className="fixture-editor-card fixture-impact-card" data-gate={report.releaseGate.gate}>
          <span>Runtime Impact</span>
          <div className="impact-summary-grid">
            <div>
              <small>Report Gate</small>
              <strong data-gate={report.gate}>{report.gate}</strong>
            </div>
            <div>
              <small>Queue</small>
              <strong>{report.reviewQueueSummary.blocked} / {report.reviewQueueSummary.todo} / {report.reviewQueueSummary.ready}</strong>
            </div>
            <div>
              <small>Release</small>
              <strong>{releaseDecisionLabels[report.releaseGate.decision]}</strong>
            </div>
            <div>
              <small>Passes</small>
              <strong>{report.passRuns.filter((run) => run.status === "run").length} run</strong>
            </div>
          </div>
          <div className="fixture-source-note">
            <code>{sourceFixture.variant.sourcePath}</code>
            <p>A unit {summary.before.variantUnit}, B unit {summary.after.variantUnit}; A materials {sourceFixture.baseline.materialCount}, B materials {summary.after.variantMaterialCount}.</p>
            <p>Edited fields: {changedLabel}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function MetricEditor({
  label,
  value,
  min,
  max,
  step,
  unit,
  gate,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: "%" | "score";
  gate: ReviewGate;
  onChange: (value: number) => void;
}) {
  const displayValue = unit === "%" ? `${value.toFixed(1)}%` : value.toFixed(2);

  return (
    <label className="metric-editor-row" data-gate={gate}>
      <span>
        <strong>{label}</strong>
        <em>{displayValue} · {gate}</em>
      </span>
      <input
        aria-label={`${label} slider`}
        max={max}
        min={min}
        step={step}
        type="range"
        value={value}
        onChange={(event) => onChange(Number(event.currentTarget.value))}
      />
      <input
        aria-label={label}
        max={max}
        min={min}
        step={step}
        type="number"
        value={value}
        onChange={(event) => onChange(Number(event.currentTarget.value))}
      />
    </label>
  );
}

function IntegerEditor({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="field-control compact-field">
      <span>{label}</span>
      <input
        aria-label={label}
        max={max}
        min={min}
        step={1}
        type="number"
        value={value}
        onChange={(event) => onChange(Number(event.currentTarget.value))}
      />
    </label>
  );
}

function getWorkflowSectionGate(sectionId: VisualWorkflowSectionId, report: VisualReviewReport): ReviewGate {
  const criterionGate = (criterionId: VisualReleaseCriterion["id"]) => (
    report.releaseGate.criteria.find((criterion) => criterion.id === criterionId)?.gate ?? "Ready"
  );

  switch (sectionId) {
    case "setup":
      return getStrongestWorkflowGate([
        report.fixtureEditSummary.changed ? "Review" : "Ready",
        criterionGate("capture_contract"),
      ]);
    case "capture":
      return getStrongestWorkflowGate([
        criterionGate("capture_contract"),
        criterionGate("signal_thresholds"),
      ]);
    case "triage":
      return criterionGate("queue_resolution");
    case "handoff":
      return getStrongestWorkflowGate([
        criterionGate("handoff_ack"),
        report.releaseGate.gate,
      ]);
    case "batch":
      return report.gate;
    case "draft":
      return getStrongestWorkflowGate([
        criterionGate("review_decision"),
        criterionGate("evidence_package"),
      ]);
  }
}

function getStrongestWorkflowGate(gates: ReviewGate[]): ReviewGate {
  if (gates.includes("Blocked")) {
    return "Blocked";
  }
  if (gates.includes("Review")) {
    return "Review";
  }
  return "Ready";
}

function PassDrilldownPanel({
  drilldown,
  selectedSignalId,
}: {
  drilldown: VisualPassDrilldown;
  selectedSignalId?: VisualSignalId;
}) {
  const visibleShots = drilldown.shots.slice(0, 6);

  return (
    <section className="logic-block wide pass-drilldown-panel">
      <div className="editor-header">
        <div className="section-title">
          <GitBranch size={17} aria-hidden="true" />
          <h3>Pass Drilldown</h3>
        </div>
        <strong className="drilldown-gate" data-gate={drilldown.gate}>{drilldown.gate}</strong>
      </div>

      <div className="pass-drilldown-summary">
        <div>
          <span>Selected Pass</span>
          <strong>{drilldown.label}</strong>
          <p>{drilldown.reason}</p>
        </div>
        <dl>
          <div>
            <dt>Status</dt>
            <dd>{passStatusLabels[drilldown.status]}</dd>
          </div>
          <div>
            <dt>Shots</dt>
            <dd>{drilldown.imageCount}</dd>
          </div>
          <div>
            <dt>Cameras</dt>
            <dd>{drilldown.cameraCount}</dd>
          </div>
          <div>
            <dt>Pattern</dt>
            <dd>{drilldown.outputPattern}</dd>
          </div>
        </dl>
      </div>

      <div className="drilldown-grid">
        <div className="drilldown-card">
          <span>Related Signals</span>
          <div className="drilldown-stack">
            {drilldown.relatedSignals.map((signal) => (
              <div
                className="drilldown-signal-row"
                data-gate={signal.gate}
                data-selected={signal.signalId === selectedSignalId ? "true" : undefined}
                key={signal.signalId}
              >
                <strong>{signal.label}</strong>
                <em>{formatMetric(signal.value, signal.unit)} · {signal.gate}</em>
                <p>{signal.evidence}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="drilldown-card">
          <span>Camera Shots</span>
          {visibleShots.length > 0 ? (
            <div className="drilldown-shot-list">
              {visibleShots.map((shot) => (
                <div className="drilldown-shot-row" key={shot.outputName}>
                  <span>{shot.cameraGroup}</span>
                  <strong>{shot.cameraName}</strong>
                  <code>{shot.outputName}</code>
                </div>
              ))}
              {drilldown.shots.length > visibleShots.length ? (
                <p className="muted-note">+{drilldown.shots.length - visibleShots.length} more shots in this pass.</p>
              ) : null}
            </div>
          ) : (
            <p className="muted-note">{drilldown.reason}</p>
          )}
        </div>

        <div className="drilldown-card">
          <span>Linked Findings</span>
          {drilldown.relatedFindings.length > 0 ? (
            <div className="drilldown-stack">
              {drilldown.relatedFindings.map((finding) => (
                <div className="drilldown-finding-row" data-severity={finding.severity} key={finding.findingId}>
                  <strong>{finding.title}</strong>
                  <em>{severityLabels[finding.severity]} · {finding.channel}</em>
                  <p>{finding.suggestedAction}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted-note">No linked finding. Keep this pass as clean evidence.</p>
          )}
        </div>

        <div className="drilldown-card action-contract-card">
          <span>Action Contract</span>
          <code>{drilldown.materialContract}</code>
          <p>{drilldown.nextAction}</p>
        </div>
      </div>
    </section>
  );
}

function ReviewQueuePanel({
  summary,
  items,
  selectedItem,
  ownerFilter,
  gateFilter,
  onOwnerFilterChange,
  onGateFilterChange,
  onSelectItem,
  onSelectPass,
  onUpdateState,
}: {
  summary: {
    total: number;
    todo: number;
    blocked: number;
    ready: number;
    artist: number;
    ta: number;
    reviewer: number;
  };
  items: ReviewQueueItem[];
  selectedItem?: ReviewQueueItem;
  ownerFilter: QueueOwnerFilter;
  gateFilter: QueueGateFilter;
  onOwnerFilterChange: (filter: QueueOwnerFilter) => void;
  onGateFilterChange: (filter: QueueGateFilter) => void;
  onSelectItem: (itemId: string) => void;
  onSelectPass: (passId: PassPresetId) => void;
  onUpdateState: (item: ReviewQueueItem, state: ReviewQueueState) => void;
}) {
  return (
    <section className="logic-block wide review-queue-panel">
      <div className="editor-header">
        <div className="section-title">
          <UserCheck size={17} aria-hidden="true" />
          <h3>Review Queue Drilldown</h3>
        </div>
        <div className="queue-filter-toolbar">
          <ListFilter size={16} aria-hidden="true" />
          <span>{items.length} shown / {summary.total} total</span>
        </div>
      </div>

      <div className="review-queue-summary" aria-label="review queue summary">
        <div>
          <span>Blocked</span>
          <strong data-state="blocked">{summary.blocked}</strong>
        </div>
        <div>
          <span>Todo</span>
          <strong data-state="todo">{summary.todo}</strong>
        </div>
        <div>
          <span>Ready</span>
          <strong data-state="ready">{summary.ready}</strong>
        </div>
        <div>
          <span>Owner Split</span>
          <strong>{summary.artist} A / {summary.ta} TA / {summary.reviewer} R</strong>
        </div>
      </div>

      <div className="queue-filter-grid">
        <div className="queue-filter-group" aria-label="owner filter">
          <span>Owner</span>
          <div>
            {queueOwnerOptions.map((option) => (
              <button
                aria-pressed={ownerFilter === option}
                className="toggle-pill"
                key={option}
                onClick={() => onOwnerFilterChange(option)}
                type="button"
              >
                <span>{option === "all" ? "All" : queueOwnerLabels[option]}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="queue-filter-group" aria-label="gate filter">
          <span>Gate</span>
          <div>
            {queueGateOptions.map((option) => (
              <button
                aria-pressed={gateFilter === option}
                className="toggle-pill"
                key={option}
                onClick={() => onGateFilterChange(option)}
                type="button"
              >
                <span>{option}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="queue-drilldown-grid">
        <div className="queue-table" role="table" aria-label="review action queue">
          <div role="row">
            <span>Owner</span>
            <span>State</span>
            <span>Gate</span>
            <span>Priority</span>
            <span>Action</span>
          </div>
          {items.length > 0 ? (
            items.map((item) => (
              <button
                aria-pressed={selectedItem?.id === item.id}
                className="queue-row"
                data-gate={item.gate}
                data-state={item.state}
                key={item.id}
                onClick={() => onSelectItem(item.id)}
                role="row"
                type="button"
              >
                <span>{queueOwnerLabels[item.owner]}</span>
                <span>{queueStateLabels[item.state]}</span>
                <span>{item.gate}</span>
                <strong>{item.priority}</strong>
                <code>{item.title}</code>
              </button>
            ))
          ) : (
            <div className="queue-empty-row">No queue items match the current filters.</div>
          )}
        </div>

        <div className="queue-detail-card">
          {selectedItem ? (
            <>
              <div className="queue-detail-head">
                <div>
                  <span>{queueOwnerLabels[selectedItem.owner]} · {selectedItem.channel}</span>
                  <strong>{selectedItem.sourceFindingTitle}</strong>
                </div>
                <b data-state={selectedItem.state}>{queueStateLabels[selectedItem.state]}</b>
              </div>
              <dl className="queue-detail-facts">
                <div>
                  <dt>Gate</dt>
                  <dd>{selectedItem.gate}</dd>
                </div>
                <div>
                  <dt>Severity</dt>
                  <dd>{severityLabels[selectedItem.severity]}</dd>
                </div>
                <div>
                  <dt>Priority</dt>
                  <dd>{selectedItem.priority}</dd>
                </div>
              </dl>
              <div className="queue-detail-section">
                <span>Evidence</span>
                <p>{selectedItem.evidence}</p>
              </div>
              <div className="queue-detail-section">
                <span>Next Check</span>
                <p>{selectedItem.nextCheck}</p>
              </div>
              <div className="queue-pass-links">
                <span>Related Passes</span>
                <div>
                  {selectedItem.relatedPasses.map((passId) => (
                    <button
                      className="icon-button compact"
                      key={passId}
                      onClick={() => onSelectPass(passId)}
                      type="button"
                    >
                      <GitBranch size={15} aria-hidden="true" />
                      <span>{passId}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="queue-handoff-note">
                <span>Handoff Note</span>
                <code>{selectedItem.handoffNote}</code>
              </div>
              <div className="queue-state-actions" aria-label="queue state actions">
                <button className="icon-button compact" onClick={() => onUpdateState(selectedItem, "todo")} type="button">
                  <RefreshCw size={15} aria-hidden="true" />
                  <span>Mark Todo</span>
                </button>
                <button className="icon-button compact" onClick={() => onUpdateState(selectedItem, "blocked")} type="button">
                  <CircleSlash size={15} aria-hidden="true" />
                  <span>Mark Blocked</span>
                </button>
                <button className="primary-button compact" onClick={() => onUpdateState(selectedItem, "ready")} type="button">
                  <Check size={15} aria-hidden="true" />
                  <span>Mark Ready</span>
                </button>
              </div>
            </>
          ) : (
            <p className="muted-note">Clean fixture. No review queue item is required.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function HandoffPacketPanel({
  packet,
  selectedSection,
  onSelectOwner,
  onUpdateDelivery,
  onExport,
}: {
  packet: ReviewHandoffPacket;
  selectedSection: ReviewHandoffSection;
  onSelectOwner: (owner: ReviewQueueOwner) => void;
  onUpdateDelivery: (owner: ReviewQueueOwner, state: HandoffDeliveryState) => void;
  onExport: () => void;
}) {
  return (
    <section className="logic-block wide handoff-packet-panel">
      <div className="editor-header">
        <div className="section-title">
          <Send size={17} aria-hidden="true" />
          <h3>Owner Handoff Packet</h3>
        </div>
        <button className="primary-button compact" onClick={onExport} type="button">
          <Download size={16} aria-hidden="true" />
          <span>Export Handoff</span>
        </button>
      </div>

      <div className="handoff-delivery-summary" aria-label="handoff delivery summary">
        <div>
          <span>Draft</span>
          <strong data-state="draft">{packet.deliverySummary.pending}</strong>
        </div>
        <div>
          <span>Sent</span>
          <strong data-state="sent">{packet.deliverySummary.sent}</strong>
        </div>
        <div>
          <span>Failed</span>
          <strong data-state="failed">{packet.deliverySummary.failed}</strong>
        </div>
        <div>
          <span>Ack</span>
          <strong data-state="acknowledged">{packet.deliverySummary.acknowledged}</strong>
        </div>
      </div>

      <div className="handoff-owner-grid" aria-label="handoff owners">
        {packet.sections.map((section) => (
          <button
            aria-pressed={section.owner === selectedSection.owner}
            className="handoff-owner-card"
            data-gate={section.gate}
            data-delivery={section.delivery.state}
            key={section.owner}
            onClick={() => onSelectOwner(section.owner)}
            type="button"
          >
            <span>{section.ownerLabel}</span>
            <strong>{section.total} item{section.total === 1 ? "" : "s"}</strong>
            <code>{section.blocked} blocked / {section.todo} todo / {section.ready} ready</code>
            <b>{deliveryStateLabels[section.delivery.state]} · {section.delivery.attempts} tries</b>
          </button>
        ))}
      </div>

      <div className="handoff-detail-grid">
        <div className="handoff-message-card">
          <span>{selectedSection.ownerLabel} Message Preview</span>
          <pre>{selectedSection.messagePreview}</pre>
        </div>

        <div className="handoff-evidence-card">
          <span>Shared Evidence</span>
          <code>{packet.evidencePackage.outputDir}</code>
          <code>{packet.evidencePackage.htmlOverview}</code>
          <code>{packet.evidencePackage.sceneBackup || "scene backup disabled"}</code>
          <p>{packet.evidencePackage.imageCount} captured images in this review package.</p>
        </div>

        <div className="handoff-delivery-card" data-state={selectedSection.delivery.state}>
          <span>{selectedSection.ownerLabel} Delivery Receipt</span>
          <dl>
            <div>
              <dt>State</dt>
              <dd>{deliveryStateLabels[selectedSection.delivery.state]}</dd>
            </div>
            <div>
              <dt>Channel</dt>
              <dd>{selectedSection.delivery.channel}</dd>
            </div>
            <div>
              <dt>Recipient</dt>
              <dd>{selectedSection.delivery.recipient}</dd>
            </div>
            <div>
              <dt>Attempts</dt>
              <dd>{selectedSection.delivery.attempts}</dd>
            </div>
          </dl>
          <p>{selectedSection.delivery.lastEvent}</p>
          <code>{selectedSection.delivery.nextAction}</code>
          <div className="handoff-delivery-actions" aria-label="handoff delivery actions">
            <button
              className="primary-button compact"
              disabled={selectedSection.total === 0}
              onClick={() => onUpdateDelivery(selectedSection.owner, "sent")}
              type="button"
            >
              <Send size={15} aria-hidden="true" />
              <span>Send Packet</span>
            </button>
            <button
              className="icon-button compact"
              disabled={selectedSection.total === 0}
              onClick={() => onUpdateDelivery(selectedSection.owner, "failed")}
              type="button"
            >
              <CircleSlash size={15} aria-hidden="true" />
              <span>Simulate Fail</span>
            </button>
            <button
              className="icon-button compact"
              disabled={selectedSection.total === 0}
              onClick={() => onUpdateDelivery(selectedSection.owner, "read")}
              type="button"
            >
              <Eye size={15} aria-hidden="true" />
              <span>Mark Read</span>
            </button>
            <button
              className="primary-button compact"
              disabled={selectedSection.total === 0}
              onClick={() => onUpdateDelivery(selectedSection.owner, "acknowledged")}
              type="button"
            >
              <Check size={15} aria-hidden="true" />
              <span>Acknowledge</span>
            </button>
          </div>
        </div>

        <div className="handoff-action-card">
          <span>{selectedSection.ownerLabel} Action List</span>
          {selectedSection.items.length > 0 ? (
            <div className="handoff-item-list">
              {selectedSection.items.map((item) => (
                <div className="handoff-item-row" data-state={item.state} key={item.queueId}>
                  <div>
                    <strong>P{item.priority} · {item.sourceFindingTitle}</strong>
                    <p>{item.nextCheck}</p>
                  </div>
                  <code>{item.relatedPasses.join(" / ") || "no pass"}</code>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted-note">No handoff item for this owner.</p>
          )}
        </div>

        <div className="handoff-packet-preview">
          <MessageSquare size={16} aria-hidden="true" />
          <pre>{packet.notificationPreview}</pre>
        </div>
      </div>
    </section>
  );
}

function ReleaseGatePanel({
  gate,
  onExport,
}: {
  gate: VisualReleaseGate;
  onExport: () => void;
}) {
  return (
    <section className="logic-block wide release-gate-panel">
      <div className="editor-header">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Final Release Gate</h3>
        </div>
        <button className="primary-button compact" onClick={onExport} type="button">
          <Download size={16} aria-hidden="true" />
          <span>Export Release</span>
        </button>
      </div>

      <div className="release-gate-summary" data-gate={gate.gate}>
        <div>
          <span>Decision</span>
          <strong>{releaseDecisionLabels[gate.decision]}</strong>
        </div>
        <div>
          <span>Gate</span>
          <strong>{gate.gate}</strong>
        </div>
        <div>
          <span>Criteria</span>
          <strong>{gate.ready} ready / {gate.review} review / {gate.blocked} blocked</strong>
        </div>
        <div>
          <span>Blockers</span>
          <strong>{gate.blockers.length}</strong>
        </div>
      </div>

      <div className="release-criteria-grid">
        {gate.criteria.map((criterion) => (
          <ReleaseCriterionCard criterion={criterion} key={criterion.id} />
        ))}
      </div>

      <div className="release-detail-grid">
        <div className="release-checklist-card">
          <span>Publish Checklist</span>
          <div>
            {gate.publishChecklist.map((item) => (
              <code key={item}>{item}</code>
            ))}
          </div>
        </div>
        <div className="release-note-card">
          <MessageSquare size={16} aria-hidden="true" />
          <pre>{gate.releaseNotePreview}</pre>
        </div>
      </div>
    </section>
  );
}

function ReleaseCriterionCard({ criterion }: { criterion: VisualReleaseCriterion }) {
  return (
    <article className="release-criterion-card" data-gate={criterion.gate}>
      <div>
        <span>{criterion.required ? "Required" : "Optional"}</span>
        <strong>{criterion.label}</strong>
      </div>
      <b>{criterion.gate}</b>
      <p>{criterion.summary}</p>
      <code>{criterion.evidence}</code>
      <small>{criterion.nextAction}</small>
    </article>
  );
}

function BatchItemDetail({ item }: { item: VisualBatchItem }) {
  return (
    <div className="batch-detail-panel" data-gate={item.reviewGate}>
      <div className="batch-detail-head">
        <div>
          <Target size={16} aria-hidden="true" />
          <strong>{item.name}</strong>
        </div>
        <span>{item.reviewGate}</span>
      </div>
      <div className="batch-detail-grid">
        <div>
          <span>Evidence</span>
          <code>{item.outputDir}</code>
          <code>{item.sceneBackup || "scene backup disabled"}</code>
          <code>{item.htmlOverview}</code>
        </div>
        <div>
          <span>Primary Signal</span>
          {item.primarySignal ? (
            <>
              <strong>{item.primarySignal.label}</strong>
              <p>{formatMetric(item.primarySignal.value, item.primarySignal.unit)} · {item.primarySignal.gate}</p>
            </>
          ) : (
            <p>No signal summary.</p>
          )}
          <p>Queue: {item.queueBlocked} blocked / {item.queueTodo} todo / {item.queueReady} ready</p>
          <p>Handoff: {item.handoffOwners.map((owner) => queueOwnerLabels[owner]).join(", ") || "none"}</p>
          <p>Delivery: {item.handoffDelivery.map((receipt) => `${queueOwnerLabels[receipt.owner]} ${deliveryStateLabels[receipt.state]}`).join(", ")}</p>
          <p>Release: {releaseDecisionLabels[item.releaseDecision]} · {item.releaseGate} · {item.releaseBlockers} blockers</p>
          <p>Fixture: {item.fixtureEditSummary.changed ? item.fixtureEditSummary.changedFields.join(", ") : "source fixture"}</p>
          {item.firstSkippedPass ? (
            <p>{item.firstSkippedPass.label}: {item.firstSkippedPass.reason}</p>
          ) : (
            <p>No skipped pass.</p>
          )}
        </div>
        <div>
          <span>Top Findings</span>
          <div className="batch-finding-list">
            {item.topFindings.map((finding) => (
              <p data-severity={finding.severity} key={finding.findingId}>
                {finding.gate} · {finding.title}
              </p>
            ))}
          </div>
        </div>
        <div className="batch-item-preview">
          <span>Report Preview</span>
          <pre>{item.reportPreview}</pre>
        </div>
        <div className="batch-item-preview">
          <span>Handoff Preview</span>
          <pre>{item.handoffPreview}</pre>
        </div>
        <div className="batch-item-preview">
          <span>Release Preview</span>
          <pre>{item.releasePreview}</pre>
        </div>
      </div>
    </div>
  );
}

function SignalCard({
  signal,
  isSelected,
  onSelect,
}: {
  signal: VisualDiffSignal;
  isSelected: boolean;
  onSelect: (signal: VisualDiffSignal) => void;
}) {
  const valueLabel = signal.unit === "%"
    ? `${signal.value.toFixed(1)}%`
    : signal.value.toFixed(2);
  const reviewLabel = signal.unit === "%"
    ? `${signal.reviewThreshold.toFixed(1)}%`
    : signal.reviewThreshold.toFixed(2);
  const blockLabel = signal.unit === "%"
    ? `${signal.blockThreshold.toFixed(1)}%`
    : signal.blockThreshold.toFixed(2);

  return (
    <button
      aria-pressed={isSelected}
      className="signal-card"
      data-gate={signal.gate}
      data-selected={isSelected ? "true" : undefined}
      onClick={() => onSelect(signal)}
      type="button"
    >
      <div className="signal-card-head">
        <div>
          <span>{signal.direction === "above" ? "Higher is risk" : "Lower is risk"}</span>
          <strong>{signal.label}</strong>
        </div>
        <b>{signal.gate}</b>
      </div>
      <div className="signal-meter" aria-label={`${signal.label} ${valueLabel}`}>
        <i style={{ width: `${signal.fillPercent}%` }} />
      </div>
      <dl>
        <div>
          <dt>Value</dt>
          <dd>{valueLabel}</dd>
        </div>
        <div>
          <dt>Review</dt>
          <dd>{reviewLabel}</dd>
        </div>
        <div>
          <dt>Block</dt>
          <dd>{blockLabel}</dd>
        </div>
      </dl>
      <p>{signal.evidence}</p>
      <code>{signal.relatedPasses.join(" / ")}</code>
    </button>
  );
}

function PassCard({
  run,
  isSelected,
  onSelect,
}: {
  run: VisualPassRun;
  isSelected: boolean;
  onSelect: (passId: PassPresetId) => void;
}) {
  const preset = visualPassPresets.find((item) => item.id === run.presetId) ?? visualPassPresets[0];

  return (
    <button
      aria-pressed={isSelected}
      className="pass-card"
      data-selected={isSelected ? "true" : undefined}
      data-status={run.status}
      onClick={() => onSelect(run.presetId)}
      type="button"
    >
      <div className="pass-card-header">
        <div>
          <span>{preset.shortLabel}</span>
          <strong>{run.label}</strong>
        </div>
        <b>{passStatusLabels[run.status]}</b>
      </div>
      <PassPreview presetId={run.presetId} />
      <p>{preset.intent}</p>
      <small>{run.reason}</small>
      <div className="pass-card-foot">
        <span>{run.imageCount} images</span>
        <span>{preset.materialContract}</span>
      </div>
    </button>
  );
}

function PassPreview({ presetId }: { presetId: string }) {
  return (
    <div className="pass-preview" data-preset={presetId} aria-hidden="true">
      <i />
      <i />
      <i />
    </div>
  );
}

function normalizeVisualDccRun(action: VisualDccAction, raw: unknown): VisualDccRun {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const manifest = asRecord(record?.manifest ?? report?.manifest);
  const capturePreview = asRecord(report?.capturePreview);
  const manifestSummary = asRecord(manifest?.summary);
  const meshSummary = asRecord(manifest?.mesh_summary);
  const captureSummary = asRecord(record?.summary ?? capturePreview?.summary);
  const cameras = asRecordArray(manifest?.cameras);
  const passes = normalizeVisualDccPasses(manifest?.passes);
  const captures = asRecordArray(record?.captures ?? capturePreview?.captures);
  const created = asRecordArray(record?.created);
  const path = readString(record?.path);
  const outputDir = readString(record?.output_dir) ?? readString(capturePreview?.outputDir);

  return {
    action: action.id,
    label: action.label,
    raw,
    cameraCount: cameras.length || created.length || readNumber(record?.count) || 0,
    meshCount: readNumber(meshSummary?.total) ?? 0,
    runCount: readNumber(manifestSummary?.run) ?? readNumber(captureSummary?.passes_run) ?? 0,
    skippedCount: readNumber(manifestSummary?.skipped) ?? readNumber(captureSummary?.passes_skipped) ?? 0,
    imageCount: readNumber(manifestSummary?.image_count) ?? captures.length,
    plannedCaptures: readNumber(captureSummary?.planned) ?? captures.length,
    gate: readString(manifestSummary?.gate) ?? readString(captureSummary?.gate) ?? (created.length ? "Ready" : "Preview"),
    outputDir: outputDir ?? undefined,
    path: path ?? undefined,
    passes,
    updatedAt: new Date().toLocaleTimeString(),
  };
}

function normalizeVisualDccPasses(value: unknown): VisualDccPassRow[] {
  return asRecordArray(value).map((item) => ({
    id: readString(item.id) ?? "<unknown>",
    label: readString(item.label) ?? "<unnamed pass>",
    status: readString(item.status) ?? "skipped",
    reason: readString(item.reason) ?? "-",
    cameraCount: readNumber(item.camera_count) ?? 0,
    imageCount: readNumber(item.image_count) ?? 0,
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

function formatMetric(value: number, unit: "%" | "score"): string {
  return unit === "%" ? `${value.toFixed(1)}%` : value.toFixed(2);
}

function getNextDeliveryAttempts(
  previousState: HandoffDeliveryState,
  nextState: HandoffDeliveryState,
  previousAttempts: number,
): number {
  if (nextState === "draft" || nextState === "not_required") {
    return 0;
  }
  if (nextState === "sent") {
    return previousState === "failed" ? previousAttempts + 1 : Math.max(previousAttempts, 1);
  }
  if (nextState === "failed") {
    return Math.max(previousAttempts, 1);
  }
  return Math.max(previousAttempts, 1);
}

function getDeliveryAuditAction(state: HandoffDeliveryState): VisualReviewAuditAction {
  if (state === "failed") {
    return "handoff_failed";
  }
  if (state === "read") {
    return "handoff_read";
  }
  if (state === "acknowledged") {
    return "handoff_acknowledged";
  }
  return "handoff_sent";
}
