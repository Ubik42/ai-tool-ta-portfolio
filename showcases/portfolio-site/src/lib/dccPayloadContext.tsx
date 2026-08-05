import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { defaultProtocolPayload } from "./auroraviewBridge";

export interface DccPayloadSnapshot {
  id: string;
  moduleId: string;
  moduleName: string;
  label: string;
  readinessStatus: string;
  readinessScore?: number;
  diffCount?: number;
  payload: Record<string, unknown>;
  report?: unknown;
  updatedAt: string;
}

export type DccPayloadInput = Omit<DccPayloadSnapshot, "updatedAt">;

export interface DccSceneProtocolRow {
  node: string;
  has_protocol: boolean;
  payload?: Record<string, unknown>;
  raw?: string;
  payload_error?: string;
  [key: string]: unknown;
}

export interface DccSceneInspectionSnapshot {
  sourceAction: string;
  activePayloadId: string;
  activePayloadLabel: string;
  rows: DccSceneProtocolRow[];
  count: number;
  raw: unknown;
  updatedAt: string;
}

export type DccSceneInspectionInput = Omit<DccSceneInspectionSnapshot, "updatedAt">;

interface DccPayloadContextValue {
  activePayload: DccPayloadSnapshot;
  sceneInspection: DccSceneInspectionSnapshot | null;
  publishPayload: (payload: DccPayloadInput) => void;
  publishSceneInspection: (inspection: DccSceneInspectionInput) => void;
}

const initialPayload: DccPayloadSnapshot = {
  id: "fallback:asset-protocol",
  moduleId: "maya-bridge",
  moduleName: "Maya Bridge",
  label: "Fallback asset protocol payload",
  readinessStatus: "Preview",
  diffCount: 0,
  payload: defaultProtocolPayload,
  updatedAt: "Not published",
};

const DccPayloadContext = createContext<DccPayloadContextValue | null>(null);

export function DccPayloadProvider({ children }: { children: ReactNode }) {
  const [activePayload, setActivePayload] = useState<DccPayloadSnapshot>(initialPayload);
  const [sceneInspection, setSceneInspection] = useState<DccSceneInspectionSnapshot | null>(null);

  const publishPayload = useCallback((payload: DccPayloadInput) => {
    setActivePayload({
      ...payload,
      updatedAt: new Date().toLocaleTimeString(),
    });
  }, []);

  const publishSceneInspection = useCallback((inspection: DccSceneInspectionInput) => {
    setSceneInspection({
      ...inspection,
      updatedAt: new Date().toLocaleTimeString(),
    });
  }, []);

  const value = useMemo(
    () => ({
      activePayload,
      sceneInspection,
      publishPayload,
      publishSceneInspection,
    }),
    [activePayload, publishPayload, publishSceneInspection, sceneInspection],
  );

  return <DccPayloadContext.Provider value={value}>{children}</DccPayloadContext.Provider>;
}

export function useDccPayload() {
  const context = useContext(DccPayloadContext);
  if (!context) {
    throw new Error("useDccPayload must be used inside DccPayloadProvider.");
  }
  return context;
}
