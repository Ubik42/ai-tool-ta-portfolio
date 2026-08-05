from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_COMPILE_OUTPUT"])
    source_deformation = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_COMPILE_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.compile_status import build_compile_status_report, public_path

    source = json.loads(source_deformation.read_text(encoding="utf-8"))
    characters = [_compile_row(unreal, row) for row in source.get("facts", {}).get("characters", [])]
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "transient ControlRigBlueprint compile probe; no asset save",
        },
        "characters": characters,
    }
    report = build_compile_status_report(source_deformation, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_COMPILE_OUTPUT=%s" % output_path)


def _compile_row(unreal, source_row: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = str(source_row.get("assetId"))
    control_rig_path = str(source_row.get("controlRigPath") or "")
    control_rig = _load_asset(unreal, control_rig_path)
    compile_methods = _method_names(control_rig, ["compile", "recompile", "vm", "rig"]) if control_rig else []
    status_methods = _method_names(control_rig, ["status", "diagnostic", "message", "error", "warning", "log"]) if control_rig else []
    dirty_before = _package_dirty(control_rig)
    class_rows = _class_rows(control_rig)
    settings_rows = _property_rows(
        control_rig,
        [
            "vm_compile_settings",
            "compile_status",
            "last_compile_status",
            "status",
            "compile_log",
            "last_compile_results",
            "model_compile_result",
        ],
    )
    diagnostic_rows_before = _diagnostic_method_rows(control_rig, status_methods)
    invocation_rows = _compile_invocation_rows(control_rig)
    dirty_after = _package_dirty(control_rig)
    status_rows_after = _property_rows(
        control_rig,
        [
            "vm_compile_settings",
            "compile_status",
            "last_compile_status",
            "status",
            "compile_log",
            "last_compile_results",
            "model_compile_result",
        ],
    )
    diagnostic_rows_after = _diagnostic_method_rows(control_rig, status_methods)
    direct_status_rows = [
        row
        for row in status_rows_after
        if row.get("ok") and any(term in str(row.get("attribute", "")).lower() for term in ("status", "diagnostic", "result", "log"))
    ]
    diagnostic_ok_rows = [row for row in diagnostic_rows_after if row.get("ok")]
    settings_ok_rows = [row for row in status_rows_after if row.get("ok") and "setting" in str(row.get("attribute", "")).lower()]
    return {
        "assetId": asset_id,
        "assetLabel": source_row.get("assetLabel"),
        "sourceStatus": source_row.get("sourceStatus"),
        "controlRigPath": control_rig_path,
        "controlRigExists": bool(control_rig),
        "controlRigClass": _asset_class(unreal, control_rig_path) if control_rig else None,
        "compileMethods": compile_methods[:120],
        "statusMethods": status_methods[:120],
        "compileMethodVisible": any("compile" in name.lower() or "recompile" in name.lower() for name in compile_methods),
        "packageDirtyBefore": dirty_before,
        "packageDirtyAfter": dirty_after,
        "classRows": class_rows,
        "settingsRowsBefore": settings_rows,
        "statusRows": status_rows_after,
        "diagnosticRowsBefore": diagnostic_rows_before,
        "diagnosticRowsAfter": diagnostic_rows_after,
        "compileInvocationRows": invocation_rows,
        "compileInvocationAttempted": bool(invocation_rows),
        "compileInvocationSucceeded": any(row.get("ok") for row in invocation_rows),
        "directStatusReadable": bool(direct_status_rows),
        "diagnosticReadable": bool(diagnostic_ok_rows),
        "compileSettingsReadable": bool(settings_ok_rows),
    }


def _compile_invocation_rows(asset: Any) -> List[Dict[str, Any]]:
    if not asset:
        return []
    rows = []
    for method_name in ("recompile_vm_if_required", "recompile_vm"):
        method = getattr(asset, method_name, None)
        if not method:
            continue
        row = {"method": method_name, "args": [], "ok": False, "value": None, "error": None}
        try:
            value = method()
            row["ok"] = True
            row["value"] = _short_repr(value)
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    return rows


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = ["ControlRigBlueprint", "RigVMBlueprint", "RigVMController", "EditorAssetLibrary"]
    return {
        "classes": {name: hasattr(unreal, name) for name in class_names},
        "controlRigBlueprintMethods": _method_names(unreal.ControlRigBlueprint, ["compile", "status", "diagnostic", "vm", "message", "log"])[:160]
        if hasattr(unreal, "ControlRigBlueprint")
        else [],
    }


def _load_asset(unreal, path: Optional[str]):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _asset_class(unreal, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
        if not asset_data or not asset_data.is_valid():
            return None
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return None


def _class_rows(asset: Any) -> List[Dict[str, Any]]:
    rows = []
    for method_name in ("get_control_rig_class", "get_rig_vm_host_class"):
        rows.extend(_call_variants(asset, method_name, [()]))
    return rows


def _property_rows(asset: Any, attributes: List[str]) -> List[Dict[str, Any]]:
    rows = []
    if not asset:
        return rows
    for attr in attributes:
        row = {"attribute": attr, "ok": False, "value": None, "error": None}
        try:
            value = asset.get_editor_property(attr)
            row["ok"] = True
            row["value"] = _short_repr(value)
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    return rows


def _diagnostic_method_rows(asset: Any, method_names: List[str]) -> List[Dict[str, Any]]:
    rows = []
    if not asset:
        return rows
    for method_name in method_names[:40]:
        if not method_name.startswith("get"):
            continue
        if any(skip in method_name.lower() for skip in ("set_", "compile", "recompile")):
            continue
        rows.extend(_call_variants(asset, method_name, [()]))
    return rows


def _package_dirty(asset: Any) -> Optional[bool]:
    if not asset:
        return None
    package = _safe(lambda: asset.get_outermost(), None)
    if package is None:
        package = _safe(lambda: asset.get_package(), None)
    if package is None:
        return None
    dirty = _safe(lambda: package.is_dirty(), None)
    if dirty is None:
        dirty = _safe(lambda: package.get_editor_property("dirty"), None)
    return bool(dirty) if dirty is not None else None


def _call_variants(obj: Any, method_name: str, arg_variants: List[tuple]) -> List[Dict[str, Any]]:
    method = getattr(obj, method_name, None) if obj else None
    if not method:
        return []
    rows = []
    for args in arg_variants:
        row = {"method": method_name, "args": [str(arg) for arg in args], "ok": False, "value": None, "error": None}
        try:
            value = method(*args)
            row["ok"] = True
            row["value"] = _short_repr(value)
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
        if row["ok"]:
            break
    return rows


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _short_repr(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 240 else text[:237] + "..."


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
