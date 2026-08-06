from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_NATIVE_BRIDGE_OUTPUT"])
    source_compile_status = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_COMPILE_STATUS_SOURCE"])
    plugin_dir = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_NATIVE_BRIDGE_PLUGIN"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.control_rig_native_bridge import build_control_rig_native_bridge_report, public_path

    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "hasCompiledBridgeBinary": _has_compiled_binary(plugin_dir),
            "commandletVisible": _commandlet_visible(unreal),
            "pluginDir": public_path(plugin_dir),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only Control Rig native bridge source/runtime readiness probe",
        }
    }
    report = build_control_rig_native_bridge_report(source_compile_status, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_NATIVE_BRIDGE_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "ControlRigBlueprint",
        "RigVMBlueprint",
        "RigVMController",
        "RigVMCompileSettings",
        "ControlRig",
        "EditorAssetLibrary",
    ]
    return {
        "classes": {name: hasattr(unreal, name) for name in class_names},
        "controlRigBlueprintMethods": _method_names(unreal.ControlRigBlueprint, ["compile", "status", "diagnostic", "vm", "message", "log"])[:160]
        if hasattr(unreal, "ControlRigBlueprint")
        else [],
    }


def _has_compiled_binary(plugin_dir: Path) -> bool:
    binary_dir = plugin_dir / "Binaries" / "Win64"
    if not binary_dir.exists():
        return False
    return any(path.name.startswith("UnrealEditor-AI_Tool_TA_ControlRigBridge") and path.suffix.lower() == ".dll" for path in binary_dir.glob("*.dll"))


def _commandlet_visible(unreal) -> bool:
    names = dir(unreal)
    return any("AiToolTaControlRigDiagnostics" in name for name in names)


def _method_names(obj: Any, terms: list[str]) -> list[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
