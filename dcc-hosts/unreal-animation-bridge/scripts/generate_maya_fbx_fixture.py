from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def _initialize_maya():
    import maya.standalone  # type: ignore

    maya.standalone.initialize(name="python")
    from maya import cmds, mel  # type: ignore

    cmds.loadPlugin("fbxmaya", quiet=True)
    return cmds, mel, maya.standalone


def _build_skeleton(cmds) -> Dict[str, str]:
    cmds.select(clear=True)
    root = cmds.joint(name="Root", position=(0.0, 0.0, 0.0))
    hips = cmds.joint(name="Hips", position=(0.0, 3.0, 0.0))
    spine = cmds.joint(name="Spine", position=(0.0, 5.0, 0.0))
    chest = cmds.joint(name="Chest", position=(0.0, 6.5, 0.0))
    neck = cmds.joint(name="Neck", position=(0.0, 7.3, 0.0))
    head = cmds.joint(name="Head", position=(0.0, 8.2, 0.0))

    cmds.select(hips)
    left_leg = cmds.joint(name="LeftLeg", position=(-0.45, 1.6, 0.0))
    left_foot = cmds.joint(name="LeftFoot", position=(-0.45, 0.0, 0.65))

    cmds.select(hips)
    right_leg = cmds.joint(name="RightLeg", position=(0.45, 1.6, 0.0))
    right_foot = cmds.joint(name="RightFoot", position=(0.45, 0.0, 0.65))

    cmds.select(chest)
    left_arm = cmds.joint(name="LeftArm", position=(-1.15, 5.9, 0.0))
    left_hand = cmds.joint(name="LeftHand", position=(-2.0, 4.6, 0.0))

    cmds.select(chest)
    right_arm = cmds.joint(name="RightArm", position=(1.15, 5.9, 0.0))
    right_hand = cmds.joint(name="RightHand", position=(2.0, 4.6, 0.0))
    weapon_socket = cmds.joint(name="WeaponSocket", position=(2.55, 4.35, 0.0))

    cmds.select(root)
    cmds.joint(edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True)
    return {
        "root": root,
        "hips": hips,
        "spine": spine,
        "chest": chest,
        "neck": neck,
        "head": head,
        "leftLeg": left_leg,
        "leftFoot": left_foot,
        "rightLeg": right_leg,
        "rightFoot": right_foot,
        "leftArm": left_arm,
        "leftHand": left_hand,
        "rightArm": right_arm,
        "rightHand": right_hand,
        "weaponSocket": weapon_socket,
    }


def _build_mesh(cmds, joints: Dict[str, str]) -> str:
    mesh, _shape = cmds.polyCube(name="SK_Hero", width=1.1, height=2.4, depth=0.7)
    cmds.move(0.0, 3.2, 0.0, mesh)
    cmds.makeIdentity(mesh, apply=True, translate=True, rotate=True, scale=True)
    cmds.skinCluster(
        joints["root"],
        joints["hips"],
        joints["spine"],
        joints["chest"],
        mesh,
        toSelectedBones=True,
        name="SK_Hero_skinCluster",
    )
    return mesh


def _key(cmds, node: str, attr: str, frame: float, value: float) -> None:
    cmds.setAttr("%s.%s" % (node, attr), value)
    cmds.setKeyframe(node, attribute=attr, time=frame, value=value)


def _animate_run_start(cmds, joints: Dict[str, str]) -> None:
    for frame, tx, tz, ry, lf, rf in [
        (1001, 0.0, 0.0, 0.0, 0.0, -8.0),
        (1013, 0.2, 1.1, 4.0, -28.0, 19.0),
        (1025, 0.5, 2.6, 2.0, 24.0, -24.0),
        (1037, 0.9, 4.3, -3.0, -18.0, 26.0),
        (1048, 1.4, 5.8, 0.0, 0.0, -6.0),
    ]:
        _key(cmds, joints["hips"], "translateX", frame, tx)
        _key(cmds, joints["hips"], "translateZ", frame, tz)
        _key(cmds, joints["hips"], "rotateY", frame, ry)
        _key(cmds, joints["leftFoot"], "rotateX", frame, lf)
        _key(cmds, joints["rightFoot"], "rotateX", frame, rf)


def _animate_attack_a(cmds, joints: Dict[str, str]) -> None:
    for frame, tz, ry, rf, weapon in [
        (2001, 0.0, 0.0, -4.0, -20.0),
        (2010, 0.0, -10.0, 7.0, 15.0),
        (2020, 0.0, 26.0, -2.0, 84.0),
        (2030, 0.0, 14.0, 0.0, 32.0),
        (2040, 0.0, 0.0, -4.0, -20.0),
    ]:
        _key(cmds, joints["hips"], "translateZ", frame, tz)
        _key(cmds, joints["hips"], "rotateY", frame, ry)
        _key(cmds, joints["rightFoot"], "rotateX", frame, rf)
        _key(cmds, joints["weaponSocket"], "rotateY", frame, weapon)


def _export_fbx(cmds, mel, output_path: Path, roots: List[str], start: int, end: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmds.select(roots, replace=True)
    mel.eval("FBXResetExport;")
    mel.eval("FBXExportAnimationOnly -v false;")
    mel.eval("FBXExportBakeComplexAnimation -v true;")
    mel.eval("FBXExportBakeComplexStart -v %d;" % start)
    mel.eval("FBXExportBakeComplexEnd -v %d;" % end)
    mel.eval("FBXExportBakeComplexStep -v 1;")
    mel.eval("FBXExportConstraints -v false;")
    mel.eval("FBXExportCameras -v false;")
    mel.eval("FBXExportLights -v false;")
    mel.eval('FBXExport -f "%s" -s;' % output_path.as_posix())


def _create_clip(cmds, mel, clip: Dict[str, object], output_dir: Path) -> Dict[str, object]:
    cmds.file(new=True, force=True)
    cmds.currentUnit(time="ntsc")
    start = int(clip["startFrame"])
    end = int(clip["endFrame"])
    cmds.playbackOptions(minTime=start, maxTime=end, animationStartTime=start, animationEndTime=end)
    joints = _build_skeleton(cmds)
    mesh = _build_mesh(cmds, joints)
    if clip["take"] == "RunStart":
        _animate_run_start(cmds, joints)
    else:
        _animate_attack_a(cmds, joints)
    output_path = output_dir / str(clip["filename"])
    _export_fbx(cmds, mel, output_path, [joints["root"], mesh], start, end)
    return {
        "take": clip["take"],
        "assetId": clip["assetId"],
        "sourceFbxClipName": clip["filename"],
        "path": str(output_path),
        "publicPath": public_path(output_path),
        "bytes": output_path.stat().st_size,
        "startFrame": start,
        "endFrame": end,
        "keyedChannels": clip["keyedChannels"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest-output", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    manifest_output = Path(args.manifest_output)
    clips = [
        {
            "assetId": "anim-hero-run-001",
            "take": "RunStart",
            "filename": "AS_Hero_RunStart.fbx",
            "startFrame": 1001,
            "endFrame": 1048,
            "keyedChannels": [
                "Hips.translateX",
                "Hips.translateZ",
                "Hips.rotateY",
                "LeftFoot.rotateX",
                "RightFoot.rotateX",
            ],
        },
        {
            "assetId": "anim-hero-attack-002",
            "take": "Attack_A",
            "filename": "AS_Hero_Attack_A.fbx",
            "startFrame": 2001,
            "endFrame": 2040,
            "keyedChannels": [
                "Hips.translateZ",
                "Hips.rotateY",
                "RightFoot.rotateX",
                "WeaponSocket.rotateY",
            ],
        },
    ]

    cmds, mel, standalone = _initialize_maya()
    try:
        exported = [_create_clip(cmds, mel, clip, output_dir) for clip in clips]
        manifest = {
            "reportVersion": "unreal-animation-bridge-maya-fbx-fixture@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Unreal Animation Bridge",
            "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "maya": {
                "version": cmds.about(version=True),
                "apiVersion": cmds.about(apiVersion=True),
                "fbxmayaLoaded": bool(cmds.pluginInfo("fbxmaya", query=True, loaded=True)),
            },
            "fixture": {
                "kind": "runtime-generated-public-synthetic-fbx",
                "source": "Maya mayapy procedural skeleton and keyed animCurve export",
                "clipCount": len(exported),
                "clips": exported,
            },
            "boundary": {
                "writes": "temporary FBX files only",
                "productionData": "not used",
            },
        }
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": True, "manifest": str(manifest_output), "clips": len(exported)}, ensure_ascii=False, indent=2))
    finally:
        try:
            standalone.uninitialize()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
