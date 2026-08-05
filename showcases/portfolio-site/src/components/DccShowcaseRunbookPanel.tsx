import { useState } from "react";
import { Camera, ClipboardList, FileJson, PackageCheck, Play, ShieldCheck } from "lucide-react";
import {
  callMayaBridge,
  getBridgeSnapshot,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";

type RunbookActionId = "plan" | "smoke" | "export" | "evidence";

interface RunbookAction {
  id: RunbookActionId;
  label: string;
  method: MayaBridgeMethod;
}

interface RunbookModuleRow {
  id: string;
  label: string;
  gate: string;
  proof: string;
  artifact?: string;
}

interface RunbookArtifactRow {
  moduleId: string;
  path: string;
  bytes?: number;
}

interface RunbookScriptRow {
  id: string;
  segment: string;
  operatorAction: string;
  evidenceExpected: string;
}

interface RunbookChecklistRow {
  id: string;
  target: string;
  clicks: string[];
}

interface RunbookPositioning {
  thesis: string;
  demoMode: string;
  moduleShellExplanation: string;
}

interface RunbookRouteRow {
  id: string;
  phase: string;
  moduleId: string;
  businessQuestion: string;
  operatorAction: string;
  coreLogic: string;
  evidenceToShow: string;
  reviewerValue: string;
}

interface RunbookEvidenceShotRow {
  id: string;
  captureType: string;
  target: string;
  filename: string;
  mustShow: string[];
  acceptance: string;
}

interface RunbookResult {
  action: RunbookActionId;
  label: string;
  raw: unknown;
  gate: string;
  moduleCount: number;
  artifactCount: number;
  path?: string;
  modules: RunbookModuleRow[];
  artifacts: RunbookArtifactRow[];
  positioning?: RunbookPositioning;
  route: RunbookRouteRow[];
  evidenceShots: RunbookEvidenceShotRow[];
  script: RunbookScriptRow[];
  checklist: RunbookChecklistRow[];
}

const runbookActions: RunbookAction[] = [
  { id: "plan", label: "Build Plan", method: "showcase_runbook_build_plan" },
  { id: "smoke", label: "Run Smoke", method: "showcase_runbook_run_smoke" },
  { id: "export", label: "Export Package", method: "showcase_runbook_export_package" },
  { id: "evidence", label: "Evidence Shotlist", method: "showcase_runbook_export_gui_evidence_manifest" },
];

export function DccShowcaseRunbookPanel() {
  const [snapshot, setSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [busyAction, setBusyAction] = useState<RunbookActionId | null>(null);
  const [result, setResult] = useState<RunbookResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const connected = snapshot.available;

  async function runAction(action: RunbookAction) {
    const latest = getBridgeSnapshot();
    setSnapshot(latest);

    if (!latest.available) {
      setError("Open this workbench through the Maya AuroraView host to run the showcase runbook.");
      return;
    }

    setBusyAction(action.id);
    setError(null);

    try {
      const params =
        action.id === "plan"
          ? undefined
          : { label: action.id === "evidence" ? "r10-7-gui-evidence-manifest" : "r10-7-demo-route-package" };
      const raw = await callMayaBridge<unknown>(action.method, params);
      setResult(normalizeRunbookResult(action, raw));
      setSnapshot(getBridgeSnapshot());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "DCC showcase runbook call failed.");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <section className="rail-panel showcase-runbook-panel">
      <div className="rail-title">
        <ShieldCheck size={17} aria-hidden="true" />
        <h3>DCC Showcase Runbook</h3>
      </div>

      <div className="runbook-state-row">
        <span className="bridge-state" data-state={connected ? "connected" : "offline"}>
          {connected ? "Connected" : "Preview"}
        </span>
        <strong data-gate={result?.gate ?? "Preview"}>{result?.gate ?? "Preview"}</strong>
      </div>

      <div className="runbook-action-grid" aria-label="DCC showcase runbook actions">
        {runbookActions.map((action) => {
          const busy = busyAction === action.id;

          return (
            <button
              className="bridge-action-button"
              disabled={!connected || busyAction !== null}
              key={action.id}
              onClick={() => runAction(action)}
              type="button"
            >
              {action.id === "plan" ? (
                <ClipboardList size={15} aria-hidden="true" />
              ) : action.id === "smoke" ? (
                <Play size={15} aria-hidden="true" />
              ) : action.id === "evidence" ? (
                <Camera size={15} aria-hidden="true" />
              ) : (
                <PackageCheck size={15} aria-hidden="true" />
              )}
              <span>{busy ? "Running" : action.label}</span>
            </button>
          );
        })}
      </div>

      {error ? <div className="bridge-error" role="alert">{error}</div> : null}

      <div className="runbook-summary-grid">
        <div>
          <span>Modules</span>
          <strong>{result?.moduleCount ?? "-"}</strong>
        </div>
        <div>
          <span>Artifacts</span>
          <strong>{result?.artifactCount ?? "-"}</strong>
        </div>
      </div>

      {result ? (
        <>
          {result.positioning ? (
            <div className="runbook-positioning">
              <span>{result.positioning.demoMode}</span>
              <strong>{result.positioning.thesis}</strong>
              <p>{result.positioning.moduleShellExplanation}</p>
            </div>
          ) : null}

          {result.route.length > 0 ? (
            <div className="runbook-route-list">
              {result.route.map((step) => (
                <article key={step.id}>
                  <div>
                    <span>{step.phase}</span>
                    <code>{step.moduleId}</code>
                  </div>
                  <strong>{step.businessQuestion}</strong>
                  <p>{step.coreLogic}</p>
                  <small>{step.operatorAction}</small>
                  <small>{step.evidenceToShow}</small>
                  <small>{step.reviewerValue}</small>
                </article>
              ))}
            </div>
          ) : null}

          <div className="runbook-module-list">
            {result.modules.map((module) => (
              <article data-gate={module.gate} key={module.id}>
                <div>
                  <strong>{module.label}</strong>
                  <span>{module.gate}</span>
                </div>
                <p>{module.proof}</p>
                {module.artifact ? <code>{module.artifact}</code> : null}
              </article>
            ))}
          </div>

          {result.artifacts.length > 0 ? (
            <div className="runbook-artifact-list">
              {result.artifacts.slice(0, 5).map((artifact) => (
                <article key={`${artifact.moduleId}-${artifact.path}`}>
                  <FileJson size={14} aria-hidden="true" />
                  <span>{artifact.moduleId}</span>
                  <code>{artifact.path}</code>
                </article>
              ))}
            </div>
          ) : null}

          {result.evidenceShots.length > 0 ? (
            <details className="runbook-evidence-shotlist" open>
              <summary>GUI Evidence Shotlist</summary>
              <div>
                {result.evidenceShots.map((shot) => (
                  <article key={shot.id}>
                    <div>
                      <strong>{shot.target}</strong>
                      <span>{shot.captureType}</span>
                    </div>
                    <code>{shot.filename}</code>
                    <p>{shot.mustShow.join(" / ")}</p>
                    <small>{shot.acceptance}</small>
                  </article>
                ))}
              </div>
            </details>
          ) : null}

          {result.script.length > 0 ? (
            <div className="runbook-script-list">
              {result.script.map((step) => (
                <article key={step.id}>
                  <span>{step.segment}</span>
                  <strong>{step.operatorAction}</strong>
                  <p>{step.evidenceExpected}</p>
                </article>
              ))}
            </div>
          ) : null}

          {result.checklist.length > 0 ? (
            <details className="runbook-checklist">
              <summary>GUI Click Checklist</summary>
              <div>
                {result.checklist.map((item) => (
                  <article key={item.id}>
                    <strong>{item.target}</strong>
                    <code>{item.clicks.join(" / ")}</code>
                  </article>
                ))}
              </div>
            </details>
          ) : null}

          <details className="runbook-json">
            <summary>JSON Payload</summary>
            <pre>{safeJson(result.raw)}</pre>
          </details>
        </>
      ) : (
        <p className="empty-state">Build the demo plan, then run the DCC smoke package from Maya.</p>
      )}
    </section>
  );
}

function normalizeRunbookResult(action: RunbookAction, raw: unknown): RunbookResult {
  const record = asRecord(raw);
  const report = asRecord(record?.report);
  const plan = asRecord(record?.plan ?? report?.plan ?? (record?.schema === "maya-dcc-showcase-runbook@1.0.0" ? record : null));
  const smoke = asRecord(record?.smoke ?? report?.smoke);
  const presentation = asRecord(report?.presentation);
  const guiEvidence = asRecord(record?.manifest ?? record?.guiEvidence ?? report?.guiEvidence);
  const summary = asRecord(smoke?.summary);
  const modules = normalizeRunbookModules(smoke?.modules ?? plan?.modules);
  const artifacts = normalizeRunbookArtifacts([
    ...readArray(smoke?.artifacts),
    ...readArray(presentation?.additional_artifacts),
  ]);
  const positioning = normalizeRunbookPositioning(presentation?.showcase_positioning ?? plan?.showcase_positioning);
  const route = normalizeRunbookRoute(presentation?.business_route ?? plan?.presentation_route);
  const evidenceShots = normalizeRunbookEvidenceShots(guiEvidence?.shots);
  const script = normalizeRunbookScript(presentation?.live_demo_script ?? plan?.demo_script);
  const checklist = normalizeRunbookChecklist(presentation?.gui_click_checklist ?? plan?.gui_click_checklist);
  const path = readString(record?.path);
  const gate = readString(smoke?.gate) ?? (action.id === "plan" ? "Ready" : "Preview");

  return {
    action: action.id,
    label: action.label,
    raw,
    gate,
    moduleCount: readNumber(summary?.module_count) ?? modules.length,
    artifactCount: readNumber(summary?.artifact_count) ?? artifacts.length,
    path: path ?? undefined,
    modules,
    artifacts,
    positioning,
    route,
    evidenceShots,
    script,
    checklist,
  };
}

function normalizeRunbookModules(value: unknown): RunbookModuleRow[] {
  return asRecordArray(value).map((item) => ({
    id: readString(item.id) ?? "<unknown>",
    label: readString(item.label) ?? "<unnamed module>",
    gate: readString(item.gate) ?? "Ready",
    proof: readString(item.proof) ?? readString(item.primary_method) ?? safeJson(asRecord(item.summary) ?? {}),
    artifact: readString(item.artifact) ?? undefined,
  }));
}

function normalizeRunbookArtifacts(value: unknown): RunbookArtifactRow[] {
  return asRecordArray(value).map((item) => ({
    moduleId: readString(item.module_id) ?? readString(item.moduleId) ?? "<unknown>",
    path: readString(item.path) ?? "<missing artifact path>",
    bytes: readNumber(item.bytes),
  }));
}

function normalizeRunbookPositioning(value: unknown): RunbookPositioning | undefined {
  const item = asRecord(value);
  if (!item) {
    return undefined;
  }

  return {
    thesis: readString(item.thesis) ?? "DCC-first AI Tool TA portfolio.",
    demoMode: readString(item.demo_mode) ?? readString(item.demoMode) ?? "DCC-first",
    moduleShellExplanation:
      readString(item.module_shell_explanation) ??
      readString(item.moduleShellExplanation) ??
      "The shell orchestrates the demonstration and the modules provide business evidence.",
  };
}

function normalizeRunbookRoute(value: unknown): RunbookRouteRow[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `route-${index + 1}`,
    phase: readString(item.phase) ?? `Step ${index + 1}`,
    moduleId: readString(item.module_id) ?? readString(item.moduleId) ?? "<module>",
    businessQuestion: readString(item.business_question) ?? readString(item.businessQuestion) ?? "-",
    operatorAction: readString(item.operator_action) ?? readString(item.operatorAction) ?? "-",
    coreLogic: readString(item.core_logic) ?? readString(item.coreLogic) ?? "-",
    evidenceToShow: readString(item.evidence_to_show) ?? readString(item.evidenceToShow) ?? "-",
    reviewerValue: readString(item.reviewer_value) ?? readString(item.reviewerValue) ?? "-",
  }));
}

function normalizeRunbookEvidenceShots(value: unknown): RunbookEvidenceShotRow[] {
  return asRecordArray(value).map((item, index) => {
    const mustShow = Array.isArray(item.must_show)
      ? item.must_show.filter((entry): entry is string => typeof entry === "string")
      : Array.isArray(item.mustShow)
        ? item.mustShow.filter((entry): entry is string => typeof entry === "string")
        : [];

    return {
      id: readString(item.id) ?? `shot-${index + 1}`,
      captureType: readString(item.capture_type) ?? readString(item.captureType) ?? "screenshot",
      target: readString(item.target) ?? "<target>",
      filename: readString(item.filename) ?? "<filename>",
      mustShow,
      acceptance: readString(item.acceptance) ?? "-",
    };
  });
}

function normalizeRunbookScript(value: unknown): RunbookScriptRow[] {
  return asRecordArray(value).map((item, index) => ({
    id: readString(item.id) ?? `script-${index + 1}`,
    segment: readString(item.segment) ?? "<segment>",
    operatorAction: readString(item.operator_action) ?? readString(item.operatorAction) ?? "-",
    evidenceExpected: readString(item.evidence_expected) ?? readString(item.evidenceExpected) ?? "-",
  }));
}

function normalizeRunbookChecklist(value: unknown): RunbookChecklistRow[] {
  return asRecordArray(value).map((item, index) => {
    const clicks = Array.isArray(item.clicks)
      ? item.clicks.filter((entry): entry is string => typeof entry === "string")
      : [];

    return {
      id: readString(item.id) ?? `check-${index + 1}`,
      target: readString(item.target) ?? "<target>",
      clicks,
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

function readArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
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
