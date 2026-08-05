import { useMemo, useState } from "react";
import {
  ClipboardCheck,
  Download,
  FileJson,
  FileText,
  Filter,
  Image,
  PackageCheck,
  ShieldCheck,
  Table2,
} from "lucide-react";
import {
  type CaseStudyAcceptanceState,
  type CaseStudyCheckStatus,
  type CaseStudyGate,
  type EvidenceManifestArtifactStatus,
  type EvidenceManifestGroupId,
  type CaseStudyModuleId,
  type EvidenceKind,
  type OwnerSignoffDecision,
  type PendingReceiptClosureStatus,
  type PendingReceiptEvidenceStatus,
  getPortfolioCaseStudyReport,
} from "../data/portfolioCaseStudy";

type ModuleFilter = "all" | CaseStudyModuleId;
type KindFilter = "all" | EvidenceKind;
type GateFilter = "all" | CaseStudyGate;
type ManifestGroupFilter = EvidenceManifestGroupId;

const evidenceKindLabels: Record<EvidenceKind, string> = {
  screenshot: "Screenshot",
  json: "JSON",
  doc: "Doc",
};

const gateLabels: Record<CaseStudyGate, string> = {
  Ready: "Ready",
  Review: "Review",
  Blocked: "Blocked",
};

const comparisonHeaderLabels: Record<CaseStudyModuleId, string> = {
  "asset-protocol": "Asset",
  "rule-matrix": "Rules",
  "visual-review": "Visual",
  "texture-console": "Tex",
  "task-orchestrator": "Ops",
};

const checkStatusLabels: Record<CaseStudyCheckStatus, string> = {
  pass: "Pass",
  review: "Review",
  blocked: "Blocked",
};

const acceptanceStateLabels: Record<CaseStudyAcceptanceState, string> = {
  accepted: "Accepted",
  pending: "Pending",
  rework: "Rework",
};

const manifestStatusLabels: Record<EvidenceManifestArtifactStatus, string> = {
  present: "Present",
  generated: "Generated",
  pending: "Pending",
};

const pendingClosureLabels: Record<PendingReceiptClosureStatus, string> = {
  accepted: "Accepted",
  ready_to_review: "Ready to review",
  needs_fixture: "Needs fixture",
  blocked: "Blocked",
};

const ownerSignoffDecisionLabels: Record<OwnerSignoffDecision, string> = {
  accepted: "Accepted",
  change_requested: "Change Requested",
};

const pendingEvidenceStatusLabels: Record<PendingReceiptEvidenceStatus, string> = {
  present: "Present",
  draft: "Draft",
  missing: "Missing",
};

function evidenceIcon(kind: EvidenceKind) {
  if (kind === "json") return FileJson;
  if (kind === "doc") return FileText;
  return Image;
}

function downloadReport() {
  const report = getPortfolioCaseStudyReport();
  const blob = new Blob([JSON.stringify(report, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${report.reportId}-exported-report.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function PortfolioCaseStudyIndex() {
  const report = useMemo(() => getPortfolioCaseStudyReport(), []);
  const [selectedModuleId, setSelectedModuleId] =
    useState<CaseStudyModuleId>("task-orchestrator");
  const [moduleFilter, setModuleFilter] = useState<ModuleFilter>("all");
  const [kindFilter, setKindFilter] = useState<KindFilter>("all");
  const [gateFilter, setGateFilter] = useState<GateFilter>("all");
  const [manifestGroupId, setManifestGroupId] = useState<ManifestGroupFilter>("screenshot");
  const [selectedPendingReceiptId, setSelectedPendingReceiptId] = useState(
    report.pendingReceiptReview.reviews.find((review) => review.receiptId === "accept-impact-r8")?.id ??
      report.pendingReceiptReview.reviews[0]?.id ??
      "",
  );

  const selectedModule = report.modules.find((module) => module.id === selectedModuleId);
  const selectedContract = report.caseCardContracts.find(
    (contract) => contract.moduleId === selectedModuleId,
  );
  const selectedAcceptance = report.reviewerAcceptance.items.filter(
    (item) => item.moduleId === selectedModuleId,
  );
  const evidenceLabelById = useMemo(
    () => new Map(report.evidenceIndex.map((item) => [item.id, item.label])),
    [report.evidenceIndex],
  );
  const filteredEvidence = report.evidenceIndex.filter((item) => {
    const moduleMatch = moduleFilter === "all" || item.moduleId === moduleFilter;
    const kindMatch = kindFilter === "all" || item.kind === kindFilter;
    const gateMatch = gateFilter === "all" || item.gate === gateFilter;
    return moduleMatch && kindMatch && gateMatch;
  });
  const selectedManifestGroup =
    report.evidenceManifest.groups.find((group) => group.id === manifestGroupId) ??
    report.evidenceManifest.groups[0];
  const selectedPendingReceipt =
    report.pendingReceiptReview.reviews.find((review) => review.id === selectedPendingReceiptId) ??
    report.pendingReceiptReview.reviews[0];

  const summaryItems = [
    ["Modules", report.summary.moduleCount],
    ["Evidence", report.summary.indexedEvidenceCount],
    ["Required", report.summary.requiredEvidenceCount],
    ["Manifest", report.summary.manifestArtifacts],
    ["Commands", report.summary.validationCommands],
    ["Ready Cards", report.summary.readyCaseCards],
    ["Review Cards", report.summary.reviewCaseCards],
    ["Req Pending", report.summary.acceptanceRequiredPending],
    ["Signoffs", report.summary.ownerSignoffs],
    ["Package Files", report.summary.publicPackageFiles],
    ["Public Ready", report.summary.readyForPublicPackage ? "Yes" : "No"],
    ["Receipt Reviews", report.summary.pendingReceiptReviews],
    ["Missing Proof", report.summary.pendingReceiptRequiredMissing],
  ] as const;

  return (
    <div className="portfolio-case-study-index">
      <section className="logic-block wide portfolio-case-hero">
        <div>
          <p className="eyebrow">R8.27 Package Evidence</p>
          <h3>Portfolio Case Study Index</h3>
          <p>
            作品集拆成五个工具模块，共用一个入口；每个模块都必须讲清楚业务场景、确定性核心、
            AI 边界、证据包、reviewer acceptance 和依赖影响签收。
          </p>
        </div>
        <button className="primary-button compact" type="button" onClick={downloadReport}>
          <Download size={16} aria-hidden="true" />
          <span>Export Report</span>
        </button>
      </section>

      <section className="portfolio-case-summary" aria-label="case study summary">
        {summaryItems.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Table2 size={17} aria-hidden="true" />
          <h3>Module Case Cards</h3>
        </div>

        <div className="portfolio-case-tabs" role="tablist" aria-label="case modules">
          {report.modules.map((module) => (
            <button
              aria-pressed={selectedModuleId === module.id}
              className="portfolio-case-tab"
              key={module.id}
              onClick={() => setSelectedModuleId(module.id)}
              type="button"
            >
              <span>{module.phase}</span>
              <strong>{module.shortName}</strong>
              <small>{module.gate}</small>
            </button>
          ))}
        </div>

        {selectedModule && (
          <div className="portfolio-case-detail">
            <div>
              <span>Business Scenario</span>
              <p>{selectedModule.businessScenario}</p>
            </div>
            <div>
              <span>Core Secret</span>
              <p>{selectedModule.coreSecret}</p>
            </div>
            <div>
              <span>AI Boundary</span>
              <p>{selectedModule.aiBoundary}</p>
            </div>
            <div>
              <span>Reviewer Takeaway</span>
              <p>{selectedModule.reviewerTakeaway}</p>
            </div>
            <div>
              <span>Deterministic Core</span>
              <ul className="tight-list">
                {selectedModule.deterministicCore.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <span>Source Methods</span>
              <div className="source-list">
                {selectedModule.sourceMethods.map((item) => (
                  <code key={item}>{item}</code>
                ))}
              </div>
            </div>
            <div className="portfolio-case-next">
              <span>Next Build</span>
              <p>{selectedModule.nextBuild}</p>
            </div>
            {selectedContract && (
              <div className="portfolio-card-contract">
                <span>Case Card Contract</span>
                <p>{selectedContract.presenterHook}</p>
                <div className="portfolio-contract-facts">
                  <div>
                    <span>Readiness</span>
                    <strong data-status={selectedContract.readinessStatus}>
                      {checkStatusLabels[selectedContract.readinessStatus]}
                    </strong>
                  </div>
                  <div>
                    <span>Proof Bundle</span>
                    <strong>{selectedContract.proofBundleIds.length}</strong>
                  </div>
                  <div>
                    <span>Missing</span>
                    <strong>{selectedContract.missingForReady.length}</strong>
                  </div>
                </div>
                <div className="portfolio-check-list">
                  {selectedContract.checklist.map((item) => (
                    <article className="portfolio-check-row" data-status={item.status} key={item.id}>
                      <strong>{item.label}</strong>
                      <span>{checkStatusLabels[item.status]}</span>
                      <p>{item.note}</p>
                      <div>
                        {item.evidenceIds.map((id) => (
                          <code key={id}>{evidenceLabelById.get(id) ?? id}</code>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
                {selectedContract.missingForReady.length > 0 && (
                  <ul className="tight-list">
                    {selectedContract.missingForReady.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            {selectedAcceptance.length > 0 && (
              <div className="portfolio-card-contract">
                <span>Selected Module Receipts</span>
                <div className="portfolio-check-list">
                  {selectedAcceptance.map((item) => (
                    <article className="portfolio-check-row" data-status={item.state} key={item.id}>
                      <strong>{item.owner}</strong>
                      <span>{acceptanceStateLabels[item.state]}</span>
                      <p>{item.note}</p>
                      <code>{item.nextAction}</code>
                    </article>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="logic-block wide portfolio-acceptance-panel">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Reviewer Acceptance</h3>
        </div>
        <div className="portfolio-acceptance-summary" data-gate={report.reviewerAcceptance.summary.gate}>
          <div>
            <span>Portfolio Gate</span>
            <strong>{report.reviewerAcceptance.summary.gate}</strong>
          </div>
          <div>
            <span>Accepted</span>
            <strong data-state="accepted">{report.reviewerAcceptance.summary.accepted}</strong>
          </div>
          <div>
            <span>Pending</span>
            <strong data-state="pending">{report.reviewerAcceptance.summary.pending}</strong>
          </div>
          <div>
            <span>Required Pending</span>
            <strong data-state="pending">{report.reviewerAcceptance.summary.requiredPending}</strong>
          </div>
        </div>
        <div className="portfolio-acceptance-list">
          {report.reviewerAcceptance.items.map((item) => {
            const module = report.modules.find((candidate) => candidate.id === item.moduleId);
            return (
              <article className="portfolio-acceptance-row" data-state={item.state} key={item.id}>
                <ShieldCheck size={18} aria-hidden="true" />
                <div>
                  <div className="portfolio-evidence-title">
                    <strong>{item.criterion}</strong>
                    <span>{module?.shortName ?? item.moduleId}</span>
                    <span>{acceptanceStateLabels[item.state]}</span>
                    {item.required && <span>Required</span>}
                  </div>
                  <p>{item.note}</p>
                  <code>{item.nextAction}</code>
                  <div className="portfolio-receipt-evidence">
                    {item.evidenceIds.map((id) => (
                      <code key={id}>{evidenceLabelById.get(id) ?? id}</code>
                    ))}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
        <p className="portfolio-acceptance-next">{report.reviewerAcceptance.summary.nextAction}</p>
      </section>

      <section className="logic-block wide portfolio-signoff-panel">
        <div className="section-title">
          <ShieldCheck size={17} aria-hidden="true" />
          <h3>Owner Signoff Ledger</h3>
        </div>
        <div className="source-list">
          <code>{report.ownerSignoffLedger.reportVersion}</code>
          <code>{report.ownerSignoffLedger.reportId}</code>
        </div>
        <div className="portfolio-signoff-summary" data-gate={report.ownerSignoffLedger.summary.releaseGate}>
          <div>
            <span>Release Gate</span>
            <strong>{report.ownerSignoffLedger.summary.releaseGate}</strong>
          </div>
          <div>
            <span>Accepted</span>
            <strong data-state="accepted">{report.ownerSignoffLedger.summary.accepted}</strong>
          </div>
          <div>
            <span>Required Accepted</span>
            <strong data-state="accepted">{report.ownerSignoffLedger.summary.requiredAccepted}</strong>
          </div>
          <div>
            <span>Change Requested</span>
            <strong data-state={report.ownerSignoffLedger.summary.changeRequested > 0 ? "pending" : "accepted"}>
              {report.ownerSignoffLedger.summary.changeRequested}
            </strong>
          </div>
        </div>
        <div className="portfolio-signoff-list">
          {report.ownerSignoffLedger.receipts.map((receipt) => {
            const module = report.modules.find((candidate) => candidate.id === receipt.moduleId);
            return (
              <article className="portfolio-signoff-card" data-decision={receipt.decision} key={receipt.id}>
                <div className="portfolio-signoff-head">
                  <div>
                    <span>{module?.shortName ?? receipt.moduleId}</span>
                    <strong>{receipt.owner}</strong>
                    <p>{receipt.role} / {receipt.signedAt}</p>
                  </div>
                  <div>
                    <span>{ownerSignoffDecisionLabels[receipt.decision]}</span>
                    <strong>{receipt.gateBefore} {"->"} {receipt.gateAfter}</strong>
                    <p>{receipt.receiptId}</p>
                  </div>
                </div>
                <p>{receipt.signoffStatement}</p>
                <div className="portfolio-signoff-grid">
                  <div>
                    <span>Accepted Scope</span>
                    <ul className="tight-list">
                      {receipt.acceptedScope.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span>Guardrails</span>
                    <ul className="tight-list">
                      {receipt.guardrails.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div className="portfolio-signoff-risk">
                  <span>Residual Risk</span>
                  <p>{receipt.residualRisk}</p>
                  <code>{receipt.nextAction}</code>
                </div>
                <div className="portfolio-receipt-evidence">
                  {receipt.evidenceIds.map((id) => (
                    <code key={id}>{evidenceLabelById.get(id) ?? id}</code>
                  ))}
                </div>
              </article>
            );
          })}
        </div>
        <p className="portfolio-acceptance-next">{report.ownerSignoffLedger.summary.nextAction}</p>
      </section>

      <section className="logic-block wide portfolio-package-panel">
        <div className="section-title">
          <PackageCheck size={17} aria-hidden="true" />
          <h3>Public Case Package</h3>
        </div>
        <div className="source-list">
          <code>{report.publicCasePackage.packageVersion}</code>
          <code>{report.publicCasePackage.packageId}</code>
          <code>{report.publicCasePackage.sourceReportId}</code>
          <code>{report.publicCasePackage.evidenceManifestId}</code>
        </div>
        <div className="portfolio-package-summary" data-gate={report.publicCasePackage.releaseGate}>
          <div>
            <span>Release Gate</span>
            <strong>{report.publicCasePackage.releaseGate}</strong>
          </div>
          <div>
            <span>Package Files</span>
            <strong>{report.publicCasePackage.summary.packageFileCount}</strong>
          </div>
          <div>
            <span>Evidence</span>
            <strong>{report.publicCasePackage.summary.evidenceCount}</strong>
          </div>
          <div>
            <span>Required</span>
            <strong>{report.publicCasePackage.summary.requiredEvidenceCount}</strong>
          </div>
          <div>
            <span>Validation</span>
            <strong>{report.publicCasePackage.summary.validationCommandCount}</strong>
          </div>
          <div>
            <span>Signoffs</span>
            <strong data-state="accepted">{report.publicCasePackage.summary.ownerSignoffCount}</strong>
          </div>
        </div>

        <div className="portfolio-package-body">
          <div className="portfolio-package-context">
            <span>Package Root</span>
            <code>{report.publicCasePackage.rootPath}</code>
            <span>Reviewer Order</span>
            <div className="portfolio-package-order">
              {report.publicCasePackage.moduleOrder.map((moduleId) => {
                const module = report.modules.find((candidate) => candidate.id === moduleId);
                return <strong key={moduleId}>{module?.shortName ?? moduleId}</strong>;
              })}
            </div>
            <p>{report.publicCasePackage.summary.nextAction}</p>
          </div>

          <div className="portfolio-package-files">
            {report.publicCasePackage.files.map((file) => (
              <article className="portfolio-package-file" data-kind={file.kind} key={file.id}>
                <div className="portfolio-evidence-title">
                  <strong>{file.label}</strong>
                  <span>{file.kind}</span>
                  {file.required && <span>Required</span>}
                </div>
                <code>{file.path}</code>
                <p>{file.proves}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="logic-block wide portfolio-pending-panel">
        <div className="section-title">
          <ClipboardCheck size={17} aria-hidden="true" />
          <h3>Pending Receipt Review</h3>
        </div>
        <div className="source-list">
          <code>{report.pendingReceiptReview.reportVersion}</code>
          <code>{report.pendingReceiptReview.reportId}</code>
        </div>
        <div className="portfolio-pending-summary">
          <div>
            <span>Total</span>
            <strong>{report.pendingReceiptReview.summary.total}</strong>
          </div>
          <div>
            <span>Accepted</span>
            <strong data-state="accepted">{report.pendingReceiptReview.summary.accepted}</strong>
          </div>
          <div>
            <span>Ready Review</span>
            <strong data-state="ready_to_review">
              {report.pendingReceiptReview.summary.readyToReview}
            </strong>
          </div>
          <div>
            <span>Needs Fixture</span>
            <strong data-state="needs_fixture">{report.pendingReceiptReview.summary.needsFixture}</strong>
          </div>
          <div>
            <span>Missing Proof</span>
            <strong data-state="missing">{report.pendingReceiptReview.summary.requiredMissing}</strong>
          </div>
          <div>
            <span>Draft Proof</span>
            <strong data-state="draft">{report.pendingReceiptReview.summary.draftEvidence}</strong>
          </div>
        </div>

        <div className="portfolio-pending-tabs" role="tablist" aria-label="pending receipt reviews">
          {report.pendingReceiptReview.reviews.map((review) => {
            const module = report.modules.find((candidate) => candidate.id === review.moduleId);
            return (
              <button
                aria-pressed={selectedPendingReceiptId === review.id}
                className="portfolio-pending-tab"
                data-status={review.closureStatus}
                key={review.id}
                onClick={() => setSelectedPendingReceiptId(review.id)}
                type="button"
              >
                <strong>{module?.shortName ?? review.moduleId}</strong>
                <span>{pendingClosureLabels[review.closureStatus]}</span>
                <small>{review.receiptId}</small>
              </button>
            );
          })}
        </div>

        {selectedPendingReceipt && (
          <div className="portfolio-pending-detail" data-status={selectedPendingReceipt.closureStatus}>
            <div className="portfolio-pending-facts">
              <div>
                <span>Owner</span>
                <strong>{selectedPendingReceipt.owner}</strong>
              </div>
              <div>
                <span>Gate</span>
                <strong>{selectedPendingReceipt.gate}</strong>
              </div>
              <div>
                <span>Status</span>
                <strong data-state={selectedPendingReceipt.closureStatus}>
                  {pendingClosureLabels[selectedPendingReceipt.closureStatus]}
                </strong>
              </div>
              <div>
                <span>Evidence</span>
                <strong>{selectedPendingReceipt.requiredEvidenceIds.length}</strong>
              </div>
            </div>

            <div className="portfolio-pending-copy">
              <span>Receipt</span>
              <h4>{selectedPendingReceipt.title}</h4>
              <p>{selectedPendingReceipt.problem}</p>
            </div>
            <div className="portfolio-pending-copy">
              <span>Business Risk</span>
              <p>{selectedPendingReceipt.businessRisk}</p>
            </div>
            <div className="portfolio-pending-copy">
              <span>Reviewer Question</span>
              <p>{selectedPendingReceipt.reviewerQuestion}</p>
            </div>

            <div className="portfolio-pending-proof">
              <span>Deterministic Proof</span>
              <ul className="tight-list">
                {selectedPendingReceipt.deterministicProof.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="portfolio-pending-check-list">
              {selectedPendingReceipt.evidenceChecks.map((check) => (
                <article className="portfolio-pending-check-row" data-status={check.status} key={check.id}>
                  <div className="portfolio-evidence-title">
                    <strong>{check.label}</strong>
                    <span>{pendingEvidenceStatusLabels[check.status]}</span>
                    {check.required && <span>Required</span>}
                  </div>
                  <p>{check.note}</p>
                  <code>{check.nextAction}</code>
                  <div className="portfolio-receipt-evidence">
                    {check.evidenceIds.length > 0 ? (
                      check.evidenceIds.map((id) => <code key={id}>{evidenceLabelById.get(id) ?? id}</code>)
                    ) : (
                      <code>Evidence pending</code>
                    )}
                  </div>
                </article>
              ))}
            </div>

            <div className="portfolio-pending-options">
              {selectedPendingReceipt.decisionOptions.map((option) => (
                <span key={option}>{option}</span>
              ))}
            </div>
            <code className="portfolio-pending-command">{selectedPendingReceipt.closureCommand}</code>
          </div>
        )}
        <p className="portfolio-acceptance-next">{report.pendingReceiptReview.summary.nextAction}</p>
      </section>

      <section className="logic-block wide portfolio-manifest-panel">
        <div className="section-title">
          <FileText size={17} aria-hidden="true" />
          <h3>Evidence Manifest</h3>
        </div>
        <div className="source-list">
          <code>{report.evidenceManifest.manifestVersion}</code>
          <code>{report.evidenceManifest.manifestId}</code>
        </div>
        <div className="portfolio-manifest-summary" data-gate={report.evidenceManifest.releaseGate.gate}>
          <div>
            <span>Manifest Gate</span>
            <strong>{report.evidenceManifest.releaseGate.gate}</strong>
          </div>
          <div>
            <span>Artifacts</span>
            <strong>{report.evidenceManifest.coverage.artifactCount}</strong>
          </div>
          <div>
            <span>Required</span>
            <strong>{report.evidenceManifest.coverage.requiredArtifactCount}</strong>
          </div>
          <div>
            <span>Validation</span>
            <strong>{report.evidenceManifest.coverage.validationCommandCount}</strong>
          </div>
          <div>
            <span>Generated</span>
            <strong>{report.evidenceManifest.coverage.generatedArtifactCount}</strong>
          </div>
          <div>
            <span>Pending</span>
            <strong data-state="pending">{report.evidenceManifest.coverage.pendingArtifactCount}</strong>
          </div>
        </div>

        <div className="portfolio-manifest-tabs" role="tablist" aria-label="evidence manifest groups">
          {report.evidenceManifest.groups.map((group) => (
            <button
              aria-pressed={manifestGroupId === group.id}
              className="portfolio-manifest-tab"
              key={group.id}
              onClick={() => setManifestGroupId(group.id)}
              type="button"
            >
              <strong>{group.label}</strong>
              <span>{group.itemCount} items</span>
            </button>
          ))}
        </div>

        <div className="portfolio-manifest-detail">
          <div className="portfolio-manifest-intent">
            <span>{selectedManifestGroup.label}</span>
            <p>{selectedManifestGroup.intent}</p>
          </div>
          <div className="portfolio-manifest-artifacts">
            {selectedManifestGroup.artifacts.map((artifact) => {
              const command = artifact.commandId
                ? report.evidenceManifest.validationCommands.find((item) => item.id === artifact.commandId)
                : undefined;
              const module = artifact.moduleId
                ? report.modules.find((candidate) => candidate.id === artifact.moduleId)
                : undefined;
              return (
                <article className="portfolio-manifest-row" data-status={artifact.status} key={artifact.id}>
                  <div className="portfolio-evidence-title">
                    <strong>{artifact.label}</strong>
                    {module && <span>{module.shortName}</span>}
                    <span>{manifestStatusLabels[artifact.status]}</span>
                    {artifact.required && <span>Required</span>}
                  </div>
                  {artifact.path && <code>{artifact.path}</code>}
                  {command && <code>{command.command}</code>}
                  <p>{artifact.proves}</p>
                </article>
              );
            })}
          </div>
        </div>

        <div className="portfolio-coverage-grid">
          {report.evidenceManifest.coverage.byModule.map((coverage) => {
            const module = report.modules.find((item) => item.id === coverage.moduleId);
            return (
              <article key={coverage.moduleId}>
                <span>{module?.shortName ?? coverage.moduleId}</span>
                <strong>{coverage.indexed} indexed</strong>
                <p>
                  {coverage.required} required · {coverage.screenshot} screenshots · {coverage.json} JSON ·{" "}
                  {coverage.doc} docs
                </p>
              </article>
            );
          })}
        </div>

        <div className="portfolio-validation-list">
          {report.evidenceManifest.validationCommands.map((command) => (
            <article className="portfolio-validation-row" data-state={command.lastStatus} key={command.id}>
              <div className="portfolio-evidence-title">
                <strong>{command.label}</strong>
                <span>{command.lastStatus}</span>
              </div>
              <code>{command.command}</code>
              <p>{command.proves}</p>
              <small>{command.cwd}</small>
            </article>
          ))}
        </div>
        <p className="portfolio-acceptance-next">{report.evidenceManifest.releaseGate.nextAction}</p>
      </section>

      <section className="logic-block wide">
        <div className="section-title">
          <Table2 size={17} aria-hidden="true" />
          <h3>Module Comparison Matrix</h3>
        </div>
        <div className="portfolio-case-table-scroll">
          <table className="portfolio-case-table">
            <thead>
              <tr>
                <th>Axis</th>
                {report.modules.map((module) => (
                  <th key={module.id}>{comparisonHeaderLabels[module.id]}</th>
                ))}
                <th>Portfolio Takeaway</th>
              </tr>
            </thead>
            <tbody>
              {report.comparisonRows.map((row) => (
                <tr key={row.axis}>
                  <th>{row.axis}</th>
                  {report.modules.map((module) => (
                    <td key={module.id}>{row.values[module.id]}</td>
                  ))}
                  <td>{row.portfolioTakeaway}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="logic-block wide">
        <div className="portfolio-evidence-head">
          <div className="section-title">
            <Filter size={17} aria-hidden="true" />
            <h3>Portfolio Evidence Index</h3>
          </div>
          <span>{filteredEvidence.length} items</span>
        </div>

        <div className="portfolio-evidence-filters">
          <label className="field-control">
            <span>Module</span>
            <select
              value={moduleFilter}
              onChange={(event) => setModuleFilter(event.target.value as ModuleFilter)}
            >
              <option value="all">All modules</option>
              {report.modules.map((module) => (
                <option key={module.id} value={module.id}>
                  {module.moduleName}
                </option>
              ))}
            </select>
          </label>
          <label className="field-control">
            <span>Type</span>
            <select
              value={kindFilter}
              onChange={(event) => setKindFilter(event.target.value as KindFilter)}
            >
              <option value="all">All types</option>
              {Object.entries(evidenceKindLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="field-control">
            <span>Gate</span>
            <select
              value={gateFilter}
              onChange={(event) => setGateFilter(event.target.value as GateFilter)}
            >
              <option value="all">All gates</option>
              {Object.entries(gateLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="portfolio-evidence-list">
          {filteredEvidence.map((item) => {
            const Icon = evidenceIcon(item.kind);
            const module = report.modules.find((candidate) => candidate.id === item.moduleId);
            return (
              <article className="portfolio-evidence-row" data-gate={item.gate} key={item.id}>
                <Icon size={18} aria-hidden="true" />
                <div>
                  <div className="portfolio-evidence-title">
                    <strong>{item.label}</strong>
                    <span>{module?.shortName ?? item.moduleId}</span>
                    <span>{evidenceKindLabels[item.kind]}</span>
                    {item.required && <span>Required</span>}
                  </div>
                  <code>{item.path}</code>
                  <p>{item.proves}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="logic-block wide portfolio-narrative-panel">
        <h3>Portfolio Narrative Draft</h3>
        <ol>
          {report.portfolioNarrative.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
        <h4>Next Long-running Loop</h4>
        <ul className="tight-list">
          {report.nextBuild.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
