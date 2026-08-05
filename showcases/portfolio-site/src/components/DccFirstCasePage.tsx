import { useState } from "react";
import { Download, FileJson, ListChecks, MonitorCheck, PackageCheck, RefreshCcw, Route, ShieldCheck, Video } from "lucide-react";
import { callMayaBridge, getBridgeSnapshot } from "../lib/auroraviewBridge";

const routeRows = [
  {
    id: "01-contract",
    phase: "Author Contract",
    question: "How does the scene carry gameplay and publish semantics?",
    proof: "Maya custom attr protocol rows and DCC evidence JSON.",
  },
  {
    id: "02-gate",
    phase: "Publish Gate",
    question: "Can project rules become repeatable DCC facts and fix previews?",
    proof: "Rule Matrix validation rows and fix preview artifact.",
  },
  {
    id: "03-review",
    phase: "Visual Review",
    question: "Can visual review become a fixed camera/pass contract?",
    proof: "Camera rig, pass manifest and capture preview.",
  },
  {
    id: "04-delivery",
    phase: "Texture Delivery",
    question: "Can texture handoff be checked against graph and platform rules?",
    proof: "Material/file node inspection and texture manifest.",
  },
  {
    id: "05-orchestrate",
    phase: "Batch Evidence",
    question: "Can assets become a governed dry-run queue with receipts?",
    proof: "Task queue rows, dry-run events and per-asset receipts.",
  },
  {
    id: "06-composite",
    phase: "Composite Gate",
    question: "Can the whole handoff be judged as one batch decision?",
    proof: "Asset Handoff Gate packet with 1 Ready, 1 Review, 0 Blocked.",
  },
  {
    id: "07-owner-engine",
    phase: "Owner / Engine Decision",
    question: "Who owns the Review row and what can enter engine handoff?",
    proof: "Decision packet with 2 repairs, 2 dispositions, 1 engine-ready, 1 held.",
  },
];

const artifactRows = [
  {
    id: "runbook",
    label: "DCC Runbook Package",
    version: "maya-dcc-showcase-runbook-package@1.4.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-7-dcc-first-case-page-runbook-20260803-171316.json",
    gate: "Review",
  },
  {
    id: "handoff",
    label: "Asset Handoff Gate Packet",
    version: "maya-asset-handoff-gate@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json",
    gate: "Review",
  },
  {
    id: "decision",
    label: "Owner / Engine Decision Packet",
    version: "maya-asset-handoff-decision-packet@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json",
    gate: "Review",
  },
  {
    id: "gui",
    label: "GUI Evidence Manifest",
    version: "maya-dcc-gui-evidence-manifest@1.2.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json",
    gate: "CapturePending",
  },
  {
    id: "engine-preflight",
    label: "Engine Handoff Preflight",
    version: "maya-engine-handoff-preflight@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-8-engine-handoff-preflight-fixture-20260803-172302.json",
    gate: "Review",
  },
  {
    id: "engine-preset-comparison",
    label: "Engine Preset Comparison",
    version: "maya-engine-handoff-preset-comparison@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r10-9-engine-preset-comparison-20260803-172927.json",
    gate: "Review",
  },
  {
    id: "blender-rule-adapter",
    label: "Blender Rule Adapter",
    version: "blender-rule-adapter-contract@0.1.0",
    path: "dcc-hosts/blender-rule-adapter/artifacts/blender-rule-adapter-contract-20260804-201125.json",
    gate: "Blocked",
  },
  {
    id: "blender-l3-harness",
    label: "Blender L3 Harness",
    version: "blender-rule-adapter-bpy-l3@0.1.0",
    path: "dcc-hosts/blender-rule-adapter/artifacts/blender-rule-adapter-l3-20260805-153156.json",
    gate: "Blocked",
  },
  {
    id: "max-rule-adapter",
    label: "3ds Max Rule Adapter",
    version: "max-rule-adapter-contract@0.1.0",
    path: "dcc-hosts/3dsmax-rule-adapter/artifacts/max-rule-adapter-contract-20260804-220959.json",
    gate: "Blocked",
  },
  {
    id: "max-l3-harness",
    label: "3ds Max L3 Harness",
    version: "max-rule-adapter-pymxs-l3@0.1.0",
    path: "dcc-hosts/3dsmax-rule-adapter/artifacts/max-rule-adapter-l3-20260805-153232.json",
    gate: "Blocked",
  },
  {
    id: "unreal-handoff-inspector",
    label: "Unreal Handoff Inspector",
    version: "unreal-handoff-inspector-contract@0.4.0",
    path: "dcc-hosts/unreal-handoff-inspector/artifacts/unreal-handoff-inspector-l3-20260803-184208.json",
    gate: "Blocked",
  },
  {
    id: "unreal-preset-fact-comparison",
    label: "Unreal Preset Fact Comparison",
    version: "unreal-preset-fact-comparison@0.1.0",
    path: "dcc-hosts/unreal-handoff-inspector/artifacts/unreal-preset-fact-comparison-20260803-185302.json",
    gate: "Blocked",
  },
  {
    id: "unreal-preset-fact-review",
    label: "Unreal Preset Fact Review",
    version: "maya-unreal-preset-fact-review@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r18-unreal-preset-fact-review-20260803-190519.json",
    gate: "Blocked",
  },
  {
    id: "scene-transaction-guard",
    label: "Scene Transaction Guard",
    version: "maya-scene-transaction-guard@0.1.0",
    path: "dcc-hosts/maya-auroraview-host/artifacts/r19-scene-transaction-guard-20260804-195730.json",
    gate: "Review",
  },
];

const shotRows = [
  "Maya host open",
  "Runbook business route",
  "Runbook smoke gate",
  "Asset Protocol payload",
  "Rule Matrix gate",
  "Texture Delivery graph",
  "Task Orchestrator receipts",
  "Asset Handoff Gate",
  "Owner / Engine Decision",
];

interface CasePageExport {
  ok?: boolean;
  path?: string;
  bytes?: number;
  report?: {
    reportVersion?: string;
    casePage?: {
      summary?: {
        gate?: string;
        business_route_steps?: number;
        gui_shots?: number;
        handoff_assets?: number;
        handoff_decision_engine_ready?: number;
        handoff_decision_engine_held?: number;
      };
    };
  };
}

interface MediaAuditRow {
  id?: string;
  capture_type?: string;
  filename?: string;
  expected_path?: string;
  status?: string;
  bytes?: number;
}

interface MediaAuditExport {
  ok?: boolean;
  path?: string;
  bytes?: number;
  report?: {
    reportVersion?: string;
    mediaAudit?: {
      media_root?: string;
      summary?: {
        gate?: string;
        required_files?: number;
        present?: number;
        review?: number;
        missing?: number;
      };
      rows?: MediaAuditRow[];
    };
  };
}

interface PresentationEvidenceFile {
  id?: string;
  label?: string;
  kind?: string;
  path?: string;
  state?: string;
  exists?: boolean;
  bytes?: number;
}

interface PresentationPackExport {
  ok?: boolean;
  path?: string;
  bytes?: number;
  report?: {
    reportVersion?: string;
    presentationPack?: {
      summary?: {
        gate?: string;
        demo_route_steps?: number;
        evidence_files?: number;
        present_evidence_files?: number;
        missing_required_files?: number;
        required_media_files?: number;
        gui_media_present?: number;
        gui_media_review?: number;
        gui_media_missing?: number;
        blender_rule_adapter_gate?: string;
        blender_rule_adapter_evidence_level?: string;
        blender_rule_adapter_assets?: number;
        blender_rule_adapter_l3_harness_gate?: string;
        blender_rule_adapter_l3_harness_blender_found?: boolean;
        blender_rule_adapter_l3_harness_collector_ready?: boolean;
        max_rule_adapter_gate?: string;
        max_rule_adapter_evidence_level?: string;
        max_rule_adapter_assets?: number;
        max_rule_adapter_max_batch_available?: boolean;
        max_rule_adapter_l3_harness_gate?: string;
        max_rule_adapter_l3_harness_runtime_found?: boolean;
        max_rule_adapter_l3_harness_collector_ready?: boolean;
        unreal_handoff_inspector_gate?: string;
        unreal_handoff_inspector_evidence_level?: string;
        unreal_handoff_inspector_l3_status?: string;
        unreal_handoff_inspector_engine_version?: string;
        unreal_handoff_inspector_asset_registry_queried?: boolean;
        unreal_handoff_inspector_registry_matched?: boolean;
        unreal_handoff_inspector_registry_expected_assets?: number;
        unreal_handoff_inspector_registry_matched_assets?: number;
        unreal_handoff_inspector_registry_missing_assets?: number;
        unreal_handoff_inspector_registry_class_mismatches?: number;
        unreal_handoff_inspector_engine_facts_matched?: boolean;
        unreal_handoff_inspector_engine_fact_expected?: number;
        unreal_handoff_inspector_engine_fact_matched?: number;
        unreal_handoff_inspector_engine_fact_missing?: number;
        unreal_handoff_inspector_source_import_matched?: boolean;
        unreal_handoff_inspector_material_slot_matched?: boolean;
        unreal_handoff_inspector_lod_count?: number;
        unreal_handoff_inspector_collision_simple_shapes?: number;
        unreal_handoff_inspector_intents?: number;
        unreal_preset_fact_comparison_gate?: string;
        unreal_preset_fact_comparison_presets?: number;
        unreal_preset_fact_comparison_assets?: number;
        unreal_preset_fact_comparison_rows?: number;
        unreal_preset_fact_comparison_matched?: number;
        unreal_preset_fact_comparison_drift?: number;
        unreal_preset_fact_comparison_waived?: number;
        unreal_preset_fact_comparison_blocked?: number;
        unreal_preset_fact_comparison_platform_split?: number;
        unreal_preset_fact_comparison_approved_waivers?: number;
        unreal_preset_fact_review_gate?: string;
        unreal_preset_fact_review_rows?: number;
        unreal_preset_fact_review_attention_rows?: number;
        unreal_preset_fact_review_blocked?: number;
        unreal_preset_fact_review_waivers?: number;
        scene_transaction_guard_gate?: string;
        scene_transaction_guard_created?: number;
        scene_transaction_guard_deleted?: number;
        scene_transaction_guard_modified?: number;
        scene_transaction_guard_rollback_actions?: number;
        scene_transaction_guard_risk_rows?: number;
      };
      key_evidence_files?: PresentationEvidenceFile[];
      media_audit?: {
        media_root?: string;
      };
    };
  };
}

interface UnrealPresetFactReviewRow {
  id?: string;
  asset_id?: string;
  preset?: string;
  fact_id?: string;
  status?: string;
  matched?: boolean;
  actual?: unknown;
  expected?: unknown;
  fix_preview?: string;
  waiver_id?: string | null;
  waiver_owner?: string | null;
  waiver_expires_on?: string | null;
  reviewer_action?: string;
}

interface UnrealPresetSummary {
  preset?: string;
  platform?: string;
  gate?: string;
  factRows?: number;
  matched?: number;
  drift?: number;
  waived?: number;
  blocked?: number;
  disposition?: string;
}

interface UnrealPresetAssetComparison {
  assetId?: string;
  label?: string;
  enginePath?: string;
  presetGates?: Record<string, string>;
  delta?: string;
  dispositions?: Record<string, string>;
}

interface UnrealPresetFactReviewExport {
  ok?: boolean;
  path?: string;
  bytes?: number;
  report?: {
    reportVersion?: string;
    review?: {
      schema?: string;
      source_artifact?: string;
      summary?: {
        gate?: string;
        source_evidence_level?: string;
        source_l3_status?: string;
        preset_count?: number;
        asset_count?: number;
        fact_rows?: number;
        matched?: number;
        drift?: number;
        waived?: number;
        blocked?: number;
        attention_rows?: number;
        approved_waivers?: number;
        platform_split?: number;
        review_queue?: number;
      };
      preset_summaries?: UnrealPresetSummary[];
      asset_comparisons?: UnrealPresetAssetComparison[];
      fact_rows?: UnrealPresetFactReviewRow[];
      review_queue?: UnrealPresetFactReviewRow[];
      waiver_rows?: Array<Record<string, unknown>>;
    };
  };
}

interface SceneTransactionRiskRow {
  id?: string;
  severity?: string;
  count?: number;
  reason?: string;
}

interface SceneTransactionDelta {
  field?: string;
  before?: unknown;
  after?: unknown;
}

interface SceneTransactionModifiedRow {
  node?: string;
  type?: string;
  deltas?: SceneTransactionDelta[];
}

interface SceneTransactionRollbackAction {
  id?: string;
  kind?: string;
  node?: string;
  field?: string;
  value?: unknown;
}

interface SceneTransactionExport {
  ok?: boolean;
  path?: string;
  bytes?: number;
  report?: {
    reportVersion?: string;
    transactionGuard?: {
      schema?: string;
      summary?: {
        gate?: string;
        beforeFingerprint?: string;
        afterFingerprint?: string;
        created?: number;
        deleted?: number;
        modified?: number;
        selectionChanged?: boolean;
        timeChanged?: boolean;
        rollbackActions?: number;
        riskRows?: number;
      };
      diff?: {
        created?: string[];
        deleted?: string[];
        modified?: SceneTransactionModifiedRow[];
        rollback_preview?: SceneTransactionRollbackAction[];
        selection_changed?: {
          changed?: boolean;
          before?: string[];
          after?: string[];
        };
        time_changed?: {
          changed?: boolean;
          before?: number;
          after?: number;
        };
      };
      risk_rows?: SceneTransactionRiskRow[];
      reviewer_claims?: string[];
      boundary?: {
        mutation?: string;
        sceneWrites?: string;
        engineWrites?: number;
        externalWrites?: number;
      };
    };
  };
}

function displayReviewValue(value: unknown): string {
  if (value === null || typeof value === "undefined" || value === "") {
    return "None";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export function DccFirstCasePage() {
  const [busy, setBusy] = useState(false);
  const [mediaBusy, setMediaBusy] = useState(false);
  const [presenterBusy, setPresenterBusy] = useState(false);
  const [presetReviewBusy, setPresetReviewBusy] = useState(false);
  const [transactionBusy, setTransactionBusy] = useState(false);
  const [exported, setExported] = useState<CasePageExport | null>(null);
  const [mediaAudit, setMediaAudit] = useState<MediaAuditExport | null>(null);
  const [presenterPack, setPresenterPack] = useState<PresentationPackExport | null>(null);
  const [presetReview, setPresetReview] = useState<UnrealPresetFactReviewExport | null>(null);
  const [transactionReceipt, setTransactionReceipt] = useState<SceneTransactionExport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const connected = getBridgeSnapshot().available;
  const presetReviewData = presetReview?.report?.review;
  const presetReviewSummary = presetReviewData?.summary;
  const transactionData = transactionReceipt?.report?.transactionGuard;
  const transactionSummary = transactionData?.summary;

  async function exportCasePage() {
    if (!getBridgeSnapshot().available) {
      setError("Open this page through the Maya AuroraView host to export the case page artifact.");
      return;
    }

    setBusy(true);
    setError(null);

    try {
      const result = await callMayaBridge<CasePageExport>("showcase_runbook_export_case_page", {
        label: "r10-7-dcc-first-case-page",
      });
      setExported(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "DCC-first case page export failed.");
    } finally {
      setBusy(false);
    }
  }

  async function exportMediaAudit() {
    if (!getBridgeSnapshot().available) {
      setError("Open this page through the Maya AuroraView host to audit GUI media files.");
      return;
    }

    setMediaBusy(true);
    setError(null);

    try {
      const result = await callMayaBridge<MediaAuditExport>("showcase_runbook_export_gui_media_audit", {
        label: "r10-7-gui-media-audit",
      });
      setMediaAudit(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "GUI media audit failed.");
    } finally {
      setMediaBusy(false);
    }
  }

  async function exportPresenterPack() {
    if (!getBridgeSnapshot().available) {
      setError("Open this page through the Maya AuroraView host to export the presenter pack.");
      return;
    }

    setPresenterBusy(true);
    setError(null);

    try {
      const result = await callMayaBridge<PresentationPackExport>("dcc_presentation_export_pack", {
        label: "r22-blender-max-l3-presentation-pack",
      });
      setPresenterPack(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "DCC presenter pack export failed.");
    } finally {
      setPresenterBusy(false);
    }
  }

  async function exportPresetFactReview() {
    if (!getBridgeSnapshot().available) {
      setError("Open this page through the Maya AuroraView host to review Unreal preset facts.");
      return;
    }

    setPresetReviewBusy(true);
    setError(null);

    try {
      const result = await callMayaBridge<UnrealPresetFactReviewExport>("unreal_preset_fact_review_export", {
        label: "r18-unreal-preset-fact-review",
      });
      setPresetReview(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unreal preset fact review failed.");
    } finally {
      setPresetReviewBusy(false);
    }
  }

  async function exportSceneTransactionGuard() {
    if (!getBridgeSnapshot().available) {
      setError("Open this page through the Maya AuroraView host to run the scene transaction guard.");
      return;
    }

    setTransactionBusy(true);
    setError(null);

    try {
      const result = await callMayaBridge<SceneTransactionExport>("scene_transaction_export_receipt", {
        label: "r19-scene-transaction-guard",
      });
      setTransactionReceipt(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Scene transaction guard failed.");
    } finally {
      setTransactionBusy(false);
    }
  }

  return (
    <div className="dcc-case-page">
      <section className="logic-block wide dcc-case-hero">
        <div>
          <p className="eyebrow">R22 Cross-DCC / Engine Reviewer Pack</p>
          <h3>AI Tool TA DCC-first Portfolio Case</h3>
          <p>
            Maya / AuroraView 内展示的资产交付案例：5 个模块提供证据流，Asset Handoff Gate
            把证据压成 Ready / Review / Blocked 判定，再由 Decision Packet 输出 owner / engine handoff 决策，并接入 Blender/3ds Max L3 runtime adapter、Unreal inspector、preset fact reviewer 和 scene transaction guard。
          </p>
        </div>
        <div className="dcc-case-actions">
          <button className="primary-button compact" disabled={!connected || busy} onClick={exportCasePage} type="button">
            <Download size={16} aria-hidden="true" />
            <span>{busy ? "Exporting" : "Export Case Page"}</span>
          </button>
          <button
            className="primary-button compact"
            data-variant="secondary"
            disabled={!connected || mediaBusy}
            onClick={exportMediaAudit}
            type="button"
          >
            <MonitorCheck size={16} aria-hidden="true" />
            <span>{mediaBusy ? "Auditing" : "Audit Media"}</span>
          </button>
          <button
            className="primary-button compact"
            data-variant="secondary"
            disabled={!connected || presenterBusy}
            onClick={exportPresenterPack}
            type="button"
          >
            <PackageCheck size={16} aria-hidden="true" />
            <span>{presenterBusy ? "Exporting" : "Presenter Pack"}</span>
          </button>
          <button
            className="primary-button compact"
            data-variant="secondary"
            disabled={!connected || presetReviewBusy}
            onClick={exportPresetFactReview}
            type="button"
          >
            <ListChecks size={16} aria-hidden="true" />
            <span>{presetReviewBusy ? "Loading" : "Preset Facts"}</span>
          </button>
          <button
            className="primary-button compact"
            data-variant="secondary"
            disabled={!connected || transactionBusy}
            onClick={exportSceneTransactionGuard}
            type="button"
          >
            <RefreshCcw size={16} aria-hidden="true" />
            <span>{transactionBusy ? "Running" : "Txn Guard"}</span>
          </button>
        </div>
      </section>

      {error ? <div className="bridge-error" role="alert">{error}</div> : null}

      <section className="dcc-case-summary" aria-label="DCC-first case summary">
        {[
          ["Route", 7],
          ["Modules", 5],
          ["Artifacts", 14],
          ["GUI Shots", 9],
          ["Recordings", 1],
          ["Handoff", "1 / 1 / 0"],
          ["Decision", "1 / 1"],
          ["Cross-DCC", "Blender + Max L3"],
          ["Engine", "Preset Facts"],
          ["Scene Txn", "Review"],
        ].map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Route size={17} aria-hidden="true" />
          <h3>Business Route</h3>
        </div>
        <div className="dcc-case-route">
          {routeRows.map((row) => (
            <article key={row.id}>
              <span>{row.phase}</span>
              <strong>{row.question}</strong>
              <p>{row.proof}</p>
            </article>
          ))}
        </div>
      </section>

      {presetReviewData ? (
        <section className="logic-block wide dcc-case-export dcc-preset-fact-review">
          <div className="section-title">
            <ListChecks size={17} aria-hidden="true" />
            <h3>Unreal Preset Fact Review</h3>
          </div>
          <div className="dcc-case-gate">
            <div>
              <span>Gate</span>
              <strong data-gate={presetReviewSummary?.gate}>{presetReviewSummary?.gate}</strong>
            </div>
            <div>
              <span>Rows / Queue</span>
              <strong>
                {presetReviewSummary?.fact_rows ?? 0} / {presetReviewSummary?.review_queue ?? 0}
              </strong>
            </div>
            <div>
              <span>Matched / Drift / Waived / Blocked</span>
              <strong>
                {presetReviewSummary?.matched ?? 0} / {presetReviewSummary?.drift ?? 0} /{" "}
                {presetReviewSummary?.waived ?? 0} / {presetReviewSummary?.blocked ?? 0}
              </strong>
            </div>
            <p>{presetReviewData.source_artifact}</p>
          </div>

          <div className="dcc-preset-review-grid">
            <div className="handoff-preset-summary-list">
              {presetReviewData.preset_summaries?.map((row) => (
                <article data-gate={row.gate} key={row.preset}>
                  <div>
                    <strong>{row.preset}</strong>
                    <span>{row.gate}</span>
                  </div>
                  <p>
                    rows {row.factRows ?? 0} · matched {row.matched ?? 0} · drift {row.drift ?? 0} · waived{" "}
                    {row.waived ?? 0} · blocked {row.blocked ?? 0}
                  </p>
                  <code>{row.disposition}</code>
                </article>
              ))}
            </div>
            <div className="handoff-comparison-list">
              {presetReviewData.asset_comparisons?.map((row) => (
                <article data-delta={row.delta} key={row.assetId}>
                  <div>
                    <strong>{row.label ?? row.assetId}</strong>
                    <span>{row.delta}</span>
                  </div>
                  <p>
                    PC {row.presetGates?.pc ?? "n/a"} · Mobile {row.presetGates?.mobile ?? "n/a"}
                  </p>
                  <code>{row.enginePath}</code>
                </article>
              ))}
            </div>
          </div>

          <div className="dcc-preset-fact-list">
            {presetReviewData.fact_rows?.map((row) => (
              <article data-status={row.status} key={row.id}>
                <div>
                  <strong>
                    {row.preset} / {row.fact_id}
                  </strong>
                  <span>{row.status}</span>
                </div>
                <dl>
                  <div>
                    <dt>Actual</dt>
                    <dd>{displayReviewValue(row.actual)}</dd>
                  </div>
                  <div>
                    <dt>Expected</dt>
                    <dd>{displayReviewValue(row.expected)}</dd>
                  </div>
                  <div>
                    <dt>Action</dt>
                    <dd>{row.reviewer_action}</dd>
                  </div>
                </dl>
                <p>{row.fix_preview}</p>
                {row.waiver_id ? (
                  <code>
                    {row.waiver_id} / {row.waiver_owner} / expires {row.waiver_expires_on}
                  </code>
                ) : null}
              </article>
            ))}
          </div>
          <code>{presetReview.path}</code>
        </section>
      ) : null}

      {transactionData ? (
        <section className="logic-block wide dcc-case-export dcc-transaction-guard">
          <div className="section-title">
            <RefreshCcw size={17} aria-hidden="true" />
            <h3>Scene Transaction Guard</h3>
          </div>
          <div className="dcc-case-gate">
            <div>
              <span>Gate</span>
              <strong data-gate={transactionSummary?.gate}>{transactionSummary?.gate}</strong>
            </div>
            <div>
              <span>Created / Deleted</span>
              <strong>
                {transactionSummary?.created ?? 0} / {transactionSummary?.deleted ?? 0}
              </strong>
            </div>
            <div>
              <span>Modified / Rollback</span>
              <strong>
                {transactionSummary?.modified ?? 0} / {transactionSummary?.rollbackActions ?? 0}
              </strong>
            </div>
            <p>
              {transactionSummary?.beforeFingerprint} {"->"} {transactionSummary?.afterFingerprint}
            </p>
          </div>

          <div className="dcc-transaction-grid">
            <article>
              <span>Selection</span>
              <strong>{transactionData.diff?.selection_changed?.changed ? "Changed" : "Stable"}</strong>
              <p>
                {(transactionData.diff?.selection_changed?.before ?? []).join(", ")} {"->"}{" "}
                {(transactionData.diff?.selection_changed?.after ?? []).join(", ")}
              </p>
            </article>
            <article>
              <span>Timeline</span>
              <strong>{transactionData.diff?.time_changed?.changed ? "Changed" : "Stable"}</strong>
              <p>
                {transactionData.diff?.time_changed?.before ?? "n/a"} {"->"}{" "}
                {transactionData.diff?.time_changed?.after ?? "n/a"}
              </p>
            </article>
            <article>
              <span>Boundary</span>
              <strong>{transactionData.boundary?.mutation}</strong>
              <p>
                scene {transactionData.boundary?.sceneWrites} · engine {transactionData.boundary?.engineWrites ?? 0} · external{" "}
                {transactionData.boundary?.externalWrites ?? 0}
              </p>
            </article>
          </div>

          <div className="dcc-transaction-list">
            <h4>Risk Rows</h4>
            {transactionData.risk_rows?.map((row) => (
              <article data-severity={row.severity} key={row.id}>
                <div>
                  <strong>{row.id}</strong>
                  <span>{row.severity}</span>
                </div>
                <p>
                  {row.count ?? 0} · {row.reason}
                </p>
              </article>
            ))}
          </div>

          <div className="dcc-transaction-list">
            <h4>Rollback Preview</h4>
            {transactionData.diff?.rollback_preview?.slice(0, 9).map((row) => (
              <article key={row.id}>
                <div>
                  <strong>{row.kind}</strong>
                  <span>{row.node ?? row.field ?? "context"}</span>
                </div>
                <p>{row.field}</p>
                <code>{displayReviewValue(row.value)}</code>
              </article>
            ))}
          </div>

          <div className="dcc-transaction-list">
            <h4>Modified Nodes</h4>
            {transactionData.diff?.modified?.map((row) => (
              <article key={row.node}>
                <div>
                  <strong>{row.node}</strong>
                  <span>{row.type}</span>
                </div>
                <p>{row.deltas?.map((delta) => delta.field).join(", ")}</p>
              </article>
            ))}
          </div>
          <code>{transactionReceipt.path}</code>
        </section>
      ) : null}

      <section className="logic-block wide">
        <div className="section-title">
          <ShieldCheck size={17} aria-hidden="true" />
          <h3>Composite Gate</h3>
        </div>
        <div className="dcc-case-gate">
          <div>
            <span>Gate</span>
            <strong data-gate="Review">Review</strong>
          </div>
          <div>
            <span>Assets</span>
            <strong>2</strong>
          </div>
          <div>
            <span>Ready / Review / Blocked</span>
            <strong>1 / 1 / 0</strong>
          </div>
          <p>
            Handoff packet merges protocol, rule, texture, visual, and queue evidence. The Review asset remains visible
            as an owner/TA decision, not hidden by presentation copy.
          </p>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <ShieldCheck size={17} aria-hidden="true" />
          <h3>Owner / Engine Decision</h3>
        </div>
        <div className="dcc-case-gate">
          <div>
            <span>Repairs</span>
            <strong>2</strong>
          </div>
          <div>
            <span>Owner Required</span>
            <strong data-gate="Review">1</strong>
          </div>
          <div>
            <span>Engine Ready / Held</span>
            <strong>1 / 1</strong>
          </div>
          <p>
            Decision Packet keeps all repair actions as preview rows, assigns Review ownership explicitly, and emits
            engine handoff intents without touching engine state.
          </p>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <FileJson size={17} aria-hidden="true" />
          <h3>Evidence Artifacts</h3>
        </div>
        <div className="dcc-case-artifacts">
          {artifactRows.map((artifact) => (
            <article data-gate={artifact.gate} key={artifact.id}>
              <div>
                <strong>{artifact.label}</strong>
                <span>{artifact.gate}</span>
              </div>
              <p>{artifact.version}</p>
              <code>{artifact.path}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <MonitorCheck size={17} aria-hidden="true" />
          <h3>GUI Evidence Plan</h3>
        </div>
        <div className="dcc-case-shot-grid">
          {shotRows.map((shot, index) => (
            <article key={shot}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{shot}</strong>
            </article>
          ))}
        </div>
        <div className="dcc-case-recording">
          <Video size={16} aria-hidden="true" />
          <span>Primary Maya route recording, target 120 seconds, R10.7 case package.</span>
        </div>
      </section>

      {exported ? (
        <section className="logic-block wide dcc-case-export">
          <div className="section-title">
            <FileJson size={17} aria-hidden="true" />
            <h3>Exported Case Page</h3>
          </div>
          <code>{exported.path}</code>
          <p>
            {exported.report?.reportVersion} / gate {exported.report?.casePage?.summary?.gate} / route{" "}
            {exported.report?.casePage?.summary?.business_route_steps} / shots{" "}
            {exported.report?.casePage?.summary?.gui_shots} / engine{" "}
            {exported.report?.casePage?.summary?.handoff_decision_engine_ready} /{" "}
            {exported.report?.casePage?.summary?.handoff_decision_engine_held}
          </p>
        </section>
      ) : null}

      {mediaAudit ? (
        <section className="logic-block wide dcc-case-export dcc-case-media-audit">
          <div className="section-title">
            <MonitorCheck size={17} aria-hidden="true" />
            <h3>GUI Media Audit</h3>
          </div>
          <div className="dcc-case-gate">
            <div>
              <span>Gate</span>
              <strong data-gate={mediaAudit.report?.mediaAudit?.summary?.gate}>
                {mediaAudit.report?.mediaAudit?.summary?.gate}
              </strong>
            </div>
            <div>
              <span>Present / Review / Missing</span>
              <strong>
                {mediaAudit.report?.mediaAudit?.summary?.present} / {mediaAudit.report?.mediaAudit?.summary?.review} /{" "}
                {mediaAudit.report?.mediaAudit?.summary?.missing}
              </strong>
            </div>
            <div>
              <span>Required</span>
              <strong>{mediaAudit.report?.mediaAudit?.summary?.required_files}</strong>
            </div>
            <p>{mediaAudit.report?.mediaAudit?.media_root}</p>
          </div>
          <div className="dcc-case-media-list">
            {mediaAudit.report?.mediaAudit?.rows?.map((row) => (
              <article data-status={row.status} key={row.id}>
                <div>
                  <strong>{row.filename}</strong>
                  <span>{row.status}</span>
                </div>
                <p>{row.capture_type} / {row.bytes ?? 0} bytes</p>
                <code>{row.expected_path}</code>
              </article>
            ))}
          </div>
          <code>{mediaAudit.path}</code>
        </section>
      ) : null}

      {presenterPack ? (
        <section className="logic-block wide dcc-case-export dcc-presenter-pack">
          <div className="section-title">
            <PackageCheck size={17} aria-hidden="true" />
            <h3>Exported Presenter Pack</h3>
          </div>
          <div className="dcc-case-gate">
            <div>
              <span>Gate</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.gate}>
                {presenterPack.report?.presentationPack?.summary?.gate}
              </strong>
            </div>
            <div>
              <span>Evidence Present / Missing</span>
              <strong>
                {presenterPack.report?.presentationPack?.summary?.present_evidence_files} /{" "}
                {presenterPack.report?.presentationPack?.summary?.missing_required_files}
              </strong>
            </div>
            <div>
              <span>Unreal Inspector</span>
              <strong>
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_evidence_level} /{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_gate}
              </strong>
              <p>{presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_l3_status}</p>
              <p>
                Registry{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_registry_matched ? "matched" : "pending"} ·{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_registry_matched_assets ?? 0}/
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_registry_expected_assets ?? 0}
              </p>
              <p>
                Engine facts{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_engine_facts_matched ? "matched" : "pending"} ·{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_engine_fact_matched ?? 0}/
                {presenterPack.report?.presentationPack?.summary?.unreal_handoff_inspector_engine_fact_expected ?? 0}
              </p>
            </div>
            <div>
              <span>Preset Facts</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_gate}>
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_gate}
              </strong>
              <p>
                rows {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_rows ?? 0} · matched{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_matched ?? 0} · drift{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_drift ?? 0} · waived{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_waived ?? 0} · blocked{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_comparison_blocked ?? 0}
              </p>
            </div>
            <div>
              <span>Preset Review</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_gate}>
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_gate}
              </strong>
              <p>
                rows {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_rows ?? 0} · queue{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_attention_rows ?? 0} · blocked{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_blocked ?? 0} · waivers{" "}
                {presenterPack.report?.presentationPack?.summary?.unreal_preset_fact_review_waivers ?? 0}
              </p>
            </div>
            <div>
              <span>Scene Txn</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_gate}>
                {presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_gate}
              </strong>
              <p>
                created {presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_created ?? 0} · deleted{" "}
                {presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_deleted ?? 0} · modified{" "}
                {presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_modified ?? 0} · rollback{" "}
                {presenterPack.report?.presentationPack?.summary?.scene_transaction_guard_rollback_actions ?? 0}
              </p>
            </div>
            <div>
              <span>Blender Adapter</span>
              <strong>
                {presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_evidence_level} /{" "}
                {presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_gate}
              </strong>
            </div>
            <div>
              <span>Blender L3 Harness</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_l3_harness_gate}>
                {presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_l3_harness_gate}
              </strong>
              <p>
                collector{" "}
                {presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_l3_harness_collector_ready
                  ? "ready"
                  : "pending"}{" "}
                · blender{" "}
                {presenterPack.report?.presentationPack?.summary?.blender_rule_adapter_l3_harness_blender_found
                  ? "found"
                : "missing"}
              </p>
            </div>
            <div>
              <span>3ds Max Adapter</span>
              <strong>
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_evidence_level} /{" "}
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_gate}
              </strong>
              <p>
                assets {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_assets ?? 0} · batch{" "}
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_max_batch_available ? "found" : "missing"}
              </p>
            </div>
            <div>
              <span>3ds Max L3 Harness</span>
              <strong data-gate={presenterPack.report?.presentationPack?.summary?.max_rule_adapter_l3_harness_gate}>
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_l3_harness_gate}
              </strong>
              <p>
                collector{" "}
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_l3_harness_collector_ready
                  ? "ready"
                  : "pending"}{" "}
                · runtime{" "}
                {presenterPack.report?.presentationPack?.summary?.max_rule_adapter_l3_harness_runtime_found
                  ? "found"
                  : "missing"}
              </p>
            </div>
            <div>
              <span>Media Present / Review / Missing</span>
              <strong>
                {presenterPack.report?.presentationPack?.summary?.gui_media_present} /{" "}
                {presenterPack.report?.presentationPack?.summary?.gui_media_review} /{" "}
                {presenterPack.report?.presentationPack?.summary?.gui_media_missing}
              </strong>
            </div>
            <p>{presenterPack.report?.presentationPack?.media_audit?.media_root}</p>
          </div>
          <div className="dcc-presenter-file-list">
            {presenterPack.report?.presentationPack?.key_evidence_files?.map((row) => (
              <article data-state={row.state} key={row.id}>
                <div>
                  <strong>{row.label}</strong>
                  <span>{row.state}</span>
                </div>
                <p>{row.kind} / {row.bytes ?? 0} bytes</p>
                <code>{row.path}</code>
              </article>
            ))}
          </div>
          <code>{presenterPack.path}</code>
          <p>
            {presenterPack.report?.reportVersion} / route{" "}
            {presenterPack.report?.presentationPack?.summary?.demo_route_steps} / evidence{" "}
            {presenterPack.report?.presentationPack?.summary?.evidence_files} / media required{" "}
            {presenterPack.report?.presentationPack?.summary?.required_media_files}
          </p>
        </section>
      ) : null}
    </div>
  );
}
