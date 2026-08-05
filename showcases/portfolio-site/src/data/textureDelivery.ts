export type TextureDeliveryGate = "Ready" | "Review" | "Blocked";
export type TexturePlatformId = "pc_dx12" | "mobile_astc" | "switch_lite";
export type TexturePackingPresetId = "ue_orm_bc" | "mobile_mask_astc" | "sprite_atlas_png";
export type TextureRole =
  | "baseColor"
  | "normal"
  | "roughness"
  | "metallic"
  | "ao"
  | "emissive"
  | "opacity"
  | "height";
export type TextureColorSpace = "sRGB" | "linear";
export type TextureSourceFormat = "png" | "tga" | "exr" | "psd";
export type TextureOutputFormat = "dds" | "ktx2" | "png";
export type TextureCompression = "BC7" | "BC5" | "BC1" | "ASTC_6x6" | "ASTC_8x8" | "RGBA8";
export type TextureOutputChannel = "RGB" | "R" | "G" | "B" | "A";
export type TextureRiskSeverity = "info" | "warning" | "error";
export type TextureQueueMode =
  | "dry_run"
  | "submitted"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled"
  | "retrying"
  | "resumed";
export type TextureQueueStatus = "queued" | "running" | "done" | "failed" | "skipped" | "cancelled" | "retrying";
export type TextureQueueFailureClass =
  | "none"
  | "source_contract"
  | "platform_gate"
  | "budget_gate"
  | "external_process"
  | "operator_cancelled";
export type TextureQueueRecoveryAction = "none" | "cancel" | "retry_failed_task" | "resume_from_checkpoint" | "resolve_gate";
export type TexturePresetEditField =
  | "format"
  | "compression"
  | "colorSpace"
  | "mipmaps"
  | "textureGroup"
  | `channel:${TextureOutputChannel}`;
export type TexturePublishDecision = "ready_to_publish" | "needs_review" | "blocked";
export type TexturePublishChecklistStatus = "pass" | "review" | "block";
export type TexturePublishDiffChannel = "manifest" | "output" | "preset" | "queue" | "risk" | "size";
export type TextureApprovedDeltaState = "added" | "changed" | "unchanged" | "removed" | "blocked";
export type TextureMutationScope = "metadata_only" | "file_write" | "engine_import" | "blocked";
export type TexturePublicFixtureScope = "portfolio_public_synthetic" | "synthetic_reference";
export type TextureAdapterId = "photoshop_normalize" | "substance_export" | "cli_compressor" | "engine_import";
export type TextureAdapterKind = "dcc_host" | "authoring_tool" | "command_line" | "engine";
export type TextureAdapterStage = "normalize" | "export" | "compress" | "import";
export type TextureAdapterStatus = "ready" | "dry_run" | "blocked" | "skipped";
export type TextureAdapterDiagnosticSeverity = "info" | "warning" | "error";

export interface TextureSourceFile {
  id: string;
  fileName: string;
  path: string;
  role: TextureRole;
  width: number;
  height: number;
  format: TextureSourceFormat;
  colorSpace: TextureColorSpace;
  bitDepth: 8 | 16 | 32;
  hasAlpha: boolean;
  fileSizeMb: number;
}

export interface TextureAssetFixture {
  id: string;
  name: string;
  assetCode: string;
  assetClass: "weapon" | "vehicle" | "character" | "ui";
  sourceRoot: string;
  targetRoot: string;
  textureSet: string;
  defaultPresetId: TexturePackingPresetId;
  defaultPlatformId: TexturePlatformId;
  sourceFiles: TextureSourceFile[];
}

export interface TexturePlatformProfile {
  id: TexturePlatformId;
  label: string;
  maxTextureSize: number;
  packageBudgetMb: number;
  importRoot: string;
  preferredFormat: TextureOutputFormat;
  preferredCompression: TextureCompression[];
  textureGroupPrefix: string;
  notes: string;
}

export interface TextureChannelMapEntry {
  channel: TextureOutputChannel;
  role: TextureRole;
}

export interface TextureOutputRule {
  id: string;
  label: string;
  suffix: string;
  format: TextureOutputFormat;
  compression: TextureCompression;
  colorSpace: TextureColorSpace;
  requiredRoles: TextureRole[];
  channelMap: TextureChannelMapEntry[];
  mipmaps: boolean;
  textureGroup: string;
}

export interface TexturePackingPreset {
  id: TexturePackingPresetId;
  label: string;
  description: string;
  outputRules: TextureOutputRule[];
}

export interface TextureOutputRuleEditState {
  ruleId: string;
  format: TextureOutputFormat;
  compression: TextureCompression;
  colorSpace: TextureColorSpace;
  mipmaps: boolean;
  textureGroup: string;
  channelMap: TextureChannelMapEntry[];
}

export interface TexturePresetEditorState {
  presetId: TexturePackingPresetId;
  ruleEdits: TextureOutputRuleEditState[];
}

export interface TexturePresetDiffItem {
  ruleId: string;
  ruleLabel: string;
  field: TexturePresetEditField;
  before: string;
  after: string;
}

export interface TexturePresetEditSummary {
  mode: "source_preset" | "runtime_preset_editor";
  sourcePresetLabel: string;
  editedPresetLabel: string;
  changedCount: number;
  changedFields: string[];
  diffs: TexturePresetDiffItem[];
}

export type TexturePresetVersionState = "approved" | "draft" | "deprecated";
export type TexturePromotionChecklistStatus = "pass" | "review" | "block";

export interface TexturePresetVersion {
  id: string;
  presetId: TexturePackingPresetId;
  version: string;
  label: string;
  state: TexturePresetVersionState;
  owner: string;
  updatedAt: string;
  platformIds: TexturePlatformId[];
  notes: string;
  ruleFingerprint: string;
}

export interface TexturePromotionChecklistItem {
  id: string;
  label: string;
  status: TexturePromotionChecklistStatus;
  detail: string;
}

export interface TexturePresetPromotionReport {
  gate: TextureDeliveryGate;
  sourceVersion: TexturePresetVersion;
  stagedVersion: TexturePresetVersion;
  changeCount: number;
  compatibilitySummary: string;
  checklist: TexturePromotionChecklistItem[];
  publishSummary: string;
}

export interface TextureFrozenManifestItem extends TextureImportManifestItem {
  outputId: string;
  sourceSignature: string;
  settingsSignature: string;
}

export interface TextureFrozenManifest {
  manifestId: string;
  frozenAt: string;
  assetCode: string;
  textureSet: string;
  platformId: TexturePlatformId;
  presetVersionId: string;
  hash: string;
  itemCount: number;
  totalEstimatedSizeMb: number;
  items: TextureFrozenManifestItem[];
}

export interface TextureApprovedPackage {
  id: string;
  fixtureId: string;
  version: string;
  approvedAt: string;
  owner: string;
  presetVersionId: string;
  manifestHash: string;
  totalEstimatedSizeMb: number;
  outputCount: number;
  outputFingerprints: string[];
  notes: string;
}

export interface TexturePublishDiffItem {
  id: string;
  channel: TexturePublishDiffChannel;
  status: TexturePublishChecklistStatus;
  title: string;
  before: string;
  after: string;
  action: string;
}

export interface TexturePublishChecklistItem {
  id: string;
  label: string;
  status: TexturePublishChecklistStatus;
  detail: string;
}

export interface TextureReviewPacket {
  packetId: string;
  gate: TextureDeliveryGate;
  title: string;
  reviewers: string[];
  summary: string;
  attachments: string[];
  handoffMessage: string;
}

export interface TexturePublishPackage {
  gate: TextureDeliveryGate;
  decision: TexturePublishDecision;
  frozenManifest: TextureFrozenManifest;
  lastApproved: TextureApprovedPackage;
  checklist: TexturePublishChecklistItem[];
  diffs: TexturePublishDiffItem[];
  reviewPacket: TextureReviewPacket;
}

export interface TexturePublicFixtureFile {
  role: TextureRole;
  fileName: string;
  path: string;
  dimensions: string;
  colorSpace: TextureColorSpace;
  sourceLicense: string;
}

export interface TexturePublicFixtureContract {
  fixtureId: string;
  scope: TexturePublicFixtureScope;
  license: string;
  sourceRoot: string;
  targetRoot: string;
  reproductionNote: string;
  privacyNote: string;
  files: TexturePublicFixtureFile[];
}

export interface TextureApprovedDeltaRow {
  id: string;
  textureName: string;
  state: TextureApprovedDeltaState;
  mutationScope: TextureMutationScope;
  before: string;
  after: string;
  importPath: string;
  sourceSignature: string;
  reason: string;
  ownerAction: string;
}

export interface TextureCommittedManifestFile {
  id: string;
  textureName: string;
  state: TextureApprovedDeltaState;
  mutationScope: TextureMutationScope;
  importPath: string;
  settingsSignature: string;
  sourceSignature: string;
}

export interface TextureCommittedManifest {
  manifestId: string;
  reportVersion: "texture-committed-manifest@0.1.0";
  status: "ready_to_commit" | "review_required" | "blocked";
  fixtureId: string;
  packageId: string;
  baselinePackageId: string;
  frozenManifestId: string;
  committedAt: string;
  targetRoot: string;
  owner: string;
  presetVersionId: string;
  manifestHash: string;
  mutationBoundary: string;
  fileCount: number;
  added: number;
  changed: number;
  unchanged: number;
  removed: number;
  blocked: number;
  files: TextureCommittedManifestFile[];
}

export interface TextureApprovedPackageDelta {
  reportVersion: "texture-approved-package-delta@0.1.0";
  deltaId: string;
  fixtureId: string;
  gate: TextureDeliveryGate;
  decision: TexturePublishDecision;
  publicFixture: TexturePublicFixtureContract;
  baselinePackageId: string;
  frozenManifestId: string;
  committedManifestId: string;
  summary: {
    added: number;
    changed: number;
    unchanged: number;
    removed: number;
    blocked: number;
    fileWriteCount: number;
    metadataOnlyCount: number;
    nextAction: string;
  };
  rows: TextureApprovedDeltaRow[];
  committedManifest: TextureCommittedManifest;
}

export interface TextureAdapterProfile {
  id: TextureAdapterId;
  label: string;
  kind: TextureAdapterKind;
  stage: TextureAdapterStage;
  owner: string;
  executable: string;
  timeoutMs: number;
  mutatesFilesystem: boolean;
  reads: string[];
  writes: string[];
  boundary: string;
}

export interface TextureAdapterPlanStep {
  id: string;
  adapterId: TextureAdapterId;
  adapterLabel: string;
  stage: TextureAdapterStage;
  mode: "portfolio_dry_run";
  status: TextureAdapterStatus;
  command: string;
  reads: string[];
  writes: string[];
  guard: string;
  mutationAllowed: boolean;
  logSample: string;
  aiDiagnostic: string;
}

export interface TextureAdapterDiagnostic {
  id: string;
  adapterId: TextureAdapterId;
  severity: TextureAdapterDiagnosticSeverity;
  title: string;
  detail: string;
  action: string;
}

export interface TextureAdapterExecutionPlan {
  planId: string;
  mode: "portfolio_dry_run";
  gate: TextureDeliveryGate;
  executorPolicy: string;
  boundaryRules: string[];
  adapters: TextureAdapterProfile[];
  steps: TextureAdapterPlanStep[];
  diagnostics: TextureAdapterDiagnostic[];
  aiLogSummary: string;
}

export interface ParsedTextureName {
  fileId: string;
  fileName: string;
  valid: boolean;
  assetToken: string;
  textureSetToken: string;
  roleToken: string;
  role: TextureRole;
  resolutionToken: string;
  warnings: string[];
}

export interface TextureOutputChannelSource {
  channel: TextureOutputChannel;
  role: TextureRole;
  sourceFileId: string | null;
  sourceFileName: string;
}

export interface TexturePackedOutput {
  id: string;
  label: string;
  fileName: string;
  outputPath: string;
  format: TextureOutputFormat;
  compression: TextureCompression;
  colorSpace: TextureColorSpace;
  width: number;
  height: number;
  mipmaps: boolean;
  textureGroup: string;
  estimatedSizeMb: number;
  channelSources: TextureOutputChannelSource[];
  missingRoles: TextureRole[];
  gate: TextureDeliveryGate;
}

export interface TextureRiskItem {
  id: string;
  severity: TextureRiskSeverity;
  gate: TextureDeliveryGate;
  channel: "naming" | "colorspace" | "packing" | "platform" | "budget" | "queue";
  title: string;
  detail: string;
  evidence: string;
  suggestedAction: string;
}

export interface TextureQueueTask {
  id: string;
  label: string;
  stage: "parse" | "pack" | "compress" | "manifest" | "sync";
  outputId: string | null;
  command: string;
  retryCommand: string;
  status: TextureQueueStatus;
  durationMs: number;
  log: string;
  canRetry: boolean;
  attempts: TextureQueueAttempt[];
  failureClass: TextureQueueFailureClass;
  recoveryAction: TextureQueueRecoveryAction;
  commandDiff: TextureQueueCommandDiff[];
  checkpoint: string;
}

export interface TextureQueueAttempt {
  attempt: number;
  status: TextureQueueStatus;
  durationMs: number;
  log: string;
}

export interface TextureQueueCommandDiff {
  field: string;
  before: string;
  after: string;
  reason: string;
}

export interface TextureQueueSummary {
  queued: number;
  running: number;
  done: number;
  failed: number;
  skipped: number;
  cancelled: number;
  retrying: number;
}

export interface TextureQueueRecoverySummary {
  mode: TextureQueueMode;
  statusLabel: string;
  failureClass: TextureQueueFailureClass;
  recoveryAction: TextureQueueRecoveryAction;
  activeTaskId: string | null;
  activeTaskLabel: string;
  checkpoint: string;
  commandBefore: string;
  commandAfter: string;
  commandDiff: TextureQueueCommandDiff[];
  auditTrail: string[];
}

export interface TextureImportManifestItem {
  textureName: string;
  importPath: string;
  textureGroup: string;
  compression: TextureCompression;
  colorSpace: TextureColorSpace;
  mipmaps: boolean;
  estimatedSizeMb: number;
}

export interface TextureDeliveryReport {
  reportVersion: "texture-delivery-report@0.7.0";
  fixtureId: string;
  fixtureName: string;
  presetId: TexturePackingPresetId;
  presetLabel: string;
  presetSnapshot: TexturePackingPreset;
  presetEditSummary: TexturePresetEditSummary;
  presetPromotion: TexturePresetPromotionReport;
  platformId: TexturePlatformId;
  platformLabel: string;
  gate: TextureDeliveryGate;
  sourceCount: number;
  outputCount: number;
  totalEstimatedSizeMb: number;
  parsedNames: ParsedTextureName[];
  packedOutputs: TexturePackedOutput[];
  risks: TextureRiskItem[];
  queueMode: TextureQueueMode;
  queueSummary: TextureQueueSummary;
  queueTasks: TextureQueueTask[];
  queueRecovery: TextureQueueRecoverySummary;
  importManifest: TextureImportManifestItem[];
  publishPackage: TexturePublishPackage;
  approvedPackageDelta: TextureApprovedPackageDelta;
  committedManifest: TextureCommittedManifest;
  adapterExecutionPlan: TextureAdapterExecutionPlan;
  notificationPreview: string;
  aiRiskBrief: string;
}

export const texturePlatforms: TexturePlatformProfile[] = [
  {
    id: "pc_dx12",
    label: "PC DX12",
    maxTextureSize: 4096,
    packageBudgetMb: 42,
    importRoot: "/Game/Weapons/Textures",
    preferredFormat: "dds",
    preferredCompression: ["BC7", "BC5", "BC1"],
    textureGroupPrefix: "World",
    notes: "Desktop build accepts high quality BC compression and 4K hero textures.",
  },
  {
    id: "mobile_astc",
    label: "Mobile ASTC",
    maxTextureSize: 2048,
    packageBudgetMb: 18,
    importRoot: "/Game/Mobile/Textures",
    preferredFormat: "ktx2",
    preferredCompression: ["ASTC_6x6", "ASTC_8x8"],
    textureGroupPrefix: "Mobile",
    notes: "Mobile build favors ASTC, lower resolution, and strict package budgets.",
  },
  {
    id: "switch_lite",
    label: "Switch Lite",
    maxTextureSize: 2048,
    packageBudgetMb: 24,
    importRoot: "/Game/Switch/Textures",
    preferredFormat: "dds",
    preferredCompression: ["BC7", "BC5", "BC1"],
    textureGroupPrefix: "Console",
    notes: "Console-lite target keeps BC formats but enforces 2K texture size.",
  },
];

export const texturePackingPresets: TexturePackingPreset[] = [
  {
    id: "ue_orm_bc",
    label: "UE ORM BC",
    description: "BaseColor, Normal, and ORM packed as AO/Roughness/Metallic for Unreal import.",
    outputRules: [
      {
        id: "basecolor_bc7",
        label: "BaseColor",
        suffix: "BC",
        format: "dds",
        compression: "BC7",
        colorSpace: "sRGB",
        requiredRoles: ["baseColor"],
        channelMap: [{ channel: "RGB", role: "baseColor" }],
        mipmaps: true,
        textureGroup: "WorldDiffuse",
      },
      {
        id: "normal_bc5",
        label: "Normal",
        suffix: "N",
        format: "dds",
        compression: "BC5",
        colorSpace: "linear",
        requiredRoles: ["normal"],
        channelMap: [{ channel: "RGB", role: "normal" }],
        mipmaps: true,
        textureGroup: "WorldNormalMap",
      },
      {
        id: "orm_bc1",
        label: "ORM",
        suffix: "ORM",
        format: "dds",
        compression: "BC1",
        colorSpace: "linear",
        requiredRoles: ["ao", "roughness", "metallic"],
        channelMap: [
          { channel: "R", role: "ao" },
          { channel: "G", role: "roughness" },
          { channel: "B", role: "metallic" },
        ],
        mipmaps: true,
        textureGroup: "WorldSpecular",
      },
    ],
  },
  {
    id: "mobile_mask_astc",
    label: "Mobile Mask ASTC",
    description: "Downstream mobile preset with ASTC color, normal, and packed mask outputs.",
    outputRules: [
      {
        id: "basecolor_astc",
        label: "BaseColor",
        suffix: "BC",
        format: "ktx2",
        compression: "ASTC_6x6",
        colorSpace: "sRGB",
        requiredRoles: ["baseColor"],
        channelMap: [{ channel: "RGB", role: "baseColor" }],
        mipmaps: true,
        textureGroup: "MobileDiffuse",
      },
      {
        id: "normal_astc",
        label: "Normal",
        suffix: "N",
        format: "ktx2",
        compression: "ASTC_8x8",
        colorSpace: "linear",
        requiredRoles: ["normal"],
        channelMap: [{ channel: "RGB", role: "normal" }],
        mipmaps: true,
        textureGroup: "MobileNormal",
      },
      {
        id: "mask_astc",
        label: "Mask",
        suffix: "MSK",
        format: "ktx2",
        compression: "ASTC_8x8",
        colorSpace: "linear",
        requiredRoles: ["roughness", "metallic", "ao"],
        channelMap: [
          { channel: "R", role: "roughness" },
          { channel: "G", role: "metallic" },
          { channel: "B", role: "ao" },
          { channel: "A", role: "opacity" },
        ],
        mipmaps: true,
        textureGroup: "MobileMask",
      },
    ],
  },
  {
    id: "sprite_atlas_png",
    label: "Sprite Atlas PNG",
    description: "UI or VFX sprite atlas output with base color in RGB and opacity in alpha.",
    outputRules: [
      {
        id: "sprite_rgba",
        label: "Sprite RGBA",
        suffix: "Atlas",
        format: "png",
        compression: "RGBA8",
        colorSpace: "sRGB",
        requiredRoles: ["baseColor", "opacity"],
        channelMap: [
          { channel: "RGB", role: "baseColor" },
          { channel: "A", role: "opacity" },
        ],
        mipmaps: false,
        textureGroup: "UI",
      },
    ],
  },
];

export const texturePresetVersions: TexturePresetVersion[] = [
  {
    id: "ue_orm_bc@1.0.0",
    presetId: "ue_orm_bc",
    version: "1.0.0",
    label: "UE ORM BC",
    state: "approved",
    owner: "TA Texture",
    updatedAt: "2026-07-20",
    platformIds: ["pc_dx12", "switch_lite"],
    notes: "Approved desktop and console ORM package contract.",
    ruleFingerprint: "basecolor:BC7:sRGB:mips|normal:BC5:linear:mips|orm:BC1:linear:mips",
  },
  {
    id: "mobile_mask_astc@1.0.0",
    presetId: "mobile_mask_astc",
    version: "1.0.0",
    label: "Mobile Mask ASTC",
    state: "approved",
    owner: "Mobile TA",
    updatedAt: "2026-07-22",
    platformIds: ["mobile_astc"],
    notes: "Approved mobile ASTC preset with mask packing.",
    ruleFingerprint: "basecolor:ASTC_6x6:sRGB:mips|normal:ASTC_8x8:linear:mips|mask:ASTC_8x8:linear:mips",
  },
  {
    id: "sprite_atlas_png@1.0.0",
    presetId: "sprite_atlas_png",
    version: "1.0.0",
    label: "Sprite Atlas PNG",
    state: "approved",
    owner: "UI TA",
    updatedAt: "2026-07-18",
    platformIds: ["pc_dx12"],
    notes: "Approved UI sprite atlas preset.",
    ruleFingerprint: "sprite:RGBA8:sRGB:no-mips",
  },
];

export const textureApprovedPackages: TextureApprovedPackage[] = [
  {
    id: "approved-rifle-body-1.0.0",
    fixtureId: "rifle_orm_pack",
    version: "1.0.0",
    approvedAt: "2026-07-24",
    owner: "TA Texture",
    presetVersionId: "ue_orm_bc@1.0.0",
    manifestHash: "txpkg_5m4v2x",
    totalEstimatedSizeMb: 10,
    outputCount: 3,
    outputFingerprints: [
      "WPN_Rifle_A_Body_BC.dds|World.WorldDiffuse|BC7|sRGB|mips|4",
      "WPN_Rifle_A_Body_N.dds|World.WorldNormalMap|BC5|linear|mips|4",
      "WPN_Rifle_A_Body_ORM.dds|World.WorldSpecular|BC1|linear|mips|2",
    ],
    notes: "Last accepted desktop rifle texture package.",
  },
  {
    id: "approved-hover-chassis-mobile-0.9.0",
    fixtureId: "vehicle_mobile_overbudget",
    version: "0.9.0",
    approvedAt: "2026-07-16",
    owner: "Mobile TA",
    presetVersionId: "mobile_mask_astc@1.0.0",
    manifestHash: "txpkg_8q7b1n",
    totalEstimatedSizeMb: 8,
    outputCount: 3,
    outputFingerprints: [
      "VEH_Hover_01_Chassis_BC.ktx2|Mobile.MobileDiffuse|ASTC_6x6|sRGB|mips|3.6",
      "VEH_Hover_01_Chassis_N.ktx2|Mobile.MobileNormal|ASTC_8x8|linear|mips|2.2",
      "VEH_Hover_01_Chassis_MSK.ktx2|Mobile.MobileMask|ASTC_8x8|linear|mips|2.2",
    ],
    notes: "Mobile baseline was approved before current source resolution drift.",
  },
  {
    id: "approved-skill-fire-icon-1.0.0",
    fixtureId: "skill_sprite_sheet",
    version: "1.0.0",
    approvedAt: "2026-07-19",
    owner: "UI TA",
    presetVersionId: "sprite_atlas_png@1.0.0",
    manifestHash: "txpkg_2k9p6c",
    totalEstimatedSizeMb: 4,
    outputCount: 1,
    outputFingerprints: [
      "UI_Skill_Fire_Icon_Atlas.png|World.UI|RGBA8|sRGB|no-mips|4",
    ],
    notes: "Approved UI icon atlas package.",
  },
  {
    id: "approved-public-crate-body-1.0.0",
    fixtureId: "public_crate_orm",
    version: "1.0.0",
    approvedAt: "2026-07-25",
    owner: "Portfolio Texture TA",
    presetVersionId: "ue_orm_bc@1.0.0",
    manifestHash: "txpkg_public_crate_v100",
    totalEstimatedSizeMb: 7.8,
    outputCount: 2,
    outputFingerprints: [
      "PUB_Crate_A_Body_BC.dds|World.WorldDiffuse|BC7|sRGB|mips|4",
      "PUB_Crate_A_Body_N.dds|World.WorldNormalMap|BC5|linear|no-mips|3.8",
    ],
    notes: "Public synthetic fixture baseline used for portfolio-safe approved package delta.",
  },
];

export const textureAdapterProfiles: TextureAdapterProfile[] = [
  {
    id: "photoshop_normalize",
    label: "Photoshop Normalize",
    kind: "dcc_host",
    stage: "normalize",
    owner: "Texture TA",
    executable: "photoshop-batch.exe",
    timeoutMs: 180000,
    mutatesFilesystem: true,
    reads: ["source PSD/TGA/PNG", "color profile tags"],
    writes: ["normalized temp images", "flattened alpha audit"],
    boundary: "Runs as an isolated host process. Portfolio mode records command and temp paths only.",
  },
  {
    id: "substance_export",
    label: "Substance Export",
    kind: "authoring_tool",
    stage: "export",
    owner: "Material TA",
    executable: "sbsrender.exe",
    timeoutMs: 300000,
    mutatesFilesystem: true,
    reads: ["Substance graph", "export preset", "mesh bake context"],
    writes: ["raw material maps", "export log"],
    boundary: "Exports are treated as untrusted raw inputs until naming, color, and size gates pass.",
  },
  {
    id: "cli_compressor",
    label: "CLI Compressor",
    kind: "command_line",
    stage: "compress",
    owner: "Build Pipeline",
    executable: "texture-compress.exe",
    timeoutMs: 240000,
    mutatesFilesystem: true,
    reads: ["packed channel outputs", "platform compression preset"],
    writes: ["DDS/KTX2/PNG outputs", "compression trace"],
    boundary: "Command arguments are deterministic. AI cannot rewrite codec flags.",
  },
  {
    id: "engine_import",
    label: "Engine Import",
    kind: "engine",
    stage: "import",
    owner: "Engine TA",
    executable: "ue-import-textures.exe",
    timeoutMs: 240000,
    mutatesFilesystem: true,
    reads: ["frozen import manifest", "engine project settings"],
    writes: ["engine texture assets", "import receipt"],
    boundary: "Engine import is blocked unless publish gate is ready or explicitly in review packet mode.",
  },
];

export const textureRoleOptions: TextureRole[] = [
  "baseColor",
  "normal",
  "roughness",
  "metallic",
  "ao",
  "emissive",
  "opacity",
  "height",
];

export const textureOutputFormatOptions: TextureOutputFormat[] = ["dds", "ktx2", "png"];

export const textureCompressionOptions: TextureCompression[] = [
  "BC7",
  "BC5",
  "BC1",
  "ASTC_6x6",
  "ASTC_8x8",
  "RGBA8",
];

export const textureColorSpaceOptions: TextureColorSpace[] = ["sRGB", "linear"];

export const textureDeliveryFixtures: TextureAssetFixture[] = [
  {
    id: "rifle_orm_pack",
    name: "Rifle ORM Pack",
    assetCode: "WPN_Rifle_A",
    assetClass: "weapon",
    sourceRoot: "P:/weapon/rifle/sourceimages",
    targetRoot: "P:/weapon/rifle/export",
    textureSet: "Body",
    defaultPresetId: "ue_orm_bc",
    defaultPlatformId: "pc_dx12",
    sourceFiles: [
      makeTextureSource("rifle_bc", "WPN_Rifle_A_Body_BC_2K.tga", "baseColor", 2048, 2048, "tga", "sRGB", 8, false, 12.4),
      makeTextureSource("rifle_n", "WPN_Rifle_A_Body_N_2K.tga", "normal", 2048, 2048, "tga", "linear", 8, false, 16.8),
      makeTextureSource("rifle_r", "WPN_Rifle_A_Body_R_2K.tga", "roughness", 2048, 2048, "tga", "linear", 8, false, 4.2),
      makeTextureSource("rifle_m", "WPN_Rifle_A_Body_M_2K.tga", "metallic", 2048, 2048, "tga", "linear", 8, false, 4.1),
      makeTextureSource("rifle_ao", "WPN_Rifle_A_Body_AO_2K.tga", "ao", 2048, 2048, "tga", "linear", 8, false, 4.3),
    ],
  },
  {
    id: "vehicle_mobile_overbudget",
    name: "Vehicle Mobile Overbudget",
    assetCode: "VEH_Hover_01",
    assetClass: "vehicle",
    sourceRoot: "P:/vehicle/hover/sourceimages",
    targetRoot: "P:/vehicle/hover/mobile",
    textureSet: "Chassis",
    defaultPresetId: "mobile_mask_astc",
    defaultPlatformId: "mobile_astc",
    sourceFiles: [
      makeTextureSource("hover_bc", "VEH_Hover_01_Chassis_BC_4K.psd", "baseColor", 4096, 4096, "psd", "sRGB", 16, true, 96),
      makeTextureSource("hover_n", "VEH_Hover_01_Chassis_N_4K.tga", "normal", 4096, 4096, "tga", "sRGB", 8, false, 64),
      makeTextureSource("hover_r", "VEH_Hover_01_Chassis_R_4K.tga", "roughness", 4096, 4096, "tga", "linear", 8, false, 16),
      makeTextureSource("hover_m", "VEH_Hover_01_Chassis_M_4K.tga", "metallic", 4096, 4096, "tga", "linear", 8, false, 16),
    ],
  },
  {
    id: "skill_sprite_sheet",
    name: "Skill Sprite Sheet",
    assetCode: "UI_Skill_Fire",
    assetClass: "ui",
    sourceRoot: "P:/ui/skill/sourceimages",
    targetRoot: "P:/ui/skill/export",
    textureSet: "Icon",
    defaultPresetId: "sprite_atlas_png",
    defaultPlatformId: "pc_dx12",
    sourceFiles: [
      makeTextureSource("skill_bc", "UI_Skill_Fire_Icon_BC_1K.png", "baseColor", 1024, 1024, "png", "sRGB", 8, true, 3.4),
      makeTextureSource("skill_opacity", "UI_Skill_Fire_Icon_A_1K.png", "opacity", 1024, 1024, "png", "linear", 8, false, 0.9),
      makeTextureSource("skill_emissive_badname", "FireIconGlow.png", "emissive", 1024, 768, "png", "sRGB", 8, true, 2.1),
    ],
  },
  {
    id: "public_crate_orm",
    name: "Public Crate ORM Fixture",
    assetCode: "PUB_Crate_A",
    assetClass: "weapon",
    sourceRoot: "<repo>/fixtures/public_texture_crate/sourceimages",
    targetRoot: "<repo>/fixtures/public_texture_crate/approved",
    textureSet: "Body",
    defaultPresetId: "ue_orm_bc",
    defaultPlatformId: "pc_dx12",
    sourceFiles: [
      makeTextureSource("public_crate_bc", "PUB_Crate_A_Body_BC_2K.png", "baseColor", 2048, 2048, "png", "sRGB", 8, false, 4.2),
      makeTextureSource("public_crate_n", "PUB_Crate_A_Body_N_2K.png", "normal", 2048, 2048, "png", "linear", 8, false, 4.1),
      makeTextureSource("public_crate_r", "PUB_Crate_A_Body_R_2K.png", "roughness", 2048, 2048, "png", "linear", 8, false, 1.3),
      makeTextureSource("public_crate_m", "PUB_Crate_A_Body_M_2K.png", "metallic", 2048, 2048, "png", "linear", 8, false, 1.2),
      makeTextureSource("public_crate_ao", "PUB_Crate_A_Body_AO_2K.png", "ao", 2048, 2048, "png", "linear", 8, false, 1.1),
    ],
  },
];

export function buildTextureDeliveryReport(
  fixture: TextureAssetFixture,
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
  queueMode: TextureQueueMode,
  presetEditSummary: TexturePresetEditSummary = getTexturePresetEditSummary(preset, preset),
): TextureDeliveryReport {
  const parsedNames = fixture.sourceFiles.map((file) => parseTextureFileName(file));
  const packedOutputs = buildPackedOutputs(fixture, preset, platform);
  const risks = buildTextureRisks(fixture, preset, platform, parsedNames, packedOutputs);
  const gate = highestTextureGate(risks.map((risk) => risk.gate));
  const queueTasks = buildTextureQueueTasks(fixture, preset, packedOutputs, risks, queueMode);
  const queueSummary = buildTextureQueueSummary(queueTasks);
  const queueRecovery = buildTextureQueueRecoverySummary(queueMode, queueTasks, risks);
  const presetPromotion = buildTexturePresetPromotionReport(preset, platform, risks, presetEditSummary);
  const importManifest = packedOutputs.map<TextureImportManifestItem>((output) => ({
    textureName: output.fileName,
    importPath: `${platform.importRoot}/${fixture.assetCode}/${output.fileName}`,
    textureGroup: `${platform.textureGroupPrefix}.${output.textureGroup}`,
    compression: output.compression,
    colorSpace: output.colorSpace,
    mipmaps: output.mipmaps,
    estimatedSizeMb: output.estimatedSizeMb,
  }));
  const totalEstimatedSizeMb = roundMb(
    packedOutputs.reduce((sum, output) => sum + output.estimatedSizeMb, 0),
  );
  const publishPackage = buildTexturePublishPackage(
    fixture,
    platform,
    gate,
    packedOutputs,
    importManifest,
    risks,
    queueSummary,
    queueTasks,
    queueRecovery,
    presetEditSummary,
    presetPromotion,
    totalEstimatedSizeMb,
  );
  const approvedPackageDelta = buildTextureApprovedPackageDelta(fixture, platform, publishPackage);
  const committedManifest = approvedPackageDelta.committedManifest;
  const adapterExecutionPlan = buildTextureAdapterExecutionPlan(
    fixture,
    platform,
    packedOutputs,
    risks,
    queueTasks,
    queueSummary,
    publishPackage,
  );
  const baseReport = {
    fixtureName: fixture.name,
    gate,
    platformLabel: platform.label,
    presetLabel: preset.label,
    totalEstimatedSizeMb,
    riskCount: risks.filter((risk) => risk.severity !== "info").length,
    queueSummary,
  };

  return {
    reportVersion: "texture-delivery-report@0.7.0",
    fixtureId: fixture.id,
    fixtureName: fixture.name,
    presetId: preset.id,
    presetLabel: preset.label,
    presetSnapshot: cloneTexturePackingPreset(preset),
    presetEditSummary,
    presetPromotion,
    platformId: platform.id,
    platformLabel: platform.label,
    gate,
    sourceCount: fixture.sourceFiles.length,
    outputCount: packedOutputs.length,
    totalEstimatedSizeMb,
    parsedNames,
    packedOutputs,
    risks,
    queueMode,
    queueSummary,
    queueTasks,
    queueRecovery,
    importManifest,
    publishPackage,
    approvedPackageDelta,
    committedManifest,
    adapterExecutionPlan,
    notificationPreview: buildTextureNotification(baseReport),
    aiRiskBrief: buildTextureAiRiskBrief(fixture, platform, preset, risks, gate),
  };
}

export function getTexturePlatform(id: TexturePlatformId): TexturePlatformProfile {
  return texturePlatforms.find((platform) => platform.id === id) ?? texturePlatforms[0];
}

export function getTexturePreset(id: TexturePackingPresetId): TexturePackingPreset {
  return texturePackingPresets.find((preset) => preset.id === id) ?? texturePackingPresets[0];
}

export function getDefaultTextureReport(): TextureDeliveryReport {
  const fixture = textureDeliveryFixtures[0];
  return buildTextureDeliveryReport(
    fixture,
    getTexturePreset(fixture.defaultPresetId),
    getTexturePlatform(fixture.defaultPlatformId),
    "dry_run",
  );
}

export function createTexturePresetEditorState(preset: TexturePackingPreset): TexturePresetEditorState {
  return {
    presetId: preset.id,
    ruleEdits: preset.outputRules.map((rule) => ({
      ruleId: rule.id,
      format: rule.format,
      compression: rule.compression,
      colorSpace: rule.colorSpace,
      mipmaps: rule.mipmaps,
      textureGroup: rule.textureGroup,
      channelMap: cloneChannelMap(rule.channelMap),
    })),
  };
}

export function applyTexturePresetEditorState(
  preset: TexturePackingPreset,
  editorState: TexturePresetEditorState,
): TexturePackingPreset {
  if (editorState.presetId !== preset.id) {
    return cloneTexturePackingPreset(preset);
  }

  const editsByRule = new Map(editorState.ruleEdits.map((rule) => [rule.ruleId, rule]));
  return {
    ...preset,
    outputRules: preset.outputRules.map((rule) => {
      const edit = editsByRule.get(rule.id);
      if (!edit) {
        return cloneOutputRule(rule);
      }
      return {
        ...rule,
        format: edit.format,
        compression: edit.compression,
        colorSpace: edit.colorSpace,
        mipmaps: edit.mipmaps,
        textureGroup: edit.textureGroup,
        channelMap: cloneChannelMap(edit.channelMap),
      };
    }),
  };
}

export function getTexturePresetEditSummary(
  sourcePreset: TexturePackingPreset,
  editedPreset: TexturePackingPreset,
): TexturePresetEditSummary {
  const diffs: TexturePresetDiffItem[] = [];

  for (const sourceRule of sourcePreset.outputRules) {
    const editedRule = editedPreset.outputRules.find((rule) => rule.id === sourceRule.id);
    if (!editedRule) {
      continue;
    }

    appendPresetDiff(diffs, sourceRule, editedRule, "format", sourceRule.format, editedRule.format);
    appendPresetDiff(diffs, sourceRule, editedRule, "compression", sourceRule.compression, editedRule.compression);
    appendPresetDiff(diffs, sourceRule, editedRule, "colorSpace", sourceRule.colorSpace, editedRule.colorSpace);
    appendPresetDiff(diffs, sourceRule, editedRule, "mipmaps", String(sourceRule.mipmaps), String(editedRule.mipmaps));
    appendPresetDiff(diffs, sourceRule, editedRule, "textureGroup", sourceRule.textureGroup, editedRule.textureGroup);

    for (const sourceChannel of sourceRule.channelMap) {
      const editedChannel = editedRule.channelMap.find((entry) => entry.channel === sourceChannel.channel);
      if (!editedChannel) {
        continue;
      }
      appendPresetDiff(
        diffs,
        sourceRule,
        editedRule,
        `channel:${sourceChannel.channel}`,
        sourceChannel.role,
        editedChannel.role,
      );
    }
  }

  return {
    mode: diffs.length > 0 ? "runtime_preset_editor" : "source_preset",
    sourcePresetLabel: sourcePreset.label,
    editedPresetLabel: editedPreset.label,
    changedCount: diffs.length,
    changedFields: diffs.map((diff) => `${diff.ruleLabel}.${diff.field}`),
    diffs,
  };
}

export function getTextureRoleLabel(role: TextureRole): string {
  return roleLabels[role];
}

export function getTexturePresetVersion(presetId: TexturePackingPresetId): TexturePresetVersion {
  return texturePresetVersions.find((version) => version.presetId === presetId && version.state === "approved")
    ?? texturePresetVersions[0];
}

function buildTexturePresetPromotionReport(
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
  risks: TextureRiskItem[],
  editSummary: TexturePresetEditSummary,
): TexturePresetPromotionReport {
  const sourceVersion = getTexturePresetVersion(preset.id);
  const stagedVersion: TexturePresetVersion = {
    ...sourceVersion,
    id: `${preset.id}@${editSummary.changedCount > 0 ? bumpMinorVersion(sourceVersion.version) : sourceVersion.version}-staged`,
    version: editSummary.changedCount > 0 ? bumpMinorVersion(sourceVersion.version) : sourceVersion.version,
    state: editSummary.changedCount > 0 ? "draft" : sourceVersion.state,
    updatedAt: "2026-07-30",
    platformIds: Array.from(new Set([...sourceVersion.platformIds, platform.id])),
    notes: editSummary.changedCount > 0
      ? `Runtime edits staged for review: ${editSummary.changedFields.join(", ")}.`
      : "Source preset is unchanged.",
    ruleFingerprint: buildTextureRuleFingerprint(preset),
  };
  const checklist = buildTexturePromotionChecklist(preset, platform, risks, editSummary, sourceVersion);
  const gate = getPromotionGate(checklist);

  return {
    gate,
    sourceVersion,
    stagedVersion,
    changeCount: editSummary.changedCount,
    compatibilitySummary: buildPromotionCompatibilitySummary(gate, preset, platform, editSummary, checklist),
    checklist,
    publishSummary: buildPromotionPublishSummary(gate, sourceVersion, stagedVersion),
  };
}

function buildTexturePromotionChecklist(
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
  risks: TextureRiskItem[],
  editSummary: TexturePresetEditSummary,
  sourceVersion: TexturePresetVersion,
): TexturePromotionChecklistItem[] {
  const hasBlocker = risks.some((risk) => risk.gate === "Blocked");
  const unsupportedCompression = preset.outputRules.filter((rule) => !platform.preferredCompression.includes(rule.compression));
  const nonPreferredFormat = preset.outputRules.filter((rule) => rule.format !== platform.preferredFormat);
  const mipmapChanges = editSummary.diffs.filter((diff) => diff.field === "mipmaps");

  return [
    {
      id: "platform_scope",
      label: "Platform scope",
      status: sourceVersion.platformIds.includes(platform.id) ? "pass" : "review",
      detail: sourceVersion.platformIds.includes(platform.id)
        ? `${sourceVersion.label} already targets ${platform.label}.`
        : `${platform.label} is new for this preset version.`,
    },
    {
      id: "deterministic_gate",
      label: "Deterministic gate",
      status: hasBlocker ? "block" : "pass",
      detail: hasBlocker
        ? risks.filter((risk) => risk.gate === "Blocked").map((risk) => risk.title).join("; ")
        : "No blocking source, packing, platform, or budget risk.",
    },
    {
      id: "compression_contract",
      label: "Compression contract",
      status: unsupportedCompression.length > 0 ? "block" : "pass",
      detail: unsupportedCompression.length > 0
        ? unsupportedCompression.map((rule) => `${rule.label}:${rule.compression}`).join("; ")
        : `All output rules use ${platform.label} supported compression.`,
    },
    {
      id: "format_contract",
      label: "Format contract",
      status: nonPreferredFormat.length > 0 ? "review" : "pass",
      detail: nonPreferredFormat.length > 0
        ? nonPreferredFormat.map((rule) => `${rule.label}:${rule.format}`).join("; ")
        : `All output rules match ${platform.preferredFormat.toUpperCase()} platform format.`,
    },
    {
      id: "runtime_override",
      label: "Runtime override",
      status: editSummary.changedCount > 0 ? "review" : "pass",
      detail: editSummary.changedCount > 0
        ? editSummary.changedFields.join("; ")
        : "No runtime preset edits.",
    },
    {
      id: "mipmap_policy",
      label: "Mipmap policy",
      status: mipmapChanges.length > 0 ? "review" : "pass",
      detail: mipmapChanges.length > 0
        ? mipmapChanges.map((diff) => `${diff.ruleLabel}:${diff.before}->${diff.after}`).join("; ")
        : "Mipmap flags match approved source version.",
    },
  ];
}

function getPromotionGate(checklist: TexturePromotionChecklistItem[]): TextureDeliveryGate {
  if (checklist.some((item) => item.status === "block")) {
    return "Blocked";
  }
  if (checklist.some((item) => item.status === "review")) {
    return "Review";
  }
  return "Ready";
}

function buildPromotionCompatibilitySummary(
  gate: TextureDeliveryGate,
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
  editSummary: TexturePresetEditSummary,
  checklist: TexturePromotionChecklistItem[],
): string {
  if (gate === "Blocked") {
    return `${preset.label} cannot be promoted for ${platform.label}: ${checklist.filter((item) => item.status === "block").map((item) => item.label).join(", ")}.`;
  }
  if (gate === "Review") {
    return `${preset.label} can stage a draft for ${platform.label}, with ${editSummary.changedCount} runtime override(s) requiring TA review.`;
  }
  return `${preset.label} matches ${platform.label} and can reuse the approved preset version.`;
}

function buildPromotionPublishSummary(
  gate: TextureDeliveryGate,
  sourceVersion: TexturePresetVersion,
  stagedVersion: TexturePresetVersion,
): string {
  if (gate === "Blocked") {
    return `${stagedVersion.id} is blocked and must not replace ${sourceVersion.id}.`;
  }
  if (gate === "Review") {
    return `${stagedVersion.id} is a draft candidate. Record reviewer approval before publishing as a shared preset.`;
  }
  return `${sourceVersion.id} remains the active approved preset.`;
}

function buildTextureRuleFingerprint(preset: TexturePackingPreset): string {
  return preset.outputRules
    .map((rule) => `${rule.label.toLowerCase()}:${rule.compression}:${rule.colorSpace}:${rule.mipmaps ? "mips" : "no-mips"}`)
    .join("|");
}

function bumpMinorVersion(version: string): string {
  const [major, minor, patch] = version.split(".").map((part) => Number(part));
  if ([major, minor, patch].some((part) => Number.isNaN(part))) {
    return `${version}.draft`;
  }
  return `${major}.${minor + 1}.0`;
}

function buildTexturePublishPackage(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  gate: TextureDeliveryGate,
  packedOutputs: TexturePackedOutput[],
  importManifest: TextureImportManifestItem[],
  risks: TextureRiskItem[],
  queueSummary: TextureQueueSummary,
  queueTasks: TextureQueueTask[],
  queueRecovery: TextureQueueRecoverySummary,
  editSummary: TexturePresetEditSummary,
  promotion: TexturePresetPromotionReport,
  totalEstimatedSizeMb: number,
): TexturePublishPackage {
  const frozenManifest = buildFrozenManifest(fixture, platform, packedOutputs, importManifest, promotion, totalEstimatedSizeMb);
  const lastApproved = getTextureApprovedPackage(fixture.id);
  const diffs = buildTexturePublishDiffs(
    lastApproved,
    frozenManifest,
    risks,
    queueSummary,
    queueTasks,
    queueRecovery,
    editSummary,
    promotion,
  );
  const checklist = buildTexturePublishChecklist(gate, queueSummary, queueTasks, promotion, diffs, frozenManifest);
  const publishGate = getPublishGate(checklist);
  const decision = getPublishDecision(publishGate);
  const reviewPacket = buildTextureReviewPacket(fixture, platform, publishGate, decision, frozenManifest, lastApproved, diffs, risks);

  return {
    gate: publishGate,
    decision,
    frozenManifest,
    lastApproved,
    checklist,
    diffs,
    reviewPacket,
  };
}

function buildFrozenManifest(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  packedOutputs: TexturePackedOutput[],
  importManifest: TextureImportManifestItem[],
  promotion: TexturePresetPromotionReport,
  totalEstimatedSizeMb: number,
): TextureFrozenManifest {
  const items = importManifest.map<TextureFrozenManifestItem>((item) => {
    const output = packedOutputs.find((candidate) => candidate.fileName === item.textureName);
    return {
      ...item,
      outputId: output?.id ?? item.textureName,
      sourceSignature: output?.channelSources.map((source) => `${source.channel}:${source.sourceFileName}`).join("|") ?? "source:unknown",
      settingsSignature: buildOutputFingerprint(item),
    };
  });
  const manifestSource = items.map((item) => `${item.importPath}|${item.settingsSignature}|${item.sourceSignature}`).join(";");
  const hash = stableTextureId("txpkg", manifestSource);

  return {
    manifestId: `${fixture.assetCode}_${fixture.textureSet}_${platform.id}_${hash}`,
    frozenAt: "2026-07-30T20:30:00+08:00",
    assetCode: fixture.assetCode,
    textureSet: fixture.textureSet,
    platformId: platform.id,
    presetVersionId: promotion.stagedVersion.id,
    hash,
    itemCount: items.length,
    totalEstimatedSizeMb,
    items,
  };
}

function getTextureApprovedPackage(fixtureId: string): TextureApprovedPackage {
  return textureApprovedPackages.find((item) => item.fixtureId === fixtureId) ?? textureApprovedPackages[0];
}

function buildTexturePublishDiffs(
  lastApproved: TextureApprovedPackage,
  frozenManifest: TextureFrozenManifest,
  risks: TextureRiskItem[],
  queueSummary: TextureQueueSummary,
  queueTasks: TextureQueueTask[],
  queueRecovery: TextureQueueRecoverySummary,
  editSummary: TexturePresetEditSummary,
  promotion: TexturePresetPromotionReport,
): TexturePublishDiffItem[] {
  const diffs: TexturePublishDiffItem[] = [];
  const currentFingerprints = frozenManifest.items.map((item) => item.settingsSignature);

  if (lastApproved.outputCount !== frozenManifest.itemCount) {
    diffs.push({
      id: "output-count-delta",
      channel: "manifest",
      status: "review",
      title: "Output count changed",
      before: String(lastApproved.outputCount),
      after: String(frozenManifest.itemCount),
      action: "Review added or removed texture outputs before publish.",
    });
  }

  const approvedByTexture = new Map(lastApproved.outputFingerprints.map((fingerprint) => [fingerprint.split("|")[0], fingerprint]));
  for (const current of currentFingerprints) {
    const textureName = current.split("|")[0];
    const approved = approvedByTexture.get(textureName);
    if (!approved) {
      diffs.push({
        id: `new-output-${textureName}`,
        channel: "output",
        status: "review",
        title: "New output texture",
        before: "not in approved package",
        after: current,
        action: "Ask TA to confirm this output belongs in the package.",
      });
      continue;
    }
    if (approved !== current) {
      diffs.push({
        id: `changed-output-${textureName}`,
        channel: "output",
        status: "review",
        title: `${textureName} settings changed`,
        before: approved,
        after: current,
        action: "Verify compression, color space, mipmaps, group, and estimated size.",
      });
    }
  }

  for (const approved of lastApproved.outputFingerprints) {
    const textureName = approved.split("|")[0];
    if (!currentFingerprints.some((current) => current.startsWith(`${textureName}|`))) {
      diffs.push({
        id: `removed-output-${textureName}`,
        channel: "output",
        status: "review",
        title: "Approved output missing",
        before: approved,
        after: "not in frozen manifest",
        action: "Restore the output or record an explicit removal approval.",
      });
    }
  }

  if (lastApproved.totalEstimatedSizeMb !== frozenManifest.totalEstimatedSizeMb) {
    diffs.push({
      id: "package-size-delta",
      channel: "size",
      status: "review",
      title: "Estimated package size changed",
      before: `${lastApproved.totalEstimatedSizeMb} MB`,
      after: `${frozenManifest.totalEstimatedSizeMb} MB`,
      action: "Confirm package budget impact before replacing the approved build.",
    });
  }

  if (editSummary.changedCount > 0) {
    diffs.push({
      id: "runtime-preset-overrides",
      channel: "preset",
      status: promotion.gate === "Blocked" ? "block" : "review",
      title: "Runtime preset edits need owner approval",
      before: editSummary.sourcePresetLabel,
      after: editSummary.changedFields.join("; "),
      action: "Promote the staged preset or attach reviewer approval to this package.",
    });
  }

  if (!isQueueComplete(queueSummary, queueTasks)) {
    diffs.push({
      id: "queue-not-complete",
      channel: "queue",
      status: "block",
      title: "Queue has not completed cleanly",
      before: "all tasks done",
      after: `${queueSummary.done} done, ${queueSummary.failed} failed, ${queueSummary.retrying} retrying, ${queueSummary.skipped} skipped`,
      action: queueRecovery.recoveryAction === "none" ? "Run the queue to completion." : queueRecovery.statusLabel,
    });
  }

  for (const risk of risks.filter((item) => item.severity !== "info")) {
    diffs.push({
      id: `risk-${risk.id}`,
      channel: "risk",
      status: risk.gate === "Blocked" ? "block" : "review",
      title: risk.title,
      before: "approved package had no open risk",
      after: risk.detail,
      action: risk.suggestedAction,
    });
  }

  if (diffs.length === 0) {
    diffs.push({
      id: "no-publish-delta",
      channel: "manifest",
      status: "pass",
      title: "Frozen manifest matches the approved package",
      before: lastApproved.manifestHash,
      after: frozenManifest.hash,
      action: "Package can reuse the approved delivery contract.",
    });
  }

  return diffs;
}

function buildTexturePublishChecklist(
  gate: TextureDeliveryGate,
  queueSummary: TextureQueueSummary,
  queueTasks: TextureQueueTask[],
  promotion: TexturePresetPromotionReport,
  diffs: TexturePublishDiffItem[],
  frozenManifest: TextureFrozenManifest,
): TexturePublishChecklistItem[] {
  const hasBlockingDiff = diffs.some((diff) => diff.status === "block");
  const hasReviewDiff = diffs.some((diff) => diff.status === "review");
  return [
    {
      id: "deterministic_package_gate",
      label: "Package gate",
      status: gate === "Blocked" ? "block" : gate === "Review" ? "review" : "pass",
      detail: gate === "Ready" ? "Source, packing, platform, and budget checks are clean." : `${gate} risks must be resolved or accepted.`,
    },
    {
      id: "queue_completion",
      label: "Queue completion",
      status: isQueueComplete(queueSummary, queueTasks) ? "pass" : "block",
      detail: `${queueSummary.done}/${queueTasks.length} task(s) done, ${queueSummary.failed} failed, ${queueSummary.retrying} retrying, ${queueSummary.skipped} skipped.`,
    },
    {
      id: "preset_promotion",
      label: "Preset promotion",
      status: promotion.gate === "Blocked" ? "block" : promotion.gate === "Review" ? "review" : "pass",
      detail: promotion.publishSummary,
    },
    {
      id: "manifest_freeze",
      label: "Manifest freeze",
      status: frozenManifest.itemCount > 0 ? "pass" : "block",
      detail: `${frozenManifest.itemCount} item(s), ${frozenManifest.totalEstimatedSizeMb} MB, hash ${frozenManifest.hash}.`,
    },
    {
      id: "approved_delta",
      label: "Approved delta",
      status: hasBlockingDiff ? "block" : hasReviewDiff ? "review" : "pass",
      detail: hasReviewDiff || hasBlockingDiff
        ? `${diffs.filter((diff) => diff.status !== "pass").length} publish diff(s) require review.`
        : "No meaningful delta against the last approved package.",
    },
  ];
}

function getPublishGate(checklist: TexturePublishChecklistItem[]): TextureDeliveryGate {
  if (checklist.some((item) => item.status === "block")) {
    return "Blocked";
  }
  if (checklist.some((item) => item.status === "review")) {
    return "Review";
  }
  return "Ready";
}

function getPublishDecision(gate: TextureDeliveryGate): TexturePublishDecision {
  if (gate === "Blocked") {
    return "blocked";
  }
  if (gate === "Review") {
    return "needs_review";
  }
  return "ready_to_publish";
}

function buildTextureReviewPacket(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  gate: TextureDeliveryGate,
  decision: TexturePublishDecision,
  frozenManifest: TextureFrozenManifest,
  lastApproved: TextureApprovedPackage,
  diffs: TexturePublishDiffItem[],
  risks: TextureRiskItem[],
): TextureReviewPacket {
  const reviewers = buildTextureReviewers(diffs, risks);
  const diffSummary = diffs.filter((diff) => diff.status !== "pass").map((diff) => diff.title);
  const packetId = stableTextureId("review", `${frozenManifest.manifestId}|${decision}|${diffSummary.join("|")}`);

  return {
    packetId,
    gate,
    title: `${fixture.name} ${platform.label} texture publish`,
    reviewers,
    summary: diffSummary.length > 0
      ? `${diffSummary.length} item(s) need review before replacing ${lastApproved.id}.`
      : `Frozen manifest can reuse ${lastApproved.id}.`,
    attachments: [
      "frozen manifest",
      "publish diff",
      "risk gate",
      "queue trace",
      "preset diff",
      "platform import manifest",
    ],
    handoffMessage: buildTextureReviewHandoffMessage(fixture, platform, gate, decision, frozenManifest, diffSummary),
  };
}

function buildTextureReviewers(diffs: TexturePublishDiffItem[], risks: TextureRiskItem[]): string[] {
  const reviewers = new Set<string>(["TA Texture"]);
  if (diffs.some((diff) => ["manifest", "output", "size"].includes(diff.channel))) {
    reviewers.add("Build Pipeline");
  }
  if (risks.some((risk) => ["platform", "budget"].includes(risk.channel))) {
    reviewers.add("Platform TA");
  }
  if (diffs.some((diff) => diff.channel === "preset")) {
    reviewers.add("Preset Owner");
  }
  return [...reviewers];
}

function buildTextureReviewHandoffMessage(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  gate: TextureDeliveryGate,
  decision: TexturePublishDecision,
  frozenManifest: TextureFrozenManifest,
  diffSummary: string[],
): string {
  return [
    `[Texture Publish] ${fixture.name}`,
    `Decision: ${decision}`,
    `Gate: ${gate}`,
    `Platform: ${platform.label}`,
    `Frozen manifest: ${frozenManifest.manifestId}`,
    `Estimate: ${frozenManifest.totalEstimatedSizeMb} MB`,
    `Review items: ${diffSummary.length > 0 ? diffSummary.join("; ") : "none"}`,
  ].join("\n");
}

function buildTextureApprovedPackageDelta(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  publishPackage: TexturePublishPackage,
): TextureApprovedPackageDelta {
  const { frozenManifest, lastApproved } = publishPackage;
  const approvedByTexture = new Map(lastApproved.outputFingerprints.map((fingerprint) => [fingerprint.split("|")[0], fingerprint]));
  const currentByTexture = new Map(frozenManifest.items.map((item) => [item.textureName, item]));
  const rows: TextureApprovedDeltaRow[] = frozenManifest.items.map((item) => {
    const before = approvedByTexture.get(item.textureName);
    const state: TextureApprovedDeltaState = before ? (before === item.settingsSignature ? "unchanged" : "changed") : "added";
    return {
      id: `${fixture.id}-${item.textureName}`,
      textureName: item.textureName,
      state,
      mutationScope: state === "unchanged" ? "metadata_only" : "file_write",
      before: before ?? "not in approved package",
      after: item.settingsSignature,
      importPath: item.importPath,
      sourceSignature: item.sourceSignature,
      reason: buildTextureDeltaReason(state, item.textureName),
      ownerAction: buildTextureDeltaOwnerAction(state, publishPackage.gate),
    };
  });

  for (const approved of lastApproved.outputFingerprints) {
    const textureName = approved.split("|")[0];
    if (currentByTexture.has(textureName)) {
      continue;
    }
    rows.push({
      id: `${fixture.id}-${textureName}-removed`,
      textureName,
      state: "removed",
      mutationScope: publishPackage.gate === "Blocked" ? "blocked" : "file_write",
      before: approved,
      after: "not in frozen manifest",
      importPath: `${platform.importRoot}/${fixture.assetCode}/${textureName}`,
      sourceSignature: "approved package only",
      reason: "Previously approved output is absent from the frozen manifest.",
      ownerAction: "Record explicit removal approval before replacing the package.",
    });
  }

  const blockedRows = publishPackage.gate === "Blocked"
    ? rows.map<TextureApprovedDeltaRow>((row) => ({
        ...row,
        state: row.state === "unchanged" ? row.state : "blocked",
        mutationScope: row.state === "unchanged" ? row.mutationScope : "blocked",
        ownerAction: row.state === "unchanged"
          ? row.ownerAction
          : "Resolve blocking publish checklist items before any file write.",
      }))
    : rows;
  const counts = countTextureDeltaRows(blockedRows);
  const committedManifest = buildTextureCommittedManifest(fixture, publishPackage, blockedRows, counts);

  return {
    reportVersion: "texture-approved-package-delta@0.1.0",
    deltaId: stableTextureId("txdelta", `${lastApproved.id}|${frozenManifest.manifestId}|${blockedRows.map((row) => `${row.textureName}:${row.state}`).join("|")}`),
    fixtureId: fixture.id,
    gate: publishPackage.gate,
    decision: publishPackage.decision,
    publicFixture: buildTexturePublicFixtureContract(fixture),
    baselinePackageId: lastApproved.id,
    frozenManifestId: frozenManifest.manifestId,
    committedManifestId: committedManifest.manifestId,
    summary: {
      ...counts,
      fileWriteCount: blockedRows.filter((row) => row.mutationScope === "file_write" || row.mutationScope === "engine_import").length,
      metadataOnlyCount: blockedRows.filter((row) => row.mutationScope === "metadata_only").length,
      nextAction: buildTextureApprovedDeltaNextAction(publishPackage.gate, counts),
    },
    rows: blockedRows,
    committedManifest,
  };
}

function buildTexturePublicFixtureContract(fixture: TextureAssetFixture): TexturePublicFixtureContract {
  const isPublicFixture = fixture.sourceRoot.startsWith("<repo>/fixtures/");
  return {
    fixtureId: fixture.id,
    scope: isPublicFixture ? "portfolio_public_synthetic" : "synthetic_reference",
    license: isPublicFixture ? "CC0-style synthetic fixture, authored for portfolio reproduction" : "Synthetic internal-path reference data",
    sourceRoot: fixture.sourceRoot,
    targetRoot: fixture.targetRoot,
    reproductionNote: isPublicFixture
      ? "Fixture paths, names, channel roles, and expected outputs are public-safe and can be regenerated locally."
      : "Fixture is useful for logic comparison but should not be used as public package evidence.",
    privacyNote: isPublicFixture
      ? "No proprietary asset name, project code, or internal storage path is embedded."
      : "Internal-style path is anonymized but not sufficient for public evidence closure.",
    files: fixture.sourceFiles.map<TexturePublicFixtureFile>((file) => ({
      role: file.role,
      fileName: file.fileName,
      path: `${fixture.sourceRoot}/${file.fileName}`,
      dimensions: `${file.width}x${file.height}`,
      colorSpace: file.colorSpace,
      sourceLicense: isPublicFixture ? "synthetic_public" : "synthetic_reference",
    })),
  };
}

function buildTextureCommittedManifest(
  fixture: TextureAssetFixture,
  publishPackage: TexturePublishPackage,
  rows: TextureApprovedDeltaRow[],
  counts: Pick<TextureCommittedManifest, "added" | "changed" | "unchanged" | "removed" | "blocked">,
): TextureCommittedManifest {
  const status = publishPackage.gate === "Blocked"
    ? "blocked"
    : publishPackage.gate === "Review"
      ? "review_required"
      : "ready_to_commit";
  const files = publishPackage.frozenManifest.items.map<TextureCommittedManifestFile>((item) => {
    const row = rows.find((candidate) => candidate.textureName === item.textureName);
    return {
      id: `${fixture.id}-${item.outputId}`,
      textureName: item.textureName,
      state: row?.state ?? "added",
      mutationScope: row?.mutationScope ?? "file_write",
      importPath: item.importPath,
      settingsSignature: item.settingsSignature,
      sourceSignature: item.sourceSignature,
    };
  });

  return {
    manifestId: stableTextureId("commit", `${publishPackage.frozenManifest.manifestId}|${rows.map((row) => row.after).join("|")}`),
    reportVersion: "texture-committed-manifest@0.1.0",
    status,
    fixtureId: fixture.id,
    packageId: `${fixture.assetCode}_${fixture.textureSet}_${publishPackage.frozenManifest.platformId}@${publishPackage.frozenManifest.hash}`,
    baselinePackageId: publishPackage.lastApproved.id,
    frozenManifestId: publishPackage.frozenManifest.manifestId,
    committedAt: "2026-07-30T21:10:00+08:00",
    targetRoot: fixture.targetRoot,
    owner: publishPackage.lastApproved.owner,
    presetVersionId: publishPackage.frozenManifest.presetVersionId,
    manifestHash: publishPackage.frozenManifest.hash,
    mutationBoundary:
      "Only files listed in this committed manifest may be written by external adapters; AI may summarize and route receipts only.",
    fileCount: files.length,
    ...counts,
    files,
  };
}

function countTextureDeltaRows(rows: TextureApprovedDeltaRow[]): Pick<TextureCommittedManifest, "added" | "changed" | "unchanged" | "removed" | "blocked"> {
  return {
    added: rows.filter((row) => row.state === "added").length,
    changed: rows.filter((row) => row.state === "changed").length,
    unchanged: rows.filter((row) => row.state === "unchanged").length,
    removed: rows.filter((row) => row.state === "removed").length,
    blocked: rows.filter((row) => row.state === "blocked").length,
  };
}

function buildTextureDeltaReason(state: TextureApprovedDeltaState, textureName: string): string {
  if (state === "added") {
    return `${textureName} exists in the frozen manifest but not in the approved baseline.`;
  }
  if (state === "changed") {
    return `${textureName} keeps its output identity but settings fingerprint changed.`;
  }
  if (state === "removed") {
    return `${textureName} was approved previously and is missing from this package.`;
  }
  if (state === "blocked") {
    return `${textureName} is blocked by the publish checklist.`;
  }
  return `${textureName} matches the approved package fingerprint.`;
}

function buildTextureDeltaOwnerAction(state: TextureApprovedDeltaState, gate: TextureDeliveryGate): string {
  if (gate === "Blocked" && state !== "unchanged") {
    return "Resolve publish blockers before approving any mutation.";
  }
  if (state === "added") {
    return "Confirm the new output is expected and belongs in the platform package.";
  }
  if (state === "changed") {
    return "Review compression, color space, mipmap, texture group, and size delta.";
  }
  if (state === "removed") {
    return "Approve removal or restore the missing output.";
  }
  if (state === "blocked") {
    return "Do not commit this file until the blocking checklist item is cleared.";
  }
  return "No owner action required beyond receipt acknowledgement.";
}

function buildTextureApprovedDeltaNextAction(
  gate: TextureDeliveryGate,
  counts: Pick<TextureCommittedManifest, "added" | "changed" | "unchanged" | "removed" | "blocked">,
): string {
  if (gate === "Blocked" || counts.blocked > 0) {
    return "Resolve blocking queue, source, or package checks before committing the manifest.";
  }
  if (counts.added + counts.changed + counts.removed > 0) {
    return "Attach this approved package delta to the Texture TA receipt and request owner signoff.";
  }
  return "Archive the manifest as an unchanged approved package receipt.";
}

function isQueueComplete(queueSummary: TextureQueueSummary, queueTasks: TextureQueueTask[]): boolean {
  return queueTasks.length > 0
    && queueSummary.done === queueTasks.length
    && queueSummary.failed === 0
    && queueSummary.running === 0
    && queueSummary.retrying === 0
    && queueSummary.cancelled === 0
    && queueSummary.skipped === 0
    && queueSummary.queued === 0;
}

function buildOutputFingerprint(item: TextureImportManifestItem): string {
  return [
    item.textureName,
    item.textureGroup,
    item.compression,
    item.colorSpace,
    item.mipmaps ? "mips" : "no-mips",
    item.estimatedSizeMb,
  ].join("|");
}

function stableTextureId(prefix: string, value: string): string {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `${prefix}_${(hash >>> 0).toString(36)}`;
}

function buildTextureAdapterExecutionPlan(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  packedOutputs: TexturePackedOutput[],
  risks: TextureRiskItem[],
  queueTasks: TextureQueueTask[],
  queueSummary: TextureQueueSummary,
  publishPackage: TexturePublishPackage,
): TextureAdapterExecutionPlan {
  const hasSourceBlocker = risks.some((risk) => ["naming", "colorspace", "packing", "platform", "budget"].includes(risk.channel) && risk.gate === "Blocked");
  const queueComplete = isQueueComplete(queueSummary, queueTasks);
  const adapters = textureAdapterProfiles.map((adapter) => ({ ...adapter, reads: [...adapter.reads], writes: [...adapter.writes] }));
  const steps = adapters.map((adapter) => buildTextureAdapterStep(
    adapter,
    fixture,
    platform,
    packedOutputs,
    hasSourceBlocker,
    queueComplete,
    publishPackage,
  ));
  const diagnostics = buildTextureAdapterDiagnostics(steps, risks, queueComplete, publishPackage);
  const gate = highestTextureGate([
    publishPackage.gate,
    ...diagnostics.map((diagnostic) => diagnostic.severity === "error" ? "Blocked" : diagnostic.severity === "warning" ? "Review" : "Ready"),
  ]);

  return {
    planId: stableTextureId("adapter", `${fixture.id}|${platform.id}|${publishPackage.frozenManifest.hash}|${steps.map((step) => step.status).join("|")}`),
    mode: "portfolio_dry_run",
    gate,
    executorPolicy: "Adapters are planned as dry-run commands. No DCC, compressor, or engine process is launched from the portfolio.",
    boundaryRules: [
      "AI can summarize logs and suggest routing only.",
      "Deterministic gates decide whether an adapter can move past dry-run.",
      "Any filesystem mutation must be owned by the adapter process, not by AI text.",
      "Engine import requires a frozen manifest and publish gate context.",
    ],
    adapters,
    steps,
    diagnostics,
    aiLogSummary: buildTextureAdapterAiLogSummary(steps, diagnostics),
  };
}

function buildTextureAdapterStep(
  adapter: TextureAdapterProfile,
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  packedOutputs: TexturePackedOutput[],
  hasSourceBlocker: boolean,
  queueComplete: boolean,
  publishPackage: TexturePublishPackage,
): TextureAdapterPlanStep {
  const status = getAdapterStatus(adapter, hasSourceBlocker, queueComplete, publishPackage);
  const command = buildAdapterCommand(adapter, fixture, platform, packedOutputs, publishPackage);
  const writes = adapter.writes.map((target) => `${fixture.targetRoot}/${adapter.stage}/${target}`);
  const reads = adapter.reads.map((source) => source.includes("manifest")
    ? publishPackage.frozenManifest.manifestId
    : source.includes("source") || source.includes("PSD") || source.includes("Substance")
      ? fixture.sourceRoot
      : source);

  return {
    id: `${fixture.id}-${adapter.id}`,
    adapterId: adapter.id,
    adapterLabel: adapter.label,
    stage: adapter.stage,
    mode: "portfolio_dry_run",
    status,
    command,
    reads,
    writes,
    guard: buildAdapterGuard(adapter, status, publishPackage, hasSourceBlocker, queueComplete),
    mutationAllowed: false,
    logSample: buildAdapterLogSample(adapter, status, fixture, publishPackage),
    aiDiagnostic: buildAdapterAiDiagnostic(adapter, status, publishPackage),
  };
}

function getAdapterStatus(
  adapter: TextureAdapterProfile,
  hasSourceBlocker: boolean,
  queueComplete: boolean,
  publishPackage: TexturePublishPackage,
): TextureAdapterStatus {
  if (hasSourceBlocker && ["compress", "import"].includes(adapter.stage)) {
    return "blocked";
  }
  if (!queueComplete && adapter.stage === "import") {
    return "blocked";
  }
  if (publishPackage.gate === "Blocked" && adapter.stage === "import") {
    return "blocked";
  }
  if (publishPackage.gate === "Review" && adapter.stage === "import") {
    return "dry_run";
  }
  if (adapter.stage === "normalize" || adapter.stage === "export") {
    return hasSourceBlocker ? "dry_run" : "ready";
  }
  return "dry_run";
}

function buildAdapterCommand(
  adapter: TextureAdapterProfile,
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  packedOutputs: TexturePackedOutput[],
  publishPackage: TexturePublishPackage,
): string {
  switch (adapter.id) {
    case "photoshop_normalize":
      return `${adapter.executable} --source ${fixture.sourceRoot} --asset ${fixture.assetCode} --set ${fixture.textureSet} --dry-run`;
    case "substance_export":
      return `${adapter.executable} --preset ${publishPackage.frozenManifest.presetVersionId} --target ${fixture.targetRoot}/raw --dry-run`;
    case "cli_compressor":
      return `${adapter.executable} --platform ${platform.id} --outputs ${packedOutputs.map((output) => output.fileName).join(",")} --dry-run`;
    case "engine_import":
      return `${adapter.executable} --manifest ${publishPackage.frozenManifest.manifestId} --gate ${publishPackage.gate} --dry-run`;
  }
}

function buildAdapterGuard(
  adapter: TextureAdapterProfile,
  status: TextureAdapterStatus,
  publishPackage: TexturePublishPackage,
  hasSourceBlocker: boolean,
  queueComplete: boolean,
): string {
  if (status === "blocked" && hasSourceBlocker) {
    return "Blocked by deterministic source, platform, packing, or budget gate.";
  }
  if (status === "blocked" && !queueComplete) {
    return "Blocked until queue tasks finish and checkpoints are stable.";
  }
  if (adapter.stage === "import" && publishPackage.gate === "Review") {
    return "Engine import stays dry-run until review packet is accepted.";
  }
  return "Portfolio dry-run records command, reads, writes, and logs without mutation.";
}

function buildAdapterLogSample(
  adapter: TextureAdapterProfile,
  status: TextureAdapterStatus,
  fixture: TextureAssetFixture,
  publishPackage: TexturePublishPackage,
): string {
  const lines = [
    `[${adapter.label}] ${status}`,
    `asset=${fixture.assetCode}`,
    `stage=${adapter.stage}`,
    `manifest=${publishPackage.frozenManifest.hash}`,
  ];
  if (status === "blocked") {
    lines.push("result=blocked by gate");
  } else {
    lines.push("result=dry-run trace captured");
  }
  return lines.join("\n");
}

function buildAdapterAiDiagnostic(
  adapter: TextureAdapterProfile,
  status: TextureAdapterStatus,
  publishPackage: TexturePublishPackage,
): string {
  if (status === "blocked") {
    return `${adapter.label} should not run because the package gate is ${publishPackage.gate}.`;
  }
  if (adapter.stage === "import" && publishPackage.gate === "Review") {
    return "AI can prepare review context, but engine import waits for owner approval.";
  }
  return `${adapter.label} can be represented as a dry-run adapter step with deterministic arguments.`;
}

function buildTextureAdapterDiagnostics(
  steps: TextureAdapterPlanStep[],
  risks: TextureRiskItem[],
  queueComplete: boolean,
  publishPackage: TexturePublishPackage,
): TextureAdapterDiagnostic[] {
  const diagnostics: TextureAdapterDiagnostic[] = [];
  for (const step of steps) {
    if (step.status === "blocked") {
      diagnostics.push({
        id: `adapter-blocked-${step.adapterId}`,
        adapterId: step.adapterId,
        severity: "error",
        title: `${step.adapterLabel} is blocked`,
        detail: step.guard,
        action: "Resolve deterministic gates or complete the queue before launching this adapter.",
      });
    } else if (step.status === "dry_run") {
      diagnostics.push({
        id: `adapter-dryrun-${step.adapterId}`,
        adapterId: step.adapterId,
        severity: "warning",
        title: `${step.adapterLabel} stays in dry-run`,
        detail: step.guard,
        action: "Record the trace and attach it to the review packet.",
      });
    }
  }
  if (risks.some((risk) => risk.channel === "colorspace" && risk.gate === "Blocked")) {
    diagnostics.push({
      id: "adapter-colorspace-source",
      adapterId: "photoshop_normalize",
      severity: "error",
      title: "Color space normalization needs source fix",
      detail: "A blocked color space risk exists before external tool launch.",
      action: "Correct the source tag or rerun Photoshop normalize in controlled mode.",
    });
  }
  if (!queueComplete) {
    diagnostics.push({
      id: "adapter-queue-incomplete",
      adapterId: "cli_compressor",
      severity: "error",
      title: "Queue checkpoints are incomplete",
      detail: "Adapter execution cannot prove what was already packed or compressed.",
      action: "Complete or recover the queue before importing to engine.",
    });
  }
  if (publishPackage.gate === "Review") {
    diagnostics.push({
      id: "adapter-review-mode",
      adapterId: "engine_import",
      severity: "warning",
      title: "Engine import is review-bound",
      detail: "Publish package is in review, so engine mutation remains disabled.",
      action: "Use the exported review packet as the handoff artifact.",
    });
  }
  if (diagnostics.length === 0) {
    diagnostics.push({
      id: "adapter-plan-ready",
      adapterId: "cli_compressor",
      severity: "info",
      title: "Adapter plan is ready",
      detail: "All adapter steps have deterministic commands and dry-run boundaries.",
      action: "Archive the adapter plan with the publish report.",
    });
  }
  return diagnostics;
}

function buildTextureAdapterAiLogSummary(
  steps: TextureAdapterPlanStep[],
  diagnostics: TextureAdapterDiagnostic[],
): string {
  const blocked = steps.filter((step) => step.status === "blocked");
  const dryRun = steps.filter((step) => step.status === "dry_run");
  const lines = [
    `Adapter plan: ${steps.length} step(s), ${blocked.length} blocked, ${dryRun.length} dry-run.`,
    `Diagnostics: ${diagnostics.map((diagnostic) => diagnostic.title).join("; ")}.`,
    "AI boundary: summarize logs, group failure reasons, and draft handoff text only.",
    "Mutation boundary: external adapter processes own any filesystem or engine writes.",
  ];
  return lines.join("\n");
}

function makeTextureSource(
  id: string,
  fileName: string,
  role: TextureRole,
  width: number,
  height: number,
  format: TextureSourceFormat,
  colorSpace: TextureColorSpace,
  bitDepth: 8 | 16 | 32,
  hasAlpha: boolean,
  fileSizeMb: number,
): TextureSourceFile {
  return {
    id,
    fileName,
    path: `sourceimages/${fileName}`,
    role,
    width,
    height,
    format,
    colorSpace,
    bitDepth,
    hasAlpha,
    fileSizeMb,
  };
}

function parseTextureFileName(file: TextureSourceFile): ParsedTextureName {
  const stem = file.fileName.replace(/\.[^.]+$/, "");
  const parts = stem.split("_");
  const resolutionToken = parts.find((part) => /^[1-8]K$/i.test(part)) ?? "";
  const roleToken = parts.find((part) => roleTokenMap[part.toUpperCase()] === file.role) ?? "";
  const role = roleToken ? roleTokenMap[roleToken.toUpperCase()] : file.role;
  const textureSetToken = roleToken
    ? parts.slice(Math.max(0, parts.indexOf(roleToken) - 1), parts.indexOf(roleToken)).join("_")
    : "";
  const assetToken = roleToken
    ? parts.slice(0, Math.max(1, parts.indexOf(roleToken) - 1)).join("_")
    : "";
  const warnings: string[] = [];

  if (!roleToken) {
    warnings.push("role token missing");
  }
  if (!resolutionToken) {
    warnings.push("resolution token missing");
  }
  if (!assetToken) {
    warnings.push("asset token missing");
  }

  return {
    fileId: file.id,
    fileName: file.fileName,
    valid: warnings.length === 0,
    assetToken,
    textureSetToken,
    roleToken,
    role,
    resolutionToken,
    warnings,
  };
}

const roleTokenMap: Record<string, TextureRole> = {
  BC: "baseColor",
  BASECOLOR: "baseColor",
  N: "normal",
  NORMAL: "normal",
  R: "roughness",
  ROUGHNESS: "roughness",
  M: "metallic",
  METAL: "metallic",
  METALLIC: "metallic",
  AO: "ao",
  OCCLUSION: "ao",
  E: "emissive",
  EMISSIVE: "emissive",
  A: "opacity",
  ALPHA: "opacity",
  OPACITY: "opacity",
  H: "height",
  HEIGHT: "height",
};

function buildPackedOutputs(
  fixture: TextureAssetFixture,
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
): TexturePackedOutput[] {
  return preset.outputRules.map<TexturePackedOutput>((rule) => {
    const sources = rule.channelMap.map<TextureOutputChannelSource>((entry) => {
      const source = findSourceForRole(fixture, entry.role);
      return {
        channel: entry.channel,
        role: entry.role,
        sourceFileId: source?.id ?? null,
        sourceFileName: source?.fileName ?? "missing",
      };
    });
    const presentRoles = new Set(fixture.sourceFiles.map((file) => file.role));
    const missingRoles = rule.requiredRoles.filter((role) => !presentRoles.has(role));
    const primarySource = rule.requiredRoles.map((role) => findSourceForRole(fixture, role)).find(Boolean)
      ?? fixture.sourceFiles[0];
    const width = Math.min(primarySource?.width ?? platform.maxTextureSize, platform.maxTextureSize);
    const height = Math.min(primarySource?.height ?? platform.maxTextureSize, platform.maxTextureSize);
    const compression = platform.preferredCompression.includes(rule.compression)
      ? rule.compression
      : platform.preferredCompression[0];
    const format = platform.preferredFormat === rule.format ? rule.format : platform.preferredFormat;

    return {
      id: `${fixture.id}-${rule.id}`,
      label: rule.label,
      fileName: `${fixture.assetCode}_${fixture.textureSet}_${rule.suffix}.${format}`,
      outputPath: `${fixture.targetRoot}/${fixture.assetCode}_${fixture.textureSet}_${rule.suffix}.${format}`,
      format,
      compression,
      colorSpace: rule.colorSpace,
      width,
      height,
      mipmaps: rule.mipmaps,
      textureGroup: rule.textureGroup,
      estimatedSizeMb: estimateOutputSize(width, height, compression),
      channelSources: sources,
      missingRoles,
      gate: missingRoles.length > 0 ? "Blocked" : "Ready",
    };
  });
}

function buildTextureRisks(
  fixture: TextureAssetFixture,
  preset: TexturePackingPreset,
  platform: TexturePlatformProfile,
  parsedNames: ParsedTextureName[],
  outputs: TexturePackedOutput[],
): TextureRiskItem[] {
  const risks: TextureRiskItem[] = [];

  for (const parsed of parsedNames) {
    if (!parsed.valid) {
      risks.push({
        id: `naming-${parsed.fileId}`,
        severity: "warning",
        gate: "Review",
        channel: "naming",
        title: "Texture filename cannot be fully parsed",
        detail: `${parsed.fileName} misses ${parsed.warnings.join(", ")}.`,
        evidence: "Naming parser expects <asset>_<set>_<role>_<resolution>.",
        suggestedAction: "Rename or map this source before building the export manifest.",
      });
    }
  }

  for (const file of fixture.sourceFiles) {
    const expectedColorSpace = getExpectedColorSpace(file.role);
    if (file.colorSpace !== expectedColorSpace) {
      risks.push({
        id: `colorspace-${file.id}`,
        severity: file.role === "normal" ? "error" : "warning",
        gate: file.role === "normal" ? "Blocked" : "Review",
        channel: "colorspace",
        title: `${getTextureRoleLabel(file.role)} colorspace mismatch`,
        detail: `${file.fileName} is tagged ${file.colorSpace}, expected ${expectedColorSpace}.`,
        evidence: `${getTextureRoleLabel(file.role)} participates in ${preset.label}.`,
        suggestedAction: "Correct the source file color space tag before packing.",
      });
    }

    if (file.width > platform.maxTextureSize || file.height > platform.maxTextureSize) {
      risks.push({
        id: `platform-size-${file.id}`,
        severity: "error",
        gate: "Blocked",
        channel: "platform",
        title: "Source texture exceeds platform max size",
        detail: `${file.fileName} is ${file.width}x${file.height}, platform limit is ${platform.maxTextureSize}.`,
        evidence: platform.notes,
        suggestedAction: "Downscale this source or switch to a platform profile that accepts the resolution.",
      });
    }

    if (!isPowerOfTwo(file.width) || !isPowerOfTwo(file.height)) {
      risks.push({
        id: `pot-${file.id}`,
        severity: "warning",
        gate: "Review",
        channel: "platform",
        title: "Texture dimensions are not power of two",
        detail: `${file.fileName} is ${file.width}x${file.height}.`,
        evidence: "Mip generation and block compression expect stable power-of-two dimensions.",
        suggestedAction: "Crop or pad the texture before final import.",
      });
    }
  }

  for (const output of outputs) {
    if (output.missingRoles.length > 0) {
      risks.push({
        id: `missing-${output.id}`,
        severity: "error",
        gate: "Blocked",
        channel: "packing",
        title: `${output.label} output has missing channels`,
        detail: `${output.missingRoles.map(getTextureRoleLabel).join(", ")} source role missing.`,
        evidence: output.channelSources.map((source) => `${source.channel}:${source.sourceFileName}`).join("; "),
        suggestedAction: "Restore the missing source file or choose a preset that does not require this channel.",
      });
    }
  }

  const totalSize = outputs.reduce((sum, output) => sum + output.estimatedSizeMb, 0);
  if (totalSize > platform.packageBudgetMb * 1.25) {
    risks.push({
      id: "package-budget-block",
      severity: "error",
      gate: "Blocked",
      channel: "budget",
      title: "Estimated texture package exceeds block budget",
      detail: `${roundMb(totalSize)} MB against ${platform.packageBudgetMb} MB budget.`,
      evidence: outputs.map((output) => `${output.fileName}:${output.estimatedSizeMb} MB`).join("; "),
      suggestedAction: "Downscale, change compression, or split the texture set before publish.",
    });
  } else if (totalSize > platform.packageBudgetMb) {
    risks.push({
      id: "package-budget-review",
      severity: "warning",
      gate: "Review",
      channel: "budget",
      title: "Estimated texture package exceeds review budget",
      detail: `${roundMb(totalSize)} MB against ${platform.packageBudgetMb} MB budget.`,
      evidence: outputs.map((output) => `${output.fileName}:${output.estimatedSizeMb} MB`).join("; "),
      suggestedAction: "Ask TA or platform owner to accept the size or pick a tighter preset.",
    });
  }

  if (risks.length === 0) {
    risks.push({
      id: "texture-package-ready",
      severity: "info",
      gate: "Ready",
      channel: "queue",
      title: "Texture package is ready for export",
      detail: "All required source roles are present and platform constraints are satisfied.",
      evidence: `${outputs.length} output file(s) will be written to ${fixture.targetRoot}.`,
      suggestedAction: "Run the queue and archive the generated manifest.",
    });
  }

  return risks;
}

type TextureQueueTaskSeed = Omit<
  TextureQueueTask,
  | "attempts"
  | "checkpoint"
  | "commandDiff"
  | "failureClass"
  | "log"
  | "recoveryAction"
  | "retryCommand"
  | "status"
>;

function buildTextureQueueTasks(
  fixture: TextureAssetFixture,
  preset: TexturePackingPreset,
  outputs: TexturePackedOutput[],
  risks: TextureRiskItem[],
  mode: TextureQueueMode,
): TextureQueueTask[] {
  const hasBlocker = risks.some((risk) => risk.gate === "Blocked");
  const failureClass = classifyTextureQueueFailure(risks, hasBlocker);
  const baseTasks: TextureQueueTaskSeed[] = [
    {
      id: "parse_sources",
      label: "Parse source names",
      stage: "parse",
      outputId: null,
      command: `scan_sourceimages --root ${fixture.sourceRoot}`,
      durationMs: 640,
      canRetry: false,
    },
    ...outputs.flatMap((output) => [
      {
        id: `pack_${output.id}`,
        label: `Pack ${output.label}`,
        stage: "pack" as const,
        outputId: output.id,
        command: `pack_channels --preset ${preset.id} --output ${output.outputPath}`,
        durationMs: 1800 + Math.round(output.estimatedSizeMb * 45),
        canRetry: true,
      },
      {
        id: `compress_${output.id}`,
        label: `Compress ${output.label}`,
        stage: "compress" as const,
        outputId: output.id,
        command: `compress_texture --codec ${output.compression} --input ${output.outputPath}`,
        durationMs: 1300 + Math.round(output.estimatedSizeMb * 60),
        canRetry: true,
      },
    ]),
    {
      id: "write_manifest",
      label: "Write platform manifest",
      stage: "manifest",
      outputId: null,
      command: `write_import_manifest --target ${fixture.targetRoot}`,
      durationMs: 420,
      canRetry: true,
    },
    {
      id: "sync_engine",
      label: "Sync import manifest",
      stage: "sync",
      outputId: null,
      command: `sync_to_engine --asset ${fixture.assetCode}`,
      durationMs: 760,
      canRetry: true,
    },
  ];
  const failureIndex = getQueueFailureIndex(baseTasks, hasBlocker);

  return baseTasks.map<TextureQueueTask>((task, index) => {
    const status = getQueueStatusForMode(mode, index, baseTasks.length, hasBlocker, task.stage, failureIndex);
    const checkpoint = buildQueueCheckpoint(task, index);
    const taskFailureClass = status === "failed" || status === "retrying"
      ? failureClass
      : status === "cancelled"
        ? "operator_cancelled"
        : "none";
    const recoveryAction = getQueueRecoveryAction(status, taskFailureClass, hasBlocker);
    const retryCommand = buildRetryCommand(task.command, status, recoveryAction, checkpoint);
    const commandDiff = buildQueueCommandDiff(task.command, retryCommand, status, recoveryAction, checkpoint);
    return {
      ...task,
      retryCommand,
      status,
      log: buildQueueLog(task.label, status, hasBlocker),
      attempts: buildQueueAttempts(task, status, mode, index, failureIndex),
      failureClass: taskFailureClass,
      recoveryAction,
      commandDiff,
      checkpoint,
    };
  });
}

function getQueueStatusForMode(
  mode: TextureQueueMode,
  index: number,
  total: number,
  hasBlocker: boolean,
  stage: TextureQueueTask["stage"],
  failureIndex: number,
): TextureQueueStatus {
  if (mode === "dry_run") {
    return "queued";
  }
  if (mode === "submitted") {
    return index === 0 ? "done" : "queued";
  }
  if (mode === "processing") {
    if (index === 0) {
      return "done";
    }
    return index === 1 ? "running" : "queued";
  }
  if (mode === "failed") {
    if (index < failureIndex) {
      return "done";
    }
    return index === failureIndex ? "failed" : "skipped";
  }
  if (mode === "cancelled") {
    if (index < failureIndex) {
      return "done";
    }
    return index === failureIndex ? "cancelled" : "skipped";
  }
  if (mode === "retrying") {
    if (index < failureIndex) {
      return "done";
    }
    return index === failureIndex ? "retrying" : "skipped";
  }
  if (mode === "resumed") {
    if (hasBlocker) {
      if (index < failureIndex) {
        return "done";
      }
      return index === failureIndex ? "retrying" : "skipped";
    }
    if (index <= failureIndex) {
      return "done";
    }
    return index === Math.min(failureIndex + 1, total - 1) ? "running" : "queued";
  }
  if (hasBlocker && stage !== "parse") {
    return "skipped";
  }
  return index < total ? "done" : "queued";
}

function buildQueueLog(label: string, status: TextureQueueStatus, hasBlocker: boolean): string {
  switch (status) {
    case "queued":
      return `${label} is waiting for queue execution.`;
    case "running":
      return `${label} is running with deterministic command arguments.`;
    case "done":
      return `${label} completed and wrote trace metadata.`;
    case "failed":
      return `${label} failed, inspect channel mapping and compression input.`;
    case "skipped":
      return hasBlocker ? `${label} skipped because package blockers are unresolved.` : `${label} skipped by queue mode.`;
    case "cancelled":
      return `${label} was cancelled after checkpoint metadata was written.`;
    case "retrying":
      return `${label} is retrying from its last stable checkpoint.`;
  }
}

function buildTextureQueueSummary(tasks: TextureQueueTask[]): TextureQueueSummary {
  return {
    queued: tasks.filter((task) => task.status === "queued").length,
    running: tasks.filter((task) => task.status === "running").length,
    done: tasks.filter((task) => task.status === "done").length,
    failed: tasks.filter((task) => task.status === "failed").length,
    skipped: tasks.filter((task) => task.status === "skipped").length,
    cancelled: tasks.filter((task) => task.status === "cancelled").length,
    retrying: tasks.filter((task) => task.status === "retrying").length,
  };
}

function buildTextureQueueRecoverySummary(
  mode: TextureQueueMode,
  tasks: TextureQueueTask[],
  risks: TextureRiskItem[],
): TextureQueueRecoverySummary {
  const activeTask = tasks.find((task) => ["failed", "retrying", "cancelled", "running"].includes(task.status)) ?? null;
  const hasBlocker = risks.some((risk) => risk.gate === "Blocked");
  const failureClass = activeTask?.failureClass ?? classifyTextureQueueFailure(risks, hasBlocker);
  const recoveryAction = activeTask?.recoveryAction ?? (hasBlocker ? "resolve_gate" : "none");
  const checkpoint = activeTask?.checkpoint ?? "queue:start";
  const commandBefore = activeTask?.command ?? "";
  const commandAfter = activeTask?.retryCommand ?? commandBefore;
  const commandDiff = activeTask?.commandDiff ?? [];

  return {
    mode,
    statusLabel: textureQueueModeStatusLabels[mode],
    failureClass,
    recoveryAction,
    activeTaskId: activeTask?.id ?? null,
    activeTaskLabel: activeTask?.label ?? "No active recovery task",
    checkpoint,
    commandBefore,
    commandAfter,
    commandDiff,
    auditTrail: buildQueueAuditTrail(mode, activeTask, risks, hasBlocker),
  };
}

function classifyTextureQueueFailure(risks: TextureRiskItem[], hasBlocker: boolean): TextureQueueFailureClass {
  if (!hasBlocker) {
    return "external_process";
  }
  if (risks.some((risk) => risk.channel === "budget" && risk.gate === "Blocked")) {
    return "budget_gate";
  }
  if (risks.some((risk) => risk.channel === "platform" && risk.gate === "Blocked")) {
    return "platform_gate";
  }
  if (risks.some((risk) => ["packing", "naming", "colorspace"].includes(risk.channel) && risk.gate === "Blocked")) {
    return "source_contract";
  }
  return "source_contract";
}

function getQueueFailureIndex(tasks: TextureQueueTaskSeed[], hasBlocker: boolean): number {
  if (hasBlocker) {
    return Math.max(1, tasks.findIndex((task) => task.stage === "pack"));
  }
  const compressIndex = tasks.findIndex((task) => task.stage === "compress");
  return compressIndex >= 0 ? compressIndex : Math.max(1, tasks.length - 2);
}

function getQueueRecoveryAction(
  status: TextureQueueStatus,
  failureClass: TextureQueueFailureClass,
  hasBlocker: boolean,
): TextureQueueRecoveryAction {
  if (status === "cancelled") {
    return "resume_from_checkpoint";
  }
  if (status === "failed" || status === "retrying") {
    return hasBlocker || failureClass === "platform_gate" || failureClass === "budget_gate" || failureClass === "source_contract"
      ? "resolve_gate"
      : "retry_failed_task";
  }
  return "none";
}

function buildRetryCommand(
  command: string,
  status: TextureQueueStatus,
  recoveryAction: TextureQueueRecoveryAction,
  checkpoint: string,
): string {
  if (recoveryAction === "none") {
    return command;
  }
  if (recoveryAction === "resolve_gate") {
    return `${command} --dry-run --gate-report ${checkpoint}`;
  }
  if (status === "cancelled" || recoveryAction === "resume_from_checkpoint") {
    return `${command} --resume ${checkpoint} --attempt 2`;
  }
  return `${command} --retry ${checkpoint} --attempt 2`;
}

function buildQueueCommandDiff(
  command: string,
  retryCommand: string,
  status: TextureQueueStatus,
  recoveryAction: TextureQueueRecoveryAction,
  checkpoint: string,
): TextureQueueCommandDiff[] {
  if (command === retryCommand || recoveryAction === "none") {
    return [];
  }
  const diffs: TextureQueueCommandDiff[] = [
    {
      field: "attempt",
      before: "1",
      after: "2",
      reason: status === "retrying" ? "Retry keeps original deterministic arguments." : "Recovery command must be traceable.",
    },
    {
      field: "checkpoint",
      before: "queue:start",
      after: checkpoint,
      reason: "Queue recovery resumes from the last stable task boundary.",
    },
  ];
  if (recoveryAction === "resolve_gate") {
    diffs.push({
      field: "mode",
      before: "execute",
      after: "dry-run gate report",
      reason: "Blocked packages should not mutate target files before deterministic gates pass.",
    });
  }
  return diffs;
}

function buildQueueAttempts(
  task: TextureQueueTaskSeed,
  status: TextureQueueStatus,
  mode: TextureQueueMode,
  index: number,
  failureIndex: number,
): TextureQueueAttempt[] {
  if (status === "queued" || status === "skipped") {
    return [];
  }
  if (mode === "resumed" && index === failureIndex && status === "done") {
    return [
      { attempt: 1, status: "failed", durationMs: task.durationMs, log: `${task.label} failed before recovery.` },
      { attempt: 2, status: "done", durationMs: Math.round(task.durationMs * 0.72), log: `${task.label} resumed from checkpoint.` },
    ];
  }
  if (status === "retrying") {
    return [
      { attempt: 1, status: "failed", durationMs: task.durationMs, log: `${task.label} failed before retry.` },
      { attempt: 2, status: "retrying", durationMs: Math.round(task.durationMs * 0.4), log: `${task.label} retry is active.` },
    ];
  }
  return [
    {
      attempt: 1,
      status,
      durationMs: task.durationMs,
      log: buildQueueLog(task.label, status, false),
    },
  ];
}

function buildQueueCheckpoint(task: TextureQueueTaskSeed, index: number): string {
  return `${String(index + 1).padStart(2, "0")}:${task.stage}:${task.outputId ?? "asset"}`;
}

function buildQueueAuditTrail(
  mode: TextureQueueMode,
  activeTask: TextureQueueTask | null,
  risks: TextureRiskItem[],
  hasBlocker: boolean,
): string[] {
  const riskSummary = risks.filter((risk) => risk.severity !== "info").map((risk) => risk.title);
  const lines = [
    `Queue mode: ${textureQueueModeStatusLabels[mode]}.`,
    activeTask ? `Active task: ${activeTask.label} at ${activeTask.checkpoint}.` : "No active task, queue is stable.",
  ];
  if (hasBlocker) {
    lines.push(`Gate blockers: ${riskSummary.join("; ")}.`);
  }
  if (activeTask?.commandDiff.length) {
    lines.push(`Command diff: ${activeTask.commandDiff.map((diff) => `${diff.field} ${diff.before}->${diff.after}`).join("; ")}.`);
  }
  if (!hasBlocker && !activeTask) {
    lines.push("All tasks can proceed without recovery.");
  }
  return lines;
}

const textureQueueModeStatusLabels: Record<TextureQueueMode, string> = {
  dry_run: "Dry run queued",
  submitted: "Submitted",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
  retrying: "Retrying",
  resumed: "Resumed",
};

function buildTextureNotification(report: {
  fixtureName: string;
  gate: TextureDeliveryGate;
  platformLabel: string;
  presetLabel: string;
  totalEstimatedSizeMb: number;
  riskCount: number;
  queueSummary: TextureQueueSummary;
}): string {
  return [
    `[Texture Delivery] ${report.fixtureName}`,
    `Gate: ${report.gate}`,
    `Preset: ${report.presetLabel}`,
    `Platform: ${report.platformLabel}`,
    `Estimate: ${report.totalEstimatedSizeMb} MB`,
    `Risks: ${report.riskCount}`,
    `Queue: ${report.queueSummary.done} done / ${report.queueSummary.failed} failed / ${report.queueSummary.queued} queued`,
  ].join("\n");
}

function buildTextureAiRiskBrief(
  fixture: TextureAssetFixture,
  platform: TexturePlatformProfile,
  preset: TexturePackingPreset,
  risks: TextureRiskItem[],
  gate: TextureDeliveryGate,
): string {
  const blockers = risks.filter((risk) => risk.gate === "Blocked");
  const reviews = risks.filter((risk) => risk.gate === "Review");
  const lines = [
    `${fixture.name}: texture delivery gate is ${gate}.`,
    `Preset ${preset.label} targets ${platform.label}.`,
  ];
  if (blockers.length > 0) {
    lines.push(`Blockers: ${blockers.map((risk) => risk.title).join("; ")}.`);
  }
  if (reviews.length > 0) {
    lines.push(`Review: ${reviews.map((risk) => risk.title).join("; ")}.`);
  }
  if (blockers.length === 0 && reviews.length === 0) {
    lines.push("All deterministic channel, naming, platform, and budget checks passed.");
  }
  lines.push("AI text summarizes the deterministic package state. It does not override packing rules.");
  return lines.join("\n");
}

function findSourceForRole(fixture: TextureAssetFixture, role: TextureRole): TextureSourceFile | undefined {
  return fixture.sourceFiles.find((file) => file.role === role);
}

function getExpectedColorSpace(role: TextureRole): TextureColorSpace {
  return role === "baseColor" || role === "emissive" ? "sRGB" : "linear";
}

function estimateOutputSize(width: number, height: number, compression: TextureCompression): number {
  const megapixels = (width * height) / (1024 * 1024);
  const mbPerMegapixel: Record<TextureCompression, number> = {
    BC7: 1,
    BC5: 1,
    BC1: 0.5,
    ASTC_6x6: 0.9,
    ASTC_8x8: 0.55,
    RGBA8: 4,
  };
  return roundMb(megapixels * mbPerMegapixel[compression]);
}

function highestTextureGate(gates: TextureDeliveryGate[]): TextureDeliveryGate {
  if (gates.includes("Blocked")) {
    return "Blocked";
  }
  if (gates.includes("Review")) {
    return "Review";
  }
  return "Ready";
}

function isPowerOfTwo(value: number): boolean {
  return value > 0 && (value & (value - 1)) === 0;
}

function roundMb(value: number): number {
  return Math.round(value * 10) / 10;
}

function appendPresetDiff(
  diffs: TexturePresetDiffItem[],
  sourceRule: TextureOutputRule,
  editedRule: TextureOutputRule,
  field: TexturePresetEditField,
  before: string,
  after: string,
) {
  if (before === after) {
    return;
  }
  diffs.push({
    ruleId: editedRule.id,
    ruleLabel: sourceRule.label,
    field,
    before,
    after,
  });
}

function cloneTexturePackingPreset(preset: TexturePackingPreset): TexturePackingPreset {
  return {
    ...preset,
    outputRules: preset.outputRules.map(cloneOutputRule),
  };
}

function cloneOutputRule(rule: TextureOutputRule): TextureOutputRule {
  return {
    ...rule,
    requiredRoles: [...rule.requiredRoles],
    channelMap: cloneChannelMap(rule.channelMap),
  };
}

function cloneChannelMap(channelMap: TextureChannelMapEntry[]): TextureChannelMapEntry[] {
  return channelMap.map((entry) => ({ ...entry }));
}

const roleLabels: Record<TextureRole, string> = {
  baseColor: "BaseColor",
  normal: "Normal",
  roughness: "Roughness",
  metallic: "Metallic",
  ao: "AO",
  emissive: "Emissive",
  opacity: "Opacity",
  height: "Height",
};
