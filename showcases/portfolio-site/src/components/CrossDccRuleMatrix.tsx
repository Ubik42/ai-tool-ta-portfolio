import { useMemo, useState } from "react";
import {
  Bot,
  Braces,
  Cable,
  Check,
  ClipboardCheck,
  CircleSlash,
  Download,
  FileJson,
  GitBranch,
  RotateCcw,
  Send,
  ShieldCheck,
  SlidersHorizontal,
  Wrench,
} from "lucide-react";
import { assetFixtures } from "../data/assetProtocol";
import {
  adapterCapabilityLabels,
  buildAdapterTrace,
  buildRuleEvaluations,
  buildRuleMatrixReport,
  cloneDefaultCapabilities,
  createAuthoringAuditEvent,
  dccAdapters,
  defaultRuleDraftPrompt,
  draftRuleFromPrompt,
  getAdapterSummary,
  getEvaluation,
  getRuleFixQueue,
  ruleDefinitions,
  ruleRunStages,
  type AdapterCapabilityKey,
  type DccId,
  type FixActionState,
  type FixPreviewMutationScope,
  type ManualDispositionItem,
  type ManualDispositionState,
  type RuleAuthoringAuditEvent,
  type RuleStatus,
} from "../data/ruleMatrix";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

const statusLabels: Record<RuleStatus, string> = {
  pass: "Pass",
  warning: "Review",
  error: "Block",
  skipped: "Skip",
};

const capabilityOrder: AdapterCapabilityKey[] = [
  "protocolCarrier",
  "collision",
  "lod",
  "materialTexture",
  "exportRoot",
  "manifest",
];

const fixScopeLabels: Record<FixPreviewMutationScope, string> = {
  safe_auto: "Safe Auto",
  manual_only: "Manual Only",
  adapter_gap: "Adapter Gap",
};

const manualDispositionLabels: Record<ManualDispositionItem["disposition"], string> = {
  manual_only: "Manual Only",
  adapter_required: "Adapter Required",
};

const manualDispositionStateLabels: Record<ManualDispositionState, string> = {
  owner_required: "Owner Required",
  owner_accepted: "Owner Accepted",
  blocked: "Blocked",
  documented: "Documented",
};

type DccRuleSceneActionId = "collect" | "validate" | "preview" | "export";

interface DccRuleSceneAction {
  id: DccRuleSceneActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface DccRuleSceneFact {
  node: string;
  schema?: string;
  role?: string;
  lod?: string;
  collision?: string;
  meshShapeCount: number;
  materialCount: number;
  hasProtocol: boolean;
  payloadValid: boolean;
}

interface DccRuleSceneResult {
  ruleId: string;
  name: string;
  stage: string;
  severity: string;
  status: string;
  message: string;
  evidence: string;
  fixPreview: string;
}

interface DccRuleSceneFix {
  id: string;
  node: string;
  ruleId: string;
  kind: string;
  owner: string;
  mutation: string;
  preview: string;
}

interface DccRuleSceneSummary {
  gate?: string;
  score?: number;
  pass?: number;
  warning?: number;
  error?: number;
  skipped?: number;
  total?: number;
  safeAuto?: number;
  manualOnly?: number;
}

interface DccRuleSceneRun {
  action: DccRuleSceneActionId;
  label: string;
  raw: unknown;
  facts: DccRuleSceneFact[];
  results: DccRuleSceneResult[];
  fixes: DccRuleSceneFix[];
  summary: DccRuleSceneSummary;
  path?: string;
  updatedAt: string;
}

const dccRuleSceneActions: DccRuleSceneAction[] = [
  { id: "collect", label: "Collect Scene", method: "rule_matrix_collect_scene" },
  { id: "validate", label: "Validate Scene", method: "rule_matrix_validate_scene" },
  { id: "preview", label: "Preview Fixes", method: "rule_matrix_preview_fixes" },
  { id: "export", label: "Export DCC Report", method: "rule_matrix_export_report" },
];

export function CrossDccRuleMatrix() {
  const [selectedAdapterId, setSelectedAdapterId] = useState<DccId>("maya");
  const [selectedRuleId, setSelectedRuleId] = useState(ruleDefinitions[1].id);
  const [selectedAssetId, setSelectedAssetId] = useState(assetFixtures[1].id);
  const [capabilityState, setCapabilityState] = useState(cloneDefaultCapabilities);
  const [fixActionStates, setFixActionStates] = useState<Record<string, FixActionState>>({});
  const [ruleDraftPrompt, setRuleDraftPrompt] = useState(defaultRuleDraftPrompt);
  const [draftReviewState, setDraftReviewState] = useState<"draft" | "accepted">("draft");
  const [authoringAudit, setAuthoringAudit] = useState<RuleAuthoringAuditEvent[]>([]);
  const [dccSnapshot, setDccSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [dccBusyAction, setDccBusyAction] = useState<DccRuleSceneActionId | null>(null);
  const [dccSceneRun, setDccSceneRun] = useState<DccRuleSceneRun | null>(null);
  const [dccSceneError, setDccSceneError] = useState<string | null>(null);

  const selectedAsset = useMemo(
    () => assetFixtures.find((asset) => asset.id === selectedAssetId) ?? assetFixtures[1],
    [selectedAssetId],
  );
  const selectedAdapter = useMemo(
    () => dccAdapters.find((adapter) => adapter.id === selectedAdapterId) ?? dccAdapters[0],
    [selectedAdapterId],
  );
  const authoringDraft = useMemo(
    () => draftRuleFromPrompt(ruleDraftPrompt, selectedAsset, selectedAdapter.id, draftReviewState),
    [draftReviewState, ruleDraftPrompt, selectedAdapter.id, selectedAsset],
  );
  const evaluations = useMemo(
    () => buildRuleEvaluations(selectedAsset, capabilityState),
    [capabilityState, selectedAsset],
  );
  const selectedRule = useMemo(
    () => ruleDefinitions.find((rule) => rule.id === selectedRuleId) ?? ruleDefinitions[0],
    [selectedRuleId],
  );
  const selectedEvaluation = getEvaluation(selectedAdapter.id, selectedRule.id, evaluations);
  const summary = getAdapterSummary(selectedAdapter.id, evaluations);
  const fixQueue = getRuleFixQueue(selectedAdapter.id, selectedAsset, evaluations, fixActionStates);
  const adapterTrace = buildAdapterTrace(selectedAdapter.id, selectedAsset, capabilityState);
  const report = buildRuleMatrixReport(selectedAdapter.id, selectedAsset, capabilityState, evaluations, {
    actionStates: fixActionStates,
    authoringDraft,
    authoringAudit,
  });
  const dccConnected = dccSnapshot.available;
  const dccSceneGate = dccSceneRun?.summary.gate ?? "Preview";

  function toggleCapability(key: AdapterCapabilityKey) {
    setCapabilityState((current) => ({
      ...current,
      [selectedAdapter.id]: {
        ...current[selectedAdapter.id],
        [key]: !current[selectedAdapter.id][key],
      },
    }));
  }

  function resetCapabilities() {
    setCapabilityState(cloneDefaultCapabilities());
  }

  function setFixActionState(id: string, state: FixActionState) {
    setFixActionStates((current) => ({
      ...current,
      [id]: state,
    }));
  }

  function handleDraftPrompt(value: string) {
    setRuleDraftPrompt(value);
    setDraftReviewState("draft");
  }

  function acceptDraft() {
    setAuthoringAudit((current) => [
      ...current,
      createAuthoringAuditEvent(current.length + 1, "accepted", draftReviewState, "accepted", authoringDraft),
    ]);
    setDraftReviewState("accepted");
  }

  function reopenDraft() {
    setAuthoringAudit((current) => [
      ...current,
      createAuthoringAuditEvent(current.length + 1, "reopened", draftReviewState, "draft", authoringDraft),
    ]);
    setDraftReviewState("draft");
  }

  function downloadReport() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${selectedAdapter.id}-${selectedAsset.id}-rule-report.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function runDccSceneAction(action: DccRuleSceneAction) {
    const latest = getBridgeSnapshot();
    setDccSnapshot(latest);

    if (!latest.available) {
      setDccSceneError("Open this module through the Maya AuroraView host to run scene rules.");
      return;
    }

    setDccBusyAction(action.id);
    setDccSceneError(null);

    try {
      const result = await callMayaBridge<unknown>(action.method, {
        include_all: false,
        label: "rule-matrix-dcc-scene",
      });
      setDccSceneRun(normalizeDccRuleSceneRun(action, result));
      setDccSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setDccSceneError(caught instanceof Error ? caught.message : "Rule Matrix DCC call failed.");
    } finally {
      setDccBusyAction(null);
    }
  }

  return (
    <div className="view-grid rule-workbench">
      <section className="logic-block wide">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>
          规则不是散脚本，而是可迁移协议。DCC adapter 负责把 Maya / Blender / Max / Houdini 的私有数据采集成同一份 rule input，
          共享 rule 只判断业务事实，Fix 和 Extract 再把动作边界写进报告。
        </p>
      </section>

      <section className="logic-block wide case-study-card">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Case Study Card</h3>
        </div>
        <div className="case-grid">
          <div>
            <span>Problem</span>
            <p>同一条资产规范被拆散在 Maya、Blender、Max、Houdini 的不同数据结构里，检查脚本难以复用。</p>
          </div>
          <div>
            <span>Core Logic</span>
            <p>adapter 只做采集归一化，共享 rule 只读标准 input，fix queue 保留 safe/manual/capability 边界。</p>
          </div>
          <div>
            <span>AI Boundary</span>
            <p>AI 可以起草 rule DSL 和解释失败项，但不能把 draft 直接加入 validation matrix。</p>
          </div>
          <div>
            <span>Evidence</span>
            <p>矩阵状态、adapter trace、fix queue action state 和 report JSON 组成可复盘证据。</p>
          </div>
        </div>
      </section>

      <section className="logic-block wide dcc-rule-scene-panel">
        <div className="editor-header">
          <div className="section-title">
            <Cable size={17} aria-hidden="true" />
            <h3>Maya Scene Rule Run</h3>
          </div>
          <span className="bridge-state" data-state={dccConnected ? "connected" : "offline"}>
            {dccConnected ? "Connected" : "Preview"}
          </span>
        </div>

        <div className="dcc-rule-action-grid" aria-label="Maya rule matrix actions">
          {dccRuleSceneActions.map((action) => {
            const busy = dccBusyAction === action.id;

            return (
              <button
                className="bridge-action-button"
                disabled={!dccConnected || dccBusyAction !== null}
                key={action.id}
                onClick={() => runDccSceneAction(action)}
                type="button"
              >
                {action.id === "collect" ? (
                  <GitBranch size={15} aria-hidden="true" />
                ) : action.id === "validate" ? (
                  <ShieldCheck size={15} aria-hidden="true" />
                ) : action.id === "preview" ? (
                  <Wrench size={15} aria-hidden="true" />
                ) : (
                  <FileJson size={15} aria-hidden="true" />
                )}
                <span>{busy ? "Running" : action.label}</span>
              </button>
            );
          })}
        </div>

        {dccSceneError ? (
          <div className="dcc-rule-error" role="alert">
            {dccSceneError}
          </div>
        ) : null}

        <div className="dcc-rule-scene-summary">
          <div>
            <span>Last Action</span>
            <strong>{dccSceneRun?.label ?? "Not Run"}</strong>
          </div>
          <div>
            <span>Facts</span>
            <strong>{dccSceneRun?.facts.length ?? "-"}</strong>
          </div>
          <div>
            <span>Gate</span>
            <strong data-gate={dccSceneGate}>{dccSceneGate}</strong>
          </div>
          <div>
            <span>Score</span>
            <strong>{dccSceneRun?.summary.score ?? "-"}</strong>
          </div>
          <div>
            <span>Fix Preview</span>
            <strong>{dccSceneRun?.fixes.length ?? "-"}</strong>
          </div>
          <div>
            <span>Artifact</span>
            <strong>{dccSceneRun?.path ? "Saved" : "-"}</strong>
          </div>
        </div>

        {dccSceneRun ? (
          <div className="dcc-rule-scene-grid">
            <div className="dcc-rule-scene-column">
              <h4>Collected Facts</h4>
              <div className="dcc-rule-fact-list">
                {dccSceneRun.facts.slice(0, 6).map((fact) => (
                  <article data-state={fact.hasProtocol && fact.payloadValid ? "pass" : "error"} key={fact.node}>
                    <strong>{fact.node}</strong>
                    <dl>
                      <div>
                        <dt>Schema</dt>
                        <dd>{fact.schema ?? "-"}</dd>
                      </div>
                      <div>
                        <dt>Mesh</dt>
                        <dd>{fact.meshShapeCount}</dd>
                      </div>
                      <div>
                        <dt>Material</dt>
                        <dd>{fact.materialCount}</dd>
                      </div>
                      <div>
                        <dt>Collision</dt>
                        <dd>{fact.collision ?? "-"}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            </div>

            <div className="dcc-rule-scene-column">
              <h4>Validation Rows</h4>
              <div className="dcc-rule-validation-list">
                {dccSceneRun.results.length > 0 ? (
                  dccSceneRun.results.map((row) => (
                    <article data-status={row.status} key={row.ruleId}>
                      <div>
                        <strong>{row.name}</strong>
                        <span>{ruleStatusLabel(row.status)}</span>
                      </div>
                      <p>{row.message}</p>
                      <code>{row.evidence}</code>
                      <small>{row.fixPreview}</small>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">Run validation to populate rule rows.</p>
                )}
              </div>
            </div>

            <div className="dcc-rule-scene-column">
              <h4>Fix Preview</h4>
              <div className="dcc-rule-fix-list">
                {dccSceneRun.fixes.length > 0 ? (
                  dccSceneRun.fixes.slice(0, 8).map((fix) => (
                    <article data-kind={fix.kind} key={fix.id}>
                      <div>
                        <strong>{fix.ruleId}</strong>
                        <span>{fix.kind}</span>
                      </div>
                      <code>{fix.node}</code>
                      <p>{fix.preview}</p>
                      <small>{fix.owner} / {fix.mutation}</small>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">Run fix preview to list staged mutations.</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="empty-state">
            Create the Maya fixture from the Bridge rail, keep the nodes selected, then run collect and validate here.
          </p>
        )}

        {dccSceneRun ? (
          <div className="dcc-rule-json-panel">
            <div className="bridge-result-title">
              <span>{dccSceneRun.path ?? "DCC result payload"}</span>
              <strong>JSON</strong>
            </div>
            <pre>{safeJson(dccSceneRun.raw)}</pre>
          </div>
        ) : null}
      </section>

      <section className="logic-block wide">
        <div className="editor-header">
          <div className="section-title">
            <SlidersHorizontal size={17} aria-hidden="true" />
            <h3>Rule Fixture Editor</h3>
          </div>
          <button className="icon-button compact" onClick={resetCapabilities} type="button">
            <RotateCcw size={16} aria-hidden="true" />
            <span>Reset Capabilities</span>
          </button>
        </div>

        <div className="rule-fixture-editor">
          <div className="fixture-bank" aria-label="Asset context selector">
            {assetFixtures.map((asset) => (
              <button
                aria-pressed={asset.id === selectedAsset.id}
                className="fixture-button"
                key={asset.id}
                onClick={() => setSelectedAssetId(asset.id)}
                type="button"
              >
                <span>{asset.name}</span>
                <strong>{asset.platform}</strong>
              </button>
            ))}
          </div>

          <div className="capability-bank">
            {capabilityOrder.map((key) => (
              <label className="capability-toggle" key={key}>
                <input
                  checked={capabilityState[selectedAdapter.id][key]}
                  onChange={() => toggleCapability(key)}
                  type="checkbox"
                />
                <span>{adapterCapabilityLabels[key]}</span>
              </label>
            ))}
          </div>

          <div className="asset-context-panel">
            <dl>
              <div>
                <dt>Asset</dt>
                <dd>{selectedAsset.id}</dd>
              </div>
              <div>
                <dt>Platform</dt>
                <dd>{selectedAsset.platform}</dd>
              </div>
              <div>
                <dt>LOD / Collision</dt>
                <dd>{selectedAsset.lodCount} / {selectedAsset.collision}</dd>
              </div>
              <div>
                <dt>Material / Texture</dt>
                <dd>{selectedAsset.materialSlots} / {selectedAsset.textureSets}</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="editor-header">
          <div className="section-title">
            <Bot size={17} aria-hidden="true" />
            <h3>Rule Authoring Draft</h3>
          </div>
          <span className="draft-state" data-state={authoringDraft.reviewState}>
            {authoringDraft.reviewState === "accepted" ? "TA Accepted" : "Needs TA Review"}
          </span>
        </div>
        <div className="rule-authoring-grid">
          <label className="draft-prompt">
            <span>Project Spec</span>
            <textarea
              onChange={(event) => handleDraftPrompt(event.target.value)}
              value={ruleDraftPrompt}
            />
          </label>
          <div className="draft-result">
            <div className="draft-facts">
              <span>{authoringDraft.name}</span>
              <span>{authoringDraft.stage}</span>
              <span>{authoringDraft.severity}</span>
              <span>{adapterCapabilityLabels[authoringDraft.capability]}</span>
            </div>
            <pre className="protocol-code compact-code">
              {authoringDraft.dsl.map((line) => `- ${line}`).join("\n")}
            </pre>
          </div>
          <div className="draft-review-panel">
            <ul className="tight-list">
              {authoringDraft.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
            <div className="draft-actions">
              <button className="icon-button compact" onClick={reopenDraft} type="button">
                <RotateCcw size={16} aria-hidden="true" />
                <span>Reopen Draft</span>
              </button>
              <button className="primary-button compact" onClick={acceptDraft} type="button">
                <Check size={16} aria-hidden="true" />
                <span>Accept Draft</span>
              </button>
            </div>
            <div className="authoring-audit-list">
              {authoringAudit.length > 0 ? (
                authoringAudit.map((event) => (
                  <div className="authoring-audit-row" data-action={event.action} key={event.id}>
                    <strong>#{event.revision}</strong>
                    <span>{event.action}</span>
                    <em>{event.before} {"->"} {event.after}</em>
                    <p>{event.note}</p>
                  </div>
                ))
              ) : (
                <p className="empty-state">Draft review actions will be recorded here.</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="matrix-toolbar" aria-label="DCC adapter selector">
          {dccAdapters.map((adapter) => {
            const adapterSummary = getAdapterSummary(adapter.id, evaluations);
            return (
              <button
                className="dcc-button"
                data-selected={adapter.id === selectedAdapter.id}
                key={adapter.id}
                onClick={() => setSelectedAdapterId(adapter.id)}
                type="button"
              >
                <strong>{adapter.name}</strong>
                <span>{adapterSummary.gate}</span>
              </button>
            );
          })}
        </div>

        <div className="matrix-summary">
          <div>
            <span>Gate</span>
            <strong data-gate={summary.gate}>{summary.gate}</strong>
          </div>
          <div>
            <span>Score</span>
            <strong>{summary.score}</strong>
          </div>
          <div>
            <span>Pass</span>
            <strong>{summary.pass}</strong>
          </div>
          <div>
            <span>Review</span>
            <strong>{summary.warning + summary.skipped}</strong>
          </div>
          <div>
            <span>Block</span>
            <strong>{summary.error}</strong>
          </div>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Braces size={17} aria-hidden="true" />
          <h3>Rule Matrix</h3>
        </div>
        <div className="rule-matrix-grid" role="table" aria-label="Cross DCC rule status matrix">
          <div className="matrix-head" role="row">
            <span>Rule</span>
            {dccAdapters.map((adapter) => (
              <span key={adapter.id}>{adapter.name}</span>
            ))}
          </div>
          {ruleDefinitions.map((rule) => (
            <button
              className="matrix-row"
              data-selected={rule.id === selectedRule.id}
              key={rule.id}
              onClick={() => setSelectedRuleId(rule.id)}
              role="row"
              type="button"
            >
              <span>
                <strong>{rule.name}</strong>
                <em>{rule.stage} / {rule.severity}</em>
              </span>
              {dccAdapters.map((adapter) => {
                const evaluation = getEvaluation(adapter.id, rule.id, evaluations);
                return (
                  <b data-status={evaluation?.status ?? "skipped"} key={adapter.id}>
                    {statusLabels[evaluation?.status ?? "skipped"]}
                  </b>
                );
              })}
            </button>
          ))}
        </div>
      </section>

      <section className="logic-block wide">
        <h3>Severity Heatmap</h3>
        <div className="risk-heatmap">
          {dccAdapters.map((adapter) => {
            const adapterSummary = getAdapterSummary(adapter.id, evaluations);
            return (
              <div className="heatmap-row" key={adapter.id}>
                <strong>{adapter.name}</strong>
                <span data-gate={adapterSummary.gate}>{adapterSummary.gate}</span>
                <div>
                  {ruleDefinitions.map((rule) => {
                    const evaluation = getEvaluation(adapter.id, rule.id, evaluations);
                    return (
                      <button
                        aria-label={`${adapter.name} ${rule.name} ${statusLabels[evaluation?.status ?? "skipped"]}`}
                        data-status={evaluation?.status ?? "skipped"}
                        key={rule.id}
                        onClick={() => {
                          setSelectedAdapterId(adapter.id);
                          setSelectedRuleId(rule.id);
                        }}
                        type="button"
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="logic-block">
        <div className="section-title">
          <GitBranch size={17} aria-hidden="true" />
          <h3>Adapter Payload</h3>
        </div>
        <dl className="adapter-facts">
          <div>
            <dt>Source</dt>
            <dd>{selectedAdapter.methodSource}</dd>
          </div>
          <div>
            <dt>Carrier</dt>
            <dd>{selectedAdapter.protocolCarrier}</dd>
          </div>
          <div>
            <dt>Extract</dt>
            <dd>{selectedAdapter.extractTarget}</dd>
          </div>
        </dl>
        <ul className="tight-list">
          {selectedAdapter.collectShape.map((shape) => (
            <li key={shape}>{shape}</li>
          ))}
        </ul>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <GitBranch size={17} aria-hidden="true" />
          <h3>Adapter Trace</h3>
        </div>
        <div className="adapter-trace-table">
          <div className="trace-head">
            <span>Stage</span>
            <span>Source</span>
            <span>Normalized</span>
            <span>Value</span>
            <span>State</span>
          </div>
          {adapterTrace.map((row) => (
            <div className="trace-row" data-state={row.state} key={row.id}>
              <strong>{row.stage}</strong>
              <span>{row.sourceField}</span>
              <code>{row.normalizedField}</code>
              <span>{row.value}</span>
              <em>{row.state}</em>
              <small>{row.note}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <GitBranch size={17} aria-hidden="true" />
          <h3>Trace Payload Diff</h3>
        </div>
        <div className="trace-diff-grid">
          {report.traceDiff.map((row) => (
            <div className="trace-diff-row" data-state={row.state} key={row.id}>
              <span>{row.transform}</span>
              <code>{row.sourceField}</code>
              <strong>{row.sourceValue}</strong>
              <code>{row.normalizedField}</code>
              <strong>{row.normalizedValue}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block">
        <div className="section-title">
          <Wrench size={17} aria-hidden="true" />
          <h3>Selected Rule</h3>
        </div>
        <p className="rule-reason">{selectedRule.businessReason}</p>
        <div className="selected-evaluation" data-status={selectedEvaluation?.status ?? "skipped"}>
          <strong>{statusLabels[selectedEvaluation?.status ?? "skipped"]}</strong>
          <p>{selectedEvaluation?.message}</p>
          <span>{selectedEvaluation?.evidence}</span>
        </div>
        <div className="fix-preview">
          <span>{selectedRule.fixability}</span>
          <p>{selectedEvaluation?.fixPreview}</p>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Wrench size={17} aria-hidden="true" />
          <h3>Fix Preview Queue</h3>
        </div>
        {fixQueue.length > 0 ? (
          <div className="fix-queue-list">
            {fixQueue.map((item) => (
              <div className="fix-queue-row" data-kind={item.kind} key={item.id}>
                <span>{item.kind}</span>
                <strong>{item.label}</strong>
                <em>{item.owner}</em>
                <b data-state={item.actionState}>{item.actionState}</b>
                <p>{item.before} {"->"} {item.after}</p>
                <small>{item.reason}</small>
                <div className="queue-actions">
                  <button onClick={() => setFixActionState(item.id, "approved")} type="button">
                    <Check size={14} aria-hidden="true" />
                    <span>Approve</span>
                  </button>
                  <button onClick={() => setFixActionState(item.id, "blocked")} type="button">
                    <CircleSlash size={14} aria-hidden="true" />
                    <span>Block</span>
                  </button>
                  <button onClick={() => setFixActionState(item.id, "exported")} type="button">
                    <Send size={14} aria-hidden="true" />
                    <span>Exported</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">Selected adapter has no pending fix preview for this fixture.</p>
        )}
      </section>

      <section className="logic-block wide fix-diff-panel">
        <div className="section-title">
          <FileJson size={17} aria-hidden="true" />
          <h3>Fix Preview Payload Diff</h3>
        </div>
        <div className="fix-diff-summary">
          <div>
            <span>Total Rows</span>
            <strong>{report.fixPreviewDiff.summary.total}</strong>
          </div>
          <div>
            <span>Safe Auto</span>
            <strong data-scope="safe_auto">{report.fixPreviewDiff.summary.safeAuto}</strong>
          </div>
          <div>
            <span>Manual Only</span>
            <strong data-scope="manual_only">{report.fixPreviewDiff.summary.manualOnly}</strong>
          </div>
          <div>
            <span>Adapter Gap</span>
            <strong data-scope="adapter_gap">{report.fixPreviewDiff.summary.adapterGaps}</strong>
          </div>
          <div>
            <span>Blocked</span>
            <strong data-gate="Blocked">{report.fixPreviewDiff.summary.blocked}</strong>
          </div>
        </div>
        <div className="fix-diff-list">
          {report.fixPreviewDiff.rows.map((row) => (
            <article className="fix-diff-row" data-gate={row.gate} data-scope={row.mutationScope} key={row.id}>
              <div className="fix-diff-title">
                <strong>{row.label}</strong>
                <span>{fixScopeLabels[row.mutationScope]}</span>
                <span>{row.actionState}</span>
                <span>{row.gate}</span>
              </div>
              <code>{row.fieldPath}</code>
              <div className="fix-diff-payload">
                <pre>{row.beforePayload}</pre>
                <pre>{row.afterPayload}</pre>
              </div>
              <p>{row.reviewerNote}</p>
            </article>
          ))}
        </div>
        <p className="rule-next-action">{report.fixPreviewDiff.summary.nextAction}</p>
      </section>

      <section className="logic-block wide manual-disposition-panel">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Manual-only Owner Disposition</h3>
        </div>
        <div className="manual-disposition-summary">
          <div>
            <span>Total</span>
            <strong>{report.manualDispositionReceipt.summary.total}</strong>
          </div>
          <div>
            <span>Manual Only</span>
            <strong>{report.manualDispositionReceipt.summary.manualOnly}</strong>
          </div>
          <div>
            <span>Owner Pending</span>
            <strong data-state="owner_required">
              {report.manualDispositionReceipt.summary.ownerRequired}
            </strong>
          </div>
          <div>
            <span>Blocked</span>
            <strong data-state="blocked">{report.manualDispositionReceipt.summary.blocked}</strong>
          </div>
          <div>
            <span>Documented</span>
            <strong data-state="documented">{report.manualDispositionReceipt.summary.documented}</strong>
          </div>
        </div>
        <div className="manual-disposition-list">
          {report.manualDispositionReceipt.items.map((item) => (
            <article className="manual-disposition-row" data-state={item.state} key={item.id}>
              <div className="fix-diff-title">
                <strong>{item.label}</strong>
                <span>{manualDispositionLabels[item.disposition]}</span>
                <span>{manualDispositionStateLabels[item.state]}</span>
                <span>{item.owner}</span>
              </div>
              <code>{item.reasonCode}</code>
              <p>{item.policy}</p>
              <small>{item.requiredEvidence}</small>
              <small>{item.ownerQuestion}</small>
            </article>
          ))}
        </div>
        <p className="rule-next-action">{report.manualDispositionReceipt.summary.nextAction}</p>
      </section>

      <section className="logic-block wide publish-gate-panel">
        <div className="section-title">
          <ShieldCheck size={17} aria-hidden="true" />
          <h3>Publish Gate Report</h3>
        </div>
        <div className="publish-gate-summary">
          <div>
            <span>Asset Protocol</span>
            <strong data-gate={report.publishGate.assetProtocol.readiness.status}>
              {report.publishGate.assetProtocol.readiness.status}
            </strong>
          </div>
          <div>
            <span>Rule Matrix</span>
            <strong data-gate={report.publishGate.ruleMatrix.summary.gate}>
              {report.publishGate.ruleMatrix.summary.gate}
            </strong>
          </div>
          <div>
            <span>Draft</span>
            <strong data-gate={report.publishGate.ruleMatrix.acceptedDraft ? "Ready" : "Review"}>
              {report.publishGate.ruleMatrix.acceptedDraft ? "Accepted" : "Review"}
            </strong>
          </div>
          <div>
            <span>Final Gate</span>
            <strong data-gate={report.publishGate.finalGate}>{report.publishGate.finalGate}</strong>
          </div>
        </div>
        <div className="publish-gate-grid">
          <div>
            <h4>Blockers</h4>
            {report.publishGate.blockers.length > 0 ? (
              <ul className="tight-list">
                {report.publishGate.blockers.map((blocker) => (
                  <li key={blocker}>{blocker}</li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">No publish blockers in the current gate report.</p>
            )}
          </div>
          <div>
            <h4>Decision Trail</h4>
            <ul className="tight-list">
              {report.publishGate.decisionTrail.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4>Next Actions</h4>
            <ul className="tight-list">
              {report.publishGate.nextActions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="logic-block wide">
        <h3>Collect / Validate / Fix / Extract</h3>
        <div className="run-lanes">
          {ruleRunStages.map((stage) => (
            <div className="run-lane" key={stage.stage}>
              <strong>{stage.stage}</strong>
              <p>{stage.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="logic-block">
        <h3>Rule DSL</h3>
        <pre className="protocol-code compact-code">
          {selectedRule.dsl.map((line) => `- ${line}`).join("\n")}
        </pre>
      </section>

      <section className="logic-block">
        <h3>AI Brief</h3>
        <div className="ai-brief compact">
          <strong>{report.aiBrief.headline}</strong>
          <ul>
            {report.aiBrief.priorities.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p>{report.aiBrief.boundary}</p>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="editor-header">
          <div className="section-title">
            <FileJson size={17} aria-hidden="true" />
            <h3>Validation Run Report</h3>
          </div>
          <button className="icon-button compact" onClick={downloadReport} type="button">
            <Download size={16} aria-hidden="true" />
            <span>Export Report</span>
          </button>
        </div>
        <pre className="protocol-code tall">{JSON.stringify(report, null, 2)}</pre>
      </section>
    </div>
  );
}

function normalizeDccRuleSceneRun(
  action: DccRuleSceneAction,
  raw: unknown,
): DccRuleSceneRun {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const collectRecord = asRecord(report?.collect);
  const validationRecord = asRecord(report?.validation) ?? record;
  const fixPreviewRecord = asRecord(report?.fixPreview) ?? record;
  const validationSummary = asRecord(validationRecord?.summary);
  const fixSummary = asRecord(fixPreviewRecord?.summary);
  const facts = normalizeDccRuleFacts(record?.facts ?? collectRecord?.facts);
  const results = normalizeDccRuleResults(record?.results ?? validationRecord?.results ?? record?.validation);
  const fixes = normalizeDccRuleFixes(record?.previews ?? fixPreviewRecord?.previews);
  const path = readString(record?.path);

  return {
    action: action.id,
    label: action.label,
    raw,
    facts,
    results,
    fixes,
    summary: {
      gate: readString(validationSummary?.gate) ?? readString(fixSummary?.gate) ?? undefined,
      score: readNumber(validationSummary?.score),
      pass: readNumber(validationSummary?.pass),
      warning: readNumber(validationSummary?.warning),
      error: readNumber(validationSummary?.error),
      skipped: readNumber(validationSummary?.skipped),
      total: readNumber(fixSummary?.total),
      safeAuto: readNumber(fixSummary?.safe_auto),
      manualOnly: readNumber(fixSummary?.manual_only),
    },
    path: path ?? undefined,
    updatedAt: new Date().toLocaleTimeString(),
  };
}

function normalizeDccRuleFacts(value: unknown): DccRuleSceneFact[] {
  return asRecordArray(value).map((item) => ({
    node: readString(item.node) ?? "<unknown>",
    schema: readString(item.schema) ?? undefined,
    role: readString(item.role) ?? undefined,
    lod: readString(item.lod) ?? undefined,
    collision: readString(item.collision) ?? undefined,
    meshShapeCount: readNumber(item.mesh_shape_count) ?? 0,
    materialCount: readNumber(item.material_count) ?? 0,
    hasProtocol: item.has_protocol === true,
    payloadValid: item.payload_valid === true,
  }));
}

function normalizeDccRuleResults(value: unknown): DccRuleSceneResult[] {
  return asRecordArray(value).map((item) => ({
    ruleId: readString(item.rule_id) ?? "<unknown>",
    name: readString(item.name) ?? "<unnamed rule>",
    stage: readString(item.stage) ?? "-",
    severity: readString(item.severity) ?? "-",
    status: readString(item.status) ?? "skipped",
    message: readString(item.message) ?? "-",
    evidence: readString(item.evidence) ?? "-",
    fixPreview: readString(item.fix_preview) ?? "-",
  }));
}

function normalizeDccRuleFixes(value: unknown): DccRuleSceneFix[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `fix-${index}`,
    node: readString(item.node) ?? "<scene>",
    ruleId: readString(item.rule_id) ?? "<unknown>",
    kind: readString(item.kind) ?? "manual_only",
    owner: readString(item.owner) ?? "TA",
    mutation: readString(item.mutation) ?? "-",
    preview: readString(item.preview) ?? "-",
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

function ruleStatusLabel(status: string) {
  return statusLabels[status as RuleStatus] ?? status;
}

function safeJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return error instanceof Error ? error.message : "Unable to serialize payload.";
  }
}
