import {
  assetFixtures,
  getProtocolReadiness,
  previewAutoFix,
  validateAssetProtocol,
  type AssetProtocolFixture,
} from "./assetProtocol";

export type DccId = "maya" | "blender" | "max" | "houdini";
export type RuleStatus = "pass" | "warning" | "error" | "skipped";
export type Fixability = "safe" | "manual" | "none";
export type RuleStage = "Collect" | "Validate" | "Fix" | "Extract";
export type FixActionState = "pending" | "approved" | "blocked" | "exported";
export type TraceState = "mapped" | "derived" | "missing";
export type FixPreviewMutationScope = "safe_auto" | "manual_only" | "adapter_gap";
export type ManualDispositionState = "owner_required" | "owner_accepted" | "blocked" | "documented";

export type AdapterCapabilityKey =
  | "protocolCarrier"
  | "collision"
  | "lod"
  | "materialTexture"
  | "exportRoot"
  | "manifest";

export type AdapterCapabilityMap = Record<AdapterCapabilityKey, boolean>;
export type AdapterCapabilityState = Record<DccId, AdapterCapabilityMap>;
export type FixActionStateMap = Record<string, FixActionState>;

export interface DccAdapter {
  id: DccId;
  name: string;
  methodSource: string;
  protocolCarrier: string;
  collectShape: string[];
  fixBoundary: string;
  extractTarget: string;
}

export interface RuleDefinition {
  id: string;
  name: string;
  stage: RuleStage;
  severity: "blocker" | "major" | "minor";
  fixability: Fixability;
  capability: AdapterCapabilityKey;
  businessReason: string;
  dsl: string[];
}

export interface RuleEvaluation {
  adapterId: DccId;
  ruleId: string;
  status: RuleStatus;
  message: string;
  evidence: string;
  fixPreview: string;
}

export interface MatrixSummary {
  adapterId: DccId;
  score: number;
  pass: number;
  warning: number;
  error: number;
  skipped: number;
  gate: "Ready" | "Review" | "Blocked";
}

export interface RuleFixQueueItem {
  id: string;
  adapterId: DccId;
  ruleId: string;
  label: string;
  kind: "safe" | "manual" | "capability";
  status: RuleStatus;
  before: string;
  after: string;
  owner: "Tool" | "TA" | "Adapter";
  actionState: FixActionState;
  reason: string;
}

export interface AdapterTraceRow {
  id: string;
  stage: RuleStage;
  capability: AdapterCapabilityKey;
  sourceField: string;
  normalizedField: string;
  value: string;
  state: TraceState;
  note: string;
}

export interface RuleAuthoringDraft {
  prompt: string;
  name: string;
  stage: RuleStage;
  severity: RuleDefinition["severity"];
  fixability: Fixability;
  capability: AdapterCapabilityKey;
  dsl: string[];
  reviewState: "draft" | "accepted";
  warnings: string[];
}

export interface RuleAuthoringAuditEvent {
  id: string;
  revision: number;
  action: "accepted" | "reopened";
  before: string;
  after: string;
  reviewer: "TA";
  note: string;
}

export interface AdapterTraceDiffRow {
  id: string;
  sourceField: string;
  sourceValue: string;
  normalizedField: string;
  normalizedValue: string;
  transform: "copy" | "derive" | "unavailable";
  state: TraceState;
}

export interface PublishGateReport {
  reportVersion: string;
  assetId: string;
  adapterId: DccId;
  finalGate: "Ready" | "Review" | "Blocked";
  assetProtocol: {
    readiness: ReturnType<typeof getProtocolReadiness>;
    validationCount: number;
    fixPreviewCount: number;
  };
  ruleMatrix: {
    summary: MatrixSummary;
    fixQueueCount: number;
    fixPreviewDiffCount: number;
    manualDispositionCount: number;
    ownerDispositionPending: number;
    acceptedDraft: boolean;
    mappedTraceCount: number;
    missingTraceCount: number;
  };
  blockers: string[];
  decisionTrail: string[];
  nextActions: string[];
}

export interface FixPreviewPayloadDiffRow {
  id: string;
  ruleId: string;
  label: string;
  kind: RuleFixQueueItem["kind"];
  owner: RuleFixQueueItem["owner"];
  actionState: FixActionState;
  fieldPath: string;
  beforePayload: string;
  afterPayload: string;
  mutationScope: FixPreviewMutationScope;
  gate: MatrixSummary["gate"];
  reviewerNote: string;
}

export interface FixPreviewPayloadDiffReport {
  reportVersion: "fix-preview-payload-diff@0.1.0";
  adapterId: DccId;
  assetId: string;
  summary: {
    total: number;
    safeAuto: number;
    manualOnly: number;
    adapterGaps: number;
    ready: number;
    review: number;
    blocked: number;
    nextAction: string;
  };
  rows: FixPreviewPayloadDiffRow[];
}

export interface ManualDispositionItem {
  id: string;
  ruleId: string;
  label: string;
  owner: RuleFixQueueItem["owner"];
  disposition: "manual_only" | "adapter_required";
  state: ManualDispositionState;
  reasonCode: string;
  requiredEvidence: string;
  ownerQuestion: string;
  policy: string;
}

export interface ManualDispositionReceipt {
  receiptId: string;
  reportVersion: "manual-disposition-receipt@0.1.0";
  adapterId: DccId;
  assetId: string;
  summary: {
    total: number;
    manualOnly: number;
    adapterRequired: number;
    ownerRequired: number;
    blocked: number;
    documented: number;
    nextAction: string;
  };
  items: ManualDispositionItem[];
}

export interface RuleMatrixReport {
  reportVersion: string;
  generatedBy: string;
  adapter: Pick<DccAdapter, "id" | "name" | "protocolCarrier">;
  assetContext: {
    sourceModule: string;
    fixture: string;
    platform: AssetProtocolFixture["platform"];
    category: AssetProtocolFixture["category"];
    schemaVersion: string;
  };
  summary: MatrixSummary;
  capabilityState: AdapterCapabilityMap;
  evaluations: RuleEvaluation[];
  fixQueue: RuleFixQueueItem[];
  adapterTrace: AdapterTraceRow[];
  traceDiff: AdapterTraceDiffRow[];
  fixPreviewDiff: FixPreviewPayloadDiffReport;
  manualDispositionReceipt: ManualDispositionReceipt;
  authoringDraft: RuleAuthoringDraft;
  authoringAudit: RuleAuthoringAuditEvent[];
  publishGate: PublishGateReport;
  aiBrief: {
    headline: string;
    priorities: string[];
    boundary: string;
  };
}

export const dccAdapters: DccAdapter[] = [
  {
    id: "maya",
    name: "Maya",
    methodSource: "maya_publish_rule_reference / maya_asset_tool_reference",
    protocolCarrier: "DAG node custom attrs + shadingEngine + export root",
    collectShape: ["transform dag path", "custom attrs", "shading connections", "mesh shape stats"],
    fixBoundary: "Can author deterministic attrs; geometry and material edits stay staged.",
    extractTarget: "sidecar publish manifest + Maya scene note",
  },
  {
    id: "blender",
    name: "Blender",
    methodSource: "blender_rule_adapter_reference",
    protocolCarrier: "object custom properties + collections + material slots",
    collectShape: ["object path", "custom properties", "collection membership", "mesh data counts"],
    fixBoundary: "Can normalize custom props; collection and modifier edits require review.",
    extractTarget: "asset browser metadata + JSON report",
  },
  {
    id: "max",
    name: "3ds Max",
    methodSource: "max_rule_adapter_reference",
    protocolCarrier: "node user props + layer metadata + modifier stack",
    collectShape: ["node handle", "user props", "layer path", "modifier stack summary"],
    fixBoundary: "Can write user props; stack and collision generation stay manual.",
    extractTarget: "publish manifest + layer validation report",
  },
  {
    id: "houdini",
    name: "Houdini",
    methodSource: "houdini_rule_adapter_reference",
    protocolCarrier: "geometry attributes + primitive groups + SOP node parms",
    collectShape: ["SOP path", "detail attrs", "primitive groups", "work item metadata"],
    fixBoundary: "Can set detail attrs; SOP topology changes must be queued.",
    extractTarget: "PDG work item payload + validation JSON",
  },
];

export const adapterCapabilityLabels: Record<AdapterCapabilityKey, string> = {
  protocolCarrier: "Protocol Carrier",
  collision: "Collision",
  lod: "LOD",
  materialTexture: "Material / Texture",
  exportRoot: "Export Root",
  manifest: "Manifest",
};

export const defaultAdapterCapabilities: AdapterCapabilityState = {
  maya: {
    protocolCarrier: true,
    collision: true,
    lod: true,
    materialTexture: true,
    exportRoot: true,
    manifest: true,
  },
  blender: {
    protocolCarrier: true,
    collision: true,
    lod: true,
    materialTexture: true,
    exportRoot: false,
    manifest: true,
  },
  max: {
    protocolCarrier: true,
    collision: true,
    lod: true,
    materialTexture: false,
    exportRoot: true,
    manifest: true,
  },
  houdini: {
    protocolCarrier: true,
    collision: true,
    lod: true,
    materialTexture: true,
    exportRoot: true,
    manifest: true,
  },
};

export const ruleDefinitions: RuleDefinition[] = [
  {
    id: "protocol-carrier",
    name: "Protocol Carrier",
    stage: "Collect",
    severity: "blocker",
    fixability: "safe",
    capability: "protocolCarrier",
    businessReason: "协议字段必须落在下游能稳定保留的 carrier，否则规则检查和导出报告无法复盘。",
    dsl: [
      "collect asset.protocol.carrier",
      "require schemaVersion matches lb_asset_protocol",
      "normalize carrier path per adapter",
    ],
  },
  {
    id: "collision-contract",
    name: "Collision Contract",
    stage: "Validate",
    severity: "blocker",
    fixability: "manual",
    capability: "collision",
    businessReason: "collision 不是普通开关，它决定资产能否进入交互、物理和性能预算链路。",
    dsl: ["require collision in [simple, complex, proxy]", "block if missing", "manual evidence for generated collision"],
  },
  {
    id: "lod-budget",
    name: "LOD Budget",
    stage: "Validate",
    severity: "major",
    fixability: "manual",
    capability: "lod",
    businessReason: "LOD、screen size、cull distance 要同时看；只检查层级数量会漏掉平台预算风险。",
    dsl: ["require lodCount >= platform.minLod", "compare screenSize curve", "warn when cull distance exceeds budget"],
  },
  {
    id: "material-texture-sync",
    name: "Material / Texture Sync",
    stage: "Validate",
    severity: "major",
    fixability: "manual",
    capability: "materialTexture",
    businessReason: "材质槽和贴图集漂移会把渲染问题延迟到引擎或发布后才暴露。",
    dsl: ["collect materialSlots", "collect textureSets", "warn when abs(materialSlots - textureSets) > 1"],
  },
  {
    id: "export-root-clean",
    name: "Export Root Clean",
    stage: "Fix",
    severity: "major",
    fixability: "safe",
    capability: "exportRoot",
    businessReason: "namespace、root、临时节点会污染导出，必须在进入 Extract 前收敛成确定结构。",
    dsl: ["require single export root", "strip temp namespace", "safe fix: tag export root"],
  },
  {
    id: "publish-manifest",
    name: "Publish Manifest",
    stage: "Extract",
    severity: "minor",
    fixability: "safe",
    capability: "manifest",
    businessReason: "检查结果要被产出为稳定 manifest，后续平台才能统计、追责和复用。",
    dsl: ["extract rule results", "include adapter payload", "include fix preview and audit trail"],
  },
];

export const ruleRunStages = [
  {
    stage: "Collect",
    detail: "adapter 把 DCC 私有结构归一化成 rule input。",
  },
  {
    stage: "Validate",
    detail: "共享 rule DSL 只读归一化数据并产出 status/evidence。",
  },
  {
    stage: "Fix Preview",
    detail: "safe fix 只改确定字段，manual action 只给证据和队列建议。",
  },
  {
    stage: "Extract",
    detail: "把 rule result、adapter payload、fix preview 打包成 report。",
  },
] as const;

export const defaultRuleDraftPrompt =
  "mobile prop publish: collision must exist, Nanite is not allowed, at least two LODs, texture sets cannot exceed mobile budget.";

export function cloneDefaultCapabilities(): AdapterCapabilityState {
  return {
    maya: { ...defaultAdapterCapabilities.maya },
    blender: { ...defaultAdapterCapabilities.blender },
    max: { ...defaultAdapterCapabilities.max },
    houdini: { ...defaultAdapterCapabilities.houdini },
  };
}

export function buildRuleEvaluations(
  asset: AssetProtocolFixture,
  capabilityState: AdapterCapabilityState,
): RuleEvaluation[] {
  return dccAdapters.flatMap((adapter) =>
    ruleDefinitions.map((rule) =>
      evaluateRuleForAdapter(adapter.id, rule, asset, capabilityState[adapter.id]),
    ),
  );
}

export function getEvaluation(adapterId: DccId, ruleId: string, evaluations: RuleEvaluation[]) {
  return evaluations.find((item) => item.adapterId === adapterId && item.ruleId === ruleId);
}

export function getAdapterSummary(adapterId: DccId, evaluations: RuleEvaluation[]): MatrixSummary {
  const adapterEvaluations = evaluations.filter((item) => item.adapterId === adapterId);
  const pass = adapterEvaluations.filter((item) => item.status === "pass").length;
  const warning = adapterEvaluations.filter((item) => item.status === "warning").length;
  const error = adapterEvaluations.filter((item) => item.status === "error").length;
  const skipped = adapterEvaluations.filter((item) => item.status === "skipped").length;
  const score = Math.max(0, 100 - error * 32 - warning * 12 - skipped * 8);
  const gate = error > 0 ? "Blocked" : warning + skipped > 0 ? "Review" : "Ready";

  return {
    adapterId,
    score,
    pass,
    warning,
    error,
    skipped,
    gate,
  };
}

export function getRuleFixQueue(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  evaluations: RuleEvaluation[],
  actionStates: FixActionStateMap = {},
): RuleFixQueueItem[] {
  return evaluations
    .filter((evaluation) => evaluation.adapterId === adapterId && evaluation.status !== "pass")
    .map((evaluation) => {
      const rule = ruleDefinitions.find((item) => item.id === evaluation.ruleId) ?? ruleDefinitions[0];
      const capabilityGap = evaluation.status === "skipped";
      const kind = capabilityGap ? "capability" : rule.fixability === "safe" ? "safe" : "manual";
      const id = `${adapterId}-${asset.id}-${rule.id}`;

      return {
        id,
        adapterId,
        ruleId: rule.id,
        label: rule.name,
        kind,
        status: evaluation.status,
        ...getFixDiff(rule.id, asset, capabilityGap),
        owner: kind === "safe" ? "Tool" : kind === "capability" ? "Adapter" : "TA",
        actionState: actionStates[id] ?? "pending",
        reason: evaluation.fixPreview,
      };
    });
}

export function buildRuleMatrixReport(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  capabilityState: AdapterCapabilityState,
  evaluations: RuleEvaluation[],
  options: {
    actionStates?: FixActionStateMap;
    authoringDraft?: RuleAuthoringDraft;
    authoringAudit?: RuleAuthoringAuditEvent[];
  } = {},
): RuleMatrixReport {
  const adapter = dccAdapters.find((item) => item.id === adapterId) ?? dccAdapters[0];
  const summary = getAdapterSummary(adapter.id, evaluations);
  const adapterEvaluations = evaluations.filter((item) => item.adapterId === adapter.id);
  const failed = adapterEvaluations.filter((item) => item.status === "error");
  const review = adapterEvaluations.filter((item) => item.status === "warning" || item.status === "skipped");
  const fixQueue = getRuleFixQueue(adapter.id, asset, evaluations, options.actionStates);
  const adapterTrace = buildAdapterTrace(adapter.id, asset, capabilityState);
  const traceDiff = buildAdapterTraceDiff(adapterTrace);
  const fixPreviewDiff = buildFixPreviewPayloadDiff(adapter.id, asset, fixQueue);
  const manualDispositionReceipt = buildManualDispositionReceipt(adapter.id, asset, fixQueue);
  const authoringDraft =
    options.authoringDraft ?? draftRuleFromPrompt(defaultRuleDraftPrompt, asset, adapter.id, "draft");
  const authoringAudit = options.authoringAudit ?? [];
  const publishGate = buildPublishGateReport(
    asset,
    adapter.id,
    summary,
    fixQueue,
    adapterTrace,
    authoringDraft,
    fixPreviewDiff,
    manualDispositionReceipt,
  );

  return {
    reportVersion: "cross-dcc-rule-report@0.4.0",
    generatedBy: "AI Tool TA Portfolio / Cross-DCC Rule Matrix",
    adapter: {
      id: adapter.id,
      name: adapter.name,
      protocolCarrier: adapter.protocolCarrier,
    },
    assetContext: {
      sourceModule: "Asset Protocol Workbench",
      fixture: asset.id,
      platform: asset.platform,
      category: asset.category,
      schemaVersion: asset.schemaVersion,
    },
    summary,
    capabilityState: capabilityState[adapter.id],
    evaluations: adapterEvaluations,
    fixQueue,
    adapterTrace,
    traceDiff,
    fixPreviewDiff,
    manualDispositionReceipt,
    authoringDraft,
    authoringAudit,
    publishGate,
    aiBrief: {
      headline:
        summary.gate === "Blocked"
          ? `${adapter.name} publish is blocked by ${failed.length} rule.`
          : summary.gate === "Review"
            ? `${adapter.name} needs TA review before publish.`
            : `${adapter.name} is ready for extract.`,
      priorities: [
        failed[0]?.message ?? review[0]?.message ?? "No blocking rule.",
        fixQueue[0]?.reason ?? "Adapter payload can be extracted.",
        "AI explains the rule result; it does not override rule gates.",
      ],
      boundary: "All evaluations are deterministic synthetic fixtures; DCC mutation is represented as staged fix preview.",
    },
  };
}

export function draftRuleFromPrompt(
  prompt: string,
  asset: AssetProtocolFixture,
  adapterId: DccId,
  reviewState: RuleAuthoringDraft["reviewState"],
): RuleAuthoringDraft {
  const normalized = prompt.toLowerCase();
  const mentionsCollision = normalized.includes("collision") || prompt.includes("碰撞");
  const mentionsLod = normalized.includes("lod") || prompt.includes("层级");
  const mentionsTexture = normalized.includes("texture") || prompt.includes("贴图");
  const mentionsNanite = normalized.includes("nanite");
  const capability: AdapterCapabilityKey = mentionsTexture
    ? "materialTexture"
    : mentionsLod
      ? "lod"
      : mentionsCollision
        ? "collision"
        : "protocolCarrier";
  const stage: RuleStage = mentionsCollision || mentionsLod || mentionsTexture || mentionsNanite ? "Validate" : "Collect";
  const severity: RuleDefinition["severity"] = mentionsCollision || mentionsNanite ? "blocker" : "major";

  return {
    prompt,
    name: buildDraftRuleName({ mentionsCollision, mentionsLod, mentionsTexture, mentionsNanite }),
    stage,
    severity,
    fixability: mentionsCollision || mentionsLod || mentionsTexture ? "manual" : "safe",
    capability,
    dsl: [
      `context asset=${asset.id}`,
      `adapter ${adapterId} collect capability.${capability}`,
      mentionsNanite ? "require not(platform == Mobile and nanite == true)" : `require ${capability} collector available`,
      mentionsCollision ? "require collision in [simple, complex, proxy]" : "record collision evidence when present",
      mentionsLod ? `require lodCount >= ${asset.platform === "Mobile" ? 2 : 3}` : "record lod budget input",
      mentionsTexture ? "warn when mobile textureSets > 3 or material/texture drift > 1" : "record material texture input",
    ],
    reviewState,
    warnings: [
      "Draft is not active in the validation matrix until a TA accepts it.",
      "Generated DSL must map to an adapter capability before implementation.",
      "AI can draft rule shape, but deterministic evaluators own final pass/fail.",
    ],
  };
}

export function buildAdapterTrace(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  capabilityState: AdapterCapabilityState,
): AdapterTraceRow[] {
  const capabilities = capabilityState[adapterId];
  const adapter = dccAdapters.find((item) => item.id === adapterId) ?? dccAdapters[0];

  return [
    {
      id: `${adapterId}-carrier`,
      stage: "Collect",
      capability: "protocolCarrier",
      sourceField: adapter.protocolCarrier,
      normalizedField: "asset.protocol.carrier",
      value: asset.semanticCarrier,
      state: capabilities.protocolCarrier ? "mapped" : "missing",
      note: capabilities.protocolCarrier ? "Protocol carrier can be normalized for shared rules." : "Rule input loses carrier evidence.",
    },
    {
      id: `${adapterId}-collision`,
      stage: "Validate",
      capability: "collision",
      sourceField: adapterSource(adapterId, "collision"),
      normalizedField: "asset.delivery.collision",
      value: asset.collision,
      state: capabilities.collision ? "mapped" : "missing",
      note: capabilities.collision ? "Collision contract can be evaluated." : "Collision rule must be skipped.",
    },
    {
      id: `${adapterId}-lod`,
      stage: "Validate",
      capability: "lod",
      sourceField: adapterSource(adapterId, "lod"),
      normalizedField: "asset.delivery.lodCount",
      value: String(asset.lodCount),
      state: capabilities.lod ? "mapped" : "missing",
      note: capabilities.lod ? "LOD budget joins platform and distance facts." : "LOD budget cannot be trusted.",
    },
    {
      id: `${adapterId}-material-texture`,
      stage: "Validate",
      capability: "materialTexture",
      sourceField: adapterSource(adapterId, "materialTexture"),
      normalizedField: "asset.render.materialTextureBudget",
      value: `${asset.materialSlots} material / ${asset.textureSets} texture`,
      state: capabilities.materialTexture ? "mapped" : "missing",
      note: capabilities.materialTexture ? "Material and texture drift can be scored." : "Adapter must expose material and texture facts.",
    },
    {
      id: `${adapterId}-export-root`,
      stage: "Fix",
      capability: "exportRoot",
      sourceField: adapterSource(adapterId, "exportRoot"),
      normalizedField: "asset.export.root",
      value: capabilities.exportRoot ? `${asset.id}_export_root` : "<unavailable>",
      state: capabilities.exportRoot ? "derived" : "missing",
      note: capabilities.exportRoot ? "Export root is derived from DCC hierarchy." : "Fix preview cannot tag export root.",
    },
    {
      id: `${adapterId}-manifest`,
      stage: "Extract",
      capability: "manifest",
      sourceField: "validation result + adapter payload",
      normalizedField: "publish.manifest",
      value: capabilities.manifest ? "serializable" : "<unavailable>",
      state: capabilities.manifest ? "derived" : "missing",
      note: capabilities.manifest ? "Report contains evaluations, trace, draft and fix state." : "Extract step cannot produce evidence.",
    },
  ];
}

export function buildAdapterTraceDiff(trace: AdapterTraceRow[]): AdapterTraceDiffRow[] {
  return trace.map((row) => ({
    id: `${row.id}-diff`,
    sourceField: row.sourceField,
    sourceValue: row.value,
    normalizedField: row.normalizedField,
    normalizedValue: row.state === "missing" ? "<missing>" : row.value,
    transform: row.state === "missing" ? "unavailable" : row.state === "derived" ? "derive" : "copy",
    state: row.state,
  }));
}

export function buildFixPreviewPayloadDiff(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  fixQueue: RuleFixQueueItem[],
): FixPreviewPayloadDiffReport {
  const rows = fixQueue.map<FixPreviewPayloadDiffRow>((item) => ({
    id: `${item.id}-payload-diff`,
    ruleId: item.ruleId,
    label: item.label,
    kind: item.kind,
    owner: item.owner,
    actionState: item.actionState,
    fieldPath: getFixPayloadPath(item.ruleId),
    beforePayload: formatFixPayload(item.before, asset, "before"),
    afterPayload: formatFixPayload(item.after, asset, "after"),
    mutationScope: getFixMutationScope(item.kind),
    gate: getFixPreviewDiffGate(item),
    reviewerNote: getFixPreviewReviewerNote(item),
  }));
  const blocked = rows.filter((row) => row.gate === "Blocked").length;
  const review = rows.filter((row) => row.gate === "Review").length;

  return {
    reportVersion: "fix-preview-payload-diff@0.1.0",
    adapterId,
    assetId: asset.id,
    summary: {
      total: rows.length,
      safeAuto: rows.filter((row) => row.mutationScope === "safe_auto").length,
      manualOnly: rows.filter((row) => row.mutationScope === "manual_only").length,
      adapterGaps: rows.filter((row) => row.mutationScope === "adapter_gap").length,
      ready: rows.filter((row) => row.gate === "Ready").length,
      review,
      blocked,
      nextAction:
        blocked > 0
          ? "Resolve blocked manual dispositions before owner signoff."
          : review > 0
            ? "Ask the owner to accept or document every non-safe payload diff."
            : "Attach payload diff to the R2 receipt and request final owner signoff.",
    },
    rows,
  };
}

export function buildManualDispositionReceipt(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  fixQueue: RuleFixQueueItem[],
): ManualDispositionReceipt {
  const items = fixQueue
    .filter((item) => item.kind !== "safe")
    .map<ManualDispositionItem>((item) => ({
      id: `${item.id}-manual-disposition`,
      ruleId: item.ruleId,
      label: item.label,
      owner: item.owner,
      disposition: item.kind === "capability" ? "adapter_required" : "manual_only",
      state: getManualDispositionState(item.actionState),
      reasonCode: getManualDispositionReasonCode(item),
      requiredEvidence: getManualDispositionEvidence(item, asset),
      ownerQuestion: getManualDispositionQuestion(item),
      policy:
        item.kind === "capability"
          ? "Do not run this rule as trusted validation until the adapter collector exists."
          : "Do not auto-fix this failure; attach owner evidence and keep the asset in review.",
    }));
  const ownerRequired = items.filter((item) => item.state === "owner_required").length;
  const blocked = items.filter((item) => item.state === "blocked").length;
  const documented = items.filter((item) => item.state === "documented" || item.state === "owner_accepted").length;

  return {
    receiptId: `manual-disposition-${adapterId}-${asset.id}`,
    reportVersion: "manual-disposition-receipt@0.1.0",
    adapterId,
    assetId: asset.id,
    summary: {
      total: items.length,
      manualOnly: items.filter((item) => item.disposition === "manual_only").length,
      adapterRequired: items.filter((item) => item.disposition === "adapter_required").length,
      ownerRequired,
      blocked,
      documented,
      nextAction:
        blocked > 0
          ? "Blocked manual dispositions must be resolved before R2 owner acceptance."
          : ownerRequired > 0
            ? "Collect owner disposition for every manual-only failure."
            : "Manual-only policy is documented; attach this receipt to accept-rules-r2.",
    },
    items,
  };
}

export function createAuthoringAuditEvent(
  revision: number,
  action: RuleAuthoringAuditEvent["action"],
  before: RuleAuthoringDraft["reviewState"],
  after: RuleAuthoringDraft["reviewState"],
  draft: RuleAuthoringDraft,
): RuleAuthoringAuditEvent {
  return {
    id: `rule-draft-${revision}-${action}`,
    revision,
    action,
    before,
    after,
    reviewer: "TA",
    note:
      action === "accepted"
        ? `${draft.name} accepted for report evidence; validation matrix remains deterministic.`
        : `${draft.name} reopened for manual review before implementation.`,
  };
}

export function buildPublishGateReport(
  asset: AssetProtocolFixture,
  adapterId: DccId,
  ruleSummary: MatrixSummary,
  fixQueue: RuleFixQueueItem[],
  adapterTrace: AdapterTraceRow[],
  authoringDraft: RuleAuthoringDraft,
  fixPreviewDiff: FixPreviewPayloadDiffReport,
  manualDispositionReceipt: ManualDispositionReceipt,
): PublishGateReport {
  const assetValidation = validateAssetProtocol(asset);
  const assetReadiness = getProtocolReadiness(assetValidation);
  const assetFixPreview = previewAutoFix(asset).actions;
  const mappedTraceCount = adapterTrace.filter((row) => row.state !== "missing").length;
  const missingTraceCount = adapterTrace.filter((row) => row.state === "missing").length;
  const blockers = [
    ...assetValidation
      .filter((result) => result.severity === "error")
      .map((result) => `Asset Protocol: ${result.label}`),
    ...fixQueue
      .filter((item) => item.status === "error" || item.actionState === "blocked")
      .map((item) => `Rule Matrix: ${item.label}`),
    ...(authoringDraft.reviewState === "accepted" ? [] : ["Rule Draft: TA acceptance missing"]),
    ...(missingTraceCount > 0 ? [`Adapter Trace: ${missingTraceCount} missing mapping`] : []),
    ...(manualDispositionReceipt.summary.ownerRequired > 0
      ? [`Manual Disposition: ${manualDispositionReceipt.summary.ownerRequired} owner decision pending`]
      : []),
    ...(manualDispositionReceipt.summary.blocked > 0
      ? [`Manual Disposition: ${manualDispositionReceipt.summary.blocked} blocked disposition`]
      : []),
  ];
  const finalGate = blockers.length > 0 ? "Blocked" : ruleSummary.gate === "Review" || assetReadiness.status === "Review" ? "Review" : "Ready";

  return {
    reportVersion: "publish-gate-report@0.1.0",
    assetId: asset.id,
    adapterId,
    finalGate,
    assetProtocol: {
      readiness: assetReadiness,
      validationCount: assetValidation.length,
      fixPreviewCount: assetFixPreview.length,
    },
    ruleMatrix: {
      summary: ruleSummary,
      fixQueueCount: fixQueue.length,
      fixPreviewDiffCount: fixPreviewDiff.summary.total,
      manualDispositionCount: manualDispositionReceipt.summary.total,
      ownerDispositionPending: manualDispositionReceipt.summary.ownerRequired,
      acceptedDraft: authoringDraft.reviewState === "accepted",
      mappedTraceCount,
      missingTraceCount,
    },
    blockers,
    decisionTrail: [
      `Asset Protocol gate: ${assetReadiness.status}.`,
      `Rule Matrix gate: ${ruleSummary.gate}.`,
      `Rule draft: ${authoringDraft.reviewState}.`,
      `Adapter trace: ${mappedTraceCount}/${adapterTrace.length} mappings available.`,
      `Fix preview diff: ${fixPreviewDiff.summary.total} rows, ${fixPreviewDiff.summary.safeAuto} safe-auto, ${fixPreviewDiff.summary.manualOnly} manual-only.`,
      `Manual disposition: ${manualDispositionReceipt.summary.documented}/${manualDispositionReceipt.summary.total} documented, ${manualDispositionReceipt.summary.ownerRequired} owner pending.`,
      `Final publish gate: ${finalGate}.`,
    ],
    nextActions:
      blockers.length > 0
        ? blockers.map((blocker) => `Resolve ${blocker}.`)
        : ["Export validation report.", "Attach sidecar manifest.", "Move asset package to publish review."],
  };
}

function evaluateRuleForAdapter(
  adapterId: DccId,
  rule: RuleDefinition,
  asset: AssetProtocolFixture,
  capabilities: AdapterCapabilityMap,
): RuleEvaluation {
  if (!capabilities[rule.capability]) {
    return {
      adapterId,
      ruleId: rule.id,
      status: "skipped",
      message: `${adapterLabel(adapterId)} adapter cannot collect ${adapterCapabilityLabels[rule.capability]}.`,
      evidence: `capability.${rule.capability}=false`,
      fixPreview: "Adapter gap: implement collector before trusting this rule.",
    };
  }

  switch (rule.id) {
    case "protocol-carrier":
      return protocolCarrierEvaluation(adapterId, asset);
    case "collision-contract":
      return collisionEvaluation(adapterId, asset);
    case "lod-budget":
      return lodEvaluation(adapterId, asset);
    case "material-texture-sync":
      return materialTextureEvaluation(adapterId, asset);
    case "export-root-clean":
      return exportRootEvaluation(adapterId, asset);
    case "publish-manifest":
      return publishManifestEvaluation(adapterId, asset, capabilities);
    default:
      return {
        adapterId,
        ruleId: rule.id,
        status: "skipped",
        message: "Rule is not implemented in this synthetic matrix.",
        evidence: "No evaluator registered.",
        fixPreview: "None.",
      };
  }
}

function protocolCarrierEvaluation(adapterId: DccId, asset: AssetProtocolFixture): RuleEvaluation {
  const isStaleMaxSchema = adapterId === "max" && asset.schemaVersion.endsWith("@1.0.0");
  const isWeakCarrier = asset.semanticCarrier === "customAttr" && asset.uv3U === 0;

  return {
    adapterId,
    ruleId: "protocol-carrier",
    status: isStaleMaxSchema || isWeakCarrier ? "warning" : "pass",
    message:
      isStaleMaxSchema || isWeakCarrier
        ? "protocol carrier exists but needs a stable downstream mirror."
        : `${adapterLabel(adapterId)} carrier maps to protocol fields.`,
    evidence: `${asset.semanticCarrier}, schema=${asset.schemaVersion}, uv3U=${asset.uv3U}`,
    fixPreview: isWeakCarrier ? "Safe: mirror semantic class to UV3 before extract." : "No fix needed.",
  };
}

function collisionEvaluation(adapterId: DccId, asset: AssetProtocolFixture): RuleEvaluation {
  if (asset.collision === "missing") {
    return {
      adapterId,
      ruleId: "collision-contract",
      status: "error",
      message: "collision declaration is missing.",
      evidence: `${adapterLabel(adapterId)} payload reports collision=missing.`,
      fixPreview: "Manual: author simple collision or approve generated proxy.",
    };
  }

  return {
    adapterId,
    ruleId: "collision-contract",
    status: asset.collision === "simple" && asset.category === "vehicle" ? "warning" : "pass",
    message:
      asset.collision === "simple" && asset.category === "vehicle"
        ? "vehicle uses simple collision; TA review is required."
        : `${asset.collision} collision is declared.`,
    evidence: `collision=${asset.collision}, category=${asset.category}`,
    fixPreview: "No fix needed.",
  };
}

function lodEvaluation(adapterId: DccId, asset: AssetProtocolFixture): RuleEvaluation {
  const expected = asset.platform === "Mobile" ? 2 : asset.platform === "Console" ? 3 : 3;
  const houdiniQueue = adapterId === "houdini" && asset.streamable && asset.lodCount === expected;

  return {
    adapterId,
    ruleId: "lod-budget",
    status: asset.lodCount < expected || houdiniQueue ? "warning" : "pass",
    message:
      asset.lodCount < expected
        ? "LOD count is below platform budget."
        : houdiniQueue
          ? "PDG LOD bake should finish before extract."
          : `${asset.lodCount} LOD levels satisfy ${asset.platform} budget.`,
    evidence: `lodCount=${asset.lodCount}, expected>=${expected}, screenSize=${asset.screenSize}, cullDistance=${asset.cullDistance}`,
    fixPreview:
      asset.lodCount < expected
        ? `Manual: queue LOD generation to reach ${expected}+ levels.`
        : houdiniQueue
          ? "Manual: wait for queued PDG LOD bake result."
          : "No fix needed.",
  };
}

function materialTextureEvaluation(adapterId: DccId, asset: AssetProtocolFixture): RuleEvaluation {
  const mobileBudgetMiss = asset.platform === "Mobile" && asset.textureSets > 3;
  const drift = Math.abs(asset.materialSlots - asset.textureSets) > 1;

  return {
    adapterId,
    ruleId: "material-texture-sync",
    status: mobileBudgetMiss || drift ? "warning" : "pass",
    message:
      mobileBudgetMiss || drift
        ? "material slots and texture sets need delivery review."
        : "material slots and texture sets are aligned.",
    evidence: `materialSlots=${asset.materialSlots}, textureSets=${asset.textureSets}, platform=${asset.platform}`,
    fixPreview:
      mobileBudgetMiss || drift
        ? "Manual: preview texture merge or shader binding cleanup."
        : "No fix needed.",
  };
}

function exportRootEvaluation(adapterId: DccId, asset: AssetProtocolFixture): RuleEvaluation {
  const needsReview = adapterId === "blender" && asset.category === "character";

  return {
    adapterId,
    ruleId: "export-root-clean",
    status: needsReview ? "warning" : "pass",
    message: needsReview ? "temporary bake collection may still be visible." : "single export root is detected.",
    evidence: adapterId === "houdini" ? "/obj/asset/OUT_publish" : `${asset.id}_export_root`,
    fixPreview: needsReview ? "Safe: mark temporary bake collection excluded from export." : "No fix needed.",
  };
}

function publishManifestEvaluation(
  adapterId: DccId,
  asset: AssetProtocolFixture,
  capabilities: AdapterCapabilityMap,
): RuleEvaluation {
  const missingCapabilities = Object.entries(capabilities)
    .filter(([, enabled]) => !enabled)
    .map(([key]) => key);

  return {
    adapterId,
    ruleId: "publish-manifest",
    status: missingCapabilities.length > 0 ? "warning" : "pass",
    message:
      missingCapabilities.length > 0
        ? "manifest must include adapter capability gaps."
        : "manifest can be generated from collected fields.",
    evidence:
      missingCapabilities.length > 0
        ? `missing=${missingCapabilities.join(", ")}`
        : `asset=${asset.id}, schema=${asset.schemaVersion}`,
    fixPreview:
      missingCapabilities.length > 0
        ? "Safe: include skipped rule explanations in report."
        : "No fix needed.",
  };
}

function getFixDiff(ruleId: string, asset: AssetProtocolFixture, capabilityGap: boolean) {
  if (capabilityGap) {
    return {
      before: "collector unavailable",
      after: "collector implemented",
    };
  }

  switch (ruleId) {
    case "protocol-carrier":
      return {
        before: asset.semanticCarrier,
        after: "stable carrier mirror",
      };
    case "collision-contract":
      return {
        before: asset.collision,
        after: asset.collision === "missing" ? "simple/proxy" : "review stamp",
      };
    case "lod-budget":
      return {
        before: `${asset.lodCount} LOD`,
        after: `${asset.platform === "Mobile" ? 2 : 3}+ LOD`,
      };
    case "material-texture-sync":
      return {
        before: `${asset.materialSlots} material / ${asset.textureSets} texture`,
        after: "reviewed binding budget",
      };
    case "export-root-clean":
      return {
        before: "raw DCC root",
        after: "tagged export root",
      };
    case "publish-manifest":
      return {
        before: "partial report",
        after: "capability-aware report",
      };
    default:
      return {
        before: "unknown",
        after: "reviewed",
      };
  }
}

function getFixPayloadPath(ruleId: string) {
  switch (ruleId) {
    case "protocol-carrier":
      return "payload.protocol.semanticCarrier";
    case "collision-contract":
      return "payload.physics.collision";
    case "lod-budget":
      return "payload.render.lodCount";
    case "material-texture-sync":
      return "payload.material.textureSetBudget";
    case "export-root-clean":
      return "payload.extract.exportRoot";
    case "publish-manifest":
      return "payload.publish.manifest";
    default:
      return `payload.rules.${ruleId}`;
  }
}

function formatFixPayload(value: string, asset: AssetProtocolFixture, side: "before" | "after") {
  return JSON.stringify({
    assetId: asset.id,
    side,
    value,
  });
}

function getFixMutationScope(kind: RuleFixQueueItem["kind"]): FixPreviewMutationScope {
  if (kind === "safe") {
    return "safe_auto";
  }
  if (kind === "capability") {
    return "adapter_gap";
  }
  return "manual_only";
}

function getFixPreviewDiffGate(item: RuleFixQueueItem): MatrixSummary["gate"] {
  if (item.actionState === "blocked" || item.status === "error") {
    return "Blocked";
  }
  if (item.kind === "safe" && (item.actionState === "approved" || item.actionState === "exported")) {
    return "Ready";
  }
  return "Review";
}

function getFixPreviewReviewerNote(item: RuleFixQueueItem) {
  if (item.kind === "safe") {
    return "Tool-owned safe fix: reviewer checks the payload diff before allowing export.";
  }
  if (item.kind === "capability") {
    return "Adapter-owned gap: implement collector before this rule can be trusted.";
  }
  return "Manual-only fix: reviewer records owner disposition; tool must not mutate this field.";
}

function getManualDispositionState(actionState: FixActionState): ManualDispositionState {
  if (actionState === "approved") {
    return "owner_accepted";
  }
  if (actionState === "blocked") {
    return "blocked";
  }
  if (actionState === "exported") {
    return "documented";
  }
  return "owner_required";
}

function getManualDispositionReasonCode(item: RuleFixQueueItem) {
  if (item.kind === "capability") {
    return "adapter_capability_gap";
  }
  switch (item.ruleId) {
    case "collision-contract":
      return "generated_collision_changes_gameplay";
    case "lod-budget":
      return "lod_generation_changes_runtime_budget";
    case "material-texture-sync":
      return "material_binding_changes_visual_output";
    default:
      return "asset_semantics_require_owner_review";
  }
}

function getManualDispositionEvidence(item: RuleFixQueueItem, asset: AssetProtocolFixture) {
  switch (item.ruleId) {
    case "collision-contract":
      return `${asset.id}: collision authoring note or visual-only exemption.`;
    case "lod-budget":
      return `${asset.id}: LOD bake request, owner accepted LOD count, or waiver.`;
    case "material-texture-sync":
      return `${asset.id}: texture merge preview or shader binding cleanup approval.`;
    default:
      return `${asset.id}: owner disposition attached to rule ${item.ruleId}.`;
  }
}

function getManualDispositionQuestion(item: RuleFixQueueItem) {
  switch (item.ruleId) {
    case "collision-contract":
      return "Can this asset ship with generated proxy collision, or must an artist author collision manually?";
    case "lod-budget":
      return "Should the package wait for generated LODs, or is the current LOD count accepted as an exception?";
    case "material-texture-sync":
      return "Should the tool merge texture sets, or should a TA review shader binding first?";
    default:
      return item.kind === "capability"
        ? "Who owns the missing adapter collector, and can this rule be trusted before it exists?"
        : "Which owner accepts the manual-only disposition for this rule?";
  }
}

function adapterLabel(adapterId: DccId) {
  return dccAdapters.find((adapter) => adapter.id === adapterId)?.name ?? adapterId;
}

function buildDraftRuleName(flags: {
  mentionsCollision: boolean;
  mentionsLod: boolean;
  mentionsTexture: boolean;
  mentionsNanite: boolean;
}) {
  if (flags.mentionsNanite) {
    return "Platform Render Gate";
  }

  if (flags.mentionsCollision) {
    return "Collision Publish Gate";
  }

  if (flags.mentionsLod) {
    return "LOD Budget Gate";
  }

  if (flags.mentionsTexture) {
    return "Texture Budget Gate";
  }

  return "Protocol Carrier Gate";
}

function adapterSource(adapterId: DccId, capability: AdapterCapabilityKey) {
  const map: Record<DccId, Record<AdapterCapabilityKey, string>> = {
    maya: {
      protocolCarrier: "DAG node custom attrs",
      collision: "collision mesh + LB_collision attr",
      lod: "LOD group + LB_lod_count attr",
      materialTexture: "shadingEngine + texture set table",
      exportRoot: "export root transform",
      manifest: "rule result sidecar JSON",
    },
    blender: {
      protocolCarrier: "object custom properties",
      collision: "collision collection",
      lod: "LOD collections",
      materialTexture: "material slots + image datablocks",
      exportRoot: "scene collection export flag",
      manifest: "asset browser metadata",
    },
    max: {
      protocolCarrier: "node user props",
      collision: "UCX layer + node property",
      lod: "LOD nodes + modifier stack",
      materialTexture: "material editor slots + bitmap refs",
      exportRoot: "EXPORT layer",
      manifest: "layer validation report",
    },
    houdini: {
      protocolCarrier: "detail attributes",
      collision: "primitive group @name=collision_proxy",
      lod: "PDG work item + SOP detail attr",
      materialTexture: "shop_materialpath + texture_set attr",
      exportRoot: "OUT_publish SOP",
      manifest: "PDG validation payload",
    },
  };

  return map[adapterId][capability];
}

export const defaultRuleMatrixAsset = assetFixtures[1];

