import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Check,
  CircleSlash,
  ClipboardList,
  Download,
  FileJson,
  Gauge,
  GitCompareArrows,
  Layers3,
  PackageCheck,
  PlugZap,
  RefreshCw,
  Settings2,
  ShieldAlert,
  Sparkles,
  Undo2,
} from "lucide-react";
import {
  applyTexturePresetEditorState,
  buildTextureDeliveryReport,
  createTexturePresetEditorState,
  getTexturePlatform,
  getTexturePreset,
  getTexturePresetEditSummary,
  getTextureRoleLabel,
  textureColorSpaceOptions,
  textureCompressionOptions,
  textureDeliveryFixtures,
  textureOutputFormatOptions,
  texturePackingPresets,
  texturePlatforms,
  textureRoleOptions,
  type TextureAdapterDiagnosticSeverity,
  type TextureAdapterStatus,
  type TextureApprovedDeltaState,
  type TextureDeliveryGate,
  type TextureDeliveryReport,
  type TextureColorSpace,
  type TextureCompression,
  type TextureMutationScope,
  type TextureOutputChannel,
  type TextureOutputFormat,
  type TextureOutputRuleEditState,
  type TexturePackingPresetId,
  type TexturePlatformId,
  type TexturePromotionChecklistStatus,
  type TexturePublishChecklistStatus,
  type TexturePublishDecision,
  type TexturePresetEditorState,
  type TextureQueueFailureClass,
  type TextureQueueMode,
  type TextureQueueRecoveryAction,
  type TextureQueueStatus,
  type TextureRiskSeverity,
  type TextureRole,
} from "../data/textureDelivery";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

const textureGateLabels: Record<TextureDeliveryGate, string> = {
  Ready: "Ready",
  Review: "Review",
  Blocked: "Blocked",
};

const textureQueueModeLabels: Record<TextureQueueMode, string> = {
  dry_run: "Dry Run",
  submitted: "Submitted",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
  retrying: "Retrying",
  resumed: "Resumed",
};

const textureQueueStatusLabels: Record<TextureQueueStatus, string> = {
  queued: "Queued",
  running: "Running",
  done: "Done",
  failed: "Failed",
  skipped: "Skipped",
  cancelled: "Cancelled",
  retrying: "Retrying",
};

const riskSeverityLabels: Record<TextureRiskSeverity, string> = {
  info: "Info",
  warning: "Review",
  error: "Block",
};

const queueFailureClassLabels: Record<TextureQueueFailureClass, string> = {
  none: "None",
  source_contract: "Source Contract",
  platform_gate: "Platform Gate",
  budget_gate: "Budget Gate",
  external_process: "External Process",
  operator_cancelled: "Operator Cancelled",
};

const queueRecoveryActionLabels: Record<TextureQueueRecoveryAction, string> = {
  none: "None",
  cancel: "Cancel",
  retry_failed_task: "Retry Failed Task",
  resume_from_checkpoint: "Resume From Checkpoint",
  resolve_gate: "Resolve Gate",
};

const promotionChecklistLabels: Record<TexturePromotionChecklistStatus, string> = {
  pass: "Pass",
  review: "Review",
  block: "Block",
};

const publishChecklistLabels: Record<TexturePublishChecklistStatus, string> = {
  pass: "Pass",
  review: "Review",
  block: "Block",
};

const publishDecisionLabels: Record<TexturePublishDecision, string> = {
  ready_to_publish: "Ready To Publish",
  needs_review: "Needs Review",
  blocked: "Blocked",
};

const approvedDeltaStateLabels: Record<TextureApprovedDeltaState, string> = {
  added: "Added",
  changed: "Changed",
  unchanged: "Unchanged",
  removed: "Removed",
  blocked: "Blocked",
};

const mutationScopeLabels: Record<TextureMutationScope, string> = {
  metadata_only: "Metadata",
  file_write: "File Write",
  engine_import: "Engine Import",
  blocked: "Blocked",
};

const adapterStatusLabels: Record<TextureAdapterStatus, string> = {
  ready: "Ready",
  dry_run: "Dry Run",
  blocked: "Blocked",
  skipped: "Skipped",
};

const adapterDiagnosticLabels: Record<TextureAdapterDiagnosticSeverity, string> = {
  info: "Info",
  warning: "Review",
  error: "Block",
};

type TextureDccActionId = "fixture" | "inspect" | "validate" | "export";

interface TextureDccAction {
  id: TextureDccActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface TextureDccSourceRow {
  node: string;
  fileName: string;
  role: string;
  colorSpace: string;
  expectedColorSpace?: string;
  exists: boolean;
  resolution?: number;
}

interface TextureDccValidationRow {
  ruleId: string;
  label: string;
  status: string;
  evidence: string;
  fixPreview: string;
}

interface TextureDccRun {
  action: TextureDccActionId;
  label: string;
  raw: unknown;
  sourceCount: number;
  materialCount: number;
  meshCount: number;
  gate: string;
  path?: string;
  sources: TextureDccSourceRow[];
  validation: TextureDccValidationRow[];
  updatedAt: string;
}

const textureDccActions: TextureDccAction[] = [
  { id: "fixture", label: "Create Fixture", method: "texture_delivery_create_fixture" },
  { id: "inspect", label: "Inspect Textures", method: "texture_delivery_inspect_scene" },
  { id: "validate", label: "Validate Scene", method: "texture_delivery_validate_scene" },
  { id: "export", label: "Export Manifest", method: "texture_delivery_export_manifest" },
];

export function TextureDeliveryConsole() {
  const [selectedFixtureId, setSelectedFixtureId] = useState(textureDeliveryFixtures[0].id);
  const selectedFixture = useMemo(
    () => textureDeliveryFixtures.find((fixture) => fixture.id === selectedFixtureId) ?? textureDeliveryFixtures[0],
    [selectedFixtureId],
  );
  const [presetId, setPresetId] = useState<TexturePackingPresetId>(selectedFixture.defaultPresetId);
  const [platformId, setPlatformId] = useState<TexturePlatformId>(selectedFixture.defaultPlatformId);
  const [queueMode, setQueueMode] = useState<TextureQueueMode>("dry_run");
  const [presetEditStates, setPresetEditStates] = useState<Partial<Record<TexturePackingPresetId, TexturePresetEditorState>>>({});
  const [selectedRuleId, setSelectedRuleId] = useState(
    () => getTexturePreset(textureDeliveryFixtures[0].defaultPresetId).outputRules[0]?.id ?? "",
  );

  useEffect(() => {
    setPresetId(selectedFixture.defaultPresetId);
    setPlatformId(selectedFixture.defaultPlatformId);
    setQueueMode("dry_run");
    setSelectedRuleId(getTexturePreset(selectedFixture.defaultPresetId).outputRules[0]?.id ?? "");
  }, [selectedFixture]);

  useEffect(() => {
    const sourcePreset = getTexturePreset(presetId);
    const ruleExists = sourcePreset.outputRules.some((rule) => rule.id === selectedRuleId);
    if (!ruleExists) {
      setSelectedRuleId(sourcePreset.outputRules[0]?.id ?? "");
    }
  }, [presetId, selectedRuleId]);

  const sourcePreset = getTexturePreset(presetId);
  const presetEditorState = useMemo(
    () => presetEditStates[presetId] ?? createTexturePresetEditorState(sourcePreset),
    [presetEditStates, presetId, sourcePreset],
  );
  const preset = useMemo(
    () => applyTexturePresetEditorState(sourcePreset, presetEditorState),
    [presetEditorState, sourcePreset],
  );
  const presetEditSummary = useMemo(
    () => getTexturePresetEditSummary(sourcePreset, preset),
    [preset, sourcePreset],
  );
  const platform = getTexturePlatform(platformId);
  const report = useMemo(
    () => buildTextureDeliveryReport(selectedFixture, preset, platform, queueMode, presetEditSummary),
    [platform, preset, presetEditSummary, queueMode, selectedFixture],
  );
  const primaryRisk = report.risks.find((risk) => risk.severity !== "info") ?? report.risks[0];
  const selectedRule = presetEditorState.ruleEdits.find((rule) => rule.ruleId === selectedRuleId)
    ?? presetEditorState.ruleEdits[0];
  const selectedRuleSource = sourcePreset.outputRules.find((rule) => rule.id === selectedRule?.ruleId);
  const [dccSnapshot, setDccSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [dccBusyAction, setDccBusyAction] = useState<TextureDccActionId | null>(null);
  const [dccRun, setDccRun] = useState<TextureDccRun | null>(null);
  const [dccError, setDccError] = useState<string | null>(null);
  const dccConnected = dccSnapshot.available;

  function selectFixture(fixtureId: string) {
    setSelectedFixtureId(fixtureId);
  }

  function updatePresetRule(
    ruleId: string,
    updateRule: (rule: TextureOutputRuleEditState) => TextureOutputRuleEditState,
  ) {
    setPresetEditStates((current) => {
      const baseState = current[presetId] ?? createTexturePresetEditorState(sourcePreset);
      return {
        ...current,
        [presetId]: {
          ...baseState,
          ruleEdits: baseState.ruleEdits.map((rule) => {
            const ruleCopy = {
              ...rule,
              channelMap: rule.channelMap.map((entry) => ({ ...entry })),
            };
            return rule.ruleId === ruleId ? updateRule(ruleCopy) : ruleCopy;
          }),
        },
      };
    });
    setQueueMode("dry_run");
  }

  function updateSelectedRule(patch: Partial<Omit<TextureOutputRuleEditState, "ruleId" | "channelMap">>) {
    if (!selectedRule) {
      return;
    }
    updatePresetRule(selectedRule.ruleId, (rule) => ({ ...rule, ...patch }));
  }

  function updateChannelRole(channel: TextureOutputChannel, role: TextureRole) {
    if (!selectedRule) {
      return;
    }
    updatePresetRule(selectedRule.ruleId, (rule) => ({
      ...rule,
      channelMap: rule.channelMap.map((entry) => (entry.channel === channel ? { ...entry, role } : entry)),
    }));
  }

  function resetPresetEdits() {
    setPresetEditStates((current) => {
      const next = { ...current };
      delete next[presetId];
      return next;
    });
    setQueueMode("dry_run");
  }

  function downloadReport() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${report.fixtureId}-texture-delivery-report.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadReviewPacket() {
    const packet = {
      ...report.publishPackage.reviewPacket,
      frozenManifest: report.publishPackage.frozenManifest,
      diffs: report.publishPackage.diffs,
      checklist: report.publishPackage.checklist,
    };
    const blob = new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${report.fixtureId}-texture-review-packet.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadAdapterPlan() {
    const blob = new Blob([JSON.stringify(report.adapterExecutionPlan, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${report.fixtureId}-texture-adapter-plan.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadCommittedManifest() {
    const blob = new Blob([JSON.stringify(report.committedManifest, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${report.fixtureId}-texture-committed-manifest.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function runTextureDccAction(action: TextureDccAction) {
    const latest = getBridgeSnapshot();
    setDccSnapshot(latest);

    if (!latest.available) {
      setDccError("Open this module through the Maya AuroraView host to run texture delivery DCC actions.");
      return;
    }

    setDccBusyAction(action.id);
    setDccError(null);

    try {
      const result = await callMayaBridge<unknown>(action.method, {
        include_all: true,
        label: "texture-delivery-dcc-scene",
      });
      setDccRun(normalizeTextureDccRun(action, result));
      setDccSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setDccError(caught instanceof Error ? caught.message : "Texture Delivery DCC call failed.");
    } finally {
      setDccBusyAction(null);
    }
  }

  return (
    <div className="texture-delivery-workbench">
      <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>
          贴图交付的核心不是转换格式，而是把命名、通道、颜色空间、压缩、mipmap、平台预算和引擎导入 manifest 放进同一条可复盘队列。
        </p>
      </section>

      <section className="schema-band texture-summary-band" aria-label="texture delivery summary">
        <div>
          <span>Gate</span>
          <strong data-gate={report.gate}>{textureGateLabels[report.gate]}</strong>
        </div>
        <div>
          <span>Outputs</span>
          <strong>{report.outputCount}</strong>
        </div>
        <div>
          <span>Estimate</span>
          <strong>{report.totalEstimatedSizeMb} MB</strong>
        </div>
        <div>
          <span>Queue</span>
          <strong>{textureQueueModeLabels[queueMode]}</strong>
        </div>
      </section>

      <section className="logic-block wide texture-dcc-panel">
        <div className="editor-header">
          <div className="section-title">
            <Layers3 size={17} aria-hidden="true" />
            <h3>Maya Texture Inspection</h3>
          </div>
          <span className="bridge-state" data-state={dccConnected ? "connected" : "offline"}>
            {dccConnected ? "Connected" : "Preview"}
          </span>
        </div>

        <div className="texture-dcc-action-grid" aria-label="Maya texture delivery actions">
          {textureDccActions.map((action) => {
            const busy = dccBusyAction === action.id;

            return (
              <button
                className="bridge-action-button"
                disabled={!dccConnected || dccBusyAction !== null}
                key={action.id}
                onClick={() => runTextureDccAction(action)}
                type="button"
              >
                {action.id === "fixture" ? (
                  <PackageCheck size={15} aria-hidden="true" />
                ) : action.id === "inspect" ? (
                  <Layers3 size={15} aria-hidden="true" />
                ) : action.id === "validate" ? (
                  <ShieldAlert size={15} aria-hidden="true" />
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

        <div className="texture-dcc-summary">
          <div>
            <span>Last Action</span>
            <strong>{dccRun?.label ?? "Not Run"}</strong>
          </div>
          <div>
            <span>Sources</span>
            <strong>{dccRun?.sourceCount ?? "-"}</strong>
          </div>
          <div>
            <span>Materials</span>
            <strong>{dccRun?.materialCount ?? "-"}</strong>
          </div>
          <div>
            <span>Meshes</span>
            <strong>{dccRun?.meshCount ?? "-"}</strong>
          </div>
          <div>
            <span>Gate</span>
            <strong data-gate={dccRun?.gate ?? "Preview"}>{dccRun?.gate ?? "Preview"}</strong>
          </div>
          <div>
            <span>Artifact</span>
            <strong>{dccRun?.path ? "Written" : "Pending"}</strong>
          </div>
        </div>

        {dccRun ? (
          <div className="texture-dcc-grid">
            <div className="texture-dcc-source-list">
              {dccRun.sources.length > 0 ? (
                dccRun.sources.map((source) => (
                  <article data-exists={source.exists ? "true" : "false"} key={`${source.node}-${source.fileName}`}>
                    <div>
                      <strong>{source.fileName}</strong>
                      <span>{source.exists ? "Found" : "Missing"}</span>
                    </div>
                    <p>
                      {source.role} / {source.colorSpace}
                      {source.expectedColorSpace ? ` -> ${source.expectedColorSpace}` : ""}
                    </p>
                    <code>{source.node}{source.resolution ? ` / ${source.resolution}px` : ""}</code>
                  </article>
                ))
              ) : (
                <p className="empty-state">Create a fixture or inspect the Maya scene to populate texture source rows.</p>
              )}
            </div>

            <div className="texture-dcc-validation-list">
              {dccRun.validation.length > 0 ? (
                dccRun.validation.map((row) => (
                  <article data-status={row.status} key={row.ruleId}>
                    <div>
                      <strong>{row.label}</strong>
                      <span>{row.status}</span>
                    </div>
                    <p>{row.evidence}</p>
                    <code>{row.fixPreview}</code>
                  </article>
                ))
              ) : (
                <p className="empty-state">Run validation or export a manifest to show gate rows.</p>
              )}
            </div>

            <div className="texture-dcc-output">
              <span>Output</span>
              <code>{dccRun.path ?? "No DCC artifact path yet."}</code>
              <p>
                Scene inspection maps Maya mesh, material and file nodes into the same delivery contract used by the portfolio fixture.
              </p>
            </div>

            <div className="dcc-rule-json-panel">
              <div className="bridge-result-title">
                <span>{dccRun.path ?? "DCC texture payload"}</span>
                <strong>JSON</strong>
              </div>
              <pre>{safeJson(dccRun.raw)}</pre>
            </div>
          </div>
        ) : (
          <p className="empty-state">
            Create the texture fixture in Maya, then inspect, validate and export the delivery manifest from the embedded UI.
          </p>
        )}
      </section>

      <div className="fixture-tabs texture-fixture-tabs" aria-label="texture delivery fixtures">
        {textureDeliveryFixtures.map((fixture) => (
          <button
            aria-pressed={fixture.id === selectedFixture.id}
            className="fixture-button"
            key={fixture.id}
            onClick={() => selectFixture(fixture.id)}
            type="button"
          >
            <span>{fixture.name}</span>
            <strong>{fixture.assetClass}</strong>
          </button>
        ))}
      </div>

      <section className="logic-block wide texture-control-panel">
        <div className="editor-header">
          <div className="section-title">
            <Gauge size={17} aria-hidden="true" />
            <h3>Delivery Contract</h3>
          </div>
          <button className="primary-button compact" onClick={downloadReport} type="button">
            <Download size={16} aria-hidden="true" />
            <span>Export Report</span>
          </button>
        </div>

        <div className="texture-control-grid">
          <label className="field-control">
            <span>Packing Preset</span>
            <select
              value={presetId}
              onChange={(event) => {
                setPresetId(event.currentTarget.value as TexturePackingPresetId);
                setQueueMode("dry_run");
              }}
            >
              {texturePackingPresets.map((item) => (
                <option key={item.id} value={item.id}>{item.label}</option>
              ))}
            </select>
          </label>

          <label className="field-control">
            <span>Platform</span>
            <select
              value={platformId}
              onChange={(event) => {
                setPlatformId(event.currentTarget.value as TexturePlatformId);
                setQueueMode("dry_run");
              }}
            >
              {texturePlatforms.map((item) => (
                <option key={item.id} value={item.id}>{item.label}</option>
              ))}
            </select>
          </label>

          <div className="texture-contract-card">
            <span>Preset Intent</span>
            <p>{sourcePreset.description}</p>
          </div>

          <div className="texture-contract-card">
            <span>Platform Limit</span>
            <p>{platform.maxTextureSize}px, {platform.packageBudgetMb} MB budget, {platform.preferredFormat.toUpperCase()} preferred.</p>
          </div>
        </div>
      </section>

      {selectedRule && selectedRuleSource && (
        <section className="logic-block wide texture-preset-editor-panel">
          <div className="editor-header">
            <div className="section-title">
              <Settings2 size={17} aria-hidden="true" />
              <h3>Preset Editor</h3>
            </div>
            <button
              className="icon-button compact"
              disabled={presetEditSummary.changedCount === 0}
              onClick={resetPresetEdits}
              type="button"
            >
              <Undo2 size={15} aria-hidden="true" />
              <span>Reset Preset</span>
            </button>
          </div>

          <div className="texture-preset-editor-grid">
            <div className="texture-rule-tabs" aria-label="texture output rules">
              {presetEditorState.ruleEdits.map((rule) => {
                const sourceRule = sourcePreset.outputRules.find((item) => item.id === rule.ruleId);
                const ruleDiffs = presetEditSummary.diffs.filter((diff) => diff.ruleId === rule.ruleId).length;
                return (
                  <button
                    aria-pressed={selectedRule.ruleId === rule.ruleId}
                    key={rule.ruleId}
                    onClick={() => setSelectedRuleId(rule.ruleId)}
                    type="button"
                  >
                    <span>{sourceRule?.label ?? rule.ruleId}</span>
                    <strong>{ruleDiffs} edits</strong>
                  </button>
                );
              })}
            </div>

            <div className="texture-rule-editor-card">
              <div className="texture-rule-editor-head">
                <span>Output Rule</span>
                <strong>{selectedRuleSource.label}</strong>
                <code>{selectedRuleSource.suffix}</code>
              </div>
              <div className="texture-rule-fields">
                <label className="field-control">
                  <span>Format</span>
                  <select
                    value={selectedRule.format}
                    onChange={(event) => updateSelectedRule({ format: event.currentTarget.value as TextureOutputFormat })}
                  >
                    {textureOutputFormatOptions.map((format) => (
                      <option key={format} value={format}>{format.toUpperCase()}</option>
                    ))}
                  </select>
                </label>

                <label className="field-control">
                  <span>Compression</span>
                  <select
                    value={selectedRule.compression}
                    onChange={(event) => updateSelectedRule({ compression: event.currentTarget.value as TextureCompression })}
                  >
                    {textureCompressionOptions.map((compression) => (
                      <option key={compression} value={compression}>{compression}</option>
                    ))}
                  </select>
                </label>

                <label className="field-control">
                  <span>Color Space</span>
                  <select
                    value={selectedRule.colorSpace}
                    onChange={(event) => updateSelectedRule({ colorSpace: event.currentTarget.value as TextureColorSpace })}
                  >
                    {textureColorSpaceOptions.map((colorSpace) => (
                      <option key={colorSpace} value={colorSpace}>{colorSpace}</option>
                    ))}
                  </select>
                </label>

                <label className="field-control">
                  <span>Texture Group</span>
                  <input
                    value={selectedRule.textureGroup}
                    onChange={(event) => updateSelectedRule({ textureGroup: event.currentTarget.value })}
                  />
                </label>
              </div>
              <label className="texture-toggle-row">
                <input
                  checked={selectedRule.mipmaps}
                  onChange={(event) => updateSelectedRule({ mipmaps: event.currentTarget.checked })}
                  type="checkbox"
                />
                <span>Mipmaps</span>
                <strong>{selectedRule.mipmaps ? "Enabled" : "Disabled"}</strong>
              </label>
            </div>

            <div className="texture-channel-editor-card">
              <span>Channel Map</span>
              <div className="texture-channel-editor-grid">
                {selectedRule.channelMap.map((entry) => (
                  <label key={`${selectedRule.ruleId}-${entry.channel}`} className="field-control">
                    <span>{entry.channel}</span>
                    <select
                      value={entry.role}
                      onChange={(event) => updateChannelRole(entry.channel, event.currentTarget.value as TextureRole)}
                    >
                      {textureRoleOptions.map((role) => (
                        <option key={role} value={role}>{getTextureRoleLabel(role)}</option>
                      ))}
                    </select>
                  </label>
                ))}
              </div>
            </div>

            <div className="texture-preset-diff-card" data-mode={presetEditSummary.mode}>
              <div className="section-title">
                <GitCompareArrows size={16} aria-hidden="true" />
                <h4>Preset Diff</h4>
              </div>
              <p>
                {presetEditSummary.changedCount === 0
                  ? "Source preset is unchanged."
                  : `${presetEditSummary.changedCount} runtime override(s) will be archived in the report.`}
              </p>
              <div className="texture-diff-list">
                {presetEditSummary.diffs.length === 0 ? (
                  <div className="texture-diff-row">
                    <span>Source</span>
                    <strong>{sourcePreset.label}</strong>
                    <code>no overrides</code>
                  </div>
                ) : presetEditSummary.diffs.map((diff) => (
                  <div className="texture-diff-row" key={`${diff.ruleId}-${diff.field}`}>
                    <span>{diff.ruleLabel}</span>
                    <strong>{diff.field}</strong>
                    <code>{diff.before} {"->"} {diff.after}</code>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="logic-block wide texture-version-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Preset Versioning</h3>
        </div>
        <div className="texture-version-grid">
          <div className="texture-version-card">
            <span>Approved Baseline</span>
            <strong>{report.presetPromotion.sourceVersion.id}</strong>
            <p>{report.presetPromotion.sourceVersion.notes}</p>
          </div>
          <div className="texture-version-card">
            <span>Staged Version</span>
            <strong>{report.presetPromotion.stagedVersion.id}</strong>
            <p>{report.presetPromotion.stagedVersion.notes}</p>
          </div>
          <div className="texture-version-card" data-gate={report.presetPromotion.gate}>
            <span>Promotion Gate</span>
            <strong>{report.presetPromotion.gate}</strong>
            <p>{report.presetPromotion.compatibilitySummary}</p>
          </div>
          <div className="texture-version-card">
            <span>Publish Summary</span>
            <strong>{report.presetPromotion.changeCount} change(s)</strong>
            <p>{report.presetPromotion.publishSummary}</p>
          </div>
        </div>
        <div className="texture-checklist-list">
          {report.presetPromotion.checklist.map((item) => (
            <div className="texture-checklist-row" data-status={item.status} key={item.id}>
              <span>{promotionChecklistLabels[item.status]}</span>
              <strong>{item.label}</strong>
              <p>{item.detail}</p>
            </div>
          ))}
        </div>
        <div className="texture-fingerprint-block">
          <span>Rule Fingerprint</span>
          <code>{report.presetPromotion.stagedVersion.ruleFingerprint}</code>
        </div>
      </section>

      <section className="logic-block texture-source-panel">
        <div className="section-title">
          <FileJson size={17} aria-hidden="true" />
          <h3>Source Naming Parse</h3>
        </div>
        <div className="texture-source-table" role="table" aria-label="texture source parser">
          <div role="row">
            <span>File</span>
            <span>Role</span>
            <span>Size</span>
            <span>Color</span>
            <span>Parse</span>
          </div>
          {selectedFixture.sourceFiles.map((file) => {
            const parsed = report.parsedNames.find((item) => item.fileId === file.id);
            return (
              <div data-valid={parsed?.valid} key={file.id} role="row">
                <code>{file.fileName}</code>
                <span>{file.role}</span>
                <span>{file.width}x{file.height}</span>
                <span>{file.colorSpace}</span>
                <strong>{parsed?.valid ? "valid" : parsed?.warnings.join(", ")}</strong>
              </div>
            );
          })}
        </div>
      </section>

      <section className="logic-block texture-output-panel">
        <div className="section-title">
          <Layers3 size={17} aria-hidden="true" />
          <h3>Channel Packing Plan</h3>
        </div>
        <div className="texture-output-stack">
          {report.packedOutputs.map((output) => (
            <article className="texture-output-card" data-gate={output.gate} key={output.id}>
              <div className="texture-output-head">
                <div>
                  <span>{output.label}</span>
                  <strong>{output.fileName}</strong>
                </div>
                <b>{output.compression}</b>
              </div>
              <div className="texture-channel-grid">
                {output.channelSources.map((source) => (
                  <div data-missing={source.sourceFileId === null} key={`${output.id}-${source.channel}-${source.role}`}>
                    <span>{source.channel}</span>
                    <strong>{source.role}</strong>
                    <code>{source.sourceFileName}</code>
                  </div>
                ))}
              </div>
              <p>{output.width}x{output.height}, {output.estimatedSizeMb} MB, {output.colorSpace}, {output.mipmaps ? "mips" : "no mips"}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block texture-risk-panel">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Risk Gate</h3>
        </div>
        <div className="texture-risk-stack">
          {report.risks.map((risk) => (
            <article className="texture-risk-row" data-severity={risk.severity} key={risk.id}>
              <div>
                <span>{riskSeverityLabels[risk.severity]}</span>
                <strong>{risk.title}</strong>
                <p>{risk.detail}</p>
              </div>
              <code>{risk.suggestedAction}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block texture-queue-panel">
        <div className="editor-header">
          <div className="section-title">
            <Activity size={17} aria-hidden="true" />
            <h3>Queue Runner</h3>
          </div>
          <div className="mini-toolbar">
            {(["dry_run", "submitted", "processing", "completed", "failed", "cancelled", "retrying", "resumed"] as TextureQueueMode[]).map((mode) => (
              <button
                aria-pressed={queueMode === mode}
                className={queueMode === mode ? "primary-button compact" : "icon-button compact"}
                key={mode}
                onClick={() => setQueueMode(mode)}
                type="button"
              >
                {mode === "completed" || mode === "resumed" ? <Check size={15} aria-hidden="true" /> : mode === "failed" || mode === "cancelled" ? <CircleSlash size={15} aria-hidden="true" /> : <RefreshCw size={15} aria-hidden="true" />}
                <span>{textureQueueModeLabels[mode]}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="texture-queue-summary" aria-label="texture queue summary">
          <div><span>Done</span><strong data-status="done">{report.queueSummary.done}</strong></div>
          <div><span>Running</span><strong data-status="running">{report.queueSummary.running}</strong></div>
          <div><span>Queued</span><strong data-status="queued">{report.queueSummary.queued}</strong></div>
          <div><span>Failed</span><strong data-status="failed">{report.queueSummary.failed}</strong></div>
          <div><span>Retrying</span><strong data-status="retrying">{report.queueSummary.retrying}</strong></div>
          <div><span>Cancelled</span><strong data-status="cancelled">{report.queueSummary.cancelled}</strong></div>
          <div><span>Skipped</span><strong data-status="skipped">{report.queueSummary.skipped}</strong></div>
        </div>
        <div className="texture-task-list">
          {report.queueTasks.map((task) => (
            <div className="texture-task-row" data-status={task.status} key={task.id}>
              <span>{textureQueueStatusLabels[task.status]}</span>
              <strong>{task.label}</strong>
              <code>{task.command}</code>
              <em>{task.durationMs} ms</em>
              <small>
                {task.attempts.length > 0 ? `${task.attempts.length} attempt(s)` : "no attempt"}
                {task.failureClass !== "none" ? `, ${queueFailureClassLabels[task.failureClass]}` : ""}
              </small>
              {task.commandDiff.length > 0 && (
                <div className="texture-command-diff-inline">
                  {task.commandDiff.map((diff) => (
                    <code key={`${task.id}-${diff.field}`}>{diff.field}: {diff.before} {"->"} {diff.after}</code>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="texture-recovery-panel" data-mode={report.queueRecovery.mode}>
          <div className="section-title">
            <RefreshCw size={16} aria-hidden="true" />
            <h4>Queue Recovery</h4>
          </div>
          <div className="texture-recovery-grid">
            <div>
              <span>State</span>
              <strong>{report.queueRecovery.statusLabel}</strong>
            </div>
            <div>
              <span>Active Task</span>
              <strong>{report.queueRecovery.activeTaskLabel}</strong>
            </div>
            <div>
              <span>Failure Class</span>
              <strong>{queueFailureClassLabels[report.queueRecovery.failureClass]}</strong>
            </div>
            <div>
              <span>Recovery Action</span>
              <strong>{queueRecoveryActionLabels[report.queueRecovery.recoveryAction]}</strong>
            </div>
          </div>
          <div className="texture-command-diff-list">
            {report.queueRecovery.commandDiff.length === 0 ? (
              <code>{report.queueRecovery.commandAfter || "no recovery command"}</code>
            ) : report.queueRecovery.commandDiff.map((diff) => (
              <div key={diff.field}>
                <span>{diff.field}</span>
                <strong>{diff.before} {"->"} {diff.after}</strong>
                <p>{diff.reason}</p>
              </div>
            ))}
          </div>
          <pre>{report.queueRecovery.auditTrail.join("\n")}</pre>
        </div>
      </section>

      <section className="logic-block texture-manifest-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Platform Import Manifest</h3>
        </div>
        <div className="texture-manifest-table" role="table" aria-label="texture import manifest">
          <div role="row">
            <span>Texture</span>
            <span>Group</span>
            <span>Compression</span>
            <span>Color</span>
            <span>Size</span>
          </div>
          {report.importManifest.map((item) => (
            <div key={item.textureName} role="row">
              <code>{item.importPath}</code>
              <span>{item.textureGroup}</span>
              <span>{item.compression}</span>
              <span>{item.colorSpace}</span>
              <strong>{item.estimatedSizeMb} MB</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block wide texture-publish-panel">
        <div className="editor-header">
          <div className="section-title">
            <ClipboardList size={17} aria-hidden="true" />
            <h3>Publish Gate</h3>
          </div>
          <button className="icon-button compact" onClick={downloadReviewPacket} type="button">
            <Download size={15} aria-hidden="true" />
            <span>Export Packet</span>
          </button>
        </div>
        <div className="texture-publish-grid">
          <div className="texture-publish-card" data-gate={report.publishPackage.gate}>
            <span>Decision</span>
            <strong>{publishDecisionLabels[report.publishPackage.decision]}</strong>
            <p>{report.publishPackage.reviewPacket.summary}</p>
          </div>
          <div className="texture-publish-card">
            <span>Frozen Manifest</span>
            <strong>{report.publishPackage.frozenManifest.manifestId}</strong>
            <p>{report.publishPackage.frozenManifest.itemCount} item(s), {report.publishPackage.frozenManifest.totalEstimatedSizeMb} MB, hash {report.publishPackage.frozenManifest.hash}.</p>
          </div>
          <div className="texture-publish-card">
            <span>Last Approved</span>
            <strong>{report.publishPackage.lastApproved.id}</strong>
            <p>{report.publishPackage.lastApproved.version}, {report.publishPackage.lastApproved.totalEstimatedSizeMb} MB, {report.publishPackage.lastApproved.owner}.</p>
          </div>
          <div className="texture-publish-card" data-gate={report.publishPackage.reviewPacket.gate}>
            <span>Review Packet</span>
            <strong>{report.publishPackage.reviewPacket.packetId}</strong>
            <p>{report.publishPackage.reviewPacket.reviewers.join(", ")}</p>
          </div>
        </div>
        <div className="texture-publish-checklist">
          {report.publishPackage.checklist.map((item) => (
            <div className="texture-publish-check-row" data-status={item.status} key={item.id}>
              <span>{publishChecklistLabels[item.status]}</span>
              <strong>{item.label}</strong>
              <p>{item.detail}</p>
            </div>
          ))}
        </div>
        <div className="texture-publish-diff-list">
          {report.publishPackage.diffs.map((diff) => (
            <article className="texture-publish-diff-row" data-status={diff.status} key={diff.id}>
              <div>
                <span>{diff.channel}</span>
                <strong>{diff.title}</strong>
                <p>{diff.action}</p>
              </div>
              <code>{diff.before} {"->"} {diff.after}</code>
            </article>
          ))}
        </div>
        <div className="texture-review-packet">
          <span>Handoff Message</span>
          <pre>{report.publishPackage.reviewPacket.handoffMessage}</pre>
        </div>
      </section>

      <section className="logic-block wide texture-approved-delta-panel">
        <div className="editor-header">
          <div className="section-title">
            <GitCompareArrows size={17} aria-hidden="true" />
            <h3>Approved Delta</h3>
          </div>
          <button className="icon-button compact" onClick={downloadCommittedManifest} type="button">
            <Download size={15} aria-hidden="true" />
            <span>Export Manifest</span>
          </button>
        </div>
        <div className="texture-approved-summary">
          <div>
            <span>Fixture Scope</span>
            <strong>{report.approvedPackageDelta.publicFixture.scope}</strong>
            <p>{report.approvedPackageDelta.publicFixture.privacyNote}</p>
          </div>
          <div>
            <span>Baseline Package</span>
            <strong>{report.approvedPackageDelta.baselinePackageId}</strong>
            <p>{report.publishPackage.lastApproved.approvedAt}, {report.publishPackage.lastApproved.owner}</p>
          </div>
          <div data-gate={report.approvedPackageDelta.gate}>
            <span>Delta Gate</span>
            <strong>{textureGateLabels[report.approvedPackageDelta.gate]}</strong>
            <p>{report.approvedPackageDelta.summary.nextAction}</p>
          </div>
          <div data-status={report.committedManifest.status}>
            <span>Committed Manifest</span>
            <strong>{report.committedManifest.manifestId}</strong>
            <p>{report.committedManifest.status}, {report.committedManifest.fileCount} file(s)</p>
          </div>
        </div>
        <div className="texture-public-fixture-grid">
          <div>
            <span>Reproduction Contract</span>
            <strong>{report.approvedPackageDelta.publicFixture.license}</strong>
            <p>{report.approvedPackageDelta.publicFixture.reproductionNote}</p>
            <code>{report.approvedPackageDelta.publicFixture.sourceRoot}</code>
          </div>
          <div>
            <span>Mutation Boundary</span>
            <strong>{report.approvedPackageDelta.summary.fileWriteCount} file write(s)</strong>
            <p>{report.committedManifest.mutationBoundary}</p>
            <code>{report.approvedPackageDelta.publicFixture.targetRoot}</code>
          </div>
        </div>
        <div className="texture-public-file-list">
          {report.approvedPackageDelta.publicFixture.files.map((file) => (
            <div key={`${file.role}-${file.fileName}`}>
              <span>{getTextureRoleLabel(file.role)}</span>
              <strong>{file.fileName}</strong>
              <p>{file.dimensions}, {file.colorSpace}, {file.sourceLicense}</p>
            </div>
          ))}
        </div>
        <div className="texture-approved-delta-list">
          {report.approvedPackageDelta.rows.map((row) => (
            <article className="texture-approved-delta-row" data-state={row.state} key={row.id}>
              <div>
                <span>{approvedDeltaStateLabels[row.state]}</span>
                <strong>{row.textureName}</strong>
                <p>{row.reason}</p>
              </div>
              <div>
                <span>{mutationScopeLabels[row.mutationScope]}</span>
                <code>{row.before} {"->"} {row.after}</code>
                <small>{row.ownerAction}</small>
              </div>
            </article>
          ))}
        </div>
        <div className="texture-committed-file-list">
          {report.committedManifest.files.map((file) => (
            <article className="texture-committed-file-row" data-state={file.state} key={file.id}>
              <div>
                <span>{approvedDeltaStateLabels[file.state]}</span>
                <strong>{file.textureName}</strong>
              </div>
              <code>{file.importPath}</code>
              <small>{mutationScopeLabels[file.mutationScope]} / {file.settingsSignature}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block wide texture-adapter-panel">
        <div className="editor-header">
          <div className="section-title">
            <PlugZap size={17} aria-hidden="true" />
            <h3>Adapter Layer</h3>
          </div>
          <button className="icon-button compact" onClick={downloadAdapterPlan} type="button">
            <Download size={15} aria-hidden="true" />
            <span>Export Adapter Plan</span>
          </button>
        </div>
        <div className="texture-adapter-policy" data-gate={report.adapterExecutionPlan.gate}>
          <div>
            <span>Executor Policy</span>
            <strong>{report.adapterExecutionPlan.mode}</strong>
            <p>{report.adapterExecutionPlan.executorPolicy}</p>
          </div>
          <div>
            <span>Adapter Gate</span>
            <strong>{report.adapterExecutionPlan.gate}</strong>
            <p>{report.adapterExecutionPlan.planId}</p>
          </div>
        </div>
        <div className="texture-adapter-grid">
          {report.adapterExecutionPlan.adapters.map((adapter) => {
            const step = report.adapterExecutionPlan.steps.find((item) => item.adapterId === adapter.id);
            return (
              <article className="texture-adapter-card" data-status={step?.status} key={adapter.id}>
                <div>
                  <span>{adapter.kind}</span>
                  <strong>{adapter.label}</strong>
                  <p>{adapter.boundary}</p>
                </div>
                <dl>
                  <div><dt>Owner</dt><dd>{adapter.owner}</dd></div>
                  <div><dt>Stage</dt><dd>{adapter.stage}</dd></div>
                  <div><dt>Status</dt><dd>{step ? adapterStatusLabels[step.status] : "Skipped"}</dd></div>
                  <div><dt>Timeout</dt><dd>{adapter.timeoutMs} ms</dd></div>
                </dl>
              </article>
            );
          })}
        </div>
        <div className="texture-adapter-step-list">
          {report.adapterExecutionPlan.steps.map((step) => (
            <article className="texture-adapter-step" data-status={step.status} key={step.id}>
              <div>
                <span>{adapterStatusLabels[step.status]}</span>
                <strong>{step.adapterLabel}</strong>
                <p>{step.guard}</p>
              </div>
              <code>{step.command}</code>
              <div className="texture-adapter-io">
                <div>
                  <span>Reads</span>
                  {step.reads.map((item) => <code key={`${step.id}-read-${item}`}>{item}</code>)}
                </div>
                <div>
                  <span>Writes</span>
                  {step.writes.map((item) => <code key={`${step.id}-write-${item}`}>{item}</code>)}
                </div>
              </div>
            </article>
          ))}
        </div>
        <div className="texture-adapter-diagnostics">
          {report.adapterExecutionPlan.diagnostics.map((diagnostic) => (
            <article className="texture-adapter-diagnostic" data-severity={diagnostic.severity} key={diagnostic.id}>
              <span>{adapterDiagnosticLabels[diagnostic.severity]}</span>
              <strong>{diagnostic.title}</strong>
              <p>{diagnostic.detail}</p>
              <code>{diagnostic.action}</code>
            </article>
          ))}
        </div>
        <div className="texture-adapter-summary">
          <div>
            <span>Boundary Rules</span>
            <ul>
              {report.adapterExecutionPlan.boundaryRules.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
            </ul>
          </div>
          <div>
            <span>AI Log Summary</span>
            <pre>{report.adapterExecutionPlan.aiLogSummary}</pre>
          </div>
        </div>
      </section>

      <section className="logic-block texture-brief-panel">
        <div className="section-title">
          <Sparkles size={17} aria-hidden="true" />
          <h3>AI Risk Brief</h3>
        </div>
        <div className="texture-primary-risk" data-gate={primaryRisk.gate}>
          <span>{primaryRisk.channel}</span>
          <strong>{primaryRisk.title}</strong>
          <p>{primaryRisk.evidence}</p>
        </div>
        <div className="texture-brief-grid">
          <div>
            <span>Brief</span>
            <pre>{report.aiRiskBrief}</pre>
          </div>
          <div>
            <span>Notification</span>
            <pre>{report.notificationPreview}</pre>
          </div>
        </div>
      </section>
    </div>
  );
}

function normalizeTextureDccRun(action: TextureDccAction, raw: unknown): TextureDccRun {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const inspection = asRecord(record?.inspection ?? report?.inspection);
  const validationRecord = asRecord(record?.validation ?? report?.validation);
  const summary = asRecord(validationRecord?.summary);
  const meshSummary = asRecord(inspection?.mesh_summary);
  const sources = normalizeTextureSources(inspection?.file_nodes ?? record?.file_nodes);
  const validation = normalizeTextureValidation(validationRecord?.results);
  const path = readString(record?.path);

  return {
    action: action.id,
    label: action.label,
    raw,
    sourceCount: readNumber(summary?.source_count) ?? sources.length,
    materialCount: readNumber(summary?.material_count) ?? asRecordArray(inspection?.materials).length,
    meshCount: readNumber(meshSummary?.total) ?? asRecordArray(inspection?.meshes).length,
    gate: readString(summary?.gate) ?? (action.id === "fixture" ? "Ready" : "Preview"),
    path: path ?? undefined,
    sources,
    validation,
    updatedAt: new Date().toLocaleTimeString(),
  };
}

function normalizeTextureSources(value: unknown): TextureDccSourceRow[] {
  return asRecordArray(value).map((item) => ({
    node: readString(item.node) ?? "<unknown>",
    fileName: readString(item.file_name) ?? readString(item.fileName) ?? readString(item.path) ?? "<unknown>",
    role: readString(item.role) ?? "fixture",
    colorSpace: readString(item.color_space) ?? readString(item.colorSpace) ?? "-",
    expectedColorSpace: readString(item.expected_color_space) ?? readString(item.expectedColorSpace) ?? undefined,
    exists: item.exists === true || item.exists === "true",
    resolution: readNumber(item.resolution),
  }));
}

function normalizeTextureValidation(value: unknown): TextureDccValidationRow[] {
  return asRecordArray(value).map((item) => ({
    ruleId: readString(item.rule_id) ?? readString(item.ruleId) ?? "<unknown>",
    label: readString(item.label) ?? "<unnamed rule>",
    status: readString(item.status) ?? "skipped",
    evidence: readString(item.evidence) ?? "-",
    fixPreview: readString(item.fix_preview) ?? readString(item.fixPreview) ?? "-",
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
