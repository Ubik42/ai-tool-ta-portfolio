import { useState } from "react";
import { ClipboardCheck, Cuboid, FileJson, ListChecks, PackageSearch, ShieldCheck } from "lucide-react";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

type HandoffActionId = "fixture" | "collect" | "evaluate" | "actions" | "export" | "decision" | "preflight" | "compare";

interface HandoffAction {
  id: HandoffActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface HandoffAssetRow {
  id: string;
  node: string;
  gate: string;
  role: string;
  lod: string;
  platform: string;
  materials: number;
  textures: number;
  review: string[];
  blockers: string[];
}

interface HandoffPreviewAction {
  id: string;
  asset: string;
  kind: string;
  label: string;
  preview: string;
}

interface HandoffDisposition {
  id: string;
  asset: string;
  owner: string;
  state: string;
  decision: string;
  reason: string;
}

interface EngineHandoffIntent {
  id: string;
  asset: string;
  state: string;
  intent: string;
  enginePath: string;
}

interface EnginePreflightRow {
  id: string;
  asset: string;
  state: string;
  preset: string;
  enginePath: string;
  disposition: string;
  checks: string[];
}

interface EngineImportSidecar {
  id: string;
  asset: string;
  enginePath: string;
  platformPreset: string;
  preview: string;
}

interface PresetComparisonSummary {
  preset: string;
  gate: string;
  ready: number;
  held: number;
  blocked: number;
  sidecars: number;
}

interface PresetComparisonRow {
  id: string;
  asset: string;
  delta: string;
  states: string;
  reasons: string[];
}

interface HandoffResult {
  action: HandoffActionId;
  label: string;
  raw: unknown;
  gate: string;
  assetCount: number;
  ready: number;
  review: number;
  blocked: number;
  actionCount: number;
  path?: string;
  assets: HandoffAssetRow[];
  actions: HandoffPreviewAction[];
  dispositions: HandoffDisposition[];
  engineRows: EngineHandoffIntent[];
  preflightRows: EnginePreflightRow[];
  importSidecars: EngineImportSidecar[];
  presetSummaries: PresetComparisonSummary[];
  comparisonRows: PresetComparisonRow[];
}

const handoffActions: HandoffAction[] = [
  { id: "fixture", label: "Fixture", method: "asset_handoff_create_fixture" },
  { id: "collect", label: "Collect", method: "asset_handoff_collect" },
  { id: "evaluate", label: "Evaluate Gate", method: "asset_handoff_evaluate_gate" },
  { id: "actions", label: "Preview Actions", method: "asset_handoff_preview_actions" },
  { id: "export", label: "Export Packet", method: "asset_handoff_export_packet" },
  { id: "decision", label: "Decision Packet", method: "asset_handoff_export_decision_packet" },
  { id: "preflight", label: "Engine Preflight", method: "engine_handoff_export_preflight_packet" },
  { id: "compare", label: "Preset Compare", method: "engine_handoff_export_preset_comparison" },
];

export function AssetHandoffGatePanel() {
  const [snapshot, setSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [busyAction, setBusyAction] = useState<HandoffActionId | null>(null);
  const [result, setResult] = useState<HandoffResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const connected = snapshot.available;

  async function runAction(action: HandoffAction) {
    const latest = getBridgeSnapshot();
    setSnapshot(latest);

    if (!latest.available) {
      setError("Open this workbench through the Maya AuroraView host to run the handoff gate.");
      return;
    }

    setBusyAction(action.id);
    setError(null);

    try {
      const params =
        action.id === "fixture"
          ? { name: "r10_3_asset_handoff" }
          : action.id === "preflight" || action.id === "compare"
            ? {
                label: action.id === "compare" ? "r10-9-engine-preset-comparison" : "r10-8-engine-handoff-preflight",
                include_all: true,
                ...(action.id === "compare" ? { platform_presets: ["pc", "mobile"] } : { platform_preset: "pc" }),
              }
            : action.id === "export" || action.id === "decision"
              ? {
                  label: action.id === "decision" ? "r10-7-asset-handoff-decision-packet" : "r10-7-asset-handoff-gate",
                  include_all: true,
                }
            : { include_all: true };
      const raw = await callMayaBridge<unknown>(action.method, params);
      setResult(normalizeHandoffResult(action, raw));
      setSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Asset handoff gate call failed.");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <section className="rail-panel handoff-gate-panel">
      <div className="rail-title">
        <ShieldCheck size={17} aria-hidden="true" />
        <h3>Asset Handoff Gate</h3>
      </div>

      <div className="handoff-state-row">
        <span className="bridge-state" data-state={connected ? "connected" : "offline"}>
          {connected ? "Connected" : "Preview"}
        </span>
        <strong data-gate={result?.gate ?? "Preview"}>{result?.gate ?? "Preview"}</strong>
      </div>

      <div className="handoff-action-grid" aria-label="Asset handoff gate actions">
        {handoffActions.map((action) => {
          const busy = busyAction === action.id;
          const Icon = iconForAction(action.id);

          return (
            <button
              className="bridge-action-button"
              disabled={!connected || busyAction !== null}
              key={action.id}
              onClick={() => runAction(action)}
              type="button"
            >
              <Icon size={15} aria-hidden="true" />
              <span>{busy ? "Running" : action.label}</span>
            </button>
          );
        })}
      </div>

      {error ? <div className="bridge-error" role="alert">{error}</div> : null}

      <div className="handoff-summary-grid">
        <div>
          <span>Assets</span>
          <strong>{result?.assetCount ?? "-"}</strong>
        </div>
        <div>
          <span>Ready</span>
          <strong>{result?.ready ?? "-"}</strong>
        </div>
        <div>
          <span>Review</span>
          <strong>{result?.review ?? "-"}</strong>
        </div>
        <div>
          <span>Actions</span>
          <strong>{result?.actionCount ?? "-"}</strong>
        </div>
      </div>

      {result ? (
        <>
          {result.assets.length > 0 ? (
            <div className="handoff-asset-list">
              {result.assets.slice(0, 4).map((asset) => (
                <article data-gate={asset.gate} key={asset.id}>
                  <div>
                    <strong>{asset.node}</strong>
                    <span>{asset.gate}</span>
                  </div>
                  <p>{asset.role} / {asset.platform} / {asset.lod}</p>
                  <code>materials={asset.materials} textures={asset.textures}</code>
                  {asset.review.length || asset.blockers.length ? (
                    <small>{[...asset.blockers, ...asset.review].slice(0, 2).join(" / ")}</small>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}

          {result.actions.length > 0 ? (
            <div className="handoff-action-list">
              {result.actions.slice(0, 5).map((item) => (
                <article data-kind={item.kind} key={item.id}>
                  <div>
                    <strong>{item.label}</strong>
                    <span>{item.kind}</span>
                  </div>
                  <code>{item.asset}</code>
                  <p>{item.preview}</p>
                </article>
              ))}
            </div>
          ) : null}

          {result.dispositions.length > 0 ? (
            <div className="handoff-decision-list">
              {result.dispositions.slice(0, 5).map((item) => (
                <article data-state={item.state} key={item.id}>
                  <div>
                    <strong>{item.owner}</strong>
                    <span>{item.state}</span>
                  </div>
                  <code>{item.asset}</code>
                  <p>{item.decision}</p>
                  <small>{item.reason}</small>
                </article>
              ))}
            </div>
          ) : null}

          {result.engineRows.length > 0 ? (
            <div className="handoff-engine-list">
              {result.engineRows.slice(0, 5).map((item) => (
                <article data-state={item.state} key={item.id}>
                  <div>
                    <strong>{item.intent}</strong>
                    <span>{item.state}</span>
                  </div>
                  <code>{item.asset}</code>
                  <p>{item.enginePath}</p>
                </article>
              ))}
            </div>
          ) : null}

          {result.preflightRows.length > 0 ? (
            <div className="handoff-preflight-list">
              {result.preflightRows.slice(0, 5).map((item) => (
                <article data-state={item.state} key={item.id}>
                  <div>
                    <strong>{item.disposition}</strong>
                    <span>{item.state}</span>
                  </div>
                  <code>{item.asset}</code>
                  <p>{item.preset} / {item.enginePath}</p>
                  <small>{item.checks.slice(0, 3).join(" / ")}</small>
                </article>
              ))}
            </div>
          ) : null}

          {result.importSidecars.length > 0 ? (
            <div className="handoff-sidecar-list">
              {result.importSidecars.slice(0, 4).map((item) => (
                <article key={item.id}>
                  <div>
                    <strong>{item.platformPreset}</strong>
                    <span>sidecar</span>
                  </div>
                  <code>{item.enginePath}</code>
                  <p>{item.preview}</p>
                </article>
              ))}
            </div>
          ) : null}

          {result.presetSummaries.length > 0 ? (
            <div className="handoff-preset-summary-list">
              {result.presetSummaries.map((item) => (
                <article data-gate={item.gate} key={item.preset}>
                  <div>
                    <strong>{item.preset}</strong>
                    <span>{item.gate}</span>
                  </div>
                  <p>ready {item.ready} / held {item.held} / blocked {item.blocked}</p>
                  <code>sidecars={item.sidecars}</code>
                </article>
              ))}
            </div>
          ) : null}

          {result.comparisonRows.length > 0 ? (
            <div className="handoff-comparison-list">
              {result.comparisonRows.slice(0, 5).map((item) => (
                <article data-delta={item.delta} key={item.id}>
                  <div>
                    <strong>{item.delta}</strong>
                    <span>{item.states}</span>
                  </div>
                  <code>{item.asset}</code>
                  <p>{item.reasons.slice(0, 2).join(" / ") || "same state across presets"}</p>
                </article>
              ))}
            </div>
          ) : null}

          {result.path ? <code className="handoff-output-path">{result.path}</code> : null}

          <details className="handoff-json">
            <summary>JSON Payload</summary>
            <pre>{safeJson(result.raw)}</pre>
          </details>
        </>
      ) : (
        <p className="empty-state">Create a handoff fixture, then evaluate the Maya publish gate.</p>
      )}
    </section>
  );
}

function normalizeHandoffResult(action: HandoffAction, raw: unknown): HandoffResult {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const decisionPacket = asRecord(record?.decisionPacket ?? report?.decisionPacket);
  const preflightPacket = asRecord(record?.preflightPacket ?? report?.preflightPacket);
  const comparisonPacket = asRecord(record?.comparisonPacket ?? report?.comparisonPacket);
  const evaluation = asRecord(record?.evaluation ?? decisionPacket?.evaluation ?? report);
  const collect = asRecord(record?.collect ?? evaluation?.collect ?? report?.collect);
  const summary = asRecord(
    record?.summary ??
      comparisonPacket?.summary ??
      preflightPacket?.summary ??
      decisionPacket?.summary ??
      evaluation?.summary ??
      report?.summary ??
      collect?.summary,
  );
  const assets = normalizeAssets(record?.assets ?? evaluation?.assets ?? report?.assets ?? collect?.assets);
  const actions = normalizeActions(record?.actions ?? decisionPacket?.repairPreview ?? report?.actions);
  const dispositions = normalizeDispositions(decisionPacket?.ownerDispositions ?? record?.ownerDispositions);
  const engineRows = normalizeEngineRows(decisionPacket?.engineHandoff ?? record?.engineHandoff);
  const preflightRows = normalizePreflightRows(preflightPacket?.preflightRows ?? record?.preflightRows);
  const importSidecars = normalizeImportSidecars(preflightPacket?.importSidecars ?? record?.importSidecars);
  const presetSummaries = normalizePresetSummaries(comparisonPacket?.presetSummaries ?? record?.presetSummaries);
  const comparisonRows = normalizeComparisonRows(comparisonPacket?.comparisonRows ?? record?.comparisonRows);
  const fixtureNodes = Array.isArray(record?.nodes) ? record.nodes.length : 0;

  return {
    action: action.id,
    label: action.label,
    raw,
    gate: readString(summary?.gate) ?? (action.id === "fixture" ? "Ready" : "Preview"),
    assetCount: readNumber(summary?.asset_count) ?? (assets.length || fixtureNodes),
    ready: readNumber(summary?.ready) ?? readNumber(summary?.preflight_ready) ?? readNumber(summary?.platform_split) ?? 0,
    review: readNumber(summary?.review) ?? 0,
    blocked: readNumber(summary?.blocked) ?? 0,
    actionCount:
      readNumber(summary?.total) ??
      readNumber(summary?.repair_action_count) ??
      readNumber(summary?.import_sidecars) ??
      readNumber(summary?.ready_sidecars) ??
      actions.length,
    path: readString(record?.path) ?? undefined,
    assets,
    actions,
    dispositions,
    engineRows,
    preflightRows,
    importSidecars,
    presetSummaries,
    comparisonRows,
  };
}

function iconForAction(action: HandoffActionId) {
  if (action === "fixture") {
    return Cuboid;
  }
  if (action === "collect" || action === "preflight") {
    return PackageSearch;
  }
  if (action === "evaluate" || action === "compare") {
    return ClipboardCheck;
  }
  if (action === "actions") {
    return ListChecks;
  }
  if (action === "decision") {
    return ShieldCheck;
  }
  return FileJson;
}

function normalizeAssets(value: unknown): HandoffAssetRow[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.asset_id) ?? readString(item.id) ?? `asset-${index + 1}`,
    node: readString(item.node) ?? "<node>",
    gate: readString(item.gate) ?? "Preview",
    role: readString(item.role) ?? "unknown",
    lod: readString(item.lod) ?? "unknown",
    platform: readString(item.platform) ?? "unknown",
    materials: readNumber(item.materials) ?? readNumber(item.material_count) ?? 0,
    textures: readNumber(item.textures) ?? readNumber(item.texture_count) ?? 0,
    review: readStringArray(item.review),
    blockers: readStringArray(item.blockers),
  }));
}

function normalizeActions(value: unknown): HandoffPreviewAction[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `action-${index + 1}`,
    asset: readString(item.asset) ?? "<asset>",
    kind: readString(item.kind) ?? "manual_only",
    label: readString(item.label) ?? readString(item.repair_type) ?? "<action>",
    preview: readString(item.preview) ?? readString(item.preview_command) ?? readString(item.risk) ?? "-",
  }));
}

function normalizeDispositions(value: unknown): HandoffDisposition[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `disposition-${index + 1}`,
    asset: readString(item.asset) ?? "<asset>",
    owner: readString(item.owner) ?? "TA",
    state: readString(item.state) ?? "review",
    decision: readString(item.decision) ?? "hold_engine_handoff",
    reason: readString(item.reason) ?? "-",
  }));
}

function normalizeEngineRows(value: unknown): EngineHandoffIntent[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `engine-${index + 1}`,
    asset: readString(item.asset) ?? "<asset>",
    state: readString(item.state) ?? "held_for_review",
    intent: readString(item.intent) ?? "skip_engine_import_until_disposition",
    enginePath: readString(item.engine_path) ?? "-",
  }));
}

function normalizePreflightRows(value: unknown): EnginePreflightRow[] {
  return asRecordArray(value).map((item, index) => {
    const checks = asRecordArray(item.checks).map((check) => {
      const label = readString(check.label) ?? "check";
      const status = readString(check.status) ?? "preview";
      return `${label}:${status}`;
    });

    return {
      id: readString(item.id) ?? `preflight-${index + 1}`,
      asset: readString(item.asset) ?? "<asset>",
      state: readString(item.state) ?? "held_for_owner_disposition",
      preset: readString(item.preset) ?? "pc",
      enginePath: readString(item.engine_path) ?? "-",
      disposition: readString(item.disposition) ?? "hold_engine_import",
      checks,
    };
  });
}

function normalizeImportSidecars(value: unknown): EngineImportSidecar[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `sidecar-${index + 1}`,
    asset: readString(item.asset) ?? "<asset>",
    enginePath: readString(item.engine_path) ?? "-",
    platformPreset: readString(item.platform_preset) ?? "pc",
    preview: readString(item.preview_command) ?? "-",
  }));
}

function normalizePresetSummaries(value: unknown): PresetComparisonSummary[] {
  return asRecordArray(value).map((item) => ({
    preset: readString(item.preset) ?? "<preset>",
    gate: readString(item.gate) ?? "Preview",
    ready: readNumber(item.preflight_ready) ?? 0,
    held: readNumber(item.held) ?? 0,
    blocked: readNumber(item.blocked) ?? 0,
    sidecars: readNumber(item.import_sidecars) ?? 0,
  }));
}

function normalizeComparisonRows(value: unknown): PresetComparisonRow[] {
  return asRecordArray(value).map((item, index) => {
    const states = asRecord(item.presetStates) ?? {};
    const reasons = asRecord(item.blockingReasons) ?? {};
    const reasonLines = Object.entries(reasons).flatMap(([preset, value]) =>
      readStringArray(value).map((reason) => `${preset}: ${reason}`),
    );

    return {
      id: readString(item.asset_id) ?? `comparison-${index + 1}`,
      asset: readString(item.asset) ?? "<asset>",
      delta: readString(item.delta) ?? "same_state",
      states: Object.entries(states)
        .map(([preset, state]) => `${preset}:${typeof state === "string" ? state : "preview"}`)
        .join(" / "),
      reasons: reasonLines,
    };
  });
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

function readStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function safeJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return error instanceof Error ? error.message : "Unable to serialize payload.";
  }
}
