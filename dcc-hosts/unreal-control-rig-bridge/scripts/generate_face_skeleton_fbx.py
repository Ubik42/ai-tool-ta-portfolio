from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict


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


def _build_face_skeleton(cmds) -> Dict[str, str]:
    cmds.select(clear=True)
    root = cmds.joint(name="Root", position=(0.0, 0.0, 0.0))
    head_root = cmds.joint(name="HeadRoot", position=(0.0, 4.0, 0.0))
    neck = cmds.joint(name="Neck", position=(0.0, 5.0, 0.0))
    head = cmds.joint(name="Head", position=(0.0, 6.0, 0.0))

    cmds.select(head)
    jaw = cmds.joint(name="Jaw", position=(0.0, 5.55, 0.55))
    cmds.select(head)
    eye_l = cmds.joint(name="Eye_L", position=(-0.28, 6.18, 0.48))
    cmds.select(head)
    eye_r = cmds.joint(name="Eye_R", position=(0.28, 6.18, 0.48))

    cmds.select(root)
    cmds.joint(edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True)
    return {
        "root": root,
        "headRoot": head_root,
        "neck": neck,
        "head": head,
        "jaw": jaw,
        "eyeL": eye_l,
        "eyeR": eye_r,
    }


def _build_mesh(cmds, joints: Dict[str, str]) -> str:
    mesh, _shape = cmds.polyCube(name="SK_HeroFace", width=2.2, height=2.2, depth=1.4)
    cmds.move(0.0, 5.75, 0.1, mesh)
    cmds.polyAutoProjection(mesh, lm=0, pb=0, ibd=True, cm=False, l=2, sc=1, o=1, ps=0.2, ws=True)
    cmds.makeIdentity(mesh, apply=True, translate=True, rotate=True, scale=True)
    cmds.skinCluster(
        joints["headRoot"],
        joints["neck"],
        joints["head"],
        joints["jaw"],
        joints["eyeL"],
        joints["eyeR"],
        mesh,
        toSelectedBones=True,
        name="SK_HeroFace_skinCluster",
    )
    return mesh


def _export_fbx(cmds, mel, output_path: Path, root: str, mesh: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmds.select([root, mesh], replace=True)
    mel.eval("FBXResetExport;")
    mel.eval("FBXExportAnimationOnly -v false;")
    mel.eval("FBXExportBakeComplexAnimation -v false;")
    mel.eval("FBXExportConstraints -v false;")
    mel.eval("FBXExportCameras -v false;")
    mel.eval("FBXExportLights -v false;")
    mel.eval('FBXExport -f "%s" -s;' % output_path.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest-output", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    manifest_output = Path(args.manifest_output)
    output_path = output_dir / "SK_HeroFace_SkeletonFixture.fbx"
    cmds, mel, standalone = _initialize_maya()
    try:
        cmds.file(new=True, force=True)
        cmds.currentUnit(linear="cm", time="ntsc")
        joints = _build_face_skeleton(cmds)
        mesh = _build_mesh(cmds, joints)
        _export_fbx(cmds, mel, output_path, joints["root"], mesh)
        exported = {
            "assetId": "char-hero-head-001",
            "sourceFbxName": output_path.name,
            "path": str(output_path),
            "publicPath": public_path(output_path),
            "bytes": output_path.stat().st_size,
            "requiredTargets": ["Head", "Jaw", "Eye_L", "Eye_R"],
            "joints": ["Root", "HeadRoot", "Neck", "Head", "Jaw", "Eye_L", "Eye_R"],
        }
        manifest = {
            "reportVersion": "unreal-control-rig-face-skeleton-maya-fbx-fixture@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Face Skeleton Fixture",
            "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "maya": {
                "version": cmds.about(version=True),
                "apiVersion": cmds.about(apiVersion=True),
                "fbxmayaLoaded": bool(cmds.pluginInfo("fbxmaya", query=True, loaded=True)),
            },
            "fixture": {
                "kind": "runtime-generated-public-synthetic-face-skeleton-fbx",
                "source": "Maya mayapy procedural face skeleton export",
                "exported": exported,
            },
            "boundary": {
                "writes": "temporary FBX file only",
                "productionData": "not used",
            },
        }
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": True, "manifest": str(manifest_output), "fbx": str(output_path)}, ensure_ascii=False, indent=2))
    finally:
        try:
            standalone.uninitialize()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
