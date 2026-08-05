export type ReviewGate = "Ready" | "Review" | "Blocked";
export type LodBucket = "LOD0" | "DT" | "other";
export type CameraGroupId = "basic" | "detail";
export type PassPresetId = "rb_lod0" | "wb_lod0" | "rb_dt" | "wb_dt" | "solo_b";
export type PassStatus = "run" | "skipped";
export type FindingSeverity = "info" | "warning" | "error";
export type ReviewDecisionState = "pending" | "accepted" | "needs_fix";
export type ReviewQueueOwner = "artist" | "ta" | "reviewer";
export type ReviewQueueState = "todo" | "blocked" | "ready";
export type HandoffDeliveryState = "not_required" | "draft" | "sent" | "failed" | "read" | "acknowledged";
export type HandoffDeliveryChannel = "wecom" | "review_board";
export type VisualReleaseCriterionId =
  | "capture_contract"
  | "signal_thresholds"
  | "queue_resolution"
  | "handoff_ack"
  | "review_decision"
  | "evidence_package";
export type VisualReleaseDecision = "release_candidate" | "hold_for_review" | "blocked_from_release";
export type VisualSignalId = "silhouette" | "bbox" | "material" | "cameraCoverage";
export type VisualSignalDirection = "above" | "below";
export type VisualFixtureEditorPresetId =
  | "source"
  | "clean_candidate"
  | "dt_blocker"
  | "texture_review"
  | "camera_gap"
  | "unit_mismatch";
export type VisualReviewAuditAction =
  | "draft_edited"
  | "draft_regenerated"
  | "accepted"
  | "needs_fix"
  | "queue_blocked"
  | "queue_ready"
  | "queue_todo"
  | "handoff_sent"
  | "handoff_failed"
  | "handoff_read"
  | "handoff_acknowledged";
export type ReviewQueueStateOverrides = Partial<Record<string, ReviewQueueState>>;
export type HandoffDeliveryOverrides = Partial<Record<ReviewQueueOwner, HandoffDeliveryOverride>>;

export interface ReviewAssetSlot {
  label: "A" | "B";
  name: string;
  sourcePath: string;
  unit: "cm" | "m" | "mm";
  meshes: string[];
  unresolvedTextures: string[];
  materialCount: number;
}

export interface VisualComparisonSignal {
  silhouetteDeltaPercent: number;
  bboxDeltaPercent: number;
  materialDriftScore: number;
  cameraCoverageScore: number;
  reviewerNote: string;
}

export interface VisualReviewFixture {
  id: string;
  name: string;
  baseline: ReviewAssetSlot;
  variant: ReviewAssetSlot;
  cameraRig: Record<CameraGroupId, string[]>;
  discoveryMode: "fuzzy_camera_group" | "legacy_prefix";
  comparison: VisualComparisonSignal;
}

export interface VisualReviewOptions {
  cameraGroups: CameraGroupId[];
  width: number;
  height: number;
  saveSceneBackup: boolean;
  notifyEnabled: boolean;
}

export interface VisualFixtureEditorState {
  silhouetteDeltaPercent: number;
  bboxDeltaPercent: number;
  materialDriftScore: number;
  cameraCoverageScore: number;
  variantUnit: ReviewAssetSlot["unit"];
  variantMaterialCount: number;
  unresolvedTextureCount: number;
  variantDtCount: number;
  reviewerNote: string;
}

export interface VisualFixtureEditSummary {
  mode: "source_fixture" | "runtime_fixture_editor";
  sourceFixtureId: string;
  sourceFixtureName: string;
  changed: boolean;
  changedFields: string[];
  before: VisualFixtureEditorState;
  after: VisualFixtureEditorState;
}

export interface VisualFixtureEditorPreset {
  id: VisualFixtureEditorPresetId;
  label: string;
  description: string;
}

export interface VisualPassPreset {
  id: PassPresetId;
  label: string;
  shortLabel: string;
  lodLabel: "LOD0" | "DT" | "";
  kindLabel: "rb" | "wb" | "solo_b";
  requiredBucket: "LOD0" | "DT" | "variant_lod0_or_dt";
  intent: string;
  materialContract: string;
}

export interface VisualPassRun {
  presetId: PassPresetId;
  label: string;
  status: PassStatus;
  reason: string;
  cameraCount: number;
  imageCount: number;
  shotNames: string[];
  sceneBackup: string;
}

export interface LodSplitSummary {
  slot: "A" | "B";
  LOD0: number;
  DT: number;
  other: number;
}

export interface ReviewFinding {
  id: string;
  severity: FindingSeverity;
  gate: ReviewGate;
  channel: "unit" | "lod" | "material" | "silhouette" | "camera" | "texture" | "package";
  title: string;
  detail: string;
  evidence: string;
  suggestedAction: string;
}

export interface ReviewQueueItem {
  id: string;
  title: string;
  owner: ReviewQueueOwner;
  state: ReviewQueueState;
  sourceFindingId: string;
  sourceFindingTitle: string;
  gate: ReviewGate;
  severity: FindingSeverity;
  channel: ReviewFinding["channel"];
  priority: number;
  evidence: string;
  relatedPasses: PassPresetId[];
  nextCheck: string;
  handoffNote: string;
}

export interface ReviewQueueSummary {
  total: number;
  todo: number;
  blocked: number;
  ready: number;
  artist: number;
  ta: number;
  reviewer: number;
}

export interface VisualEvidencePackage {
  outputDir: string;
  sceneBackup: string;
  imageCount: number;
  htmlOverview: string;
}

export interface HandoffDeliveryOverride {
  state: HandoffDeliveryState;
  attempts: number;
  lastEvent: string;
}

export interface VisualDiffSignal {
  id: VisualSignalId;
  label: string;
  value: number;
  unit: "%" | "score";
  direction: VisualSignalDirection;
  reviewThreshold: number;
  blockThreshold: number;
  fillPercent: number;
  gate: ReviewGate;
  evidence: string;
  relatedPasses: PassPresetId[];
}

export interface VisualPassSignalLink {
  signalId: VisualSignalId;
  label: string;
  gate: ReviewGate;
  value: number;
  unit: "%" | "score";
  evidence: string;
}

export interface VisualPassFindingLink {
  findingId: string;
  severity: FindingSeverity;
  gate: ReviewGate;
  channel: ReviewFinding["channel"];
  title: string;
  evidence: string;
  suggestedAction: string;
}

export interface VisualPassShotLink {
  cameraName: string;
  cameraGroup: CameraGroupId;
  outputName: string;
  linkedSignalIds: VisualSignalId[];
}

export interface VisualPassDrilldown {
  presetId: PassPresetId;
  label: string;
  status: PassStatus;
  gate: ReviewGate;
  reason: string;
  materialContract: string;
  outputPattern: string;
  cameraCount: number;
  imageCount: number;
  shots: VisualPassShotLink[];
  relatedSignals: VisualPassSignalLink[];
  relatedFindings: VisualPassFindingLink[];
  nextAction: string;
}

export interface VisualReviewAuditEvent {
  revision: number;
  action: VisualReviewAuditAction;
  fixtureId: string;
  fixtureName: string;
  gate: ReviewGate;
  fromDecision: ReviewDecisionState;
  toDecision: ReviewDecisionState;
  draftExcerpt: string;
  note: string;
}

export interface ReviewHandoffItem {
  queueId: string;
  sourceFindingId: string;
  sourceFindingTitle: string;
  owner: ReviewQueueOwner;
  state: ReviewQueueState;
  gate: ReviewGate;
  severity: FindingSeverity;
  priority: number;
  evidence: string;
  relatedPasses: PassPresetId[];
  nextCheck: string;
  handoffNote: string;
}

export interface HandoffDeliveryReceipt {
  owner: ReviewQueueOwner;
  state: HandoffDeliveryState;
  channel: HandoffDeliveryChannel;
  recipient: string;
  attempts: number;
  ackRequired: boolean;
  lastEvent: string;
  nextAction: string;
}

export interface ReviewHandoffSection {
  owner: ReviewQueueOwner;
  ownerLabel: string;
  total: number;
  blocked: number;
  todo: number;
  ready: number;
  gate: ReviewGate;
  topPriority: number;
  items: ReviewHandoffItem[];
  delivery: HandoffDeliveryReceipt;
  messagePreview: string;
}

export interface HandoffDeliverySummary {
  totalOwners: number;
  pending: number;
  sent: number;
  failed: number;
  read: number;
  acknowledged: number;
  notRequired: number;
}

export interface ReviewHandoffPacket {
  packetVersion: "visual-review-handoff@0.2.0";
  fixtureId: string;
  fixtureName: string;
  gate: ReviewGate;
  ownerOrder: ReviewQueueOwner[];
  queueSummary: ReviewQueueSummary;
  deliverySummary: HandoffDeliverySummary;
  evidencePackage: VisualEvidencePackage;
  sections: ReviewHandoffSection[];
  notificationPreview: string;
}

export interface VisualReleaseCriterion {
  id: VisualReleaseCriterionId;
  label: string;
  gate: ReviewGate;
  required: boolean;
  summary: string;
  evidence: string;
  nextAction: string;
}

export interface VisualReleaseGate {
  reportVersion: "visual-review-release-gate@0.1.0";
  fixtureId: string;
  fixtureName: string;
  gate: ReviewGate;
  decision: VisualReleaseDecision;
  criteria: VisualReleaseCriterion[];
  ready: number;
  review: number;
  blocked: number;
  blockers: string[];
  publishChecklist: string[];
  releaseNotePreview: string;
}

export interface VisualReviewReport {
  reportVersion: "visual-review-report@0.8.0";
  fixtureId: string;
  fixtureName: string;
  gate: ReviewGate;
  options: VisualReviewOptions;
  fixtureSnapshot: VisualReviewFixture;
  fixtureEditSummary: VisualFixtureEditSummary;
  lodSplit: LodSplitSummary[];
  passRuns: VisualPassRun[];
  diffSignals: VisualDiffSignal[];
  passDrilldowns: VisualPassDrilldown[];
  findings: ReviewFinding[];
  reviewQueue: ReviewQueueItem[];
  reviewQueueSummary: ReviewQueueSummary;
  handoffPacket: ReviewHandoffPacket;
  releaseGate: VisualReleaseGate;
  reviewAudit: VisualReviewAuditEvent[];
  aiReviewDraft: string;
  decisionState: ReviewDecisionState;
  notificationPreview: string;
  evidencePackage: VisualEvidencePackage;
}

export interface VisualBatchSignalSummary {
  signalId: VisualSignalId;
  label: string;
  gate: ReviewGate;
  value: number;
  unit: "%" | "score";
}

export interface VisualBatchFindingSummary {
  findingId: string;
  severity: FindingSeverity;
  gate: ReviewGate;
  channel: ReviewFinding["channel"];
  title: string;
}

export interface VisualBatchSkippedPass {
  presetId: PassPresetId;
  label: string;
  reason: string;
}

export interface VisualBatchItem {
  fixtureId: string;
  name: string;
  captureStatus: "ok" | "failed";
  reviewGate: ReviewGate;
  reason: string;
  outputDir: string;
  imageCount: number;
  passesRun: number;
  passesSkipped: number;
  sceneBackup: string;
  htmlOverview: string;
  primarySignal: VisualBatchSignalSummary | null;
  topFindings: VisualBatchFindingSummary[];
  firstSkippedPass: VisualBatchSkippedPass | null;
  queueBlocked: number;
  queueTodo: number;
  queueReady: number;
  handoffOwners: ReviewQueueOwner[];
  handoffPreview: string;
  handoffDelivery: HandoffDeliveryReceipt[];
  releaseGate: ReviewGate;
  releaseDecision: VisualReleaseDecision;
  releaseBlockers: number;
  releasePreview: string;
  fixtureEditSummary: VisualFixtureEditSummary;
  reportPreview: string;
}

export interface VisualBatchReport {
  reportVersion: "visual-batch-review@0.7.0";
  success: number;
  failed: number;
  ready: number;
  review: number;
  blocked: number;
  sampleOutputDirs: string[];
  items: VisualBatchItem[];
  notificationPreview: string;
}

export const visualPassPresets: VisualPassPreset[] = [
  {
    id: "rb_lod0",
    label: "Red / Blue LOD0",
    shortLabel: "LOD0 RB",
    lodLabel: "LOD0",
    kindLabel: "rb",
    requiredBucket: "LOD0",
    intent: "Silhouette overlap against the baseline LOD0.",
    materialContract: "A red 45% transparent, B cyan 45% transparent.",
  },
  {
    id: "wb_lod0",
    label: "White / Blue LOD0",
    shortLabel: "LOD0 WB",
    lodLabel: "LOD0",
    kindLabel: "wb",
    requiredBucket: "LOD0",
    intent: "Readable shape delta with A on default lambert and B opaque blue.",
    materialContract: "A lambert1 white, B solid cyan, mild highlight.",
  },
  {
    id: "rb_dt",
    label: "Red / Blue DT",
    shortLabel: "DT RB",
    lodLabel: "DT",
    kindLabel: "rb",
    requiredBucket: "DT",
    intent: "High-detail delta check on detail mesh buckets.",
    materialContract: "A red 45% transparent, B cyan 45% transparent.",
  },
  {
    id: "wb_dt",
    label: "White / Blue DT",
    shortLabel: "DT WB",
    lodLabel: "DT",
    kindLabel: "wb",
    requiredBucket: "DT",
    intent: "Detail surfacing and silhouette check with a stable material pass.",
    materialContract: "A lambert1 white, B solid cyan, mild highlight.",
  },
  {
    id: "solo_b",
    label: "Variant Dual LOD",
    shortLabel: "Solo B",
    lodLabel: "",
    kindLabel: "solo_b",
    requiredBucket: "variant_lod0_or_dt",
    intent: "Inspect variant LOD0 and DT relationship without baseline occlusion.",
    materialContract: "B LOD0 dark grey, B DT light grey, A hidden.",
  },
];

export const defaultVisualReviewOptions: VisualReviewOptions = {
  cameraGroups: ["basic", "detail"],
  width: 1024,
  height: 1024,
  saveSceneBackup: true,
  notifyEnabled: true,
};

export const visualFixtureEditorPresets: VisualFixtureEditorPreset[] = [
  {
    id: "source",
    label: "Source Fixture",
    description: "Return to the checked-in fixture values.",
  },
  {
    id: "clean_candidate",
    label: "Clean Candidate",
    description: "Normalize units, restore DT, clear textures, and keep all signals below review thresholds.",
  },
  {
    id: "dt_blocker",
    label: "DT Blocker",
    description: "Remove variant DT meshes and push silhouette delta into a blocking review.",
  },
  {
    id: "texture_review",
    label: "Texture Review",
    description: "Preserve geometry but add material drift and sourceimages misses.",
  },
  {
    id: "camera_gap",
    label: "Camera Gap",
    description: "Keep geometry comparable while camera coverage drops below the block threshold.",
  },
  {
    id: "unit_mismatch",
    label: "Unit Mismatch",
    description: "Simulate a scale-risk import where B arrives in a different linear unit.",
  },
];

export const visualReviewFixtures: VisualReviewFixture[] = [
  {
    id: "rifle_dt_gap",
    name: "Rifle DT Gap",
    discoveryMode: "fuzzy_camera_group",
    baseline: {
      label: "A",
      name: "WPN_Rifle_A_baseline.ma",
      sourcePath: "P:/weapon/rifle/baseline/WPN_Rifle_A_baseline.ma",
      unit: "cm",
      meshes: [
        "weaponCmpA:WPN_Rifle_LOD0_bodyShape",
        "weaponCmpA:WPN_Rifle_LOD0_magShape",
        "weaponCmpA:WPN_Rifle_DT_receiverShape",
        "weaponCmpA:WPN_Rifle_DT_sightShape",
      ],
      unresolvedTextures: [],
      materialCount: 8,
    },
    variant: {
      label: "B",
      name: "WPN_Rifle_B_variant.ma",
      sourcePath: "P:/weapon/rifle/review/WPN_Rifle_B_variant.ma",
      unit: "m",
      meshes: [
        "weaponCmpB:WPN_Rifle_LOD0_bodyShape",
        "weaponCmpB:WPN_Rifle_LOD0_magShape",
        "weaponCmpB:WPN_Rifle_LOD1_proxyShape",
      ],
      unresolvedTextures: ["T_Rifle_Body_N.tga", "T_Rifle_Detail_MRA.tga"],
      materialCount: 5,
    },
    cameraRig: {
      basic: ["Camera_Front", "Camera_Back", "Camera_Left", "Camera_Right", "Camera_Top", "Camera_Bottom"],
      detail: ["Camera_01", "Camera_02", "Camera_03", "Camera_04"],
    },
    comparison: {
      silhouetteDeltaPercent: 14.6,
      bboxDeltaPercent: 6.8,
      materialDriftScore: 0.34,
      cameraCoverageScore: 0.92,
      reviewerNote: "DT mesh is absent on B and unit conversion risk makes the overlay unreliable.",
    },
  },
  {
    id: "blade_material_shift",
    name: "Blade Material Shift",
    discoveryMode: "legacy_prefix",
    baseline: {
      label: "A",
      name: "WPN_Blade_A_baseline.ma",
      sourcePath: "P:/weapon/blade/baseline/WPN_Blade_A_baseline.ma",
      unit: "cm",
      meshes: [
        "weaponCmpA:WPN_Blade_LOD0_bodyShape",
        "weaponCmpA:WPN_Blade_LOD0_guardShape",
        "weaponCmpA:WPN_Blade_DT_edgeShape",
        "weaponCmpA:WPN_Blade_DT_handleShape",
      ],
      unresolvedTextures: [],
      materialCount: 6,
    },
    variant: {
      label: "B",
      name: "WPN_Blade_B_material.ma",
      sourcePath: "P:/weapon/blade/review/WPN_Blade_B_material.ma",
      unit: "cm",
      meshes: [
        "weaponCmpB:WPN_Blade_LOD0_bodyShape",
        "weaponCmpB:WPN_Blade_LOD0_guardShape",
        "weaponCmpB:WPN_Blade_DT_edgeShape",
        "weaponCmpB:WPN_Blade_DT_handleShape",
      ],
      unresolvedTextures: ["T_Blade_Grip_D.tga"],
      materialCount: 4,
    },
    cameraRig: {
      basic: ["cam_front", "cam_back", "cam_left", "cam_right", "cam_top", "cam_bottom"],
      detail: ["wp_cam_01", "wp_cam_02", "wp_cam_03", "wp_cam_04", "wp_cam_05"],
    },
    comparison: {
      silhouetteDeltaPercent: 3.9,
      bboxDeltaPercent: 1.5,
      materialDriftScore: 0.27,
      cameraCoverageScore: 0.88,
      reviewerNote: "Geometry is mostly aligned, but the variant lost one texture path and material slots were merged.",
    },
  },
  {
    id: "pistol_clean",
    name: "Pistol Clean Variant",
    discoveryMode: "fuzzy_camera_group",
    baseline: {
      label: "A",
      name: "WPN_Pistol_A_baseline.ma",
      sourcePath: "P:/weapon/pistol/baseline/WPN_Pistol_A_baseline.ma",
      unit: "cm",
      meshes: [
        "weaponCmpA:WPN_Pistol_LOD0_bodyShape",
        "weaponCmpA:WPN_Pistol_LOD0_slideShape",
        "weaponCmpA:WPN_Pistol_DT_triggerShape",
      ],
      unresolvedTextures: [],
      materialCount: 5,
    },
    variant: {
      label: "B",
      name: "WPN_Pistol_B_review.ma",
      sourcePath: "P:/weapon/pistol/review/WPN_Pistol_B_review.ma",
      unit: "cm",
      meshes: [
        "weaponCmpB:WPN_Pistol_LOD0_bodyShape",
        "weaponCmpB:WPN_Pistol_LOD0_slideShape",
        "weaponCmpB:WPN_Pistol_DT_triggerShape",
      ],
      unresolvedTextures: [],
      materialCount: 5,
    },
    cameraRig: {
      basic: ["Camera_Front", "Camera_Back", "Camera_Left", "Camera_Right", "Camera_Top", "Camera_Bottom"],
      detail: ["Camera_01", "Camera_02", "Camera_03"],
    },
    comparison: {
      silhouetteDeltaPercent: 1.8,
      bboxDeltaPercent: 0.6,
      materialDriftScore: 0.08,
      cameraCoverageScore: 0.96,
      reviewerNote: "All required passes run and deltas stay below review thresholds.",
    },
  },
];

export function createVisualFixtureEditorState(fixture: VisualReviewFixture): VisualFixtureEditorState {
  return {
    silhouetteDeltaPercent: roundToStep(fixture.comparison.silhouetteDeltaPercent, 1),
    bboxDeltaPercent: roundToStep(fixture.comparison.bboxDeltaPercent, 1),
    materialDriftScore: roundToStep(fixture.comparison.materialDriftScore, 2),
    cameraCoverageScore: roundToStep(fixture.comparison.cameraCoverageScore, 2),
    variantUnit: fixture.variant.unit,
    variantMaterialCount: fixture.variant.materialCount,
    unresolvedTextureCount: fixture.variant.unresolvedTextures.length,
    variantDtCount: classifyMeshesByLod(fixture.variant.meshes).DT.length,
    reviewerNote: fixture.comparison.reviewerNote,
  };
}

export function createVisualFixtureEditorPresetState(
  fixture: VisualReviewFixture,
  presetId: VisualFixtureEditorPresetId,
): VisualFixtureEditorState {
  const source = createVisualFixtureEditorState(fixture);
  const cleanDtCount = Math.max(1, source.variantDtCount);
  const cleanMaterialCount = Math.max(1, fixture.baseline.materialCount);

  switch (presetId) {
    case "clean_candidate":
      return normalizeVisualFixtureEditorState({
        ...source,
        silhouetteDeltaPercent: 2.2,
        bboxDeltaPercent: 0.8,
        materialDriftScore: 0.08,
        cameraCoverageScore: 0.96,
        variantUnit: fixture.baseline.unit,
        variantMaterialCount: cleanMaterialCount,
        unresolvedTextureCount: 0,
        variantDtCount: cleanDtCount,
        reviewerNote: "All required passes are comparable and signal deltas stay below review thresholds.",
      });
    case "dt_blocker":
      return normalizeVisualFixtureEditorState({
        ...source,
        silhouetteDeltaPercent: 13.4,
        bboxDeltaPercent: 6.2,
        materialDriftScore: Math.max(source.materialDriftScore, 0.24),
        variantDtCount: 0,
        reviewerNote: "Variant DT meshes are missing, so detail passes cannot prove this change is safe.",
      });
    case "texture_review":
      return normalizeVisualFixtureEditorState({
        ...source,
        silhouetteDeltaPercent: 4.4,
        bboxDeltaPercent: 1.6,
        materialDriftScore: 0.31,
        variantMaterialCount: Math.max(1, cleanMaterialCount - 2),
        unresolvedTextureCount: 3,
        variantDtCount: cleanDtCount,
        reviewerNote: "Geometry remains comparable, but material slots and texture paths need artist review.",
      });
    case "camera_gap":
      return normalizeVisualFixtureEditorState({
        ...source,
        silhouetteDeltaPercent: 3.2,
        bboxDeltaPercent: 1.1,
        materialDriftScore: 0.12,
        cameraCoverageScore: 0.72,
        variantDtCount: cleanDtCount,
        reviewerNote: "Camera discovery missed key detail angles, so review evidence is incomplete.",
      });
    case "unit_mismatch":
      return normalizeVisualFixtureEditorState({
        ...source,
        silhouetteDeltaPercent: 8.1,
        bboxDeltaPercent: 5.8,
        materialDriftScore: 0.16,
        variantUnit: fixture.baseline.unit === "cm" ? "m" : "cm",
        variantDtCount: cleanDtCount,
        reviewerNote: "Variant B is imported with a different unit, making overlay interpretation unsafe.",
      });
    case "source":
      return source;
  }
}

export function applyVisualFixtureEditorState(
  fixture: VisualReviewFixture,
  state: VisualFixtureEditorState,
): VisualReviewFixture {
  const normalized = normalizeVisualFixtureEditorState(state);
  return {
    ...fixture,
    variant: {
      ...fixture.variant,
      unit: normalized.variantUnit,
      materialCount: normalized.variantMaterialCount,
      unresolvedTextures: buildEditorMissingTextures(fixture, normalized.unresolvedTextureCount),
      meshes: buildEditorVariantMeshes(fixture, normalized.variantDtCount),
    },
    comparison: {
      ...fixture.comparison,
      silhouetteDeltaPercent: normalized.silhouetteDeltaPercent,
      bboxDeltaPercent: normalized.bboxDeltaPercent,
      materialDriftScore: normalized.materialDriftScore,
      cameraCoverageScore: normalized.cameraCoverageScore,
      reviewerNote: normalized.reviewerNote.trim() || fixture.comparison.reviewerNote,
    },
  };
}

export function getVisualFixtureEditSummary(
  sourceFixture: VisualReviewFixture,
  editedFixture: VisualReviewFixture,
): VisualFixtureEditSummary {
  const before = createVisualFixtureEditorState(sourceFixture);
  const after = createVisualFixtureEditorState(editedFixture);
  const changedFields = getChangedFixtureFields(before, after);

  return {
    mode: changedFields.length > 0 ? "runtime_fixture_editor" : "source_fixture",
    sourceFixtureId: sourceFixture.id,
    sourceFixtureName: sourceFixture.name,
    changed: changedFields.length > 0,
    changedFields,
    before,
    after,
  };
}

export function classifyMeshesByLod(meshes: string[]): Record<LodBucket, string[]> {
  return meshes.reduce<Record<LodBucket, string[]>>(
    (buckets, mesh) => {
      const shortName = mesh.split("|").pop()?.split(":").pop()?.toLowerCase() ?? mesh.toLowerCase();
      if (shortName.includes("lod0")) {
        buckets.LOD0.push(mesh);
      } else if (shortName.includes("dt")) {
        buckets.DT.push(mesh);
      } else {
        buckets.other.push(mesh);
      }
      return buckets;
    },
    { LOD0: [], DT: [], other: [] },
  );
}

export function getLodSplit(asset: ReviewAssetSlot): LodSplitSummary {
  const split = classifyMeshesByLod(asset.meshes);
  return {
    slot: asset.label,
    LOD0: split.LOD0.length,
    DT: split.DT.length,
    other: split.other.length,
  };
}

export function getSelectedCameras(fixture: VisualReviewFixture, groups: CameraGroupId[]): string[] {
  const seen = new Set<string>();
  const cameras: string[] = [];
  for (const group of groups) {
    for (const camera of fixture.cameraRig[group]) {
      if (!seen.has(camera)) {
        seen.add(camera);
        cameras.push(camera);
      }
    }
  }
  return cameras;
}

export function buildPassRuns(
  fixture: VisualReviewFixture,
  options: VisualReviewOptions,
): VisualPassRun[] {
  const cameras = getSelectedCameras(fixture, options.cameraGroups);
  const aSplit = classifyMeshesByLod(fixture.baseline.meshes);
  const bSplit = classifyMeshesByLod(fixture.variant.meshes);

  return visualPassPresets.map((preset) => {
    const availability = getPresetAvailability(preset, aSplit, bSplit, cameras.length);
    const shotNames = availability.status === "run"
      ? cameras.map((camera) => composeShotName(camera, preset))
      : [];
    const sceneBackup =
      options.saveSceneBackup && preset.id === "wb_lod0" && availability.status === "run"
        ? `${fixture.variant.name.replace(/\.(ma|mb|fbx)$/i, "")}.ma`
        : "";

    return {
      presetId: preset.id,
      label: preset.label,
      status: availability.status,
      reason: availability.reason,
      cameraCount: cameras.length,
      imageCount: shotNames.length,
      shotNames,
      sceneBackup,
    };
  });
}

export function buildReviewFindings(
  fixture: VisualReviewFixture,
  passRuns: VisualPassRun[],
): ReviewFinding[] {
  const findings: ReviewFinding[] = [];
  const skipped = passRuns.filter((run) => run.status === "skipped");

  if (fixture.baseline.unit !== fixture.variant.unit) {
    findings.push({
      id: "unit-mismatch",
      severity: "error",
      gate: "Blocked",
      channel: "unit",
      title: "Baseline and variant use different linear units",
      detail: `A is authored in ${fixture.baseline.unit}, B is authored in ${fixture.variant.unit}. Overlay captures can hide scale conversion errors.`,
      evidence: "Slot A defines the baseline unit before slot B is imported.",
      suggestedAction: "Re-export B in the baseline unit before accepting visual comparison.",
    });
  }

  for (const run of skipped) {
    findings.push({
      id: `skip-${run.presetId}`,
      severity: run.presetId === "solo_b" ? "warning" : "error",
      gate: run.presetId === "solo_b" ? "Review" : "Blocked",
      channel: "lod",
      title: `${run.label} was skipped`,
      detail: run.reason,
      evidence: "Preset builders return false when the required LOD bucket is empty.",
      suggestedAction: "Restore missing LOD0 or DT mesh naming before rerunning the capture pass.",
    });
  }

  if (fixture.variant.unresolvedTextures.length > 0) {
    findings.push({
      id: "missing-textures",
      severity: "warning",
      gate: "Review",
      channel: "texture",
      title: "Variant has unresolved texture references",
      detail: `${fixture.variant.unresolvedTextures.length} file node(s) still need sourceimages remap.`,
      evidence: fixture.variant.unresolvedTextures.join(", "),
      suggestedAction: "Resolve texture basenames under the asset project or package the missing sourceimages files.",
    });
  }

  if (fixture.comparison.silhouetteDeltaPercent >= 12) {
    findings.push({
      id: "silhouette-delta",
      severity: "error",
      gate: "Blocked",
      channel: "silhouette",
      title: "Silhouette delta exceeds block threshold",
      detail: `${fixture.comparison.silhouetteDeltaPercent.toFixed(1)}% delta against a 12.0% block threshold.`,
      evidence: "Red / Blue overlay pass on LOD0 cameras.",
      suggestedAction: "Ask the artist to verify deleted parts, pivot offsets, or wrong variant source.",
    });
  } else if (fixture.comparison.silhouetteDeltaPercent >= 6) {
    findings.push({
      id: "silhouette-delta",
      severity: "warning",
      gate: "Review",
      channel: "silhouette",
      title: "Silhouette delta needs reviewer signoff",
      detail: `${fixture.comparison.silhouetteDeltaPercent.toFixed(1)}% delta against a 6.0% review threshold.`,
      evidence: "Red / Blue overlay pass on LOD0 cameras.",
      suggestedAction: "Compare front and side cameras before approving the variant.",
    });
  }

  if (fixture.comparison.bboxDeltaPercent >= 5) {
    findings.push({
      id: "bbox-delta",
      severity: "warning",
      gate: "Review",
      channel: "silhouette",
      title: "Bounding box drift needs inspection",
      detail: `${fixture.comparison.bboxDeltaPercent.toFixed(1)}% bbox delta against a 5.0% review threshold.`,
      evidence: "Default camera group coverage.",
      suggestedAction: "Check scale, root transform, and exported unit metadata.",
    });
  }

  if (fixture.comparison.materialDriftScore >= 0.22) {
    findings.push({
      id: "material-drift",
      severity: "warning",
      gate: "Review",
      channel: "material",
      title: "Material assignment changed",
      detail: `Material drift score is ${fixture.comparison.materialDriftScore.toFixed(2)} with A=${fixture.baseline.materialCount}, B=${fixture.variant.materialCount}.`,
      evidence: "White / Blue pass and original shading-group snapshot.",
      suggestedAction: "Check merged shader slots and missing material IDs before publish.",
    });
  }

  if (fixture.comparison.cameraCoverageScore < 0.9) {
    findings.push({
      id: "camera-coverage",
      severity: "warning",
      gate: "Review",
      channel: "camera",
      title: "Camera coverage is below review target",
      detail: `${Math.round(fixture.comparison.cameraCoverageScore * 100)}% coverage against a 90% target.`,
      evidence: "Camera_Group fuzzy discovery or cam_* fallback.",
      suggestedAction: "Add missing detail cameras or confirm that the reduced rig is intentional.",
    });
  }

  if (findings.length === 0) {
    findings.push({
      id: "review-clean",
      severity: "info",
      gate: "Ready",
      channel: "package",
      title: "All configured review signals passed",
      detail: fixture.comparison.reviewerNote,
      evidence: "Every required preset ran and signal thresholds stayed within ready range.",
      suggestedAction: "Package report JSON, screenshots, and the white-blue scene backup.",
    });
  }

  return findings;
}

export function buildVisualDiffSignals(fixture: VisualReviewFixture): VisualDiffSignal[] {
  return [
    {
      id: "silhouette",
      label: "Silhouette Delta",
      value: fixture.comparison.silhouetteDeltaPercent,
      unit: "%",
      direction: "above",
      reviewThreshold: 6,
      blockThreshold: 12,
      fillPercent: normalizeAbove(fixture.comparison.silhouetteDeltaPercent, 12),
      gate: gateAbove(fixture.comparison.silhouetteDeltaPercent, 6, 12),
      evidence: "LOD0 red / blue overlay cameras.",
      relatedPasses: ["rb_lod0", "wb_lod0"],
    },
    {
      id: "bbox",
      label: "Bounding Box Delta",
      value: fixture.comparison.bboxDeltaPercent,
      unit: "%",
      direction: "above",
      reviewThreshold: 5,
      blockThreshold: 9,
      fillPercent: normalizeAbove(fixture.comparison.bboxDeltaPercent, 9),
      gate: gateAbove(fixture.comparison.bboxDeltaPercent, 5, 9),
      evidence: "Default camera group and root transform check.",
      relatedPasses: ["rb_lod0", "wb_lod0"],
    },
    {
      id: "material",
      label: "Material Drift",
      value: fixture.comparison.materialDriftScore,
      unit: "score",
      direction: "above",
      reviewThreshold: 0.22,
      blockThreshold: 0.45,
      fillPercent: normalizeAbove(fixture.comparison.materialDriftScore, 0.45),
      gate: gateAbove(fixture.comparison.materialDriftScore, 0.22, 0.45),
      evidence: "White / blue material pass and original shading-group snapshot.",
      relatedPasses: ["wb_lod0", "wb_dt", "solo_b"],
    },
    {
      id: "cameraCoverage",
      label: "Camera Coverage",
      value: fixture.comparison.cameraCoverageScore * 100,
      unit: "%",
      direction: "below",
      reviewThreshold: 90,
      blockThreshold: 75,
      fillPercent: Math.max(0, Math.min(100, fixture.comparison.cameraCoverageScore * 100)),
      gate: gateBelow(fixture.comparison.cameraCoverageScore * 100, 90, 75),
      evidence: "Camera_Group fuzzy discovery or legacy cam_* fallback.",
      relatedPasses: ["rb_lod0", "wb_lod0", "rb_dt", "wb_dt", "solo_b"],
    },
  ];
}

export function buildVisualPassDrilldowns(
  fixture: VisualReviewFixture,
  options: VisualReviewOptions,
  passRuns: VisualPassRun[],
  diffSignals: VisualDiffSignal[],
  findings: ReviewFinding[],
): VisualPassDrilldown[] {
  const cameras = getSelectedCameras(fixture, options.cameraGroups);

  return passRuns.map((run) => {
    const preset = visualPassPresets.find((item) => item.id === run.presetId) ?? visualPassPresets[0];
    const relatedSignals = diffSignals
      .filter((signal) => signal.relatedPasses.includes(run.presetId))
      .map<VisualPassSignalLink>((signal) => ({
        signalId: signal.id,
        label: signal.label,
        gate: signal.gate,
        value: signal.value,
        unit: signal.unit,
        evidence: signal.evidence,
      }));
    const relatedFindings = findings
      .filter((finding) => getRelatedPassIdsForFinding(finding).includes(run.presetId))
      .map<VisualPassFindingLink>((finding) => ({
        findingId: finding.id,
        severity: finding.severity,
        gate: finding.gate,
        channel: finding.channel,
        title: finding.title,
        evidence: finding.evidence,
        suggestedAction: finding.suggestedAction,
      }));
    const linkedSignalIds = relatedSignals.map((signal) => signal.signalId);
    const shots = run.shotNames.map<VisualPassShotLink>((outputName, index) => {
      const cameraName = cameras[index] ?? outputName;
      return {
        cameraName,
        cameraGroup: getCameraGroupForName(fixture, cameraName),
        outputName,
        linkedSignalIds,
      };
    });
    const nextAction =
      relatedFindings.find((finding) => finding.severity !== "info")?.suggestedAction
      ?? (run.status === "skipped" ? run.reason : "No blocking action. Keep this pass in the evidence package.");

    return {
      presetId: run.presetId,
      label: run.label,
      status: run.status,
      gate: highestGate([
        ...relatedSignals.map((signal) => signal.gate),
        ...relatedFindings.map((finding) => finding.gate),
      ]),
      reason: run.reason,
      materialContract: preset.materialContract,
      outputPattern: preset.lodLabel
        ? `<camera>_${preset.lodLabel}_${preset.kindLabel}.png`
        : `<camera>_${preset.kindLabel}.png`,
      cameraCount: run.cameraCount,
      imageCount: run.imageCount,
      shots,
      relatedSignals,
      relatedFindings,
      nextAction,
    };
  });
}

export function getReviewGate(findings: ReviewFinding[]): ReviewGate {
  if (findings.some((finding) => finding.gate === "Blocked")) {
    return "Blocked";
  }
  if (findings.some((finding) => finding.gate === "Review")) {
    return "Review";
  }
  return "Ready";
}

export function buildReviewQueue(
  findings: ReviewFinding[],
  stateOverrides: ReviewQueueStateOverrides = {},
): ReviewQueueItem[] {
  return findings
    .filter((finding) => finding.severity !== "info")
    .map((finding, index) => {
      const id = `review-action-${index + 1}`;
      const owner = getQueueOwnerForFinding(finding);
      const relatedPasses = getRelatedPassIdsForFinding(finding);
      return {
        id,
        title: finding.suggestedAction,
        owner,
        state: stateOverrides[id] ?? (finding.gate === "Blocked" ? "blocked" : "todo"),
        sourceFindingId: finding.id,
        sourceFindingTitle: finding.title,
        gate: finding.gate,
        severity: finding.severity,
        channel: finding.channel,
        priority: getQueuePriority(finding),
        evidence: finding.evidence,
        relatedPasses,
        nextCheck: buildQueueNextCheck(finding, relatedPasses),
        handoffNote: buildQueueHandoffNote(finding, owner, relatedPasses),
      };
    });
}

export function buildReviewQueueSummary(items: ReviewQueueItem[]): ReviewQueueSummary {
  return {
    total: items.length,
    todo: items.filter((item) => item.state === "todo").length,
    blocked: items.filter((item) => item.state === "blocked").length,
    ready: items.filter((item) => item.state === "ready").length,
    artist: items.filter((item) => item.owner === "artist").length,
    ta: items.filter((item) => item.owner === "ta").length,
    reviewer: items.filter((item) => item.owner === "reviewer").length,
  };
}

export function buildReviewHandoffPacket(
  fixture: VisualReviewFixture,
  gate: ReviewGate,
  reviewQueue: ReviewQueueItem[],
  reviewQueueSummary: ReviewQueueSummary,
  evidencePackage: VisualEvidencePackage,
  deliveryOverrides: HandoffDeliveryOverrides = {},
): ReviewHandoffPacket {
  const ownerOrder: ReviewQueueOwner[] = ["artist", "ta", "reviewer"];
  const sections = ownerOrder.map<ReviewHandoffSection>((owner) => {
    const items = reviewQueue
      .filter((item) => item.owner === owner)
      .sort((a, b) => b.priority - a.priority)
      .map<ReviewHandoffItem>((item) => ({
        queueId: item.id,
        sourceFindingId: item.sourceFindingId,
        sourceFindingTitle: item.sourceFindingTitle,
        owner: item.owner,
        state: item.state,
        gate: item.gate,
        severity: item.severity,
        priority: item.priority,
        evidence: item.evidence,
        relatedPasses: item.relatedPasses,
        nextCheck: item.nextCheck,
        handoffNote: item.handoffNote,
      }));
    const blocked = items.filter((item) => item.state === "blocked").length;
    const todo = items.filter((item) => item.state === "todo").length;
    const ready = items.filter((item) => item.state === "ready").length;
    const delivery = buildHandoffDeliveryReceipt(owner, items.length, deliveryOverrides[owner]);
    const section = {
      owner,
      ownerLabel: getQueueOwnerLabel(owner),
      total: items.length,
      blocked,
      todo,
      ready,
      gate: highestGate(items.map((item) => item.gate)),
      topPriority: items[0]?.priority ?? 0,
      items,
      delivery,
      messagePreview: "",
    };
    return {
      ...section,
      messagePreview: buildHandoffSectionMessage(fixture, section, evidencePackage),
    };
  });

  return {
    packetVersion: "visual-review-handoff@0.2.0",
    fixtureId: fixture.id,
    fixtureName: fixture.name,
    gate,
    ownerOrder,
    queueSummary: reviewQueueSummary,
    deliverySummary: buildHandoffDeliverySummary(sections),
    evidencePackage,
    sections,
    notificationPreview: buildHandoffPacketPreview(fixture, gate, sections, evidencePackage),
  };
}

export function buildVisualReleaseGate(
  fixture: VisualReviewFixture,
  passRuns: VisualPassRun[],
  diffSignals: VisualDiffSignal[],
  reviewQueueSummary: ReviewQueueSummary,
  handoffPacket: ReviewHandoffPacket,
  decisionState: ReviewDecisionState,
  evidencePackage: VisualEvidencePackage,
): VisualReleaseGate {
  const skippedRequired = passRuns.filter((run) => (
    run.status === "skipped" && run.presetId !== "solo_b"
  ));
  const skippedOptional = passRuns.filter((run) => (
    run.status === "skipped" && run.presetId === "solo_b"
  ));
  const captureGate: ReviewGate =
    skippedRequired.length > 0
      ? "Blocked"
      : skippedOptional.length > 0
        ? "Review"
        : "Ready";

  const signalGate = highestGate(diffSignals.map((signal) => signal.gate));
  const queueGate: ReviewGate =
    reviewQueueSummary.blocked > 0
      ? "Blocked"
      : reviewQueueSummary.todo > 0
        ? "Review"
        : "Ready";
  const actionableDeliveries = handoffPacket.sections
    .filter((section) => section.total > 0)
    .map((section) => section.delivery);
  const handoffGate: ReviewGate =
    actionableDeliveries.some((delivery) => delivery.state === "failed")
      ? "Blocked"
      : actionableDeliveries.every((delivery) => delivery.state === "acknowledged")
        ? "Ready"
        : "Review";
  const decisionGate: ReviewGate =
    decisionState === "accepted" ? "Ready" : decisionState === "needs_fix" ? "Blocked" : "Review";
  const evidenceGate: ReviewGate =
    evidencePackage.imageCount === 0
      ? "Blocked"
      : evidencePackage.sceneBackup || !passRuns.some((run) => run.sceneBackup === "")
        ? "Ready"
        : "Review";

  const criteria: VisualReleaseCriterion[] = [
    {
      id: "capture_contract",
      label: "Capture Contract",
      gate: captureGate,
      required: true,
      summary: `${passRuns.filter((run) => run.status === "run").length} pass run / ${passRuns.filter((run) => run.status === "skipped").length} skipped`,
      evidence: skippedRequired.map((run) => `${run.label}: ${run.reason}`).join("; ") || "All required capture passes produced shots.",
      nextAction: captureGate === "Blocked" ? "Restore skipped required pass input and rerun capture." : "Keep pass outputs in the release evidence package.",
    },
    {
      id: "signal_thresholds",
      label: "Signal Thresholds",
      gate: signalGate,
      required: true,
      summary: `${diffSignals.filter((signal) => signal.gate === "Blocked").length} blocked / ${diffSignals.filter((signal) => signal.gate === "Review").length} review signals`,
      evidence: diffSignals.map((signal) => `${signal.label}=${formatReleaseSignalValue(signal)} ${signal.gate}`).join("; "),
      nextAction: signalGate === "Ready" ? "No signal follow-up required." : "Resolve blocked/review signals before release candidate signoff.",
    },
    {
      id: "queue_resolution",
      label: "Queue Resolution",
      gate: queueGate,
      required: true,
      summary: `${reviewQueueSummary.blocked} blocked / ${reviewQueueSummary.todo} todo / ${reviewQueueSummary.ready} ready`,
      evidence: `${reviewQueueSummary.artist} artist, ${reviewQueueSummary.ta} TA, ${reviewQueueSummary.reviewer} reviewer queue items.`,
      nextAction: queueGate === "Ready" ? "Queue is resolved." : "Move blocked and todo queue items to ready before release.",
    },
    {
      id: "handoff_ack",
      label: "Handoff Ack",
      gate: handoffGate,
      required: true,
      summary: `${handoffPacket.deliverySummary.acknowledged} acknowledged / ${handoffPacket.deliverySummary.pending} draft / ${handoffPacket.deliverySummary.failed} failed`,
      evidence: handoffPacket.sections.map((section) => `${section.ownerLabel}:${section.delivery.state}`).join("; "),
      nextAction: handoffGate === "Ready" ? "All owners acknowledged handoff." : "Finish owner acknowledgement before release.",
    },
    {
      id: "review_decision",
      label: "Review Decision",
      gate: decisionGate,
      required: true,
      summary: decisionState,
      evidence: "Human decision state from the AI review draft panel.",
      nextAction: decisionGate === "Ready" ? "Reviewer accepted the current package." : "Reviewer must accept the package after fixes are resolved.",
    },
    {
      id: "evidence_package",
      label: "Evidence Package",
      gate: evidenceGate,
      required: true,
      summary: `${evidencePackage.imageCount} images, overview ${evidencePackage.htmlOverview ? "ready" : "missing"}`,
      evidence: `${evidencePackage.outputDir}; ${evidencePackage.sceneBackup || "scene backup disabled"}`,
      nextAction: evidenceGate === "Ready" ? "Evidence package can be archived." : "Complete screenshots, overview HTML, and scene backup before release.",
    },
  ];
  const gate = highestGate(criteria.map((criterion) => criterion.gate));
  const decision = getReleaseDecision(gate);
  const blockers = criteria
    .filter((criterion) => criterion.gate === "Blocked")
    .map((criterion) => criterion.label);

  return {
    reportVersion: "visual-review-release-gate@0.1.0",
    fixtureId: fixture.id,
    fixtureName: fixture.name,
    gate,
    decision,
    criteria,
    ready: criteria.filter((criterion) => criterion.gate === "Ready").length,
    review: criteria.filter((criterion) => criterion.gate === "Review").length,
    blocked: criteria.filter((criterion) => criterion.gate === "Blocked").length,
    blockers,
    publishChecklist: buildReleaseChecklist(criteria),
    releaseNotePreview: buildReleaseNotePreview(fixture, decision, gate, criteria, evidencePackage),
  };
}

export function buildAiReviewDraft(
  fixture: VisualReviewFixture,
  findings: ReviewFinding[],
  gate: ReviewGate,
): string {
  const blockers = findings.filter((finding) => finding.gate === "Blocked");
  const reviews = findings.filter((finding) => finding.gate === "Review");

  if (gate === "Ready") {
    return [
      `${fixture.name}: visual review is ready.`,
      "All configured camera passes ran successfully.",
      `Silhouette delta ${fixture.comparison.silhouetteDeltaPercent.toFixed(1)}%, material drift ${fixture.comparison.materialDriftScore.toFixed(2)}.`,
      "Package the screenshots, report JSON, and scene backup for reviewer archive.",
    ].join("\n");
  }

  const lines = [
    `${fixture.name}: visual review is ${gate.toLowerCase()}.`,
    `Primary note: ${fixture.comparison.reviewerNote}`,
  ];
  if (blockers.length > 0) {
    lines.push(`Blockers: ${blockers.map((finding) => finding.title).join("; ")}.`);
  }
  if (reviews.length > 0) {
    lines.push(`Needs review: ${reviews.map((finding) => finding.title).join("; ")}.`);
  }
  lines.push("AI draft only summarizes findings. Gate comes from deterministic pass and threshold checks.");
  return lines.join("\n");
}

export function buildNotificationPreview(report: Pick<VisualReviewReport, "fixtureName" | "gate" | "evidencePackage" | "findings">): string {
  const topFindings = report.findings
    .filter((finding) => finding.severity !== "info")
    .slice(0, 3)
    .map((finding) => finding.title)
    .join("; ");
  return [
    `[Visual Review] ${report.fixtureName}`,
    `Gate: ${report.gate}`,
    `Images: ${report.evidencePackage.imageCount}`,
    `Output: ${report.evidencePackage.outputDir}`,
    topFindings ? `Issues: ${topFindings}` : "Issues: none",
  ].join("\n");
}

export function buildVisualReviewReport(
  fixture: VisualReviewFixture,
  options: VisualReviewOptions,
  decisionState: ReviewDecisionState,
  editedDraft?: string,
  reviewAudit: VisualReviewAuditEvent[] = [],
  queueStateOverrides: ReviewQueueStateOverrides = {},
  handoffDeliveryOverrides: HandoffDeliveryOverrides = {},
  fixtureEditSummary: VisualFixtureEditSummary = getVisualFixtureEditSummary(fixture, fixture),
): VisualReviewReport {
  const passRuns = buildPassRuns(fixture, options);
  const lodSplit = [getLodSplit(fixture.baseline), getLodSplit(fixture.variant)];
  const diffSignals = buildVisualDiffSignals(fixture);
  const findings = buildReviewFindings(fixture, passRuns);
  const passDrilldowns = buildVisualPassDrilldowns(fixture, options, passRuns, diffSignals, findings);
  const gate = getReviewGate(findings);
  const reviewQueue = buildReviewQueue(findings, queueStateOverrides);
  const reviewQueueSummary = buildReviewQueueSummary(reviewQueue);
  const sceneBackup = passRuns.find((run) => run.sceneBackup)?.sceneBackup ?? "";
  const outputDir = `${fixture.variant.sourcePath.replace(/[/\\][^/\\]+$/, "")}/output/20260730-1`;
  const evidencePackage = {
    outputDir,
    sceneBackup,
    imageCount: passRuns.reduce((sum, run) => sum + run.imageCount, 0),
    htmlOverview: `${outputDir}/overview.html`,
  };
  const baseReport = {
    fixtureName: fixture.name,
    gate,
    evidencePackage,
    findings,
  };
  const handoffPacket = buildReviewHandoffPacket(
    fixture,
    gate,
    reviewQueue,
    reviewQueueSummary,
    evidencePackage,
    handoffDeliveryOverrides,
  );
  const releaseGate = buildVisualReleaseGate(
    fixture,
    passRuns,
    diffSignals,
    reviewQueueSummary,
    handoffPacket,
    decisionState,
    evidencePackage,
  );

  return {
    reportVersion: "visual-review-report@0.8.0",
    fixtureId: fixture.id,
    fixtureName: fixture.name,
    gate,
    options,
    fixtureSnapshot: fixture,
    fixtureEditSummary,
    lodSplit,
    passRuns,
    diffSignals,
    passDrilldowns,
    findings,
    reviewQueue,
    reviewQueueSummary,
    handoffPacket,
    releaseGate,
    reviewAudit,
    aiReviewDraft: editedDraft ?? buildAiReviewDraft(fixture, findings, gate),
    decisionState,
    notificationPreview: options.notifyEnabled ? buildNotificationPreview(baseReport) : "Notification disabled.",
    evidencePackage,
  };
}

export function createVisualReviewAuditEvent(
  revision: number,
  action: VisualReviewAuditAction,
  fixture: VisualReviewFixture,
  gate: ReviewGate,
  fromDecision: ReviewDecisionState,
  toDecision: ReviewDecisionState,
  draft: string,
  note: string,
): VisualReviewAuditEvent {
  return {
    revision,
    action,
    fixtureId: fixture.id,
    fixtureName: fixture.name,
    gate,
    fromDecision,
    toDecision,
    draftExcerpt: draft.slice(0, 160),
    note,
  };
}

export function buildBatchReviewReport(
  fixtures: VisualReviewFixture[],
  options: VisualReviewOptions,
  fixtureEditSummaries: Partial<Record<string, VisualFixtureEditSummary>> = {},
): VisualBatchReport {
  const items = fixtures.map<VisualBatchItem>((fixture) => {
    const report = buildVisualReviewReport(
      fixture,
      options,
      "pending",
      undefined,
      [],
      {},
      {},
      fixtureEditSummaries[fixture.id],
    );
    const passesRun = report.passRuns.filter((run) => run.status === "run").length;
    const passesSkipped = report.passRuns.length - passesRun;
    const captureStatus = report.evidencePackage.imageCount > 0 ? "ok" : "failed";
    const reason = captureStatus === "failed"
      ? "no images produced, no cameras or all presets skipped"
      : `capture ok, review gate ${report.gate}`;
    const primarySignal = getPrimaryBatchSignal(report.diffSignals);
    const topFindings = report.findings.slice(0, 3).map<VisualBatchFindingSummary>((finding) => ({
      findingId: finding.id,
      severity: finding.severity,
      gate: finding.gate,
      channel: finding.channel,
      title: finding.title,
    }));
    const firstSkippedRun = report.passRuns.find((run) => run.status === "skipped");
    const firstSkippedPass = firstSkippedRun
      ? {
        presetId: firstSkippedRun.presetId,
        label: firstSkippedRun.label,
        reason: firstSkippedRun.reason,
      }
      : null;

    return {
      fixtureId: fixture.id,
      name: fixture.name,
      captureStatus,
      reviewGate: report.gate,
      reason,
      outputDir: report.evidencePackage.outputDir,
      imageCount: report.evidencePackage.imageCount,
      passesRun,
      passesSkipped,
      sceneBackup: report.evidencePackage.sceneBackup,
      htmlOverview: report.evidencePackage.htmlOverview,
      primarySignal,
      topFindings,
      firstSkippedPass,
      queueBlocked: report.reviewQueueSummary.blocked,
      queueTodo: report.reviewQueueSummary.todo,
      queueReady: report.reviewQueueSummary.ready,
      handoffOwners: report.handoffPacket.sections
        .filter((section) => section.total > 0)
        .map((section) => section.owner),
      handoffPreview: report.handoffPacket.notificationPreview,
      handoffDelivery: report.handoffPacket.sections.map((section) => section.delivery),
      releaseGate: report.releaseGate.gate,
      releaseDecision: report.releaseGate.decision,
      releaseBlockers: report.releaseGate.blocked,
      releasePreview: report.releaseGate.releaseNotePreview,
      fixtureEditSummary: report.fixtureEditSummary,
      reportPreview: buildBatchItemReportPreview(
        report,
        passesRun,
        passesSkipped,
        primarySignal,
        firstSkippedPass,
        topFindings,
      ),
    };
  });

  const success = items.filter((item) => item.captureStatus === "ok").length;
  const failed = items.length - success;
  const ready = items.filter((item) => item.reviewGate === "Ready").length;
  const review = items.filter((item) => item.reviewGate === "Review").length;
  const blocked = items.filter((item) => item.reviewGate === "Blocked").length;
  const sampleOutputDirs = items
    .filter((item) => item.outputDir)
    .slice(0, 3)
    .map((item) => item.outputDir);

  return {
    reportVersion: "visual-batch-review@0.7.0",
    success,
    failed,
    ready,
    review,
    blocked,
    sampleOutputDirs,
    items,
    notificationPreview: buildBatchNotificationPreview(items, success, failed),
  };
}

function getRelatedPassIdsForFinding(finding: ReviewFinding): PassPresetId[] {
  if (finding.id.startsWith("skip-")) {
    const presetId = finding.id.slice("skip-".length);
    if (isPassPresetId(presetId)) {
      return [presetId];
    }
  }

  switch (finding.channel) {
    case "unit":
      return ["rb_lod0", "wb_lod0", "rb_dt", "wb_dt"];
    case "lod":
      return ["rb_lod0", "wb_lod0", "rb_dt", "wb_dt", "solo_b"];
    case "material":
    case "texture":
      return ["wb_lod0", "wb_dt", "solo_b"];
    case "silhouette":
      return ["rb_lod0", "wb_lod0"];
    case "camera":
    case "package":
      return ["rb_lod0", "wb_lod0", "rb_dt", "wb_dt", "solo_b"];
  }
}

function getQueueOwnerForFinding(finding: ReviewFinding): ReviewQueueOwner {
  switch (finding.channel) {
    case "lod":
    case "material":
    case "texture":
      return "artist";
    case "unit":
    case "camera":
      return "ta";
    case "silhouette":
    case "package":
      return "reviewer";
  }
}

function getQueueOwnerLabel(owner: ReviewQueueOwner): string {
  if (owner === "artist") {
    return "Artist";
  }
  if (owner === "ta") {
    return "TA";
  }
  return "Reviewer";
}

function buildHandoffDeliveryReceipt(
  owner: ReviewQueueOwner,
  itemCount: number,
  override?: HandoffDeliveryOverride,
): HandoffDeliveryReceipt {
  const state = override?.state ?? (itemCount > 0 ? "draft" : "not_required");
  const attempts = override?.attempts ?? (state === "not_required" || state === "draft" ? 0 : 1);
  return {
    owner,
    state,
    channel: owner === "reviewer" ? "review_board" : "wecom",
    recipient: getHandoffRecipient(owner),
    attempts,
    ackRequired: itemCount > 0,
    lastEvent: override?.lastEvent ?? buildDefaultDeliveryEvent(owner, state),
    nextAction: buildDeliveryNextAction(owner, state),
  };
}

function getHandoffRecipient(owner: ReviewQueueOwner): string {
  if (owner === "artist") {
    return "weapon_artist_group";
  }
  if (owner === "ta") {
    return "tool_ta_triage";
  }
  return "lead_reviewer_board";
}

function buildDefaultDeliveryEvent(owner: ReviewQueueOwner, state: HandoffDeliveryState): string {
  const label = getQueueOwnerLabel(owner);
  switch (state) {
    case "not_required":
      return `${label} handoff has no actionable item.`;
    case "draft":
      return `${label} handoff packet is prepared but not sent.`;
    case "sent":
      return `${label} handoff packet was sent to the configured channel.`;
    case "failed":
      return `${label} handoff delivery failed and needs retry.`;
    case "read":
      return `${label} recipient opened the packet.`;
    case "acknowledged":
      return `${label} acknowledged the handoff.`;
  }
}

function buildDeliveryNextAction(owner: ReviewQueueOwner, state: HandoffDeliveryState): string {
  const label = getQueueOwnerLabel(owner);
  switch (state) {
    case "not_required":
      return "No delivery action required.";
    case "draft":
      return `Send ${label} packet.`;
    case "sent":
      return `Wait for ${label} read receipt.`;
    case "failed":
      return `Retry ${label} delivery or switch channel.`;
    case "read":
      return `Ask ${label} to acknowledge ownership.`;
    case "acknowledged":
      return `${label} ownership is confirmed.`;
  }
}

function buildHandoffDeliverySummary(sections: ReviewHandoffSection[]): HandoffDeliverySummary {
  return {
    totalOwners: sections.length,
    pending: sections.filter((section) => section.delivery.state === "draft").length,
    sent: sections.filter((section) => section.delivery.state === "sent").length,
    failed: sections.filter((section) => section.delivery.state === "failed").length,
    read: sections.filter((section) => section.delivery.state === "read").length,
    acknowledged: sections.filter((section) => section.delivery.state === "acknowledged").length,
    notRequired: sections.filter((section) => section.delivery.state === "not_required").length,
  };
}

function getQueuePriority(finding: ReviewFinding): number {
  const basePriority = finding.gate === "Blocked" ? 90 : finding.gate === "Review" ? 60 : 20;
  const channelBoost: Record<ReviewFinding["channel"], number> = {
    unit: 9,
    lod: 8,
    silhouette: 7,
    material: 5,
    texture: 4,
    camera: 3,
    package: 1,
  };
  return basePriority + channelBoost[finding.channel];
}

function getReleaseDecision(gate: ReviewGate): VisualReleaseDecision {
  if (gate === "Ready") {
    return "release_candidate";
  }
  if (gate === "Review") {
    return "hold_for_review";
  }
  return "blocked_from_release";
}

function formatReleaseSignalValue(signal: VisualDiffSignal): string {
  return signal.unit === "%" ? `${signal.value.toFixed(1)}%` : signal.value.toFixed(2);
}

function buildReleaseChecklist(criteria: VisualReleaseCriterion[]): string[] {
  return criteria.map((criterion) => (
    `[${criterion.gate}] ${criterion.label}: ${criterion.nextAction}`
  ));
}

function buildReleaseNotePreview(
  fixture: VisualReviewFixture,
  decision: VisualReleaseDecision,
  gate: ReviewGate,
  criteria: VisualReleaseCriterion[],
  evidencePackage: VisualEvidencePackage,
): string {
  const blockers = criteria
    .filter((criterion) => criterion.gate === "Blocked")
    .map((criterion) => criterion.label)
    .join("; ");
  const reviews = criteria
    .filter((criterion) => criterion.gate === "Review")
    .map((criterion) => criterion.label)
    .join("; ");

  return [
    `[Visual Release Gate] ${fixture.name}`,
    `Decision: ${decision}`,
    `Gate: ${gate}`,
    blockers ? `Blockers: ${blockers}` : "Blockers: none",
    reviews ? `Needs review: ${reviews}` : "Needs review: none",
    `Evidence: ${evidencePackage.outputDir}`,
  ].join("\n");
}

function buildHandoffSectionMessage(
  fixture: VisualReviewFixture,
  section: ReviewHandoffSection,
  evidencePackage: VisualEvidencePackage,
): string {
  const topItems = section.items.slice(0, 4).map((item) => (
    `P${item.priority} ${item.sourceFindingTitle}: ${item.nextCheck}`
  ));
  return [
    `[${section.ownerLabel} Handoff] ${fixture.name}`,
    `Gate: ${section.gate}`,
    `Queue: ${section.blocked} blocked / ${section.todo} todo / ${section.ready} ready`,
    `Delivery: ${section.delivery.state}, attempts ${section.delivery.attempts}, ${section.delivery.recipient}`,
    `Output: ${evidencePackage.outputDir}`,
    topItems.length > 0 ? `Actions:\n${topItems.map((item) => `- ${item}`).join("\n")}` : "Actions: none",
  ].join("\n");
}

function buildHandoffPacketPreview(
  fixture: VisualReviewFixture,
  gate: ReviewGate,
  sections: ReviewHandoffSection[],
  evidencePackage: VisualEvidencePackage,
): string {
  const ownerLine = sections
    .filter((section) => section.total > 0)
    .map((section) => `${section.ownerLabel} ${section.blocked}/${section.todo}/${section.ready}`)
    .join(", ");
  const deliveryLine = sections
    .filter((section) => section.total > 0)
    .map((section) => `${section.ownerLabel}:${section.delivery.state}`)
    .join(", ");

  return [
    `[Visual Review Handoff] ${fixture.name}`,
    `Gate: ${gate}`,
    `Owner packets: ${ownerLine || "none"}`,
    `Delivery: ${deliveryLine || "none"}`,
    `Images: ${evidencePackage.imageCount}`,
    `Overview: ${evidencePackage.htmlOverview}`,
  ].join("\n");
}

function buildQueueNextCheck(finding: ReviewFinding, relatedPasses: PassPresetId[]): string {
  const passLabel = relatedPasses
    .map((passId) => visualPassPresets.find((preset) => preset.id === passId)?.shortLabel ?? passId)
    .join(" / ");

  switch (finding.channel) {
    case "unit":
      return `Re-import both slots, confirm scene unit, then rerun ${passLabel}.`;
    case "lod":
      return `Restore missing bucket naming, then rerun ${passLabel || "affected passes"}.`;
    case "material":
      return `Compare shading group membership and rerun ${passLabel}.`;
    case "texture":
      return "Resolve sourceimages paths, reload file nodes, then refresh the white/blue pass.";
    case "silhouette":
      return `Open front and side captures from ${passLabel}, then check pivot and deleted mesh risk.`;
    case "camera":
      return "Review camera discovery, add missing detail cameras, then regenerate shot manifest.";
    case "package":
      return "Archive report JSON, screenshots, scene backup, and overview HTML.";
  }
}

function buildQueueHandoffNote(
  finding: ReviewFinding,
  owner: ReviewQueueOwner,
  relatedPasses: PassPresetId[],
): string {
  const passes = relatedPasses.length > 0 ? relatedPasses.join(", ") : "none";
  return `${owner} owns ${finding.id}. Evidence: ${finding.evidence}. Related passes: ${passes}.`;
}

function isPassPresetId(value: string): value is PassPresetId {
  return visualPassPresets.some((preset) => preset.id === value);
}

function getCameraGroupForName(fixture: VisualReviewFixture, cameraName: string): CameraGroupId {
  return fixture.cameraRig.detail.includes(cameraName) ? "detail" : "basic";
}

function gateRank(gate: ReviewGate): number {
  if (gate === "Blocked") {
    return 2;
  }
  if (gate === "Review") {
    return 1;
  }
  return 0;
}

function highestGate(gates: ReviewGate[]): ReviewGate {
  if (gates.some((gate) => gate === "Blocked")) {
    return "Blocked";
  }
  if (gates.some((gate) => gate === "Review")) {
    return "Review";
  }
  return "Ready";
}

function getPrimaryBatchSignal(signals: VisualDiffSignal[]): VisualBatchSignalSummary | null {
  const signal = [...signals].sort((a, b) => {
    const gateDelta = gateRank(b.gate) - gateRank(a.gate);
    if (gateDelta !== 0) {
      return gateDelta;
    }
    return b.fillPercent - a.fillPercent;
  })[0];

  if (!signal) {
    return null;
  }

  return {
    signalId: signal.id,
    label: signal.label,
    gate: signal.gate,
    value: signal.value,
    unit: signal.unit,
  };
}

function formatSignalValue(signal: VisualBatchSignalSummary): string {
  return signal.unit === "%" ? `${signal.value.toFixed(1)}%` : signal.value.toFixed(2);
}

function buildBatchItemReportPreview(
  report: VisualReviewReport,
  passesRun: number,
  passesSkipped: number,
  primarySignal: VisualBatchSignalSummary | null,
  firstSkippedPass: VisualBatchSkippedPass | null,
  topFindings: VisualBatchFindingSummary[],
): string {
  const findingLine = topFindings
    .map((finding) => `${finding.gate}:${finding.title}`)
    .join("; ");

  return [
    `[Visual Review Item] ${report.fixtureName}`,
    `Gate: ${report.gate}`,
    `Release: ${report.releaseGate.decision} (${report.releaseGate.gate})`,
    `Fixture: ${report.fixtureEditSummary.mode}${report.fixtureEditSummary.changed ? `, ${report.fixtureEditSummary.changedFields.join(", ")}` : ""}`,
    `Passes: ${passesRun} run / ${passesSkipped} skip`,
    `Queue: ${report.reviewQueueSummary.blocked} blocked / ${report.reviewQueueSummary.todo} todo / ${report.reviewQueueSummary.ready} ready`,
    `Handoff owners: ${report.handoffPacket.sections.filter((section) => section.total > 0).map((section) => section.ownerLabel).join(", ") || "none"}`,
    primarySignal ? `Primary signal: ${primarySignal.label} ${formatSignalValue(primarySignal)} (${primarySignal.gate})` : "Primary signal: none",
    firstSkippedPass ? `First skipped pass: ${firstSkippedPass.label} - ${firstSkippedPass.reason}` : "First skipped pass: none",
    findingLine ? `Findings: ${findingLine}` : "Findings: none",
    `Output: ${report.evidencePackage.outputDir}`,
  ].join("\n");
}

function getPresetAvailability(
  preset: VisualPassPreset,
  aSplit: Record<LodBucket, string[]>,
  bSplit: Record<LodBucket, string[]>,
  cameraCount: number,
): { status: PassStatus; reason: string } {
  if (cameraCount === 0) {
    return { status: "skipped", reason: "No cameras were discovered for the selected camera groups." };
  }

  if (preset.requiredBucket === "variant_lod0_or_dt") {
    if (bSplit.LOD0.length === 0 && bSplit.DT.length === 0) {
      return { status: "skipped", reason: "Variant B has no LOD0 or DT mesh bucket for solo capture." };
    }
    return { status: "run", reason: "Variant has at least one visible LOD bucket." };
  }

  const bucket = preset.requiredBucket;
  if (aSplit[bucket].length === 0 || bSplit[bucket].length === 0) {
    return {
      status: "skipped",
      reason: `A=${aSplit[bucket].length}, B=${bSplit[bucket].length} for ${bucket}; both sides are required.`,
    };
  }

  return { status: "run", reason: "Required LOD bucket exists on both A and B." };
}

function composeShotName(camera: string, preset: VisualPassPreset): string {
  const safeCamera = camera.replace(/[^A-Za-z0-9._-]+/g, "_");
  if (preset.lodLabel) {
    return `${safeCamera}_${preset.lodLabel}_${preset.kindLabel}.png`;
  }
  return `${safeCamera}_${preset.kindLabel}.png`;
}

function gateAbove(value: number, reviewThreshold: number, blockThreshold: number): ReviewGate {
  if (value >= blockThreshold) {
    return "Blocked";
  }
  if (value >= reviewThreshold) {
    return "Review";
  }
  return "Ready";
}

function gateBelow(value: number, reviewThreshold: number, blockThreshold: number): ReviewGate {
  if (value <= blockThreshold) {
    return "Blocked";
  }
  if (value < reviewThreshold) {
    return "Review";
  }
  return "Ready";
}

function normalizeAbove(value: number, blockThreshold: number): number {
  return Math.max(0, Math.min(100, (value / blockThreshold) * 100));
}

function buildBatchNotificationPreview(
  items: VisualBatchItem[],
  success: number,
  failed: number,
): string {
  const blockedNames = items
    .filter((item) => item.reviewGate === "Blocked")
    .map((item) => item.name)
    .join(", ");
  return [
    "[Visual Review Batch]",
    `Capture: ${success} ok / ${failed} failed`,
    `Review gates: ${items.filter((item) => item.reviewGate === "Ready").length} ready, ${items.filter((item) => item.reviewGate === "Review").length} review, ${items.filter((item) => item.reviewGate === "Blocked").length} blocked`,
    blockedNames ? `Blocked: ${blockedNames}` : "Blocked: none",
  ].join("\n");
}

function normalizeVisualFixtureEditorState(state: VisualFixtureEditorState): VisualFixtureEditorState {
  return {
    silhouetteDeltaPercent: roundToStep(clampNumber(state.silhouetteDeltaPercent, 0, 20), 1),
    bboxDeltaPercent: roundToStep(clampNumber(state.bboxDeltaPercent, 0, 12), 1),
    materialDriftScore: roundToStep(clampNumber(state.materialDriftScore, 0, 0.6), 2),
    cameraCoverageScore: roundToStep(clampNumber(state.cameraCoverageScore, 0.5, 1), 2),
    variantUnit: state.variantUnit,
    variantMaterialCount: clampInteger(state.variantMaterialCount, 1, 24),
    unresolvedTextureCount: clampInteger(state.unresolvedTextureCount, 0, 12),
    variantDtCount: clampInteger(state.variantDtCount, 0, 8),
    reviewerNote: state.reviewerNote,
  };
}

function buildEditorMissingTextures(fixture: VisualReviewFixture, count: number): string[] {
  const missingTextures = fixture.variant.unresolvedTextures.slice(0, count);
  const token = getFixtureToken(fixture);
  while (missingTextures.length < count) {
    missingTextures.push(`T_${token}_Missing_${String(missingTextures.length + 1).padStart(2, "0")}.tga`);
  }
  return missingTextures;
}

function buildEditorVariantMeshes(fixture: VisualReviewFixture, variantDtCount: number): string[] {
  const split = classifyMeshesByLod(fixture.variant.meshes);
  const dtMeshes = split.DT.slice(0, variantDtCount);
  while (dtMeshes.length < variantDtCount) {
    dtMeshes.push(buildEditorDtMeshName(fixture, dtMeshes.length + 1));
  }
  return [...split.LOD0, ...dtMeshes, ...split.other];
}

function buildEditorDtMeshName(fixture: VisualReviewFixture, index: number): string {
  return `weaponCmpB:${getFixtureToken(fixture)}_DT_patch${String(index).padStart(2, "0")}Shape`;
}

function getFixtureToken(fixture: VisualReviewFixture): string {
  return (
    fixture.variant.name
      .replace(/\.(ma|mb|fbx)$/i, "")
      .replace(/[^A-Za-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
    || "Variant"
  );
}

function getChangedFixtureFields(
  before: VisualFixtureEditorState,
  after: VisualFixtureEditorState,
): string[] {
  const fields: [keyof VisualFixtureEditorState, string][] = [
    ["silhouetteDeltaPercent", "silhouette delta"],
    ["bboxDeltaPercent", "bounding box delta"],
    ["materialDriftScore", "material drift"],
    ["cameraCoverageScore", "camera coverage"],
    ["variantUnit", "variant unit"],
    ["variantMaterialCount", "variant material count"],
    ["unresolvedTextureCount", "missing textures"],
    ["variantDtCount", "variant DT mesh count"],
    ["reviewerNote", "reviewer note"],
  ];

  return fields
    .filter(([field]) => before[field] !== after[field])
    .map(([, label]) => label);
}

function clampInteger(value: number, min: number, max: number): number {
  return Math.round(clampNumber(value, min, max));
}

function clampNumber(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.max(min, Math.min(max, value));
}

function roundToStep(value: number, fractionDigits: number): number {
  const factor = 10 ** fractionDigits;
  return Math.round(value * factor) / factor;
}
