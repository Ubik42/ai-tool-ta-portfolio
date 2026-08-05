import { useEffect, useMemo, useRef, useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  Cable,
  CheckCircle2,
  CircleAlert,
  Cuboid,
  FileJson,
  MousePointer2,
  PackageCheck,
  RefreshCw,
  Search,
} from "lucide-react";
import {
  callMayaBridge,
  getBridgeSnapshot,
  waitForAuroraViewReady,
  type BridgeSnapshot,
  type MayaBridgeMethod,
} from "../lib/auroraviewBridge";
import { useDccPayload, type DccSceneProtocolRow } from "../lib/dccPayloadContext";

interface BridgeAction {
  id: string;
  label: string;
  title: string;
  icon: LucideIcon;
  method: MayaBridgeMethod;
  params?: () => Record<string, unknown>;
}

const bridgeActions: BridgeAction[] = [
  {
    id: "status",
    label: "Status",
    title: "Read Maya and AuroraView environment status",
    icon: RefreshCw,
    method: "environment_status",
  },
  {
    id: "selection",
    label: "Selection",
    title: "Read current Maya selection",
    icon: MousePointer2,
    method: "scene_get_selection",
  },
  {
    id: "fixture",
    label: "Fixture",
    title: "Create a synthetic asset protocol fixture in Maya",
    icon: Cuboid,
    method: "scene_create_protocol_fixture",
    params: () => ({ name: "ai_tool_ta_fixture" }),
  },
  {
    id: "apply",
    label: "Write Attr",
    title: "Write the active workbench payload to selected Maya nodes",
    icon: PackageCheck,
    method: "asset_apply_protocol_payload",
  },
  {
    id: "inspect",
    label: "Inspect",
    title: "Inspect selected Maya nodes for aiToolTaProtocol",
    icon: Search,
    method: "asset_inspect_protocol",
  },
  {
    id: "export",
    label: "Export",
    title: "Export the latest bridge result to a JSON artifact",
    icon: FileJson,
    method: "report_export_json",
  },
];

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function arrayLength(value: unknown): number | null {
  return Array.isArray(value) ? value.length : null;
}

function safeJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return error instanceof Error ? error.message : "Unable to serialize result.";
  }
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function toSceneRows(value: unknown): DccSceneProtocolRow[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.flatMap((item) => {
    const record = asRecord(item);
    if (!record) {
      return [];
    }

    const payload = asRecord(record.payload) ?? undefined;
    return [
      {
        ...record,
        node: readString(record.node) ?? "<unknown>",
        has_protocol: record.has_protocol === true,
        payload,
        raw: readString(record.raw) ?? undefined,
        payload_error: readString(record.payload_error) ?? undefined,
      },
    ];
  });
}

export function MayaBridgePanel() {
  const { activePayload, publishSceneInspection } = useDccPayload();
  const [snapshot, setSnapshot] = useState<BridgeSnapshot>(() => getBridgeSnapshot());
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectionCount, setSelectionCount] = useState<number | null>(null);
  const [protocolRows, setProtocolRows] = useState<number | null>(null);
  const [exportPath, setExportPath] = useState<string | null>(null);
  const initializedRef = useRef(false);

  const connected = snapshot.available;
  const boundCount = useMemo(
    () => snapshot.boundMethods.filter((method) => method.startsWith("api.")).length,
    [snapshot.boundMethods],
  );

  useEffect(() => {
    let disposed = false;

    async function refreshBridge() {
      const next = await waitForAuroraViewReady();
      if (!disposed) {
        setSnapshot(next);
      }
    }

    refreshBridge();
    const timer = window.setInterval(() => {
      setSnapshot(getBridgeSnapshot());
    }, 2500);

    return () => {
      disposed = true;
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!connected || initializedRef.current) {
      return;
    }

    initializedRef.current = true;
    runBridgeAction(bridgeActions[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected]);

  async function runBridgeAction(action: BridgeAction) {
    const latest = getBridgeSnapshot();
    setSnapshot(latest);

    if (!latest.available) {
      setError("Open this page through the Maya AuroraView host to enable DCC actions.");
      setLastAction(action.label);
      setLastResult(null);
      return;
    }

    setBusyAction(action.id);
    setError(null);
    setLastAction(action.label);

    try {
      const params =
        action.id === "export"
          ? {
              label: "maya-bridge-front-end",
              report: {
                source: "ai-tool-ta-portfolio",
                action: lastAction,
                activePayload,
                result: lastResult,
              },
            }
          : action.id === "apply"
            ? { payload: activePayload.payload }
          : action.params?.();
      const result = await callMayaBridge<unknown>(action.method, params);
      const record = asRecord(result);

      setLastResult(result);
      setSnapshot(getBridgeSnapshot());

      if (action.id === "selection") {
        const count = typeof record?.count === "number" ? record.count : arrayLength(record?.selection);
        setSelectionCount(count);
      }

      if (action.id === "fixture") {
        const count = arrayLength(record?.nodes);
        setSelectionCount(count);
        setProtocolRows(count);
      }

      if (action.id === "apply") {
        const count = arrayLength(record?.changed);
        setProtocolRows(count);
      }

      if (action.id === "inspect") {
        const count = typeof record?.count === "number" ? record.count : arrayLength(record?.rows);
        setProtocolRows(count);
        publishSceneInspection({
          sourceAction: action.label,
          activePayloadId: activePayload.id,
          activePayloadLabel: activePayload.label,
          rows: toSceneRows(record?.rows),
          count: typeof count === "number" ? count : 0,
          raw: result,
        });
      }

      if (action.id === "export") {
        setExportPath(readString(record?.path));
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Maya bridge call failed.");
    } finally {
      setBusyAction(null);
    }
  }

  const resultPayload =
    error ??
    (lastResult
      ? safeJson(lastResult)
      : connected
        ? "Run a bridge action to create scene evidence."
        : "Browser preview: DCC bridge is waiting for Maya AuroraView.");

  return (
    <section className="rail-panel maya-bridge-panel" aria-label="Maya bridge">
      <div className="rail-title bridge-title-row">
        <div>
          <Cable size={17} aria-hidden="true" />
          <h3>Maya Bridge</h3>
        </div>
        <span className="bridge-state" data-state={connected ? "connected" : "offline"}>
          {connected ? "Connected" : "Preview"}
        </span>
      </div>

      <div className="bridge-status-row" data-state={connected ? "connected" : "offline"}>
        {connected ? (
          <CheckCircle2 size={18} aria-hidden="true" />
        ) : (
          <CircleAlert size={18} aria-hidden="true" />
        )}
        <div>
          <strong>{connected ? "AuroraView API bound" : "DCC bridge unavailable"}</strong>
          <p>{connected ? `${boundCount} bound API methods` : "Open from Maya to run scene actions."}</p>
        </div>
      </div>

      <div className="bridge-payload-card">
        <span>Active Payload</span>
        <strong>{activePayload.moduleName}</strong>
        <p>{activePayload.label}</p>
        <dl>
          <div>
            <dt>Gate</dt>
            <dd>{activePayload.readinessStatus}</dd>
          </div>
          <div>
            <dt>Score</dt>
            <dd>{activePayload.readinessScore ?? "-"}</dd>
          </div>
          <div>
            <dt>Diff</dt>
            <dd>{activePayload.diffCount ?? 0}</dd>
          </div>
          <div>
            <dt>Updated</dt>
            <dd>{activePayload.updatedAt}</dd>
          </div>
        </dl>
      </div>

      <div className="bridge-action-grid">
        {bridgeActions.map((action) => {
          const Icon = action.icon;
          const busy = busyAction === action.id;

          return (
            <button
              className="bridge-action-button"
              disabled={!connected || busyAction !== null}
              key={action.id}
              onClick={() => runBridgeAction(action)}
              title={action.title}
              type="button"
            >
              <Icon size={15} aria-hidden="true" />
              <span>{busy ? "Running" : action.label}</span>
            </button>
          );
        })}
      </div>

      <dl className="bridge-metrics" aria-label="bridge metrics">
        <div>
          <dt>Selection</dt>
          <dd>{selectionCount ?? "-"}</dd>
        </div>
        <div>
          <dt>Protocol Rows</dt>
          <dd>{protocolRows ?? "-"}</dd>
        </div>
        <div>
          <dt>Export</dt>
          <dd>{exportPath ? "Saved" : "-"}</dd>
        </div>
      </dl>

      <div className="bridge-result" data-state={error ? "error" : "ready"}>
        <div className="bridge-result-title">
          <span>{lastAction ?? "Bridge Output"}</span>
          <strong>{error ? "Error" : connected ? "JSON" : "Idle"}</strong>
        </div>
        <pre>{resultPayload}</pre>
      </div>
    </section>
  );
}
