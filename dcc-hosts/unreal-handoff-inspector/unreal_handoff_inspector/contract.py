"""Headless Unreal handoff inspector contract.

This module proves the engine-side inspection shape and can attach Unreal
Python runtime evidence from the public test project.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-handoff-inspector-contract@0.4.0"
PRESET_FACT_REPORT_VERSION = "unreal-preset-fact-comparison@0.1.0"
FIXTURE_SCHEMA = "synthetic-unreal-handoff@0.1.0"


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def evaluate_project(fixture: Dict[str, Any]) -> Dict[str, Any]:
    project = fixture.get("project", {})
    registry = fixture.get("contentRegistry", {})
    intents = fixture.get("importIntents", [])
    presets = {preset["id"]: preset for preset in fixture.get("platformPresets", [])}
    rows = [_evaluate_intent(intent, project, registry, presets) for intent in intents]
    summary = _summarize(rows)
    return {
        "schema": "unreal-handoff-inspector-evaluation@0.1.0",
        "summary": summary,
        "rows": rows,
        "dryRunCommands": [row["dryRunCommand"] for row in rows if row.get("dryRunCommand")],
        "blockedReasons": _blocked_reasons(rows),
    }


def build_report(
    fixture_path: str | Path,
    unreal_cli_available: bool = False,
    unreal_cli_path: str | None = None,
    unreal_project_path: str | None = None,
    unreal_python_executed: bool = False,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    evaluation = evaluate_project(fixture)
    registry_evidence = _registry_evidence(runtime_snapshot)
    engine_fact_evidence = _engine_fact_evidence(runtime_snapshot)
    l3_status = _l3_status(
        unreal_cli_available,
        unreal_project_path,
        unreal_python_executed,
        registry_evidence,
        engine_fact_evidence,
    )
    evidence_level = (
        "L3++"
        if engine_fact_evidence.get("matched")
        else "L3+"
        if registry_evidence.get("matched")
        else "L3"
        if unreal_python_executed
        else "L2"
    )
    next_step = (
        "Expand Unreal inspection to compare platform preset import options and exception waivers against the engine facts."
        if engine_fact_evidence.get("matched")
        else "Expand registry comparison to source import-data, material slots, LOD count and collision settings."
        if registry_evidence.get("matched")
        else "Expand the public Unreal test project with generated static mesh/material assets and compare real Content Registry rows."
        if unreal_python_executed
        else "Run the same import intent checks through UnrealEditor-Cmd -run=pythonscript against a test .uproject."
    )
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Handoff Inspector",
        "evidenceLevel": evidence_level,
        "l3Status": l3_status,
        "unrealCli": {
            "available": unreal_cli_available,
            "path": unreal_cli_path,
        },
        "unrealProject": {
            "available": bool(unreal_project_path),
            "path": unreal_project_path,
        },
        "unrealPython": runtime_snapshot or {
            "executed": unreal_python_executed,
            "runtime": "not_run",
        },
        "unrealRegistryEvidence": registry_evidence,
        "unrealEngineFactEvidence": engine_fact_evidence,
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "unreal-handoff-inspector",
            "name": "Unreal Handoff Inspector",
            "methodSource": "Maya Engine Handoff Preflight / Unreal Python import task inspection",
            "protocolCarrier": "DCC import sidecar + Unreal content path + asset import metadata",
            "boundary": {
                "mutation": "public_test_project_fixture_write" if registry_evidence.get("matched") else "contract_validation_only",
                "engineWrites": 0,
                "assetWrites": registry_evidence.get("assetWrites", 0) + engine_fact_evidence.get("assetWrites", 0),
                "nextStep": next_step,
            },
        },
        "projectSnapshot": {
            "engine": fixture.get("project", {}).get("engine"),
            "engineVersion": fixture.get("project", {}).get("engineVersion"),
            "mountRoots": fixture.get("project", {}).get("mountRoots", []),
            "pythonPluginEnabled": fixture.get("project", {}).get("pythonPluginEnabled"),
            "assetCount": len(fixture.get("contentRegistry", {}).get("assets", [])),
        },
        "evaluation": evaluation,
        "reviewerClaims": [
            "Engine handoff is checked after DCC preflight: the inspector validates Unreal path, import class, source fingerprint, platform preset, material dependencies, LOD/collision policy, and owner hold state.",
            "Ready and blocked paths are both present in the fixture, so the reviewer can inspect failure behavior instead of only a happy path.",
            "Unreal Python runtime evidence is included when available; any asset write is limited to the public test project fixture path.",
            "L3++ evidence reads source import data, material slots, LOD count and collision settings from the generated Unreal StaticMesh fixture.",
        ],
    }


def build_preset_fact_comparison_report(
    fixture_path: str | Path,
    unreal_report_path: str | Path,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    report_path = Path(unreal_report_path)
    unreal_report = json.loads(report_path.read_text(encoding="utf-8"))
    comparison = compare_engine_facts_to_presets(fixture, unreal_report)
    return {
        "reportVersion": PRESET_FACT_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Handoff Inspector",
        "sourceReport": {
            "path": str(report_path),
            "reportVersion": unreal_report.get("reportVersion"),
            "evidenceLevel": unreal_report.get("evidenceLevel"),
            "l3Status": unreal_report.get("l3Status"),
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "summary": comparison["summary"],
        "presetSummaries": comparison["presetSummaries"],
        "assetComparisons": comparison["assetComparisons"],
        "factRows": comparison["factRows"],
        "waiverRows": comparison["waiverRows"],
        "policy": {
            "comparisonRule": "Compare Unreal runtime facts against platform preset expectations before import approval.",
            "waiverRule": "Approved waivers convert specific preset/fact drift into Review, not Ready; expired or missing waivers keep drift visible.",
            "blockedRule": "Path, source, material and collision mismatches hold import because they affect engine addressability or gameplay behavior.",
            "engineWrites": 0,
            "mutation": "comparison_artifact_only",
        },
        "reviewerClaims": [
            "R17 joins DCC preset intent with Unreal runtime facts instead of stopping at sidecar preflight.",
            "Every preset/fact row resolves to matched, drift, waived, or blocked so reviewer decisions are auditable.",
            "The PC single-LOD exception is represented as an owner-scoped waiver row, while Mobile remains blocked by platform path and LOD policy.",
        ],
    }


def compare_engine_facts_to_presets(
    fixture: Dict[str, Any],
    unreal_report: Dict[str, Any],
) -> Dict[str, Any]:
    engine_evidence = unreal_report.get("unrealEngineFactEvidence", {})
    engine_facts = engine_evidence.get("facts", {})
    asset_path = engine_evidence.get("assetPath")
    import_intents = fixture.get("importIntents", [])
    presets = fixture.get("platformPresets", [])
    waivers = fixture.get("exceptionWaivers", [])
    intent = _find_intent_for_engine_asset(import_intents, asset_path)
    fact_rows: List[Dict[str, Any]] = []
    preset_summaries: List[Dict[str, Any]] = []
    asset_comparisons: List[Dict[str, Any]] = []

    for preset in presets:
        preset_id = preset.get("id")
        preset_rows = _compare_preset_rows(intent, preset, asset_path, engine_facts, waivers)
        fact_rows.extend(preset_rows)
        preset_summaries.append(_summarize_preset_rows(preset, preset_rows))

    if intent:
        states_by_preset = {
            summary["preset"]: summary["gate"]
            for summary in preset_summaries
        }
        unique_gates = sorted(set(states_by_preset.values()))
        asset_comparisons.append(
            {
                "assetId": intent.get("assetId"),
                "label": intent.get("label"),
                "enginePath": asset_path,
                "presetGates": states_by_preset,
                "delta": "same_state" if len(unique_gates) == 1 else "platform_split",
                "dispositions": {
                    summary["preset"]: summary["disposition"]
                    for summary in preset_summaries
                },
            }
        )

    status_counts = _status_counts(fact_rows)
    preset_gates = [summary["gate"] for summary in preset_summaries]
    summary = {
        "gate": "Blocked" if "Blocked" in preset_gates else "Review" if "Review" in preset_gates else "Ready",
        "presetCount": len(preset_summaries),
        "assetCount": len(asset_comparisons),
        "factRows": len(fact_rows),
        "matched": status_counts.get("matched", 0),
        "drift": status_counts.get("drift", 0),
        "waived": status_counts.get("waived", 0),
        "blocked": status_counts.get("blocked", 0),
        "platformSplit": sum(1 for row in asset_comparisons if row["delta"] == "platform_split"),
        "sameState": sum(1 for row in asset_comparisons if row["delta"] == "same_state"),
        "approvedWaivers": len([row for row in fact_rows if row["status"] == "waived"]),
        "sourceEvidenceLevel": unreal_report.get("evidenceLevel"),
        "sourceL3Status": unreal_report.get("l3Status"),
    }
    return {
        "summary": summary,
        "presetSummaries": preset_summaries,
        "assetComparisons": asset_comparisons,
        "factRows": fact_rows,
        "waiverRows": _waiver_rows(waivers, fact_rows),
    }


def _find_intent_for_engine_asset(
    import_intents: Iterable[Dict[str, Any]],
    asset_path: str | None,
) -> Dict[str, Any] | None:
    for intent in import_intents:
        if intent.get("enginePath") == asset_path:
            return intent
    return None


def _compare_preset_rows(
    intent: Dict[str, Any] | None,
    preset: Dict[str, Any],
    asset_path: str | None,
    engine_facts: Dict[str, Any],
    waivers: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    preset_id = preset.get("id")
    asset_id = intent.get("assetId") if intent else None
    material_dependencies = intent.get("materialDependencies", []) if intent else []
    expected_material = _expected_material(engine_facts)
    actual_collision = _actual_collision_policy(engine_facts.get("collision", {}))
    actual_lod_count = _int_or_zero(engine_facts.get("lod", {}).get("lodCount"))
    min_lods = _int_or_zero(preset.get("minLods"))
    source_matched = bool(engine_facts.get("sourceImportData", {}).get("sourceFileMatched"))
    material_matched = bool(engine_facts.get("materialSlots", {}).get("expectedMaterialAssigned")) and (
        not expected_material or expected_material in material_dependencies
    )
    path_prefix = preset.get("pathPrefix") or "/Game/AI_Tool_TA/"
    rows = [
        _preset_fact_row(
            asset_id,
            preset_id,
            "engine-path",
            asset_path,
            "startsWith:%s" % path_prefix,
            bool(asset_path and str(asset_path).startswith(path_prefix)),
            "blocked",
            "Engine path must match platform content root.",
            waivers,
        ),
        _preset_fact_row(
            asset_id,
            preset_id,
            "source-import-data",
            "matched=%s" % source_matched,
            "sourceFileMatched=true",
            source_matched,
            "blocked",
            "Regenerate Unreal asset from the expected DCC export source.",
            waivers,
        ),
        _preset_fact_row(
            asset_id,
            preset_id,
            "material-slot",
            expected_material or "missing",
            "assigned material dependency",
            material_matched,
            "blocked",
            "Relink material slot to a declared handoff dependency.",
            waivers,
        ),
        _preset_fact_row(
            asset_id,
            preset_id,
            "lod-count",
            actual_lod_count,
            "minLods=%s" % min_lods,
            actual_lod_count >= min_lods,
            "drift",
            "Generate the preset LOD chain or attach an approved platform exception.",
            waivers,
        ),
        _preset_fact_row(
            asset_id,
            preset_id,
            "collision-policy",
            actual_collision,
            "allowed=%s" % ",".join(preset.get("allowedCollision", [])),
            actual_collision in preset.get("allowedCollision", []),
            "blocked",
            "Author allowed collision or attach an approved collision waiver.",
            waivers,
        ),
    ]
    if not intent:
        return [
            {
                **row,
                "status": "blocked",
                "matched": False,
                "fixPreview": "Add a DCC import intent that targets this Unreal runtime asset.",
            }
            for row in rows
        ]
    return rows


def _preset_fact_row(
    asset_id: str | None,
    preset_id: str | None,
    fact_id: str,
    actual: Any,
    expected: Any,
    matched: bool,
    fail_status: str,
    fix_preview: str,
    waivers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    waiver = _find_approved_waiver(waivers, asset_id, preset_id, fact_id)
    status = "matched" if matched else "waived" if waiver else fail_status
    return {
        "id": "%s-%s-%s" % (asset_id or "missing-intent", preset_id or "unknown", fact_id),
        "assetId": asset_id,
        "preset": preset_id,
        "factId": fact_id,
        "status": status,
        "matched": bool(matched),
        "actual": actual,
        "expected": expected,
        "waiver": waiver,
        "fixPreview": "None" if matched else "Waiver accepted: %s" % waiver["id"] if waiver else fix_preview,
    }


def _find_approved_waiver(
    waivers: Iterable[Dict[str, Any]],
    asset_id: str | None,
    preset_id: str | None,
    fact_id: str,
) -> Dict[str, Any] | None:
    for waiver in waivers:
        if (
            waiver.get("assetId") == asset_id
            and waiver.get("preset") == preset_id
            and waiver.get("factId") == fact_id
            and waiver.get("state") == "approved"
        ):
            return {
                "id": waiver.get("id"),
                "owner": waiver.get("owner"),
                "expiresOn": waiver.get("expiresOn"),
                "reason": waiver.get("reason"),
            }
    return None


def _summarize_preset_rows(
    preset: Dict[str, Any],
    rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    counts = _status_counts(rows)
    gate = "Blocked" if counts.get("blocked", 0) else "Review" if counts.get("drift", 0) or counts.get("waived", 0) else "Ready"
    return {
        "preset": preset.get("id"),
        "platform": preset.get("platform"),
        "gate": gate,
        "factRows": len(rows),
        "matched": counts.get("matched", 0),
        "drift": counts.get("drift", 0),
        "waived": counts.get("waived", 0),
        "blocked": counts.get("blocked", 0),
        "disposition": "hold_engine_import"
        if gate == "Blocked"
        else "review_approved_exception"
        if gate == "Review"
        else "ready_for_import",
    }


def _status_counts(rows: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"matched": 0, "drift": 0, "waived": 0, "blocked": 0}
    for row in rows:
        status = row.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _waiver_rows(
    waivers: Iterable[Dict[str, Any]],
    fact_rows: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    consumed = {
        row.get("waiver", {}).get("id")
        for row in fact_rows
        if isinstance(row.get("waiver"), dict)
    }
    rows = []
    for waiver in waivers:
        rows.append(
            {
                "id": waiver.get("id"),
                "assetId": waiver.get("assetId"),
                "preset": waiver.get("preset"),
                "factId": waiver.get("factId"),
                "state": waiver.get("state"),
                "owner": waiver.get("owner"),
                "expiresOn": waiver.get("expiresOn"),
                "consumedByComparison": waiver.get("id") in consumed,
                "reason": waiver.get("reason"),
            }
        )
    return rows


def _expected_material(engine_facts: Dict[str, Any]) -> str | None:
    value = engine_facts.get("materialSlots", {}).get("expectedMaterialPath")
    return value if isinstance(value, str) and value else None


def _actual_collision_policy(collision_facts: Dict[str, Any]) -> str:
    if _int_or_zero(collision_facts.get("simpleShapeCount")) > 0:
        return "simple"
    if collision_facts.get("collisionTraceFlag"):
        return "complex"
    return "missing"


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _evaluate_intent(
    intent: Dict[str, Any],
    project: Dict[str, Any],
    registry: Dict[str, Any],
    presets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    preset = presets.get(intent.get("platformPreset"), {})
    assets_by_path = {asset.get("path"): asset for asset in registry.get("assets", [])}
    dependency_paths = set(registry.get("dependencyPaths", []))
    engine_path = str(intent.get("enginePath", ""))
    existing_asset = assets_by_path.get(engine_path)
    checks = [
        _check(
            "owner-state",
            "Owner State",
            intent.get("ownerState") == "accepted" and intent.get("state") == "ready_for_import",
            "blocked",
            "state=%s owner=%s" % (intent.get("state"), intent.get("ownerState")),
            "Keep intent held until owner disposition and DCC gate are accepted.",
        ),
        _check(
            "mount-root",
            "Mount Root",
            any(engine_path.startswith(root) for root in project.get("mountRoots", [])),
            "blocked",
            "path=%s roots=%s" % (engine_path or "-", ",".join(project.get("mountRoots", []))),
            "Move target path under an allowed Unreal mount root.",
        ),
        _check(
            "platform-preset",
            "Platform Preset",
            intent.get("platform") == preset.get("platform"),
            "review",
            "intent=%s preset=%s" % (intent.get("platform"), preset.get("platform")),
            "Choose matching platform preset or split package by platform.",
        ),
        _check(
            "asset-class",
            "Asset Class",
            intent.get("assetClass") in preset.get("allowedAssetClasses", []),
            "blocked",
            "assetClass=%s allowed=%s" % (intent.get("assetClass"), ",".join(preset.get("allowedAssetClasses", []))),
            "Use a supported Unreal import factory for this package.",
        ),
        _check(
            "source-fingerprint",
            "Source Fingerprint",
            bool(intent.get("sourceFingerprint")) and intent.get("sourceFingerprint") == intent.get("sidecarFingerprint"),
            "blocked",
            "source=%s sidecar=%s" % (intent.get("sourceFingerprint"), intent.get("sidecarFingerprint")),
            "Regenerate the sidecar from the exported DCC source file.",
        ),
        _check(
            "content-conflict",
            "Content Conflict",
            not existing_asset or existing_asset.get("sourceFingerprint") == intent.get("sourceFingerprint"),
            "review",
            "existing=%s" % (existing_asset.get("sourceFingerprint") if existing_asset else "none"),
            "Require reviewer confirmation before replacing an existing Unreal asset.",
        ),
        _check(
            "material-dependencies",
            "Material Dependencies",
            _dependencies_available(intent.get("materialDependencies", []), dependency_paths),
            "blocked",
            "deps=%s" % ",".join(intent.get("materialDependencies", [])),
            "Import or relink material dependencies before asset import.",
        ),
        _check(
            "lod-policy",
            "LOD Policy",
            int(intent.get("lodCount") or 0) >= int(preset.get("minLods") or 0),
            "review",
            "lods=%s min=%s" % (intent.get("lodCount"), preset.get("minLods")),
            "Generate required LODs or attach a platform exception.",
        ),
        _check(
            "collision-policy",
            "Collision Policy",
            intent.get("collision") in preset.get("allowedCollision", []),
            "blocked",
            "collision=%s allowed=%s" % (intent.get("collision"), ",".join(preset.get("allowedCollision", []))),
            "Author collision or attach an approved no-collision waiver.",
        ),
        _check(
            "python-plugin",
            "Python Plugin",
            bool(project.get("pythonPluginEnabled")),
            "blocked",
            "pythonPluginEnabled=%s" % project.get("pythonPluginEnabled"),
            "Enable Unreal PythonScriptPlugin for automated inspection.",
        ),
    ]
    state = _row_state(checks)
    dry_run_command = None
    if state == "import_ready":
        dry_run_command = {
            "id": "dry-run-import-%s" % intent.get("assetId"),
            "mutationAllowed": False,
            "commandPreview": "AssetImportTask(filename=%s, destination_path=%s, automated=True, save=False)"
            % (intent.get("sourceFile"), engine_path),
            "expectedFactory": intent.get("assetClass"),
            "targetPath": engine_path,
        }
    return {
        "id": "unreal-inspect-%s" % intent.get("assetId"),
        "assetId": intent.get("assetId"),
        "label": intent.get("label"),
        "platformPreset": intent.get("platformPreset"),
        "enginePath": engine_path,
        "state": state,
        "checks": checks,
        "existingAsset": existing_asset,
        "dryRunCommand": dry_run_command,
        "disposition": "create_unreal_import_task_preview" if dry_run_command else "hold_unreal_import",
    }


def _check(
    check_id: str,
    label: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _dependencies_available(required: Iterable[str], available: set[str]) -> bool:
    return all(path in available for path in required)


def _row_state(checks: List[Dict[str, Any]]) -> str:
    if any(check["status"] == "blocked" for check in checks):
        return "blocked"
    if any(check["status"] == "review" for check in checks):
        return "review"
    return "import_ready"


def _summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = [check["status"] for row in rows for check in row["checks"]]
    ready = sum(1 for row in rows if row["state"] == "import_ready")
    review = sum(1 for row in rows if row["state"] == "review")
    blocked = sum(1 for row in rows if row["state"] == "blocked")
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "intentCount": len(rows),
        "importReady": ready,
        "review": review,
        "blocked": blocked,
        "dryRunCommands": sum(1 for row in rows if row.get("dryRunCommand")),
        "passChecks": statuses.count("pass"),
        "reviewChecks": statuses.count("review"),
        "blockedChecks": statuses.count("blocked"),
    }


def _blocked_reasons(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    reasons = []
    for row in rows:
        for check in row.get("checks", []):
            if check["status"] == "pass":
                continue
            reasons.append(
                {
                    "assetId": row.get("assetId"),
                    "checkId": check["id"],
                    "status": check["status"],
                    "evidence": check["evidence"],
                    "fixPreview": check["fixPreview"],
                }
            )
    return reasons


def _l3_status(
    unreal_cli_available: bool,
    unreal_project_path: str | None,
    unreal_python_executed: bool,
    registry_evidence: Dict[str, Any] | None = None,
    engine_fact_evidence: Dict[str, Any] | None = None,
) -> str:
    if engine_fact_evidence and engine_fact_evidence.get("matched"):
        return "unreal_engine_facts_matched"
    if registry_evidence and registry_evidence.get("matched"):
        return "unreal_registry_fixture_matched"
    if unreal_python_executed:
        return "unreal_python_executed"
    if not unreal_cli_available:
        return "blocked_by_missing_unreal_cli"
    if not unreal_project_path:
        return "blocked_by_missing_unreal_project"
    return "ready_for_unreal_python_smoke"


def _registry_evidence(runtime_snapshot: Dict[str, Any] | None) -> Dict[str, Any]:
    if not runtime_snapshot:
        return {
            "matched": False,
            "expectedAssetCount": 0,
            "matchedAssetCount": 0,
            "assetWrites": 0,
            "rows": [],
        }
    fixture_assets = runtime_snapshot.get("fixtureAssets") or {}
    rows = fixture_assets.get("rows") or []
    expected = fixture_assets.get("expectedAssetCount", len(rows))
    matched = fixture_assets.get("matchedAssetCount", 0)
    return {
        "matched": bool(fixture_assets.get("matched")) and expected > 0 and matched == expected,
        "expectedAssetCount": expected,
        "matchedAssetCount": matched,
        "missingAssetCount": fixture_assets.get("missingAssetCount", 0),
        "classMismatchCount": fixture_assets.get("classMismatchCount", 0),
        "assetWrites": fixture_assets.get("assetWrites", 0),
        "fixtureRoot": fixture_assets.get("fixtureRoot"),
        "sourceFiles": fixture_assets.get("sourceFiles", []),
        "rows": rows,
    }


def _engine_fact_evidence(runtime_snapshot: Dict[str, Any] | None) -> Dict[str, Any]:
    if not runtime_snapshot:
        return {
            "matched": False,
            "expectedFactCount": 0,
            "matchedFactCount": 0,
            "assetWrites": 0,
            "facts": {},
            "rows": [],
        }
    facts = runtime_snapshot.get("engineFacts") or {}
    rows = facts.get("rows") or []
    expected = facts.get("expectedFactCount", len(rows))
    matched = facts.get("matchedFactCount", sum(1 for row in rows if row.get("matched")))
    return {
        "matched": bool(facts.get("matched")) and expected > 0 and matched == expected,
        "expectedFactCount": expected,
        "matchedFactCount": matched,
        "missingFactCount": facts.get("missingFactCount", max(expected - matched, 0)),
        "assetWrites": facts.get("assetWrites", 0),
        "assetPath": facts.get("assetPath"),
        "facts": facts.get("facts", {}),
        "rows": rows,
        "errors": facts.get("errors", []),
        "apiProbe": facts.get("apiProbe", {}),
    }
