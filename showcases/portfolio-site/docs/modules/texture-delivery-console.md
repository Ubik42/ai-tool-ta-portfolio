# Texture Delivery Console

R4 module for the AI Tool TA portfolio. The source method comes from Lightbox texture and external-process tools: `texture_to_engine_reference`, `substance_delivery_reference`, `photoshop_dds_reference`, `spritesheet_reference`, and Substance custom shader workflows.

## Business Logic

Texture delivery is not an image converter. The valuable TA logic is the contract that binds source naming, semantic texture roles, channel packing, color space, compression, mipmaps, platform limits, queue execution, and engine import manifest into one traceable package.

The tool models that contract as deterministic data:

- source file parser: reads asset, set, role, and resolution tokens.
- packing preset: declares output files, channel maps, required roles, format, compression, mipmaps, and texture group.
- platform profile: declares max texture size, package budget, preferred format, compression set, and engine import root.
- risk gate: blocks on missing channels, wrong normal color space, oversize textures, or budget overflow.
- queue runner: turns parse, pack, compress, manifest, and sync into inspectable tasks.
- import manifest: records the engine path and import settings that downstream tools can consume.

AI is deliberately secondary: it explains deterministic failures and drafts a concise risk brief. It does not decide whether a texture package is valid.

## R4.1 Baseline

Implemented:

- three synthetic fixtures: Rifle ORM Pack, Vehicle Mobile Overbudget, Skill Sprite Sheet.
- fixed preset selection and platform selection.
- source naming parse table.
- channel packing preview.
- risk gate.
- queue state simulation.
- platform import manifest.
- JSON export report.

Evidence:

- `assets/texture-delivery-r4-1-console-full.png`
- `assets/texture-delivery-r4-1-mobile-tall.png`
- `assets/texture-delivery-r4-1-exported-report.json`

## R4.2 Preset Contract Editor

Implemented in this cycle:

- runtime preset editor for each output rule.
- editable output format, compression, color space, texture group, and mipmap flag.
- editable channel role mapping.
- preset diff summary between source preset and runtime edited preset.
- report version `texture-delivery-report@0.2.0`.
- exported report now contains `presetSnapshot` and `presetEditSummary`.

This turns the module from a selector demo into a real TA workflow: the reviewer can see the exact delivery contract, modify it, and verify how the change affects output packing and archived evidence.

Verification targets:

- editing Rifle Normal compression from `BC5` to `BC1` updates packed output compression.
- disabling Rifle Normal mipmaps updates packed output and manifest.
- exported JSON records the changed preset fields.
- completed queue state remains consistent after preset edits.

Evidence:

- `assets/texture-delivery-r4-2-preset-editor-full.png`
- `assets/texture-delivery-r4-2-mobile-tall.png`
- `assets/texture-delivery-r4-2-exported-report.json`

## R4.3 Queue Recovery

Implemented in this cycle:

- queue modes: Dry Run, Submitted, Processing, Completed, Failed, Cancelled, Retrying, Resumed.
- task attempts with status, duration, and log text.
- failure classification: source contract, platform gate, budget gate, external process, operator cancelled.
- recovery actions: retry failed task, resume from checkpoint, resolve gate.
- retry command generation and command diff audit.
- report version `texture-delivery-report@0.3.0`.
- exported report now contains `queueRecovery` and per-task `attempts`, `checkpoint`, `retryCommand`, `failureClass`, `recoveryAction`, and `commandDiff`.

This models the part of texture pipeline work that is easy to underestimate: DDS compression, Substance export, Photoshop batch scripts, sprite packing, and engine import are long-running external processes. A production tool must know what already ran, what failed, what can be retried, and what must be blocked until deterministic gates are fixed.

Verification targets:

- Vehicle Mobile Overbudget in `Retrying` mode reports a blocked platform or budget recovery path.
- active task records attempt 1 failed and attempt 2 retrying.
- retry command switches to dry-run gate report when deterministic blockers exist.
- exported JSON records the queue recovery summary and command diff.

Evidence:

- `assets/texture-delivery-r4-3-queue-recovery-full.png`
- `assets/texture-delivery-r4-3-mobile-tall.png`
- `assets/texture-delivery-r4-3-exported-report.json`

## R4.4 Preset Versioning

Implemented in this cycle:

- approved preset version registry.
- staged version derived from runtime preset edits.
- rule fingerprint for review and diff stability.
- promotion checklist for platform scope, deterministic gate, compression contract, format contract, runtime override, and mipmap policy.
- promotion gate: Ready, Review, Blocked.
- report version `texture-delivery-report@0.4.0`.
- exported report now contains `presetPromotion`.

This models a real production rule: an artist or TA can temporarily override delivery settings for a package, but that override is not a shared project preset until it passes platform compatibility and reviewer approval.

Verification targets:

- Rifle ORM Pack with Normal compression `BC1` and mipmaps disabled stages `ue_orm_bc@1.1.0-staged`.
- deterministic package gate stays Ready.
- promotion gate becomes Review because runtime overrides need TA approval.
- exported JSON records checklist status, staged version, and rule fingerprint.

Evidence:

- `assets/texture-delivery-r4-4-preset-versioning-full.png`
- `assets/texture-delivery-r4-4-mobile-tall.png`
- `assets/texture-delivery-r4-4-exported-report.json`

## R4.5 Publish Gate

Implemented in this cycle:

- frozen manifest derived from current packed outputs and import settings.
- last approved package baseline for each fixture.
- publish diff across output count, output settings, package size, runtime preset overrides, queue completion, and open risks.
- publish checklist for deterministic package gate, queue completion, preset promotion, manifest freeze, and approved delta.
- review packet with reviewers, attachments, handoff message, and packet id.
- report version `texture-delivery-report@0.5.0`.
- exported report now contains `publishPackage`.

This models the final production handoff: the tool should not only say that files can be exported. It must freeze exactly what will be published, compare it against the last approved package, and produce a compact review packet that a TA or platform owner can accept or reject.

Verification targets:

- Rifle ORM Pack with Normal compression `BC1`, mipmaps disabled, and Completed queue produces a frozen manifest.
- package gate stays Ready, but publish gate becomes Review because preset and output settings differ from the approved package.
- publish diff records Normal output settings, package size, and runtime preset override.
- review packet contains reviewers, attachments, and handoff message.

Evidence:

- `assets/texture-delivery-r4-5-publish-gate-full.png`
- `assets/texture-delivery-r4-5-mobile-tall.png`
- `assets/texture-delivery-r4-5-exported-report.json`
- `assets/texture-delivery-r4-5-review-packet.json`

## R4.6 Real Adapter Layer

Implemented in this cycle:

- adapter interface for Photoshop, Substance Painter, command-line compressors, and engine import.
- deterministic portfolio dry-run mode.
- adapter registry with owner, executable, timeout, read/write boundaries, and mutation policy.
- adapter execution plan with command, guard, status, reads, writes, log sample, and AI diagnostic.
- adapter diagnostics for blocked gates, review-only execution, incomplete queues, and color-space source failures.
- report version `texture-delivery-report@0.6.0`.
- exported report now contains `adapterExecutionPlan`.

This closes the R4 module as a production-style texture delivery tool. The important logic is not pretending to run Photoshop or Unreal from the browser. The important logic is the boundary: deterministic code produces commands and gates, external adapters own mutation, and AI can only summarize logs, group failure reasons, and draft handoff text.

Verification targets:

- Rifle ORM Pack with runtime Normal changes and Completed queue produces a Review adapter plan.
- plan contains 4 adapters: Photoshop Normalize, Substance Export, CLI Compressor, Engine Import.
- every adapter step is `portfolio_dry_run` and `mutationAllowed` is false.
- engine import stays dry-run when publish gate is Review.
- exported adapter plan records diagnostics and AI log summary.

Evidence:

- `assets/texture-delivery-r4-6-adapter-layer-full.png`
- `assets/texture-delivery-r4-6-mobile-tall.png`
- `assets/texture-delivery-r4-6-exported-report.json`
- `assets/texture-delivery-r4-6-adapter-plan.json`

## R4.7 Public Fixture Approved Delta

Implemented in this cycle:

- public synthetic fixture `public_crate_orm` with source and target paths under `<repo>/fixtures/public_texture_crate`.
- baseline approved package `approved-public-crate-body-1.0.0`.
- approved package delta derived from last approved fingerprints and the current frozen manifest.
- committed manifest with targetRoot, allowed file list, settings signatures, source signatures, and mutation boundary.
- report version `texture-delivery-report@0.7.0`.
- exported report now contains `approvedPackageDelta` and `committedManifest`.

This is the R4 business point that matters for a tool TA portfolio: a texture tool has to prove what will change before it lets any Photoshop, Substance, compressor, or engine adapter write files. The public fixture makes the evidence reproducible; the delta makes the file mutation reviewable; the committed manifest keeps AI outside the write boundary.

Verification targets:

- Public Crate ORM Fixture with Completed queue produces package gate `Ready`.
- publish/delta gate stays `Review` because the approved baseline has one changed output and one newly added ORM output.
- delta summary records 1 added, 1 changed, 1 unchanged, 0 blocked.
- committed manifest status is `review_required` with 3 files.
- exported report records fixture scope `portfolio_public_synthetic`.

Evidence:

- `assets/texture-delivery-r4-7-public-fixture-delta-full.png`
- `assets/texture-delivery-r4-7-mobile-tall.png`
- `assets/texture-delivery-r4-7-exported-report.json`
- `assets/texture-delivery-r4-7-committed-manifest.json`

## R4 Status

Texture Delivery Console now covers the complete synthetic production chain and has R4.7 evidence ready for owner review:

- source parse.
- channel packing.
- platform risk gate.
- preset editing and diff.
- queue recovery.
- preset versioning.
- publish gate.
- adapter execution boundary.
- public fixture contract.
- approved package delta.
- committed manifest.

R7.4 status:

- R4 `accept-texture-r4` is accepted in `owner-signoff-ledger@0.1.0`.
- Signed scope: public fixture delta, committed manifest, and external adapter mutation boundary.
- Evidence entry: `assets/portfolio-case-study-r7-4-exported-report.json`.

Next loop: R7.5 public case package, then R8 complex asset dependency / publish impact analyzer.

