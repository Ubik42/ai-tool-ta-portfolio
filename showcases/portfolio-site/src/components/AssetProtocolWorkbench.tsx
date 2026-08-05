import { useEffect, useMemo, useState } from "react";
import {
  Download,
  FileJson,
  GitCompare,
  ListChecks,
  PackageCheck,
  RefreshCw,
  ShieldAlert,
  SlidersHorizontal,
  Sparkles,
  Wrench,
} from "lucide-react";
import {
  applySafeProtocolFixes,
  applyProtocolPreset,
  assetFixtures,
  assetProtocolSchema,
  buildAssetProtocolReport,
  createProtocolAuditEvents,
  diffAssetProtocol,
  diffEncodedProtocol,
  encodeAssetProtocol,
  getProtocolReadiness,
  previewAutoFix,
  previewProtocolPreset,
  protocolEditPresets,
  summarizeProtocolRisk,
  validateAssetProtocol,
} from "../data/assetProtocol";
import type {
  AssetPlatform,
  AssetProtocolFixture,
  ProtocolAuditEvent,
  ProtocolCarrier,
} from "../data/assetProtocol";
import { useDccPayload } from "../lib/dccPayloadContext";

const platforms: AssetPlatform[] = ["PC", "Mobile", "Console"];
const collisions: AssetProtocolFixture["collision"][] = ["complex", "simple", "missing"];
const carriers: ProtocolCarrier[] = ["uv3", "vertexColor", "customAttr"];

export function AssetProtocolWorkbench() {
  const { publishPayload, sceneInspection } = useDccPayload();
  const [selectedAssetId, setSelectedAssetId] = useState("mobile_crate_risky");
  const [selectedPresetId, setSelectedPresetId] = useState(protocolEditPresets[0].id);
  const baseAsset = useMemo(
    () => assetFixtures.find((fixture) => fixture.id === selectedAssetId) ?? assetFixtures[0],
    [selectedAssetId],
  );
  const [draft, setDraft] = useState<AssetProtocolFixture>(baseAsset);
  const [auditTrail, setAuditTrail] = useState<ProtocolAuditEvent[]>([]);

  useEffect(() => {
    setDraft(baseAsset);
    setAuditTrail([]);
  }, [baseAsset]);

  const selectedPreset =
    protocolEditPresets.find((preset) => preset.id === selectedPresetId) ?? protocolEditPresets[0];
  const results = useMemo(() => validateAssetProtocol(draft), [draft]);
  const readiness = useMemo(() => getProtocolReadiness(results), [results]);
  const baseManifest = useMemo(() => encodeAssetProtocol(baseAsset), [baseAsset]);
  const manifest = useMemo(() => encodeAssetProtocol(draft), [draft]);
  const diff = useMemo(() => diffAssetProtocol(baseAsset, draft), [baseAsset, draft]);
  const fixPreview = useMemo(() => previewAutoFix(draft), [draft]);
  const presetDiff = useMemo(
    () => previewProtocolPreset(draft, selectedPreset),
    [draft, selectedPreset],
  );
  const payloadDiff = useMemo(
    () => diffEncodedProtocol(baseManifest, manifest),
    [baseManifest, manifest],
  );
  const safeFixPayloadDiff = useMemo(
    () => diffEncodedProtocol(manifest, encodeAssetProtocol(fixPreview.fixedAsset)),
    [fixPreview.fixedAsset, manifest],
  );
  const riskBrief = useMemo(
    () => summarizeProtocolRisk(draft, results, fixPreview.actions),
    [draft, fixPreview.actions, results],
  );
  const safeFixCount = fixPreview.actions.filter((action) => action.kind === "safe").length;
  const report = useMemo(
    () => buildAssetProtocolReport(baseAsset, draft, auditTrail),
    [auditTrail, baseAsset, draft],
  );
  const dccPayload = useMemo(
    () => ({
      id: `asset-protocol:${draft.id}`,
      moduleId: "asset-protocol",
      moduleName: "Asset Protocol Workbench",
      label: `${draft.name} / ${draft.platform}`,
      readinessStatus: readiness.status,
      readinessScore: readiness.score,
      diffCount: diff.length,
      payload: {
        schema: "asset-protocol@dcc-r9",
        sourceModule: "asset-protocol-workbench",
        asset: report.asset,
        readiness: report.readiness,
        encodedPayload: manifest,
        protocolDiff: diff,
        validationSummary: {
          errors: readiness.errors,
          warnings: readiness.warnings,
          total: results.length,
        },
      },
      report,
    }),
    [diff, draft.id, draft.name, draft.platform, manifest, readiness, report, results.length],
  );

  useEffect(() => {
    publishPayload(dccPayload);
  }, [dccPayload, publishPayload]);

  const sceneComparison = useMemo(() => {
    const rows = sceneInspection?.rows ?? [];
    const protocolRows = rows.filter((row) => row.has_protocol && row.payload);
    const currentSignature = stableStringify(dccPayload.payload);
    const matchedRows = protocolRows.filter((row) => stableStringify(row.payload) === currentSignature);
    const firstProtocolPayload = protocolRows[0]?.payload;
    const diffEntries = firstProtocolPayload
      ? diffUnknownPayload(dccPayload.payload, firstProtocolPayload)
      : [];

    return {
      rows,
      protocolRows,
      matchedRows,
      stale: sceneInspection ? sceneInspection.activePayloadId !== dccPayload.id : false,
      diffEntries,
      diffPreview: diffEntries.slice(0, 10),
      nodeStates: rows.map((row) => ({
        node: row.node,
        hasProtocol: row.has_protocol,
        state:
          row.has_protocol && row.payload
            ? stableStringify(row.payload) === currentSignature
              ? "match"
              : "drift"
            : "missing",
        schema: readNestedString(row.payload, ["schema"]),
        sourceModule: readNestedString(row.payload, ["sourceModule"]),
      })),
    };
  }, [dccPayload.id, dccPayload.payload, sceneInspection]);
  const dccEvidenceGate = useMemo(
    () => getDccEvidenceGate(sceneInspection, sceneComparison, readiness),
    [readiness, sceneComparison, sceneInspection],
  );
  const dccEvidenceReport = useMemo(
    () => ({
      reportVersion: "asset-protocol-dcc-evidence@1.0.0",
      generatedBy: "AI Tool TA Portfolio / Maya AuroraView Host",
      generatedAt: new Date().toISOString(),
      module: {
        id: "asset-protocol",
        name: "Asset Protocol Workbench",
        dccHost: "maya-auroraview",
      },
      asset: report.asset,
      gate: dccEvidenceGate,
      activePayload: {
        id: dccPayload.id,
        label: dccPayload.label,
        readinessStatus: dccPayload.readinessStatus,
        readinessScore: dccPayload.readinessScore,
        diffCount: dccPayload.diffCount,
        payload: dccPayload.payload,
      },
      editorReport: report,
      sceneEvidence: sceneInspection
        ? {
            sourceAction: sceneInspection.sourceAction,
            activePayloadId: sceneInspection.activePayloadId,
            activePayloadLabel: sceneInspection.activePayloadLabel,
            updatedAt: sceneInspection.updatedAt,
            count: sceneInspection.count,
            stale: sceneComparison.stale,
            rowCount: sceneComparison.rows.length,
            protocolRowCount: sceneComparison.protocolRows.length,
            matchedRowCount: sceneComparison.matchedRows.length,
            nodeStates: sceneComparison.nodeStates,
            payloadDiff: sceneComparison.diffEntries,
            rows: sceneInspection.rows,
            raw: sceneInspection.raw,
          }
        : null,
      validationEvidence: {
        readiness,
        validation: results,
        protocolDiff: diff,
        encodedPayloadDiff: payloadDiff,
        auditTrail,
      },
    }),
    [
      auditTrail,
      dccEvidenceGate,
      dccPayload,
      diff,
      payloadDiff,
      readiness,
      report,
      results,
      sceneComparison,
      sceneInspection,
    ],
  );

  function updateDraft<K extends keyof AssetProtocolFixture>(
    key: K,
    value: AssetProtocolFixture[K],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function applySafeFixes() {
    const safeActions = fixPreview.actions.filter((action) => action.kind === "safe");

    if (safeActions.length === 0) {
      return;
    }

    setAuditTrail((current) => [
      ...createProtocolAuditEvents(current.length + 1, "Apply safe fixes", "safe", safeActions),
      ...current,
    ]);
    setDraft(applySafeProtocolFixes(draft));
  }

  function applyPreset() {
    if (presetDiff.length === 0) {
      return;
    }

    setAuditTrail((current) => [
      ...createProtocolAuditEvents(current.length + 1, selectedPreset.name, "preset", presetDiff),
      ...current,
    ]);
    setDraft(applyProtocolPreset(draft, selectedPreset));
  }

  function downloadReport() {
    downloadJson(report, `${draft.id}-protocol-report.json`);
  }

  function downloadDccEvidenceReport() {
    downloadJson(dccEvidenceReport, `${draft.id}-dcc-evidence-report.json`);
  }

  return (
    <div className="protocol-workbench">
      <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>
          资产协议不是表单，是状态机。字段必须能被反查、检查、导出，并能写入 UV、
          vertex color、custom attr 这类下游稳定通道。
        </p>
      </section>

      <section className="schema-band" aria-label="asset protocol schema">
        <div>
          <span>Schema</span>
          <strong>{assetProtocolSchema.version}</strong>
        </div>
        <div>
          <span>Fields</span>
          <strong>{assetProtocolSchema.fields.length}</strong>
        </div>
        <div>
          <span>Fixture Delta</span>
          <strong>{diff.length}</strong>
        </div>
        <div>
          <span>Safe Fixes</span>
          <strong>{safeFixCount}</strong>
        </div>
      </section>

      <div className="fixture-tabs" aria-label="synthetic asset fixtures">
        {assetFixtures.map((fixture) => (
          <button
            aria-pressed={fixture.id === baseAsset.id}
            className="fixture-button"
            key={fixture.id}
            onClick={() => setSelectedAssetId(fixture.id)}
            type="button"
          >
            <span>{fixture.name}</span>
            <strong>{fixture.platform}</strong>
          </button>
        ))}
      </div>

      <section className="logic-block wide case-study-card">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Case Study Card</h3>
        </div>
        <div className="case-grid">
          <div>
            <span>Problem</span>
            <p>资产交付字段分散在命名、节点属性、UV 和人工备注里，publish 前难以判断协议是否完整。</p>
          </div>
          <div>
            <span>Core Logic</span>
            <p>把协议字段、稳定 carrier、rule engine、payload manifest 和 audit trail 连成闭环。</p>
          </div>
          <div>
            <span>AI Boundary</span>
            <p>AI 只解释风险、整理报告和辅助理解规则，不直接改变资产交付结论。</p>
          </div>
          <div>
            <span>Evidence</span>
            <p>规则结果、payload diff、safe-fix preview、report JSON 和截图可作为作品集证据。</p>
          </div>
        </div>
      </section>

      <section className="logic-block wide protocol-editor">
        <div className="editor-header">
          <div className="section-title">
            <SlidersHorizontal size={17} aria-hidden="true" />
            <h3>Protocol Editor</h3>
          </div>
          <div className="mini-toolbar">
            <button className="icon-button compact" onClick={() => setDraft(baseAsset)} type="button">
              <RefreshCw size={16} aria-hidden="true" />
              <span>Reset Fixture</span>
            </button>
            <button
              className="primary-button compact"
              disabled={safeFixCount === 0}
              onClick={applySafeFixes}
              type="button"
            >
              <Wrench size={16} aria-hidden="true" />
              <span>Apply Safe Fixes</span>
            </button>
          </div>
        </div>

        <div className="field-grid">
          <label className="field-control">
            <span>Platform</span>
            <select
              value={draft.platform}
              onChange={(event) => updateDraft("platform", event.currentTarget.value as AssetPlatform)}
            >
              {platforms.map((platform) => (
                <option key={platform}>{platform}</option>
              ))}
            </select>
          </label>

          <label className="field-control">
            <span>Collision</span>
            <select
              value={draft.collision}
              onChange={(event) =>
                updateDraft("collision", event.currentTarget.value as AssetProtocolFixture["collision"])
              }
            >
              {collisions.map((collision) => (
                <option key={collision}>{collision}</option>
              ))}
            </select>
          </label>

          <label className="field-control">
            <span>Semantic Carrier</span>
            <select
              value={draft.semanticCarrier}
              onChange={(event) =>
                updateDraft("semanticCarrier", event.currentTarget.value as ProtocolCarrier)
              }
            >
              {carriers.map((carrier) => (
                <option key={carrier}>{carrier}</option>
              ))}
            </select>
          </label>

          <NumberField
            label="LOD Count"
            max={8}
            min={0}
            step={1}
            value={draft.lodCount}
            onChange={(value) => updateDraft("lodCount", value)}
          />

          <NumberField
            label="Material Slots"
            max={12}
            min={0}
            step={1}
            value={draft.materialSlots}
            onChange={(value) => updateDraft("materialSlots", value)}
          />

          <NumberField
            label="Texture Sets"
            max={12}
            min={0}
            step={1}
            value={draft.textureSets}
            onChange={(value) => updateDraft("textureSets", value)}
          />

          <NumberField
            label="Screen Size"
            max={1}
            min={0}
            step={0.01}
            value={draft.screenSize}
            onChange={(value) => updateDraft("screenSize", value)}
          />

          <NumberField
            label="Cull Distance"
            max={20000}
            min={0}
            step={100}
            value={draft.cullDistance}
            onChange={(value) => updateDraft("cullDistance", value)}
          />

          <NumberField
            label="Semantic Mask"
            max={15}
            min={0}
            step={1}
            value={draft.semanticMask}
            onChange={(value) => updateDraft("semanticMask", value)}
          />

          <NumberField
            label="UV3 U Class"
            max={1}
            min={0}
            step={0.01}
            value={draft.uv3U}
            onChange={(value) => updateDraft("uv3U", value)}
          />

          <label className="toggle-control">
            <input
              checked={draft.nanite}
              onChange={(event) => updateDraft("nanite", event.currentTarget.checked)}
              type="checkbox"
            />
            <span>Nanite</span>
          </label>

          <label className="toggle-control">
            <input
              checked={draft.streamable}
              onChange={(event) => updateDraft("streamable", event.currentTarget.checked)}
              type="checkbox"
            />
            <span>Streamable</span>
          </label>
        </div>
      </section>

      <section className="logic-block wide preset-panel">
        <div className="editor-header">
          <div className="section-title">
            <Wrench size={17} aria-hidden="true" />
            <h3>Edit Presets</h3>
          </div>
          <button
            className="primary-button compact"
            disabled={presetDiff.length === 0}
            onClick={applyPreset}
            type="button"
          >
            <Wrench size={16} aria-hidden="true" />
            <span>Stage Preset</span>
          </button>
        </div>

        <div className="preset-grid">
          {protocolEditPresets.map((preset) => (
            <button
              aria-pressed={preset.id === selectedPreset.id}
              className="preset-button"
              key={preset.id}
              onClick={() => setSelectedPresetId(preset.id)}
              type="button"
            >
              <strong>{preset.name}</strong>
              <span>{preset.intent}</span>
            </button>
          ))}
        </div>

        <div className="preset-preview">
          <div>
            <h4>Preset Diff</h4>
            {presetDiff.length > 0 ? (
              <div className="diff-list">
                {presetDiff.map((entry) => (
                  <div className="diff-row" key={entry.field}>
                    <strong>{entry.label}</strong>
                    <span>{entry.before}</span>
                    <span>{entry.after}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">Selected preset does not change the current draft.</p>
            )}
          </div>
          <div>
            <h4>Required Evidence</h4>
            <ul className="tight-list">
              {selectedPreset.evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <div className="protocol-grid">
        <section className="logic-block">
          <h3>Protocol Facts</h3>
          <dl className="fact-grid">
            <div>
              <dt>Category</dt>
              <dd>{draft.category}</dd>
            </div>
            <div>
              <dt>LOD</dt>
              <dd>{draft.lodCount}</dd>
            </div>
            <div>
              <dt>Collision</dt>
              <dd>{draft.collision}</dd>
            </div>
            <div>
              <dt>Nanite</dt>
              <dd>{draft.nanite ? "on" : "off"}</dd>
            </div>
            <div>
              <dt>Materials</dt>
              <dd>{draft.materialSlots}</dd>
            </div>
            <div>
              <dt>Texture Sets</dt>
              <dd>{draft.textureSets}</dd>
            </div>
          </dl>
          <p className="protocol-note">{draft.authoringNote}</p>
        </section>

        <section className="logic-block readiness-panel">
          <h3>Publish Readiness</h3>
          <div className="readiness-score" data-status={readiness.status}>
            <strong>{readiness.score}</strong>
            <span>{readiness.status}</span>
          </div>
          <p>
            {readiness.errors} error / {readiness.warnings} warning. Rule-gated; AI explains.
          </p>
        </section>

        <section className="logic-block wide risk-brief">
          <div className="section-title">
            <Sparkles size={17} aria-hidden="true" />
            <h3>AI Risk Brief</h3>
          </div>
          <div className="brief-header">
            <strong data-gate={riskBrief.gate}>{riskBrief.gate}</strong>
            <span>{riskBrief.priority}</span>
          </div>
          <p>{riskBrief.headline}</p>
          <ul className="tight-list">
            {riskBrief.bullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <GitCompare size={17} aria-hidden="true" />
            <h3>Before / After Diff</h3>
          </div>
          {diff.length > 0 ? (
            <div className="diff-list">
              {diff.map((entry) => (
                <div className="diff-row" key={entry.field}>
                  <strong>{entry.label}</strong>
                  <span>{entry.before}</span>
                  <span>{entry.after}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No protocol edits against the selected fixture.</p>
          )}
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <FileJson size={17} aria-hidden="true" />
            <h3>Encoded Payload Diff</h3>
          </div>
          {payloadDiff.length > 0 ? (
            <div className="diff-list">
              {payloadDiff.map((entry) => (
                <div className="diff-row encoded" key={entry.path}>
                  <strong>{entry.path}</strong>
                  <span>{entry.before}</span>
                  <span>{entry.after}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">Encoded payload still matches the selected fixture.</p>
          )}
        </section>

        <section className="logic-block wide scene-payload-panel">
          <div className="editor-header">
            <div className="section-title">
              <PackageCheck size={17} aria-hidden="true" />
              <h3>DCC Scene Payload</h3>
            </div>
            <span
              className="scene-sync-chip"
              data-state={
                !sceneInspection
                  ? "waiting"
                  : sceneComparison.stale
                      ? "stale"
                    : sceneComparison.diffEntries.length > 0
                      ? "drift"
                      : "match"
              }
            >
              {!sceneInspection
                ? "Waiting"
                : sceneComparison.stale
                  ? "Stale"
                  : sceneComparison.diffEntries.length > 0
                    ? "Drift"
                    : "Synced"}
            </span>
          </div>

          {sceneInspection ? (
            <>
              <dl className="scene-payload-summary">
                <div>
                  <dt>Rows</dt>
                  <dd>{sceneComparison.rows.length}</dd>
                </div>
                <div>
                  <dt>Protocol Rows</dt>
                  <dd>{sceneComparison.protocolRows.length}</dd>
                </div>
                <div>
                  <dt>Matched</dt>
                  <dd>{sceneComparison.matchedRows.length}</dd>
                </div>
                <div>
                  <dt>Updated</dt>
                  <dd>{sceneInspection.updatedAt}</dd>
                </div>
              </dl>

              <p className="protocol-note">
                Inspect source: {sceneInspection.activePayloadLabel}. Current editor payload: {dccPayload.label}.
              </p>

              <div className="scene-payload-node-list">
                {sceneComparison.nodeStates.map((row) => (
                  <article data-state={row.state} key={row.node}>
                    <span>{row.state}</span>
                    <div>
                      <strong>{row.node}</strong>
                      <p>
                        {row.hasProtocol
                          ? `${row.schema ?? "unknown schema"} / ${row.sourceModule ?? "unknown source"}`
                          : "No aiToolTaProtocol custom attr found."}
                      </p>
                    </div>
                  </article>
                ))}
              </div>

              {sceneComparison.diffPreview.length > 0 ? (
                <div className="scene-payload-diff">
                  <h4>Current Payload vs First Scene Row</h4>
                  <div className="diff-list">
                    {sceneComparison.diffPreview.map((entry) => (
                      <div className="diff-row encoded" key={entry.path}>
                        <strong>{entry.path}</strong>
                        <span>{entry.before}</span>
                        <span>{entry.after}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="empty-state">
                  {sceneComparison.protocolRows.length > 0
                    ? "Scene protocol payload matches the current active payload."
                    : "Inspect returned nodes, but no protocol payload is present yet."}
                </p>
              )}
            </>
          ) : (
            <p className="empty-state">
              Run `Inspect` in the Maya Bridge after writing attrs to pull scene payloads back into this module.
            </p>
          )}
        </section>

        <section className="logic-block wide dcc-evidence-panel">
          <div className="editor-header">
            <div className="section-title">
              <FileJson size={17} aria-hidden="true" />
              <h3>DCC Evidence Report</h3>
            </div>
            <div className="mini-toolbar">
              <span className="evidence-gate-chip" data-gate={dccEvidenceGate}>
                {dccEvidenceGate}
              </span>
              <button className="icon-button compact" onClick={downloadDccEvidenceReport} type="button">
                <Download size={16} aria-hidden="true" />
                <span>Export DCC Evidence</span>
              </button>
            </div>
          </div>

          <dl className="dcc-evidence-summary">
            <div>
              <dt>Scene Rows</dt>
              <dd>{sceneComparison.rows.length}</dd>
            </div>
            <div>
              <dt>Matches</dt>
              <dd>{sceneComparison.matchedRows.length}</dd>
            </div>
            <div>
              <dt>Scene Diff</dt>
              <dd>{sceneComparison.diffEntries.length}</dd>
            </div>
            <div>
              <dt>Rule Errors</dt>
              <dd>{readiness.errors}</dd>
            </div>
          </dl>

          <p className="protocol-note">
            Evidence report combines editor rules, active payload, Maya inspect rows, scene diff,
            and audit trail into one handoff artifact.
          </p>
          <pre className="protocol-code evidence">{JSON.stringify(dccEvidenceReport, null, 2)}</pre>
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <ListChecks size={17} aria-hidden="true" />
            <h3>Validation Rules</h3>
          </div>
          <div className="rule-result-list">
            {results.map((result) => (
              <div className="rule-result" data-severity={result.severity} key={result.id}>
                <span className="rule-dot" aria-hidden="true" />
                <div>
                  <strong>{result.label}</strong>
                  <p>{result.message}</p>
                  {!result.passed && result.fix ? <em>{result.fix}</em> : null}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <Wrench size={17} aria-hidden="true" />
            <h3>Auto-fix Preview</h3>
          </div>
          {fixPreview.actions.length > 0 ? (
            <div className="fix-list">
              {fixPreview.actions.map((action) => (
                <div className="fix-row" data-kind={action.kind} key={action.id}>
                  <span>{action.kind}</span>
                  <div>
                    <strong>{action.label}</strong>
                    <p>
                      {action.before} to {action.after}. {action.reason}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No fix actions for the current protocol draft.</p>
          )}
          {safeFixPayloadDiff.length > 0 ? (
            <div className="safe-payload-preview">
              <h4>Safe Fix Payload Diff</h4>
              <div className="diff-list">
                {safeFixPayloadDiff.map((entry) => (
                  <div className="diff-row encoded" key={entry.path}>
                    <strong>{entry.path}</strong>
                    <span>{entry.before}</span>
                    <span>{entry.after}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <ListChecks size={17} aria-hidden="true" />
            <h3>Action Audit Trail</h3>
          </div>
          {auditTrail.length > 0 ? (
            <div className="audit-list">
              {auditTrail.map((event) => (
                <div className="audit-row" key={event.id}>
                  <strong>#{event.revision}</strong>
                  <span>{event.label}</span>
                  <code>
                    {event.kind}:{event.field}
                  </code>
                  <em>
                    {event.before} to {event.after}
                  </em>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No protocol action has been applied in this fixture session.</p>
          )}
        </section>

        <section className="logic-block wide">
          <div className="section-title">
            <FileJson size={17} aria-hidden="true" />
            <h3>Encoded Payload</h3>
          </div>
          <pre className="protocol-code">{JSON.stringify(manifest, null, 2)}</pre>
        </section>

        <section className="logic-block wide">
          <div className="editor-header">
            <div className="section-title">
              <FileJson size={17} aria-hidden="true" />
              <h3>Report JSON</h3>
            </div>
            <button className="icon-button compact" onClick={downloadReport} type="button">
              <Download size={16} aria-hidden="true" />
              <span>Export Report</span>
            </button>
          </div>
          <pre className="protocol-code tall">{JSON.stringify(report, null, 2)}</pre>
        </section>
      </div>
    </div>
  );
}

function NumberField({
  label,
  max,
  min,
  step,
  value,
  onChange,
}: {
  label: string;
  max: number;
  min: number;
  step: number;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="field-control">
      <span>{label}</span>
      <input
        max={max}
        min={min}
        onChange={(event) => onChange(clampNumber(event.currentTarget.value, min, max, step))}
        step={step}
        type="number"
        value={value}
      />
    </label>
  );
}

function clampNumber(rawValue: string, min: number, max: number, step: number) {
  const value = Number(rawValue);
  const fallback = Number.isFinite(value) ? value : min;
  const clamped = Math.min(max, Math.max(min, fallback));

  if (Number.isInteger(step)) {
    return Math.round(clamped);
  }

  return Number(clamped.toFixed(2));
}

function downloadJson(value: unknown, filename: string) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function getDccEvidenceGate(
  sceneInspection: unknown | null,
  sceneComparison: {
    stale: boolean;
    protocolRows: unknown[];
    matchedRows: unknown[];
    diffEntries: unknown[];
  },
  readiness: { errors: number; warnings: number },
) {
  if (!sceneInspection) {
    return "Needs Inspect";
  }

  if (sceneComparison.stale) {
    return "Stale";
  }

  if (sceneComparison.protocolRows.length === 0) {
    return "Missing";
  }

  if (sceneComparison.diffEntries.length > 0 || sceneComparison.matchedRows.length === 0) {
    return "Drift";
  }

  if (readiness.errors > 0) {
    return "Blocked";
  }

  if (readiness.warnings > 0) {
    return "Review";
  }

  return "Ready";
}

function stableStringify(value: unknown): string {
  return JSON.stringify(sortValue(value));
}

function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sortValue);
  }

  if (typeof value === "object" && value !== null) {
    return Object.keys(value as Record<string, unknown>)
      .sort()
      .reduce<Record<string, unknown>>((sorted, key) => {
        sorted[key] = sortValue((value as Record<string, unknown>)[key]);
        return sorted;
      }, {});
  }

  return value;
}

function readNestedString(value: unknown, path: string[]): string | null {
  let current = value;
  for (const key of path) {
    if (typeof current !== "object" || current === null || Array.isArray(current)) {
      return null;
    }
    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === "string" ? current : null;
}

function diffUnknownPayload(before: unknown, after: unknown) {
  const beforeFlat = flattenUnknown(before);
  const afterFlat = flattenUnknown(after);
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

function flattenUnknown(value: unknown, prefix = ""): Record<string, string> {
  if (typeof value !== "object" || value === null) {
    return { [prefix || "value"]: formatUnknown(value) };
  }

  if (Array.isArray(value)) {
    return value.reduce<Record<string, string>>((acc, item, index) => {
      Object.assign(acc, flattenUnknown(item, `${prefix}[${index}]`));
      return acc;
    }, {});
  }

  return Object.entries(value as Record<string, unknown>).reduce<Record<string, string>>(
    (acc, [key, item]) => {
      const path = prefix ? `${prefix}.${key}` : key;
      Object.assign(acc, flattenUnknown(item, path));
      return acc;
    },
    {},
  );
}

function formatUnknown(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (value === null) {
    return "null";
  }

  if (typeof value === "undefined") {
    return "<missing>";
  }

  return JSON.stringify(value);
}
