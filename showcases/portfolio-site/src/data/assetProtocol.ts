export type AssetPlatform = "PC" | "Mobile" | "Console";

export type ProtocolCarrier = "uv3" | "vertexColor" | "customAttr";

export type RuleSeverity = "pass" | "warning" | "error";

export type EditableProtocolKey =
  | "platform"
  | "lodCount"
  | "collision"
  | "nanite"
  | "streamable"
  | "screenSize"
  | "cullDistance"
  | "materialSlots"
  | "textureSets"
  | "semanticCarrier"
  | "semanticMask"
  | "uv3U";

export interface AssetProtocolFixture {
  id: string;
  name: string;
  schemaVersion: string;
  category: "vehicle" | "prop" | "character";
  platform: AssetPlatform;
  lodCount: number;
  collision: "complex" | "simple" | "missing";
  nanite: boolean;
  streamable: boolean;
  screenSize: number;
  cullDistance: number;
  materialSlots: number;
  textureSets: number;
  semanticCarrier: ProtocolCarrier;
  semanticMask: number;
  uv3U: number;
  authoringNote: string;
}

export interface RuleResult {
  id: string;
  label: string;
  severity: RuleSeverity;
  passed: boolean;
  message: string;
  fix?: string;
}

export interface EncodedProtocol {
  assetId: string;
  schemaVersion: string;
  customAttrs: Record<string, string | number | boolean>;
  uv3: {
    uClass: number;
    vMask: number;
    maskBinary: string;
  };
  delivery: {
    platform: AssetPlatform;
    lodCount: number;
    materialSlots: number;
    textureSets: number;
  };
}

export interface ProtocolDiffEntry {
  field: EditableProtocolKey;
  label: string;
  before: string;
  after: string;
}

export interface EncodedDiffEntry {
  path: string;
  before: string;
  after: string;
}

export interface FixPreviewAction {
  id: string;
  label: string;
  kind: "safe" | "manual";
  field: EditableProtocolKey;
  before: string;
  after: string;
  reason: string;
}

export interface ProtocolAuditEvent {
  id: string;
  revision: number;
  label: string;
  kind: "safe" | "manual" | "preset";
  field: string;
  before: string;
  after: string;
}

export interface ProtocolRiskBrief {
  headline: string;
  gate: "Ready" | "Needs Review" | "Blocked";
  priority: string;
  bullets: string[];
}

export interface ProtocolEditPreset {
  id: string;
  name: string;
  intent: string;
  apply: (asset: AssetProtocolFixture) => AssetProtocolFixture;
  evidence: string[];
}

export interface AssetProtocolReport {
  reportVersion: string;
  generatedBy: string;
  asset: {
    id: string;
    name: string;
    category: AssetProtocolFixture["category"];
    schemaVersion: string;
  };
  readiness: ReturnType<typeof getProtocolReadiness>;
  aiRiskBrief: ProtocolRiskBrief;
  protocolDiff: ProtocolDiffEntry[];
  encodedPayloadDiff: EncodedDiffEntry[];
  validation: RuleResult[];
  fixPreview: FixPreviewAction[];
  auditTrail: ProtocolAuditEvent[];
  encodedPayload: EncodedProtocol;
}

export const assetProtocolSchema = {
  version: "lb_asset_protocol@1.1.0",
  fields: [
    {
      key: "platform",
      label: "Platform",
      carrier: "customAttr",
      description: "Runtime target and budget profile.",
    },
    {
      key: "lodCount",
      label: "LOD Count",
      carrier: "customAttr",
      description: "Number of authored runtime LOD levels.",
    },
    {
      key: "collision",
      label: "Collision",
      carrier: "customAttr",
      description: "Collision authoring state consumed by publish checks.",
    },
    {
      key: "nanite",
      label: "Nanite",
      carrier: "customAttr",
      description: "Platform-sensitive rendering switch.",
    },
    {
      key: "streamable",
      label: "Streamable",
      carrier: "customAttr",
      description: "Streaming eligibility for large assets.",
    },
    {
      key: "semanticMask",
      label: "Semantic Mask",
      carrier: "uv3 / vertexColor / customAttr",
      description: "Bitmask carrying stacked business states.",
    },
    {
      key: "uv3U",
      label: "UV3 U Class",
      carrier: "uv3",
      description: "Discrete class value for mutually exclusive semantic categories.",
    },
  ],
} as const;

const fieldLabels: Record<EditableProtocolKey, string> = {
  platform: "Platform",
  lodCount: "LOD Count",
  collision: "Collision",
  nanite: "Nanite",
  streamable: "Streamable",
  screenSize: "Screen Size",
  cullDistance: "Cull Distance",
  materialSlots: "Material Slots",
  textureSets: "Texture Sets",
  semanticCarrier: "Semantic Carrier",
  semanticMask: "Semantic Mask",
  uv3U: "UV3 U Class",
};

const diffFields = Object.keys(fieldLabels) as EditableProtocolKey[];

export const protocolEditPresets: ProtocolEditPreset[] = [
  {
    id: "mobile-cleanup",
    name: "Mobile cleanup",
    intent: "Stage a mobile-safe protocol pass for assets that still carry PC-style budget flags.",
    apply: (asset) => ({
      ...asset,
      platform: "Mobile",
      nanite: false,
      collision: asset.collision === "missing" ? "simple" : asset.collision,
      lodCount: Math.max(asset.lodCount, 2),
      textureSets: Math.min(asset.textureSets, 3),
      cullDistance: Math.min(asset.cullDistance || 9000, 9000),
      screenSize: Math.min(asset.screenSize, 0.55),
    }),
    evidence: ["platform budget diff", "Nanite gate pass", "texture set budget"],
  },
  {
    id: "lod-prep",
    name: "LOD prep",
    intent: "Stage geometry delivery fields before sending the asset into an LOD generation queue.",
    apply: (asset) => ({
      ...asset,
      lodCount: Math.max(asset.lodCount, 4),
      streamable: true,
      screenSize: Math.max(asset.screenSize, 0.7),
      cullDistance: asset.cullDistance > 0 ? asset.cullDistance : 8000,
    }),
    evidence: ["LOD count diff", "streaming flag", "distance budget"],
  },
  {
    id: "material-sync",
    name: "Material sync",
    intent: "Stage a conservative material and texture slot alignment preview.",
    apply: (asset) => ({
      ...asset,
      textureSets: asset.materialSlots,
      semanticCarrier: asset.semanticCarrier === "customAttr" ? "uv3" : asset.semanticCarrier,
      uv3U: asset.uv3U > 0 ? asset.uv3U : 0.25,
    }),
    evidence: ["material texture count", "semantic carrier", "payload channel"],
  },
];

export const assetFixtures: AssetProtocolFixture[] = [
  {
    id: "vehicle_pc_ready",
    name: "Vehicle Body / PC ready",
    schemaVersion: assetProtocolSchema.version,
    category: "vehicle",
    platform: "PC",
    lodCount: 4,
    collision: "complex",
    nanite: false,
    streamable: true,
    screenSize: 0.72,
    cullDistance: 8200,
    materialSlots: 5,
    textureSets: 5,
    semanticCarrier: "uv3",
    semanticMask: 13,
    uv3U: 0.34,
    authoringNote: "Vehicle light/glass/body flags are encoded in UV3 and mirrored to custom attrs for review.",
  },
  {
    id: "mobile_crate_risky",
    name: "Mobile Crate / risky",
    schemaVersion: assetProtocolSchema.version,
    category: "prop",
    platform: "Mobile",
    lodCount: 1,
    collision: "missing",
    nanite: true,
    streamable: true,
    screenSize: 0.58,
    cullDistance: 12000,
    materialSlots: 4,
    textureSets: 5,
    semanticCarrier: "customAttr",
    semanticMask: 2,
    uv3U: 0,
    authoringNote: "Mobile risk case: Nanite on, too many texture sets.",
  },
  {
    id: "character_lod_partial",
    name: "Hero Character / LOD partial",
    schemaVersion: assetProtocolSchema.version,
    category: "character",
    platform: "Console",
    lodCount: 3,
    collision: "simple",
    nanite: false,
    streamable: false,
    screenSize: 0.9,
    cullDistance: 0,
    materialSlots: 7,
    textureSets: 6,
    semanticCarrier: "vertexColor",
    semanticMask: 7,
    uv3U: 0.66,
    authoringNote: "Character fixture keeps normal/tangent payload visible but still exceeds material budget.",
  },
];

export function encodeAssetProtocol(asset: AssetProtocolFixture): EncodedProtocol {
  return {
    assetId: asset.id,
    schemaVersion: asset.schemaVersion,
    customAttrs: {
      LB_platform: asset.platform,
      LB_lod_count: asset.lodCount,
      LB_collision: asset.collision,
      LB_nanite: asset.nanite,
      LB_streamable: asset.streamable,
      LB_screen_size: asset.screenSize,
      LB_cull_distance: asset.cullDistance,
      LB_semantic_carrier: asset.semanticCarrier,
    },
    uv3: {
      uClass: Number(asset.uv3U.toFixed(2)),
      vMask: asset.semanticMask,
      maskBinary: asset.semanticMask.toString(2).padStart(4, "0"),
    },
    delivery: {
      platform: asset.platform,
      lodCount: asset.lodCount,
      materialSlots: asset.materialSlots,
      textureSets: asset.textureSets,
    },
  };
}

export function diffAssetProtocol(
  before: AssetProtocolFixture,
  after: AssetProtocolFixture,
): ProtocolDiffEntry[] {
  return diffFields.flatMap((field) => {
    const beforeValue = formatProtocolValue(before[field]);
    const afterValue = formatProtocolValue(after[field]);

    if (beforeValue === afterValue) {
      return [];
    }

    return [
      {
        field,
        label: fieldLabels[field],
        before: beforeValue,
        after: afterValue,
      },
    ];
  });
}

export function diffEncodedProtocol(
  before: EncodedProtocol,
  after: EncodedProtocol,
): EncodedDiffEntry[] {
  const beforeFlat = flattenEncodedProtocol(before);
  const afterFlat = flattenEncodedProtocol(after);
  const paths = Array.from(new Set([...Object.keys(beforeFlat), ...Object.keys(afterFlat)])).sort();

  return paths.flatMap((path) => {
    const beforeValue = beforeFlat[path] ?? "<missing>";
    const afterValue = afterFlat[path] ?? "<missing>";

    if (beforeValue === afterValue) {
      return [];
    }

    return [
      {
        path,
        before: beforeValue,
        after: afterValue,
      },
    ];
  });
}

export function applyProtocolPreset(
  asset: AssetProtocolFixture,
  preset: ProtocolEditPreset,
): AssetProtocolFixture {
  return preset.apply(asset);
}

export function previewProtocolPreset(
  asset: AssetProtocolFixture,
  preset: ProtocolEditPreset,
): ProtocolDiffEntry[] {
  return diffAssetProtocol(asset, applyProtocolPreset(asset, preset));
}

export function previewAutoFix(asset: AssetProtocolFixture) {
  const fixedAsset: AssetProtocolFixture = { ...asset };
  const actions: FixPreviewAction[] = [];

  if (asset.platform === "Mobile" && asset.nanite) {
    fixedAsset.nanite = false;
    actions.push({
      id: "disable-mobile-nanite",
      label: "Disable Nanite for Mobile",
      kind: "safe",
      field: "nanite",
      before: "on",
      after: "off",
      reason: "This is a deterministic protocol flag change and does not invent geometry.",
    });
  }

  if (asset.collision === "missing") {
    actions.push({
      id: "author-collision",
      label: "Author simple collision",
      kind: "manual",
      field: "collision",
      before: "missing",
      after: "simple",
      reason: "Collision geometry must be reviewed by a TA or authored by a mesh generator.",
    });
  }

  if (asset.lodCount < 2) {
    actions.push({
      id: "queue-lod",
      label: "Queue LOD generation",
      kind: "manual",
      field: "lodCount",
      before: String(asset.lodCount),
      after: "2+",
      reason: "LOD generation changes geometry and should remain a queued operation.",
    });
  }

  if (asset.platform === "Mobile" && asset.textureSets > 3) {
    actions.push({
      id: "merge-texture-sets",
      label: "Queue texture-set merge",
      kind: "manual",
      field: "textureSets",
      before: String(asset.textureSets),
      after: "3",
      reason: "Merging texture sets changes material authoring and needs preview evidence.",
    });
  }

  if (Math.abs(asset.materialSlots - asset.textureSets) > 1) {
    actions.push({
      id: "sync-material-texture-count",
      label: "Review material / texture drift",
      kind: "manual",
      field: "materialSlots",
      before: `${asset.materialSlots} materials / ${asset.textureSets} textures`,
      after: "aligned counts",
      reason: "Slot removal can break shader bindings, so the tool previews instead of mutating.",
    });
  }

  return { actions, fixedAsset };
}

export function applySafeProtocolFixes(asset: AssetProtocolFixture): AssetProtocolFixture {
  return previewAutoFix(asset).fixedAsset;
}

export function createProtocolAuditEvents(
  startRevision: number,
  label: string,
  kind: ProtocolAuditEvent["kind"],
  diff: Array<ProtocolDiffEntry | FixPreviewAction>,
): ProtocolAuditEvent[] {
  return diff.map((entry, index) => ({
    id: `${startRevision + index}-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
    revision: startRevision + index,
    label,
    kind,
    field: entry.field,
    before: entry.before,
    after: entry.after,
  }));
}

export function buildAssetProtocolReport(
  baseAsset: AssetProtocolFixture,
  draft: AssetProtocolFixture,
  auditTrail: ProtocolAuditEvent[],
): AssetProtocolReport {
  const validation = validateAssetProtocol(draft);
  const fixPreview = previewAutoFix(draft).actions;
  const encodedPayload = encodeAssetProtocol(draft);

  return {
    reportVersion: "asset-protocol-report@1.0.0",
    generatedBy: "AI Tool TA Portfolio / Asset Protocol Workbench",
    asset: {
      id: draft.id,
      name: draft.name,
      category: draft.category,
      schemaVersion: draft.schemaVersion,
    },
    readiness: getProtocolReadiness(validation),
    aiRiskBrief: summarizeProtocolRisk(draft, validation, fixPreview),
    protocolDiff: diffAssetProtocol(baseAsset, draft),
    encodedPayloadDiff: diffEncodedProtocol(encodeAssetProtocol(baseAsset), encodedPayload),
    validation,
    fixPreview,
    auditTrail,
    encodedPayload,
  };
}

export function summarizeProtocolRisk(
  asset: AssetProtocolFixture,
  results: RuleResult[],
  actions: FixPreviewAction[],
): ProtocolRiskBrief {
  const errors = results.filter((result) => result.severity === "error");
  const warnings = results.filter((result) => result.severity === "warning");
  const manualActions = actions.filter((action) => action.kind === "manual");
  const safeActions = actions.filter((action) => action.kind === "safe");

  if (errors.length > 0) {
    return {
      headline: `${formatCount(errors.length, "gate")} block publish.`,
      gate: "Blocked",
      priority: errors[0].label,
      bullets: [
        `${formatCount(safeActions.length, "safe protocol fix")}.`,
        `${formatCount(manualActions.length, "TA review action")}.`,
        `Priority: ${errors[0].label}.`,
      ],
    };
  }

  if (warnings.length > 0) {
    return {
      headline: "Warnings remain before publish.",
      gate: "Needs Review",
      priority: warnings[0].label,
      bullets: [
        `${formatCount(warnings.length, "warning")} ${
          warnings.length === 1 ? "remains" : "remain"
        } after hard blockers pass.`,
        `${formatCount(manualActions.length, "manual action")} should keep evidence.`,
        `Priority: ${warnings[0].label}.`,
      ],
    };
  }

  return {
    headline: `${asset.name} is ready for protocol packaging.`,
    gate: "Ready",
    priority: "No blocking rule",
    bullets: [
      "All current protocol checks pass.",
      "Encoded payload can be exported as sidecar manifest.",
      "AI summary remains explanatory and does not mutate the asset.",
    ],
  };
}

export function validateAssetProtocol(asset: AssetProtocolFixture): RuleResult[] {
  return [
    {
      id: "semantic-carrier",
      label: "Semantic carrier",
      severity: "pass",
      passed: asset.semanticMask > 0,
      message:
        asset.semanticMask > 0
          ? `${asset.semanticCarrier} carries semantic mask ${asset.semanticMask}.`
          : "No semantic payload is encoded for downstream tools.",
      fix: "Choose UV3, vertex color, or custom attr as the authoritative carrier.",
    },
    {
      id: "mobile-nanite",
      label: "Mobile Nanite gate",
      severity: asset.platform === "Mobile" && asset.nanite ? "error" : "pass",
      passed: asset.platform !== "Mobile" || !asset.nanite,
      message:
        asset.platform === "Mobile" && asset.nanite
          ? "Mobile target cannot publish with Nanite enabled."
          : "Nanite setting is compatible with the selected platform.",
      fix: "Disable Nanite or switch the platform protocol.",
    },
    {
      id: "lod-budget",
      label: "LOD budget",
      severity: asset.lodCount < 2 ? "warning" : "pass",
      passed: asset.lodCount >= 2,
      message:
        asset.lodCount >= 2
          ? `${asset.lodCount} LOD levels are available for runtime switching.`
          : "Only one LOD level exists; review distance and platform budget will be fragile.",
      fix: "Generate at least one additional LOD or lower cull distance.",
    },
    {
      id: "collision",
      label: "Collision protocol",
      severity: asset.collision === "missing" ? "error" : "pass",
      passed: asset.collision !== "missing",
      message:
        asset.collision === "missing"
          ? "Collision is missing while the asset is marked for delivery."
          : `${asset.collision} collision is declared.`,
      fix: "Author collision or mark the asset as visual-only with an explicit exemption.",
    },
    {
      id: "texture-budget",
      label: "Texture budget",
      severity: asset.platform === "Mobile" && asset.textureSets > 3 ? "warning" : "pass",
      passed: asset.platform !== "Mobile" || asset.textureSets <= 3,
      message:
        asset.platform === "Mobile" && asset.textureSets > 3
          ? `${asset.textureSets} texture sets exceed the mobile review budget.`
          : "Texture set count is inside the current platform budget.",
      fix: "Merge texture sets or lower target resolution before publish.",
    },
    {
      id: "material-sync",
      label: "Material / texture sync",
      severity: Math.abs(asset.materialSlots - asset.textureSets) > 1 ? "warning" : "pass",
      passed: Math.abs(asset.materialSlots - asset.textureSets) <= 1,
      message:
        Math.abs(asset.materialSlots - asset.textureSets) <= 1
          ? "Material slots and texture sets are aligned enough for review."
          : "Material slot count and texture set count drift apart.",
      fix: "Run material-slot cleanup or texture-set merge preview.",
    },
  ];
}

function formatProtocolValue(value: AssetProtocolFixture[EditableProtocolKey]): string {
  if (typeof value === "boolean") {
    return value ? "on" : "off";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }

  return value;
}

function formatCount(count: number, label: string): string {
  return `${count} ${label}${count === 1 ? "" : "s"}`;
}

function flattenEncodedProtocol(
  value: EncodedProtocol | Record<string, unknown>,
  prefix = "",
): Record<string, string> {
  return Object.entries(value).reduce<Record<string, string>>((acc, [key, child]) => {
    const path = prefix ? `${prefix}.${key}` : key;

    if (child !== null && typeof child === "object" && !Array.isArray(child)) {
      return {
        ...acc,
        ...flattenEncodedProtocol(child as Record<string, unknown>, path),
      };
    }

    return {
      ...acc,
      [path]: String(child),
    };
  }, {});
}

export function getProtocolReadiness(results: RuleResult[]) {
  const errors = results.filter((result) => result.severity === "error").length;
  const warnings = results.filter((result) => result.severity === "warning").length;
  const passed = results.filter((result) => result.passed).length;
  const score = Math.round((passed / results.length) * 100);

  return {
    score,
    errors,
    warnings,
    status: errors > 0 ? "Blocked" : warnings > 0 ? "Review" : "Ready",
  };
}
