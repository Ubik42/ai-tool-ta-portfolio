"""Unreal-side Groom import readiness facts.

The module joins R46 Maya groom export facts with a read-only Unreal Python
probe. It checks whether the public project can see Groom / Alembic import API
surfaces, target assets, and the intended Groom / Binding paths before any
Alembic import executor is allowed to write public assets.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


REPORT_VERSION = "groom-unreal-readiness@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def resolve_public_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    return Path(path)


def build_unreal_readiness_report(
    source_groom_path: str | Path,
    runtime_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_groom_path)
    source_exists = source_path.exists()
    source = json.loads(source_path.read_text(encoding="utf-8")) if source_exists else {}
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "assets": [],
    }
    facts = build_readiness_facts(source, source_exists, runtime_snapshot)
    evaluation = evaluate_readiness(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    blocked_reason = runtime.get("blockedReason")
    executed = bool(runtime.get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_groom_import_readiness_collected" if executed else "contract_groom_unreal_readiness"),
        "sourceArtifact": {
            "path": public_path(source_path),
            "exists": source_exists,
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "sourceGroomSummary": source.get("evaluation", {}).get("summary", {}),
        "unrealRuntime": runtime,
        "apiAvailability": runtime.get("api", {}),
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "groom-unreal-readiness",
            "name": "Groom Unreal Import Readiness",
            "methodSource": "R46 Maya Groom Export Inspector + Unreal Python read-only asset/API probe",
            "protocolCarrier": "Groom Alembic cache intent + Unreal GroomAsset / GroomBindingAsset / AssetImportTask API surface",
            "boundary": {
                "mutation": "unreal_read_only_import_readiness_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "read-only probe; no import and no save"),
            },
        },
        "reviewerClaims": [
            "R47 extends Groom Export Inspector from Maya-side groom facts to Unreal-side import readiness without writing assets.",
            "The report separates source groom contract health, Unreal Groom/Alembic API visibility, target SkeletalMesh presence, and missing expected Groom/Binding assets.",
            "Missing Groom or Binding assets are review gaps for the next Alembic executor; source TMP groom defects and absent Unreal runtime/API surfaces remain hard blockers.",
        ],
    }


def build_readiness_facts(
    source: Dict[str, Any],
    source_exists: bool,
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    source_assets = source.get("facts", {}).get("assets", [])
    source_summary = source.get("evaluation", {}).get("summary", {})
    runtime_assets = {str(row.get("assetId")): row for row in runtime_snapshot.get("assets", [])}
    runtime = runtime_snapshot.get("runtime", {})
    api = runtime.get("api", {})
    rows = []
    for source_row in source_assets:
        asset_id = str(source_row.get("assetId"))
        normalized = source_row.get("normalized", {})
        runtime_row = runtime_assets.get(asset_id, {})
        rows.append(_merge_asset_row(asset_id, source_row, normalized, source_summary, runtime_row, runtime, api))
    return {
        "schema": "groom-unreal-readiness-facts@0.1.0",
        "sourceReadable": source_exists,
        "sourceAssetCount": len(source_assets),
        "runtimeCollected": bool(runtime.get("executed")),
        "assets": rows,
        "summary": summarize_facts(rows, runtime_snapshot, source_exists),
    }


def summarize_facts(
    assets: Iterable[Dict[str, Any]],
    runtime_snapshot: Dict[str, Any],
    source_exists: bool,
) -> Dict[str, Any]:
    rows = list(assets)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "sourceReadable": source_exists,
        "assetRows": len(rows),
        "sourceReadyRows": sum(1 for row in rows if row.get("sourceStatus") == "Ready"),
        "sourceBlockedRows": sum(1 for row in rows if row.get("sourceStatus") == "Blocked"),
        "runtimeCollected": bool(runtime.get("executed")),
        "groomApiVisibleRows": sum(1 for row in rows if row.get("groomApiVisible")),
        "groomBindingApiVisibleRows": sum(1 for row in rows if row.get("groomBindingApiVisible")),
        "importTaskVisibleRows": sum(1 for row in rows if row.get("importTaskVisible")),
        "groomImportFactoryVisibleRows": sum(1 for row in rows if row.get("groomImportFactoryVisible")),
        "alembicImportFactoryVisibleRows": sum(1 for row in rows if row.get("alembicImportFactoryVisible")),
        "groomImportOptionsVisibleRows": sum(1 for row in rows if row.get("groomImportOptionsVisible")),
        "targetSkeletalMeshPresentRows": sum(1 for row in rows if row.get("targetSkeletalMeshExists")),
        "expectedGroomAssetsPresentRows": sum(1 for row in rows if row.get("expectedGroomAssetExists")),
        "expectedBindingAssetsPresentRows": sum(1 for row in rows if row.get("expectedBindingAssetExists")),
        "cacheContractReadyRows": sum(1 for row in rows if row.get("cacheContractReady")),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def evaluate_readiness(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    if not facts.get("sourceReadable"):
        evaluations.append(
            _eval(
                "source-groom-artifact",
                "source-artifact-readable",
                False,
                "error",
                "Source Groom Artifact",
                "Unreal readiness must start from the R46 Maya groom export artifact.",
                "missing",
                "Regenerate Groom Export Inspector Maya L3 before Unreal readiness.",
            )
        )
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row, runtime_snapshot))
    return {
        "schema": "groom-unreal-readiness-evaluation@0.1.0",
        "summary": summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": owner_actions(evaluations),
    }


def summarize_evaluations(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    asset_ids = sorted({row["assetId"] for row in rows})
    blocked = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked))
    ready = sorted(set(asset_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready),
        "reviewAssets": len(review),
        "blockedAssets": len(blocked),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready,
        "reviewAssetIds": review,
        "blockedAssetIds": blocked,
    }


def owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "owner": owner_for_rule(row["ruleId"]),
                "preview": row["fixPreview"],
                "writeBoundary": "readiness_only_no_import",
            }
        )
    return actions


def owner_for_rule(rule_id: str) -> str:
    if rule_id in ("unreal-python-runtime", "groom-api-surface", "import-api-surface", "target-skeletal-mesh-exists"):
        return "engine-ta"
    if rule_id in ("source-groom-row-ready", "cache-payload-contract", "source-artifact-readable"):
        return "groom-ta"
    if rule_id in ("groom-target-path-declared", "binding-target-path-declared", "expected-groom-asset-gap", "expected-binding-asset-gap"):
        return "content-owner"
    if rule_id == "no-write-boundary":
        return "pipeline-ta"
    return "reviewer"


def _merge_asset_row(
    asset_id: str,
    source_row: Dict[str, Any],
    normalized: Dict[str, Any],
    source_summary: Dict[str, Any],
    runtime_row: Dict[str, Any],
    runtime: Dict[str, Any],
    api: Dict[str, Any],
) -> Dict[str, Any]:
    source_status = _source_status(asset_id, source_summary)
    class_flags = api.get("classes", {}) if isinstance(api.get("classes"), dict) else {}
    expected_groom = str(normalized.get("unreal.expectedGroomAsset") or "")
    expected_binding = str(normalized.get("unreal.expectedBindingAsset") or "")
    target_mesh = str(normalized.get("unreal.targetSkeletalMesh") or "")
    include_root_uv = bool(normalized.get("export.includeRootUV"))
    include_strand_ids = bool(normalized.get("export.includeStrandIds"))
    include_guides = bool(normalized.get("export.includeGuideCurves"))
    frame_start = normalized.get("export.frameStart")
    frame_end = normalized.get("export.frameEnd")
    extension_matched = bool(normalized.get("export.extensionMatched"))
    cache_contract_ready = bool(
        extension_matched
        and include_root_uv
        and include_strand_ids
        and include_guides
        and frame_start is not None
        and frame_end is not None
        and int(frame_start) <= int(frame_end)
    )
    groom_api_visible = bool(api.get("groomApiVisible") or class_flags.get("GroomAsset"))
    groom_binding_api_visible = bool(api.get("groomBindingApiVisible") or class_flags.get("GroomBindingAsset"))
    import_task_visible = bool(api.get("importTaskVisible") or class_flags.get("AssetImportTask"))
    groom_import_factory_visible = bool(api.get("groomImportFactoryVisible") or class_flags.get("GroomImportFactory"))
    alembic_import_factory_visible = bool(api.get("alembicImportFactoryVisible") or class_flags.get("AlembicImportFactory"))
    groom_import_options_visible = bool(
        api.get("groomImportOptionsVisible")
        or class_flags.get("GroomImportOptions")
        or class_flags.get("GroomCacheImportOptions")
    )
    return {
        "assetId": asset_id,
        "assetLabel": source_row.get("assetLabel"),
        "sourceStatus": source_status,
        "sourceDcc": source_row.get("sourceDcc"),
        "descriptionName": normalized.get("description.name"),
        "ownerState": normalized.get("groom.ownerState"),
        "cachePath": normalized.get("export.cachePath"),
        "cacheExtensionMatched": extension_matched,
        "includeRootUV": include_root_uv,
        "includeStrandIds": include_strand_ids,
        "includeGuideCurves": include_guides,
        "frameStart": frame_start,
        "frameEnd": frame_end,
        "cacheContractReady": cache_contract_ready,
        "expectedGroomAsset": expected_groom,
        "expectedBindingAsset": expected_binding,
        "targetSkeletalMesh": target_mesh,
        "materialSlot": normalized.get("unreal.materialSlot"),
        "runtimeExecuted": bool(runtime.get("executed")),
        "runtimeMatched": bool(runtime_row),
        "groomApiVisible": groom_api_visible,
        "groomBindingApiVisible": groom_binding_api_visible,
        "importTaskVisible": import_task_visible,
        "groomImportFactoryVisible": groom_import_factory_visible,
        "alembicImportFactoryVisible": alembic_import_factory_visible,
        "groomImportOptionsVisible": groom_import_options_visible,
        "targetSkeletalMeshExists": bool(runtime_row.get("targetSkeletalMeshExists")),
        "targetSkeletalMeshClass": runtime_row.get("targetSkeletalMeshClass"),
        "expectedGroomAssetExists": bool(runtime_row.get("expectedGroomAssetExists")),
        "expectedGroomAssetClass": runtime_row.get("expectedGroomAssetClass"),
        "expectedBindingAssetExists": bool(runtime_row.get("expectedBindingAssetExists")),
        "expectedBindingAssetClass": runtime_row.get("expectedBindingAssetClass"),
        "assetProbeErrors": runtime_row.get("assetProbeErrors", []),
        "apiProbe": {
            "classRows": api.get("classes", {}),
            "groomClassNames": api.get("groomClassNames", []),
            "hairClassNames": api.get("hairClassNames", []),
            "alembicClassNames": api.get("alembicClassNames", []),
            "pluginRows": api.get("plugins", {}),
        },
    }


def _evaluate_asset(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = runtime_snapshot.get("runtime", {})
    import_api_ready = bool(
        row.get("importTaskVisible")
        and (row.get("groomImportFactoryVisible") or row.get("alembicImportFactoryVisible") or row.get("groomImportOptionsVisible"))
    )
    return [
        _eval(
            row["assetId"],
            "source-groom-row-ready",
            row.get("sourceStatus") == "Ready",
            "error",
            "Source Groom Row",
            "Only approved R46 Maya groom rows can enter Unreal import readiness.",
            str(row.get("sourceStatus")),
            "Resolve R46 Groom Export Inspector owner actions before engine readiness.",
        ),
        _eval(
            row["assetId"],
            "unreal-python-runtime",
            bool(runtime.get("executed")),
            "error",
            "Unreal Python Runtime",
            "Unreal readiness must be collected inside the public Unreal project.",
            str(runtime.get("executed")),
            "Run run_unreal_readiness.py with UnrealEditor-Cmd available.",
        ),
        _eval(
            row["assetId"],
            "groom-api-surface",
            bool(row.get("groomApiVisible") and row.get("groomBindingApiVisible")),
            "error",
            "Groom API Surface",
            "Groom import readiness needs GroomAsset and GroomBindingAsset API visibility.",
            "GroomAsset=%s GroomBindingAsset=%s" % (row.get("groomApiVisible"), row.get("groomBindingApiVisible")),
            "Enable/verify Unreal Groom plugin support in the public test project.",
        ),
        _eval(
            row["assetId"],
            "import-api-surface",
            import_api_ready,
            "error",
            "Import API Surface",
            "Alembic/Groom executor readiness needs AssetImportTask plus Groom/Alembic import options or factory visibility.",
            "AssetImportTask=%s GroomFactory=%s AlembicFactory=%s GroomOptions=%s"
            % (
                row.get("importTaskVisible"),
                row.get("groomImportFactoryVisible"),
                row.get("alembicImportFactoryVisible"),
                row.get("groomImportOptionsVisible"),
            ),
            "Install/enable the Unreal import plugin path before an Alembic executor is promoted.",
        ),
        _eval(
            row["assetId"],
            "target-skeletal-mesh-exists",
            bool(row.get("targetSkeletalMeshExists")),
            "error",
            "Target SkeletalMesh",
            "Groom binding readiness needs the target SkeletalMesh to exist in the public Unreal project.",
            row.get("targetSkeletalMesh"),
            "Create or relink the public target SkeletalMesh before Groom Binding import.",
        ),
        _eval(
            row["assetId"],
            "groom-target-path-declared",
            bool(row.get("expectedGroomAsset")),
            "error",
            "Expected Groom Asset Path",
            "The handoff must declare the GroomAsset package path that the executor will create or update.",
            row.get("expectedGroomAsset"),
            "Write unreal.expectedGroomAsset on the groom handoff payload.",
        ),
        _eval(
            row["assetId"],
            "binding-target-path-declared",
            bool(row.get("expectedBindingAsset")),
            "error",
            "Expected Binding Asset Path",
            "The handoff must declare the GroomBindingAsset package path for the target SkeletalMesh.",
            row.get("expectedBindingAsset"),
            "Write unreal.expectedBindingAsset on the groom handoff payload.",
        ),
        _eval(
            row["assetId"],
            "cache-payload-contract",
            bool(row.get("cacheContractReady")),
            "error",
            "Alembic Payload Contract",
            "The cache intent must be Alembic with root UV, strand IDs, guide curves and a valid frame range.",
            "abc=%s rootUV=%s ids=%s guides=%s range=%s-%s"
            % (
                row.get("cacheExtensionMatched"),
                row.get("includeRootUV"),
                row.get("includeStrandIds"),
                row.get("includeGuideCurves"),
                row.get("frameStart"),
                row.get("frameEnd"),
            ),
            "Fix the Alembic export payload before engine import readiness.",
        ),
        _eval(
            row["assetId"],
            "expected-groom-asset-gap",
            bool(row.get("expectedGroomAssetExists")),
            "warning",
            "Expected Groom Asset Exists",
            "A readiness-only pass may precede import, but missing expected Groom assets must stay visible for the executor plan.",
            row.get("expectedGroomAsset"),
            "Promote this row to the Alembic executor only after owner approval for creating the GroomAsset.",
        ),
        _eval(
            row["assetId"],
            "expected-binding-asset-gap",
            bool(row.get("expectedBindingAssetExists")),
            "warning",
            "Expected Binding Asset Exists",
            "A readiness-only pass may precede binding import, but missing expected Binding assets must stay visible.",
            row.get("expectedBindingAsset"),
            "Promote this row to the Alembic executor only after the target GroomAsset and SkeletalMesh are validated.",
        ),
        _eval(
            row["assetId"],
            "no-write-boundary",
            int(runtime.get("assetWrites", 0) or 0) == 0
            and int(runtime.get("engineWrites", 0) or 0) == 0
            and int(runtime.get("productionWrites", 0) or 0) == 0,
            "error",
            "Read-only Boundary",
            "R47 is an import readiness probe and must not create, import or save assets.",
            "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (runtime.get("assetWrites", 0), runtime.get("engineWrites", 0), runtime.get("productionWrites", 0)),
            "Revert any write side effects and keep Alembic import for the controlled executor stage.",
        ),
    ]


def _source_status(asset_id: str, source_summary: Dict[str, Any]) -> str:
    if asset_id in set(source_summary.get("readyAssetIds", [])):
        return "Ready"
    if asset_id in set(source_summary.get("reviewAssetIds", [])):
        return "Review"
    if asset_id in set(source_summary.get("blockedAssetIds", [])):
        return "Blocked"
    return "Unknown"


def _eval(
    asset_id: Any,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    message: str,
    evidence: Any,
    fix_preview: str,
) -> Dict[str, Any]:
    status = "pass" if passed else fail_status
    return {
        "id": "%s:%s" % (rule_id, asset_id),
        "assetId": str(asset_id),
        "ruleId": rule_id,
        "label": label,
        "status": status,
        "message": message if not passed else "%s is satisfied." % label,
        "evidence": evidence,
        "fixPreview": "No action." if passed else fix_preview,
    }


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts/groom-export-inspector-maya-l3-20260806-003711.json")
    print(json.dumps(build_unreal_readiness_report(source), ensure_ascii=False, indent=2))
