import { useMemo, useState } from "react";
import {
  Activity,
  Boxes,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  GitBranch,
  ImageUp,
  LayoutDashboard,
  Network,
  Play,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";
import { AssetProtocolWorkbench } from "./components/AssetProtocolWorkbench";
import { AssetHandoffGatePanel } from "./components/AssetHandoffGatePanel";
import { CrossDccRuleMatrix } from "./components/CrossDccRuleMatrix";
import { DccFirstCasePage } from "./components/DccFirstCasePage";
import { DccShowcaseRunbookPanel } from "./components/DccShowcaseRunbookPanel";
import { MayaBridgePanel } from "./components/MayaBridgePanel";
import { PortfolioCaseStudyIndex } from "./components/PortfolioCaseStudyIndex";
import { TaskOrchestratorWorkbench } from "./components/TaskOrchestratorWorkbench";
import { TextureDeliveryConsole } from "./components/TextureDeliveryConsole";
import { VisualReviewStudio } from "./components/VisualReviewStudio";
import { developmentLoop, modules, sprintQueue } from "./data/modules";
import { DccPayloadProvider } from "./lib/dccPayloadContext";
import type { ModuleState, ToolModule } from "./types";

const moduleIcons = {
  "asset-protocol": Boxes,
  "rule-matrix": ClipboardCheck,
  "visual-review": ImageUp,
  "texture-console": Activity,
  "task-orchestrator": Network,
};

const stateLabels: Record<ModuleState, string> = {
  active: "Active",
  queued: "Queued",
  planned: "Planned",
};

function App() {
  const [selectedId, setSelectedId] = useState(modules[0].id);
  const [view, setView] = useState<"logic" | "build" | "evidence">("logic");

  const selected = useMemo(
    () => modules.find((module) => module.id === selectedId) ?? modules[0],
    [selectedId],
  );

  return (
    <DccPayloadProvider>
    <div className="app-shell">
      <aside className="sidebar" aria-label="工具模块">
        <div className="brand-lockup">
          <div className="brand-mark">
            <LayoutDashboard size={18} aria-hidden="true" />
          </div>
          <div>
            <p className="eyebrow">AI Tool TA</p>
            <h1>Production Toolbench</h1>
          </div>
        </div>

        <nav className="module-nav">
          {modules.map((module) => {
            const Icon = moduleIcons[module.id as keyof typeof moduleIcons];
            return (
              <button
                className="module-nav-item"
                data-selected={module.id === selected.id}
                key={module.id}
                onClick={() => setSelectedId(module.id)}
                type="button"
              >
                <Icon size={18} aria-hidden="true" />
                <span>{module.name}</span>
                <strong>{module.phase}</strong>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-block">
          <p className="label">Split Strategy</p>
          <p>
            5 modules: fixture, core, evidence.
          </p>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">{selected.phase} {stateLabels[selected.state]} Cycle</p>
            <h2>{selected.name}</h2>
          </div>
          <div className="toolbar" aria-label="当前动作">
            <button className="icon-button" type="button" title="同步计划">
              <RefreshCw size={17} aria-hidden="true" />
              <span>Sync</span>
            </button>
            <button className="primary-button" type="button">
              <Play size={17} aria-hidden="true" />
              <span>Run Module</span>
            </button>
          </div>
        </header>

        <section className="module-strip" aria-label="模块概览">
          {modules.map((module) => (
            <ModuleCard
              key={module.id}
              module={module}
              selected={module.id === selected.id}
              onSelect={() => setSelectedId(module.id)}
            />
          ))}
        </section>

        <div className="content-grid">
          <section className="detail-panel" aria-labelledby="selected-module">
            <div className="panel-header">
              <div>
                <p className="eyebrow">{selected.phase} / {stateLabels[selected.state]}</p>
                <h2 id="selected-module">{selected.name}</h2>
              </div>
              <StatusChip state={selected.state} />
            </div>

            <p className="thesis">{selected.thesis}</p>

            <div className="segmented-control" role="tablist" aria-label="模块视图">
              {[
                ["logic", "Core Logic"],
                ["build", "Build Plan"],
                ["evidence", "Evidence"],
              ].map(([key, label]) => (
                <button
                  aria-selected={view === key}
                  className="segment"
                  key={key}
                  onClick={() => setView(key as typeof view)}
                  role="tab"
                  type="button"
                >
                  {label}
                </button>
              ))}
            </div>

            {view === "logic" &&
              (selected.id === "asset-protocol" ? (
                <AssetProtocolWorkbench />
              ) : selected.id === "rule-matrix" ? (
                <CrossDccRuleMatrix />
              ) : selected.id === "visual-review" ? (
                <VisualReviewStudio />
              ) : selected.id === "texture-console" ? (
                <TextureDeliveryConsole />
              ) : selected.id === "task-orchestrator" ? (
                <TaskOrchestratorWorkbench />
              ) : (
                <LogicView module={selected} />
              ))}
            {view === "build" && <BuildView module={selected} />}
            {view === "evidence" && <EvidenceView module={selected} />}
          </section>

          <aside className="right-rail" aria-label="开发循环">
            <MayaBridgePanel />
            <AssetHandoffGatePanel />
            <DccShowcaseRunbookPanel />

            <section className="rail-panel">
              <div className="rail-title">
                <GitBranch size={17} aria-hidden="true" />
                <h3>Long-running Loop</h3>
              </div>
              <div className="loop-list">
                {developmentLoop.map((step) => (
                  <div className="loop-step" data-state={step.state} key={step.name}>
                    <span className="loop-dot" aria-hidden="true" />
                    <div>
                      <strong>{step.name}</strong>
                      <p>{step.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rail-panel">
              <div className="rail-title">
                <FileText size={17} aria-hidden="true" />
                <h3>Sprint Queue</h3>
              </div>
              <ol className="sprint-list">
                {sprintQueue.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            </section>
          </aside>
        </div>
      </main>
    </div>
    </DccPayloadProvider>
  );
}

function ModuleCard({
  module,
  selected,
  onSelect,
}: {
  module: ToolModule;
  selected: boolean;
  onSelect: () => void;
}) {
  const Icon = moduleIcons[module.id as keyof typeof moduleIcons];

  return (
    <button
      className="module-card"
      data-selected={selected}
      onClick={onSelect}
      type="button"
    >
      <span className="module-card-top">
        <Icon size={18} aria-hidden="true" />
        <StatusChip state={module.state} />
      </span>
      <strong>{module.name}</strong>
      <span className="module-card-source">{module.source[0]}</span>
      <span className="progress-track" aria-label={`${module.progress}%`}>
        <span style={{ width: `${module.progress}%` }} />
      </span>
    </button>
  );
}

function StatusChip({ state }: { state: ModuleState }) {
  return (
    <span className="status-chip" data-state={state}>
      {stateLabels[state]}
    </span>
  );
}

function LogicView({ module }: { module: ToolModule }) {
  return (
    <div className="view-grid">
      <section className="logic-block wide">
        <div className="section-title">
          <ShieldAlert size={17} aria-hidden="true" />
          <h3>Business Secret</h3>
        </div>
        <p>{module.businessSecret}</p>
      </section>

      <ListBlock title="Deterministic Core" items={module.deterministicCore} />
      <ListBlock title="AI Role" items={module.aiRole} />

      <section className="logic-block wide">
        <h3>Method Sources</h3>
        <div className="source-list">
          {module.source.map((source) => (
            <code key={source}>{source}</code>
          ))}
        </div>
      </section>
    </div>
  );
}

function BuildView({ module }: { module: ToolModule }) {
  return (
    <div className="view-grid">
      <ListBlock title="First Build" items={module.firstBuild} />
      <ListBlock title="Risk Controls" items={module.risks} tone="warning" />
      <section className="logic-block wide">
        <h3>Execution Shape</h3>
        <div className="pipeline-row">
          {["Fixture", "Schema", "Engine", "UI", "AI Explain", "Report"].map((stage) => (
            <span key={stage}>{stage}</span>
          ))}
        </div>
      </section>
    </div>
  );
}

function EvidenceView({ module }: { module: ToolModule }) {
  if (module.id === "task-orchestrator") {
    return (
      <div className="evidence-grid stacked">
        <DccFirstCasePage />
        <details className="legacy-case-index">
          <summary>Legacy R8 Browser Evidence Ledger</summary>
          <PortfolioCaseStudyIndex />
        </details>
      </div>
    );
  }

  return (
    <div className="evidence-grid">
      {module.evidence.map((item, index) => (
        <div className="evidence-item" key={item}>
          <CheckCircle2 size={18} aria-hidden="true" />
          <div>
            <strong>{item}</strong>
            <p>Evidence #{index + 1} for module review and case-study packaging.</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function ListBlock({
  title,
  items,
  tone = "default",
}: {
  title: string;
  items: string[];
  tone?: "default" | "warning";
}) {
  return (
    <section className="logic-block" data-tone={tone}>
      <h3>{title}</h3>
      <ul className="tight-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export default App;
