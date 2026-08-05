from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_DEEP_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_DEEP_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_animation_bridge.deep_facts import build_deep_facts_report

    source = json.loads(source_artifact.read_text(encoding="utf-8"))
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only public AnimSequence metadata probe",
        },
        "sequences": _sequence_rows(unreal, source),
    }
    report = build_deep_facts_report(str(source_artifact), runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_ANIMATION_DEEP_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "AnimSequence",
        "AnimationBlueprintLibrary",
        "AnimationDataController",
        "AnimationDataModel",
        "Skeleton",
        "EditorAssetLibrary",
        "AssetRegistryHelpers",
        "FrameRate",
        "RawCurveTrackTypes",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    return {
        "classes": classes,
        "animationBlueprintLibraryMethods": _method_names(getattr(unreal, "AnimationBlueprintLibrary", None), ["curve", "frame", "rate", "root"])[:120],
        "animSequenceClassMethods": _method_names(getattr(unreal, "AnimSequence", None), ["curve", "frame", "length", "skeleton", "rate", "compression", "root", "notify"])[:120],
    }


def _sequence_rows(unreal, source: Dict[str, Any]) -> Dict[str, Any]:
    rows = {}
    for sequence in source.get("facts", {}).get("sequences", []):
        anim_path = sequence.get("expectedAnimSequencePath")
        expected = sequence.get("expectedUnreal", {})
        asset = _load_asset(unreal, anim_path)
        row = {
            "assetId": sequence.get("assetId"),
            "animSequencePath": anim_path,
            "animSequenceExists": bool(asset),
            "deepFacts": _anim_sequence_deep_facts(unreal, asset, expected) if asset else {},
        }
        rows[anim_path] = row
    return rows


def _anim_sequence_deep_facts(unreal, asset: Any, expected: Dict[str, Any]) -> Dict[str, Any]:
    expected_rate = _float_or_none(expected.get("sampleRate"))
    expected_span = _expected_frame_span(expected)
    play_length = _first_number(
        [
            lambda: asset.get_play_length(),
            lambda: asset.sequence_length,
            lambda: asset.get_editor_property("sequence_length"),
        ]
    )
    direct_rate_rows = _property_rows(
        asset,
        [
            "sampling_frame_rate",
            "target_frame_rate",
            "display_rate",
            "imported_sample_rate",
            "rate_scale",
        ],
    )
    direct_rate = _first_frame_rate(direct_rate_rows)
    derived_span = int(round(play_length * expected_rate)) if play_length is not None and expected_rate else None
    frame_delta = None if derived_span is None or expected_span is None else abs(int(derived_span) - int(expected_span))
    skeleton = _safe(lambda: asset.get_editor_property("skeleton"), None) or _safe(lambda: asset.get_skeleton(), None)
    return {
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "skeletonPath": _asset_object_path(skeleton),
        "playLength": play_length,
        "expectedSampleRate": expected_rate,
        "expectedFrameSpan": expected_span,
        "derivedFrameSpanAtExpectedRate": derived_span,
        "frameSpanDelta": frame_delta,
        "directFrameRateReadable": direct_rate is not None,
        "directFrameRate": direct_rate,
        "derivedFrameRateSource": "playLength*expectedSampleRate" if derived_span is not None else None,
        "samplingFrameRate": direct_rate_rows,
        "numberOfFrames": _call_rows(asset, ["get_number_of_frames", "get_number_of_sampled_keys"]),
        "availableMethods": _method_names(asset, ["curve", "frame", "length", "skeleton", "rate", "compression", "root", "notify"])[:160],
        "dataModel": _data_model_facts(asset),
        "curveMetadata": _curve_metadata(unreal, asset),
        "rootMotion": _root_motion_facts(asset),
        "compression": _compression_facts(asset),
        "notifies": _notify_facts(asset),
        "assetRegistryTags": _asset_registry_tags(asset),
    }


def _curve_metadata(unreal, asset: Any) -> Dict[str, Any]:
    api = getattr(unreal, "AnimationBlueprintLibrary", None)
    methods = _method_names(api, ["curve"]) if api else []
    names: List[str] = []
    attempts = []
    if api:
        for method_name in ["get_animation_curve_names", "get_float_curve_names"]:
            method = getattr(api, method_name, None)
            if not method:
                continue
            for args in [(asset,), (asset, getattr(unreal, "RawCurveTrackTypes", object()))]:
                row = {"method": method_name, "args": len(args), "ok": False, "value": None, "error": None}
                try:
                    value = method(*args)
                    row["ok"] = True
                    row["value"] = _json_value(value)
                    for item in value or []:
                        names.append(str(item))
                    attempts.append(row)
                    break
                except Exception as exc:
                    row["error"] = str(exc)
                    attempts.append(row)
    return {
        "apiAvailable": bool(api),
        "apiMethods": methods[:80],
        "curveNamesReadable": bool(names),
        "curveNames": sorted(set(names)),
        "attempts": attempts,
        "assetCurveMethods": _method_names(asset, ["curve"])[:80],
    }


def _root_motion_facts(asset: Any) -> Dict[str, Any]:
    rows = _property_rows(
        asset,
        [
            "enable_root_motion",
            "root_motion_root_lock",
            "force_root_lock",
            "use_normalized_root_motion_scale",
            "root_motion_settings",
            "b_enable_root_motion",
        ],
    )
    return {
        "propertiesReadable": any(row.get("ok") for row in rows),
        "properties": rows,
        "methods": _method_names(asset, ["root"])[:80],
    }


def _compression_facts(asset: Any) -> Dict[str, Any]:
    rows = _property_rows(
        asset,
        [
            "compression_scheme",
            "bone_compression_settings",
            "curve_compression_settings",
            "do_not_override_compression",
            "remove_redundant_keys",
            "compress_commandlet_version",
        ],
    )
    return {
        "propertiesReadable": any(row.get("ok") for row in rows),
        "properties": rows,
        "methods": _method_names(asset, ["compression", "compress"])[:80],
    }


def _notify_facts(asset: Any) -> Dict[str, Any]:
    rows = _property_rows(asset, ["notifies", "anim_notify_tracks", "marker_data"])
    counts = []
    for row in rows:
        if row.get("ok") and isinstance(row.get("value"), list):
            counts.append({"property": row.get("property"), "count": len(row.get("value") or [])})
    return {
        "propertiesReadable": any(row.get("ok") for row in rows),
        "properties": rows,
        "counts": counts,
    }


def _data_model_facts(asset: Any) -> Dict[str, Any]:
    model = _safe(lambda: asset.get_data_model(), None)
    if not model:
        return {"available": False}
    return {
        "available": True,
        "class": _safe(lambda: model.get_class().get_name(), None),
        "methods": _method_names(model, ["frame", "rate", "curve", "bone", "play", "length"])[:120],
        "calls": _call_rows(model, ["get_frame_rate", "get_number_of_frames", "get_play_length", "get_number_of_keys"]),
    }


def _asset_registry_tags(asset: Any) -> Dict[str, Any]:
    rows = _call_rows(asset, ["get_asset_registry_tags"])
    return {
        "calls": rows,
        "readable": any(row.get("ok") for row in rows),
    }


def _property_rows(obj: Any, properties: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for prop in properties:
        row = {"property": prop, "ok": False, "value": None, "error": None}
        try:
            row["value"] = _json_value(obj.get_editor_property(prop))
            row["ok"] = True
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    return rows


def _call_rows(obj: Any, method_names: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for method_name in method_names:
        row = {"method": method_name, "ok": False, "value": None, "error": None}
        method = getattr(obj, method_name, None)
        if not method:
            row["error"] = "missing"
            rows.append(row)
            continue
        try:
            row["value"] = _json_value(method())
            row["ok"] = True
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    return rows


def _first_number(getters: List[Any]):
    for getter in getters:
        try:
            value = getter()
            number = _float_or_none(value)
            if number is not None:
                return number
        except Exception:
            continue
    return None


def _first_frame_rate(rows: List[Dict[str, Any]]):
    for row in rows:
        if not row.get("ok"):
            continue
        value = row.get("value")
        number = _float_or_none(value)
        if number is not None and number > 0:
            return number
        text = str(value)
        for token in text.replace("/", " ").replace(",", " ").split():
            number = _float_or_none(token)
            if number is not None and number > 0:
                return number
    return None


def _expected_frame_span(expected: Dict[str, Any]):
    start = expected.get("startFrame")
    end = expected.get("endFrame")
    if start is None or end is None:
        return None
    try:
        return int(round(float(end) - float(start)))
    except Exception:
        return None


def _load_asset(unreal, path):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _asset_object_path(asset: Any):
    if not asset:
        return None
    value = _safe(lambda: str(asset.get_path_name()), None)
    if not value:
        return None
    return value.split(".")[0]


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _float_or_none(value: Any):
    try:
        return float(value)
    except Exception:
        return None


def _json_value(value: Any):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [_json_value(item) for item in list(value)[:40]]
    if isinstance(value, dict):
        return {str(key): _json_value(val) for key, val in list(value.items())[:80]}
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return {
            "text": str(value),
            "numerator": _safe(lambda: int(value.numerator), None),
            "denominator": _safe(lambda: int(value.denominator), None),
        }
    return str(value)


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
