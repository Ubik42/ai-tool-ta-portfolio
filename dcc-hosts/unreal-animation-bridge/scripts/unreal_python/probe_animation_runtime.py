from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_animation_bridge.contract import build_report, public_path

    fixture_path = root / "fixtures" / "synthetic_unreal_animation_bridge.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    runtime_snapshot = {
        "executed": True,
        "runtime": "Unreal Python",
        "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
        "pythonVersion": sys.version,
        "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
        "api": _api_probe(unreal),
        "assets": _asset_probe(unreal, fixture),
        "mutation": {
            "engineWrites": 0,
            "assetWrites": 0,
            "savePackage": False,
            "writeScope": "read-only public test project probe",
        },
    }
    report = build_report(fixture_path, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> dict:
    class_names = [
        "AnimSequence",
        "AnimSequenceFactory",
        "AnimationBlueprintLibrary",
        "Skeleton",
        "SkeletalMesh",
        "EditorAssetLibrary",
        "AssetRegistryHelpers",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    animation_library = getattr(unreal, "AnimationBlueprintLibrary", None)
    library_methods = []
    if animation_library:
        library_methods = [
            name
            for name in dir(animation_library)
            if "curve" in name.lower()
            or "frame" in name.lower()
            or "root" in name.lower()
            or "rate" in name.lower()
            or "sequence" in name.lower()
        ]
    return {
        "classes": classes,
        "animationBlueprintLibraryMethods": sorted(library_methods),
    }


def _asset_probe(unreal, fixture: dict) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    rows = {}
    missing = []
    present = []
    for sequence in fixture.get("animationSequences", []):
        anim_path = sequence.get("expectedAnimSequencePath")
        skeleton_path = sequence.get("expectedSkeletonPath")
        anim_exists = bool(editor_assets.does_asset_exist(anim_path))
        skeleton_exists = bool(editor_assets.does_asset_exist(skeleton_path))
        row = {
            "assetId": sequence.get("assetId"),
            "animSequencePath": anim_path,
            "skeletonPath": skeleton_path,
            "animSequenceExists": anim_exists,
            "skeletonExists": skeleton_exists,
            "animSequenceClass": _asset_class(unreal, anim_path) if anim_exists else None,
            "skeletonClass": _asset_class(unreal, skeleton_path) if skeleton_exists else None,
            "readOnlyProbe": True,
        }
        rows[anim_path] = row
        if anim_exists and skeleton_exists:
            present.append(anim_path)
        else:
            missing.append(anim_path)
    return {
        "expectedSequenceCount": len(rows),
        "presentSequenceCount": len(present),
        "missingSequenceCount": len(missing),
        "allExpectedAssetsPresent": len(rows) > 0 and not missing,
        "present": present,
        "missing": missing,
        "rows": rows,
    }


def _asset_class(unreal, path: str) -> str | None:
    asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
    if not asset_data or not asset_data.is_valid():
        return None
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return str(asset_data.asset_class)


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
