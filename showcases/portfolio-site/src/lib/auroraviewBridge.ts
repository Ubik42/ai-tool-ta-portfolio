type AuroraViewApiMethod = (params?: unknown) => Promise<unknown>;

interface AuroraViewRuntime {
  _ready?: boolean;
  _boundMethods?: Record<string, boolean>;
  api?: Record<string, AuroraViewApiMethod>;
  call?: (method: string, params?: unknown, options?: { timeout?: number }) => Promise<unknown>;
  getBoundMethods?: () => string[];
  isReady?: () => boolean;
}

declare global {
  interface Window {
    auroraview?: AuroraViewRuntime;
  }
}

export type MayaBridgeMethod =
  | "environment_status"
  | "scene_get_selection"
  | "scene_create_protocol_fixture"
  | "asset_apply_protocol_payload"
  | "asset_inspect_protocol"
  | "rule_matrix_collect_scene"
  | "rule_matrix_validate_scene"
  | "rule_matrix_preview_fixes"
  | "rule_matrix_export_report"
  | "visual_review_create_camera_rig"
  | "visual_review_build_pass_manifest"
  | "visual_review_preview_capture"
  | "visual_review_export_report"
  | "texture_delivery_create_fixture"
  | "texture_delivery_inspect_scene"
  | "texture_delivery_validate_scene"
  | "texture_delivery_export_manifest"
  | "task_orchestrator_create_fixture"
  | "task_orchestrator_discover_scene"
  | "task_orchestrator_build_queue"
  | "task_orchestrator_run_dry_run"
  | "task_orchestrator_export_report"
  | "asset_handoff_create_fixture"
  | "asset_handoff_collect"
  | "asset_handoff_evaluate_gate"
  | "asset_handoff_preview_actions"
  | "asset_handoff_export_packet"
  | "asset_handoff_build_decision_packet"
  | "asset_handoff_export_decision_packet"
  | "engine_handoff_build_preflight_packet"
  | "engine_handoff_export_preflight_packet"
  | "engine_handoff_build_preset_comparison"
  | "engine_handoff_export_preset_comparison"
  | "scene_transaction_create_fixture"
  | "scene_transaction_capture_state"
  | "scene_transaction_run_guard"
  | "scene_transaction_export_receipt"
  | "unreal_preset_fact_review_load"
  | "unreal_preset_fact_review_export"
  | "showcase_runbook_build_plan"
  | "showcase_runbook_run_smoke"
  | "showcase_runbook_export_package"
  | "showcase_runbook_export_gui_evidence_manifest"
  | "showcase_runbook_audit_gui_media"
  | "showcase_runbook_export_gui_media_audit"
  | "showcase_runbook_export_case_page"
  | "dcc_presentation_build_pack"
  | "dcc_presentation_export_pack"
  | "report_export_json";

export interface BridgeSnapshot {
  available: boolean;
  ready: boolean;
  boundMethods: string[];
}

export const mayaBridgeMethods: MayaBridgeMethod[] = [
  "environment_status",
  "scene_get_selection",
  "scene_create_protocol_fixture",
  "asset_apply_protocol_payload",
  "asset_inspect_protocol",
  "rule_matrix_collect_scene",
  "rule_matrix_validate_scene",
  "rule_matrix_preview_fixes",
  "rule_matrix_export_report",
  "visual_review_create_camera_rig",
  "visual_review_build_pass_manifest",
  "visual_review_preview_capture",
  "visual_review_export_report",
  "texture_delivery_create_fixture",
  "texture_delivery_inspect_scene",
  "texture_delivery_validate_scene",
  "texture_delivery_export_manifest",
  "task_orchestrator_create_fixture",
  "task_orchestrator_discover_scene",
  "task_orchestrator_build_queue",
  "task_orchestrator_run_dry_run",
  "task_orchestrator_export_report",
  "asset_handoff_create_fixture",
  "asset_handoff_collect",
  "asset_handoff_evaluate_gate",
  "asset_handoff_preview_actions",
  "asset_handoff_export_packet",
  "asset_handoff_build_decision_packet",
  "asset_handoff_export_decision_packet",
  "engine_handoff_build_preflight_packet",
  "engine_handoff_export_preflight_packet",
  "engine_handoff_build_preset_comparison",
  "engine_handoff_export_preset_comparison",
  "scene_transaction_create_fixture",
  "scene_transaction_capture_state",
  "scene_transaction_run_guard",
  "scene_transaction_export_receipt",
  "unreal_preset_fact_review_load",
  "unreal_preset_fact_review_export",
  "showcase_runbook_build_plan",
  "showcase_runbook_run_smoke",
  "showcase_runbook_export_package",
  "showcase_runbook_export_gui_evidence_manifest",
  "showcase_runbook_audit_gui_media",
  "showcase_runbook_export_gui_media_audit",
  "showcase_runbook_export_case_page",
  "dcc_presentation_build_pack",
  "dcc_presentation_export_pack",
  "report_export_json",
];

export const defaultProtocolPayload = {
  schema: "asset-protocol@dcc-r9",
  role: "portfolio_demo_selected_asset",
  platform: "pc",
  lod: "lod0",
  budget: {
    triangles: 12000,
    textures: 4,
  },
  evidence: {
    source: "ai-tool-ta-portfolio",
    host: "maya-auroraview",
  },
};

export function getBridgeSnapshot(): BridgeSnapshot {
  if (typeof window === "undefined") {
    return { available: false, ready: false, boundMethods: [] };
  }

  const runtime = window.auroraview;
  if (!runtime) {
    return { available: false, ready: false, boundMethods: [] };
  }

  const boundMethods =
    typeof runtime.getBoundMethods === "function"
      ? runtime.getBoundMethods()
      : Object.keys(runtime._boundMethods ?? {});
  const hasApiMethods = mayaBridgeMethods.some(
    (method) => typeof runtime.api?.[method] === "function",
  );

  return {
    available: hasApiMethods || typeof runtime.call === "function",
    ready: runtime.isReady?.() ?? runtime._ready ?? hasApiMethods,
    boundMethods,
  };
}

export async function waitForAuroraViewReady(timeoutMs = 1500): Promise<BridgeSnapshot> {
  const current = getBridgeSnapshot();
  if (current.available) {
    return current;
  }

  if (typeof window === "undefined") {
    return current;
  }

  return new Promise((resolve) => {
    const startedAt = window.performance.now();
    let timer = 0;

    function finish(snapshot: BridgeSnapshot) {
      window.clearInterval(timer);
      window.removeEventListener("auroraviewready", handleReady);
      resolve(snapshot);
    }

    function handleReady() {
      finish(getBridgeSnapshot());
    }

    window.addEventListener("auroraviewready", handleReady);
    timer = window.setInterval(() => {
      const next = getBridgeSnapshot();
      if (next.available || window.performance.now() - startedAt >= timeoutMs) {
        finish(next);
      }
    }, 120);
  });
}

export async function callMayaBridge<T>(
  method: MayaBridgeMethod,
  params?: unknown,
): Promise<T> {
  if (typeof window === "undefined" || !window.auroraview) {
    throw new Error("AuroraView bridge is not available in this browser context.");
  }

  const apiMethod = window.auroraview.api?.[method];
  if (typeof apiMethod === "function") {
    return (await apiMethod(params)) as T;
  }

  if (typeof window.auroraview.call === "function") {
    return (await window.auroraview.call(`api.${method}`, params, { timeout: 8000 })) as T;
  }

  throw new Error(`AuroraView method api.${method} is not bound.`);
}
