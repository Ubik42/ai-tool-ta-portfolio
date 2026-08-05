export type ModulePhase = "R0" | "R1" | "R2" | "R3" | "R4" | "R5";

export type ModuleState = "active" | "queued" | "planned";

export interface ToolModule {
  id: string;
  name: string;
  phase: ModulePhase;
  state: ModuleState;
  progress: number;
  source: string[];
  thesis: string;
  businessSecret: string;
  deterministicCore: string[];
  aiRole: string[];
  firstBuild: string[];
  evidence: string[];
  risks: string[];
}

export interface DevelopmentLoopStep {
  name: string;
  state: "done" | "active" | "next";
  detail: string;
}
