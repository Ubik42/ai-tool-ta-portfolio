"""Maya group/root projection collector for groom handoff.

This layer checks a business boundary that sits between XGen-style curve data
and Unreal Groom binding: every strand root must project back to the intended
scalp UV region, group, guide coverage and material slot.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .contract import load_fixture, public_path
from .maya_collector import collect_maya_scene_facts, create_scene_from_fixture, reset_scene


REPORT_VERSION = "groom-group-root-projection@0.1.0"
GROUP_SCHEMA = "groom-group-root-projection@dcc-r59"


def build_group_root_projection_report(fixture_path: str | Path) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(cmds, fixture.get("scene", {}))
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    projection = _collect_projection_facts(cmds, facts)
    rows = _evaluate_projection_rows(projection)
    summary = _summarize(rows, projection)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "maya_groom_group_root_projection_collected",
        "mayaRuntime": {
            "version": _safe(lambda: cmds.about(version=True)),
            "apiVersion": _safe(lambda: cmds.about(apiVersion=True)),
            "batch": bool(_safe(lambda: cmds.about(batch=True), False)),
        },
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "facts": projection,
        "evaluation": {
            "schema": "groom-group-root-projection-evaluation@0.1.0",
            "summary": {
                "gate": summary["gate"],
                "checks": len(rows),
                "pass": summary["pass"],
                "warning": summary["warning"],
                "error": summary["error"],
            },
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "groom-group-root-projection",
            "name": "Groom Group / Root Projection Inspector",
            "methodSource": "Maya curve root CV projection + group/material/guide payload checks",
            "protocolCarrier": "Maya curve payload attrs, root CV world positions, scalp UV projection plane, group material slots",
            "boundary": {
                "mutation": "synthetic_maya_groom_fixture_only",
                "sceneWrites": "creates temporary public scalp planes, curve strands and custom attrs in batch scene",
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        },
        "summary": summary,
        "reviewerClaims": [
            "R59 checks that root UV values are not just present: they agree with Maya curve root projection against the declared scalp UV plane.",
            "The report links strand group IDs to guide coverage, target scalp sections and Unreal material-slot routing before the groom can enter BindingAsset work.",
            "Temporary or ambiguous groom rows stay blocked with owner actions instead of being normalized into a usable engine payload.",
        ],
    }


def _collect_projection_facts(cmds: Any, source_facts: Dict[str, Any]) -> Dict[str, Any]:
    assets = []
    for row in source_facts.get("assets", []):
        raw = row.get("raw", {})
        groom = raw.get("groom", {}) if isinstance(raw.get("groom"), dict) else {}
        scalp = raw.get("scalp", {}) if isinstance(raw.get("scalp"), dict) else {}
        export = raw.get("export", {}) if isinstance(raw.get("export"), dict) else {}
        unreal = raw.get("unreal", {}) if isinstance(raw.get("unreal"), dict) else {}
        groups = [_group_row(item) for item in groom.get("groups", []) if isinstance(item, dict)]
        group_by_id = {item["id"]: item for item in groups if item["id"] is not None}
        group_by_name = {item["name"]: item for item in groups if item["name"]}
        section_names = {str(item.get("name")) for item in scalp.get("sections", []) if isinstance(item, dict)}
        plane = _projection_plane(scalp)
        tolerance = float(groom.get("rootProjectionTolerance", 0.04) or 0.04)
        strand_rows = []
        for index, strand in enumerate(groom.get("strands", [])):
            if not isinstance(strand, dict):
                continue
            group_id = _int_or_none(strand.get("groupId"))
            group_name = str(strand.get("groupName", ""))
            group = group_by_id.get(group_id) or group_by_name.get(group_name)
            root_point = _curve_root_world_position(cmds, strand.get("node"), strand.get("points", []))
            stored_uv = _valid_uv(strand.get("rootUv"))
            projected_uv = _project_point_to_uv(root_point, plane)
            drift = _uv_drift(stored_uv, projected_uv)
            strand_rows.append(
                {
                    "assetId": row.get("assetId"),
                    "strandId": str(strand.get("id", "")),
                    "index": index,
                    "node": strand.get("node"),
                    "groupId": group_id,
                    "groupName": group_name,
                    "materialSlot": str(strand.get("materialSlot", "")),
                    "guide": bool(strand.get("guide")),
                    "pointCount": int(strand.get("pointCount") or len(strand.get("points", [])) or 0),
                    "rootWorldPosition": _round_point(root_point),
                    "storedRootUv": stored_uv,
                    "projectedRootUv": projected_uv,
                    "rootProjectionDrift": drift,
                    "rootProjectionTolerance": tolerance,
                    "groupDeclared": bool(group),
                    "groupUvMatched": bool(group and stored_uv and _uv_in_bounds(stored_uv, group.get("uvBounds"))),
                    "groupMaterialSlot": group.get("materialSlot") if group else None,
                    "materialSlotMatched": bool(group and str(strand.get("materialSlot", "")) == str(group.get("materialSlot", ""))),
                    "rootUvValid": stored_uv is not None,
                    "projectionWithinTolerance": drift is not None and drift <= tolerance,
                }
            )
        group_rows = _build_group_rows(row, groups, strand_rows, section_names)
        assets.append(
            {
                "assetId": row.get("assetId"),
                "assetLabel": row.get("assetLabel"),
                "ownerState": row.get("normalized", {}).get("groom.ownerState"),
                "descriptionName": row.get("normalized", {}).get("description.name"),
                "groupProjectionVersion": groom.get("groupProjectionVersion"),
                "rootProjectionTolerance": tolerance,
                "groups": groups,
                "sectionNames": sorted(section_names),
                "strandProjectionRows": strand_rows,
                "groupCoverageRows": group_rows,
                "export": {
                    "cachePath": export.get("cachePath"),
                    "expectedExtension": export.get("expectedExtension"),
                    "includeRootUV": bool(export.get("includeRootUV")),
                    "includeStrandIds": bool(export.get("includeStrandIds")),
                    "includeGuideCurves": bool(export.get("includeGuideCurves")),
                    "includeGroupIds": bool(export.get("includeGroupIds")),
                    "frameRange": export.get("frameRange"),
                },
                "unreal": {
                    "expectedGroomAsset": unreal.get("expectedGroomAsset"),
                    "expectedBindingAsset": unreal.get("expectedBindingAsset"),
                    "targetSkeletalMesh": unreal.get("targetSkeletalMesh"),
                    "materialSlot": unreal.get("materialSlot"),
                    "expectedMaterialSlots": [str(value) for value in unreal.get("expectedMaterialSlots", [])],
                },
            }
        )
    return {
        "schema": "groom-group-root-projection-facts@0.1.0",
        "sourceFactsSchema": source_facts.get("schema"),
        "scene": source_facts.get("scene", {}),
        "assets": assets,
    }


def _group_row(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": _int_or_none(item.get("id")),
        "name": str(item.get("name", "")),
        "materialSlot": str(item.get("materialSlot", "")),
        "targetScalpSection": str(item.get("targetScalpSection", "")),
        "uvBounds": _bounds(item.get("uvBounds")),
        "minStrands": int(item.get("minStrands", 0) or 0),
        "minGuides": int(item.get("minGuides", 0) or 0),
        "requiredGuideIds": [str(value) for value in item.get("requiredGuideIds", [])],
    }


def _build_group_rows(
    asset: Dict[str, Any],
    groups: List[Dict[str, Any]],
    strand_rows: List[Dict[str, Any]],
    section_names: set[str],
) -> List[Dict[str, Any]]:
    rows = []
    for group in groups:
        strands = [
            row
            for row in strand_rows
            if row.get("groupId") == group.get("id") or (group.get("name") and row.get("groupName") == group.get("name"))
        ]
        guide_ids = sorted({row["strandId"] for row in strands if row.get("guide") and row.get("strandId")})
        missing_required = sorted(set(group.get("requiredGuideIds", [])) - set(guide_ids))
        rows.append(
            {
                "assetId": asset.get("assetId"),
                "groupId": group.get("id"),
                "groupName": group.get("name"),
                "materialSlot": group.get("materialSlot"),
                "targetScalpSection": group.get("targetScalpSection"),
                "targetSectionPresent": group.get("targetScalpSection") in section_names,
                "strandCount": len(strands),
                "guideCount": len(guide_ids),
                "guideIds": guide_ids,
                "minStrands": group.get("minStrands"),
                "minGuides": group.get("minGuides"),
                "requiredGuideIds": group.get("requiredGuideIds", []),
                "missingRequiredGuideIds": missing_required,
                "uvMatchedStrands": sum(1 for row in strands if row.get("groupUvMatched")),
                "projectionMatchedStrands": sum(1 for row in strands if row.get("projectionWithinTolerance")),
            }
        )
    return rows


def _evaluate_projection_rows(projection: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for asset in projection.get("assets", []):
        asset_id = str(asset.get("assetId"))
        strands = asset.get("strandProjectionRows", [])
        groups = asset.get("groups", [])
        group_rows = asset.get("groupCoverageRows", [])
        export = asset.get("export", {})
        unreal = asset.get("unreal", {})
        expected_slots = set(unreal.get("expectedMaterialSlots", []))
        group_slots = {group.get("materialSlot") for group in groups if group.get("materialSlot")}
        strand_ids = [row.get("strandId") for row in strands if row.get("strandId")]
        duplicate_ids = sorted({strand_id for strand_id in strand_ids if strand_ids.count(strand_id) > 1})
        missing_or_unmatched_groups = [
            row.get("strandId") or "row_%03d" % row.get("index")
            for row in strands
            if not row.get("groupDeclared")
        ]
        projection_failures = [
            row.get("strandId") or "row_%03d" % row.get("index")
            for row in strands
            if not row.get("rootUvValid") or not row.get("projectionWithinTolerance")
        ]
        uv_region_failures = [
            row.get("strandId") or "row_%03d" % row.get("index")
            for row in strands
            if not row.get("groupUvMatched")
        ]
        material_failures = [
            row.get("strandId") or "row_%03d" % row.get("index")
            for row in strands
            if not row.get("materialSlotMatched")
        ]
        group_failures = [
            row.get("groupName") or str(row.get("groupId"))
            for row in group_rows
            if int(row.get("strandCount") or 0) < int(row.get("minStrands") or 0)
            or int(row.get("guideCount") or 0) < int(row.get("minGuides") or 0)
            or row.get("missingRequiredGuideIds")
            or not row.get("targetSectionPresent")
        ]
        frame_range = export.get("frameRange") if isinstance(export.get("frameRange"), list) else []
        frame_ok = len(frame_range) >= 2 and int(frame_range[0]) <= int(frame_range[1])
        rows.extend(
            [
                _row(
                    asset_id,
                    "group-projection-protocol",
                    asset.get("groupProjectionVersion") == GROUP_SCHEMA,
                    "error",
                    "version=%s" % asset.get("groupProjectionVersion"),
                    "Write %s on the groom group projection payload." % GROUP_SCHEMA,
                ),
                _row(
                    asset_id,
                    "group-definition-coverage",
                    bool(groups)
                    and not any(group.get("id") is None or not group.get("name") or not group.get("materialSlot") for group in groups),
                    "error",
                    "groups=%s" % [
                        {"id": group.get("id"), "name": group.get("name"), "materialSlot": group.get("materialSlot")}
                        for group in groups
                    ],
                    "Define stable group id, group name and Unreal material slot for every groom section.",
                ),
                _row(
                    asset_id,
                    "strand-identity-and-group-membership",
                    bool(strands) and not duplicate_ids and not missing_or_unmatched_groups and all(row.get("strandId") for row in strands),
                    "error",
                    "strands=%s duplicateIds=%s unmatchedGroups=%s"
                    % (len(strands), duplicate_ids, missing_or_unmatched_groups),
                    "Regenerate unique strand IDs and assign each strand to a declared groom group.",
                ),
                _row(
                    asset_id,
                    "root-projection-drift",
                    not projection_failures,
                    "error",
                    "failures=%s maxDrift=%.4f tolerance=%.4f"
                    % (projection_failures, _max_drift(strands), float(asset.get("rootProjectionTolerance") or 0.0)),
                    "Reproject curve roots to the scalp root_uv set and rewrite root UV payload before export.",
                ),
                _row(
                    asset_id,
                    "group-uv-region-match",
                    not uv_region_failures,
                    "error",
                    "failures=%s" % uv_region_failures,
                    "Move mis-bucketed strands to the correct group or fix the group's UV bounds.",
                ),
                _row(
                    asset_id,
                    "guide-group-coverage",
                    not group_failures,
                    "error",
                    "groupFailures=%s groupRows=%s" % (group_failures, group_rows),
                    "Restore required guide curves per group and verify target scalp section names.",
                ),
                _row(
                    asset_id,
                    "material-slot-routing",
                    not material_failures and group_slots.issubset(expected_slots),
                    "error",
                    "strandFailures=%s groupSlots=%s expectedSlots=%s"
                    % (material_failures, sorted(group_slots), sorted(expected_slots)),
                    "Route every groom group to an expected Unreal hair material slot.",
                ),
                _row(
                    asset_id,
                    "alembic-group-payload",
                    bool(export.get("includeRootUV"))
                    and bool(export.get("includeStrandIds"))
                    and bool(export.get("includeGuideCurves"))
                    and bool(export.get("includeGroupIds"))
                    and str(export.get("cachePath", "")).lower().endswith(str(export.get("expectedExtension", ".abc")).lower())
                    and frame_ok,
                    "error",
                    "path=%s rootUV=%s strandIds=%s guides=%s groupIds=%s frameRange=%s"
                    % (
                        export.get("cachePath"),
                        export.get("includeRootUV"),
                        export.get("includeStrandIds"),
                        export.get("includeGuideCurves"),
                        export.get("includeGroupIds"),
                        frame_range,
                    ),
                    "Export Alembic with root UV, strand ID, guide and group ID payloads over a valid frame range.",
                ),
                _row(
                    asset_id,
                    "owner-release-boundary",
                    asset.get("ownerState") == "approved" and "TMP" not in str(asset.get("descriptionName", "")).upper(),
                    "warning",
                    "ownerState=%s description=%s" % (asset.get("ownerState"), asset.get("descriptionName")),
                    "Keep temporary groom descriptions in owner review until they are explicitly approved.",
                ),
            ]
        )
    return rows


def _row(asset_id: str, rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (asset_id, rule_id),
        "assetId": asset_id,
        "ruleId": rule_id,
        "label": rule_id.replace("-", " ").title(),
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "No action." if passed else fix_preview,
    }


def _summarize(rows: Iterable[Dict[str, Any]], projection: Dict[str, Any]) -> Dict[str, Any]:
    row_list = list(rows)
    asset_ids = sorted({row.get("assetId") for row in row_list})
    blocked_assets = sorted({row.get("assetId") for row in row_list if row.get("status") == "error"})
    review_assets = sorted({row.get("assetId") for row in row_list if row.get("status") == "warning"} - set(blocked_assets))
    ready_assets = sorted(set(asset_ids) - set(blocked_assets) - set(review_assets))
    strands = [row for asset in projection.get("assets", []) for row in asset.get("strandProjectionRows", [])]
    groups = [row for asset in projection.get("assets", []) for row in asset.get("groupCoverageRows", [])]
    return {
        "gate": "Blocked" if blocked_assets else "Review" if review_assets else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready_assets),
        "reviewAssets": len(review_assets),
        "blockedAssets": len(blocked_assets),
        "readyAssetIds": ready_assets,
        "reviewAssetIds": review_assets,
        "blockedAssetIds": blocked_assets,
        "strandProjectionRows": len(strands),
        "groupCoverageRows": len(groups),
        "projectionMatchedStrands": sum(1 for row in strands if row.get("projectionWithinTolerance")),
        "groupMatchedStrands": sum(1 for row in strands if row.get("groupDeclared") and row.get("groupUvMatched")),
        "materialMatchedStrands": sum(1 for row in strands if row.get("materialSlotMatched")),
        "maxProjectionDrift": _max_drift(strands),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": 0,
        "engineWrites": 0,
        "productionWrites": 0,
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        rule_id = str(row.get("ruleId"))
        actions.append(
            {
                "id": "owner-action:%s" % row.get("id"),
                "assetId": row.get("assetId"),
                "ruleId": rule_id,
                "status": row.get("status"),
                "owner": _owner_for_rule(rule_id),
                "mutationScope": "owner_required" if row.get("status") == "error" else "manual_review",
                "preview": row.get("fixPreview"),
                "writeBoundary": "public_maya_fixture_only",
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"root-projection-drift", "group-uv-region-match", "strand-identity-and-group-membership"}:
        return "groom-owner"
    if rule_id in {"material-slot-routing", "alembic-group-payload"}:
        return "engine-ta"
    if rule_id in {"guide-group-coverage", "group-definition-coverage"}:
        return "character-ta"
    return "reviewer"


def _projection_plane(scalp: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    plane = scalp.get("projectionPlane", {}) if isinstance(scalp.get("projectionPlane"), dict) else {}
    x_range = plane.get("xRange", [-1.0, 1.0])
    z_range = plane.get("zRange", [-0.6, 0.6])
    return {
        "xRange": (float(x_range[0]), float(x_range[1])) if isinstance(x_range, list) and len(x_range) >= 2 else (-1.0, 1.0),
        "zRange": (float(z_range[0]), float(z_range[1])) if isinstance(z_range, list) and len(z_range) >= 2 else (-0.6, 0.6),
    }


def _curve_root_world_position(cmds: Any, node: Any, fallback_points: Any) -> List[float]:
    if node:
        try:
            position = cmds.pointPosition("%s.cv[0]" % node, world=True)
            if isinstance(position, list) and len(position) >= 3:
                return [float(position[0]), float(position[1]), float(position[2])]
        except Exception:
            pass
    if isinstance(fallback_points, list) and fallback_points:
        first = fallback_points[0]
        if isinstance(first, list) and len(first) >= 3:
            return [float(first[0]), float(first[1]), float(first[2])]
    return [0.0, 0.0, 0.0]


def _project_point_to_uv(point: List[float], plane: Dict[str, Tuple[float, float]]) -> List[float]:
    x_min, x_max = plane["xRange"]
    z_min, z_max = plane["zRange"]
    x_span = x_max - x_min or 1.0
    z_span = z_max - z_min or 1.0
    return [round((float(point[0]) - x_min) / x_span, 4), round((float(point[2]) - z_min) / z_span, 4)]


def _valid_uv(value: Any) -> Optional[List[float]]:
    if not isinstance(value, list) or len(value) < 2:
        return None
    try:
        uv = [float(value[0]), float(value[1])]
    except Exception:
        return None
    if not (0.0 <= uv[0] <= 1.0 and 0.0 <= uv[1] <= 1.0):
        return None
    return [round(uv[0], 4), round(uv[1], 4)]


def _uv_drift(stored: Optional[List[float]], projected: List[float]) -> Optional[float]:
    if stored is None:
        return None
    return round(max(abs(stored[0] - projected[0]), abs(stored[1] - projected[1])), 4)


def _uv_in_bounds(uv: Optional[List[float]], bounds: Any) -> bool:
    if uv is None:
        return False
    clean = _bounds(bounds)
    if clean is None:
        return False
    return clean[0] <= uv[0] <= clean[2] and clean[1] <= uv[1] <= clean[3]


def _bounds(value: Any) -> Optional[List[float]]:
    if not isinstance(value, list) or len(value) < 4:
        return None
    try:
        return [float(value[0]), float(value[1]), float(value[2]), float(value[3])]
    except Exception:
        return None


def _max_drift(strands: List[Dict[str, Any]]) -> float:
    values = [float(row.get("rootProjectionDrift")) for row in strands if row.get("rootProjectionDrift") is not None]
    return round(max(values), 4) if values else 0.0


def _int_or_none(value: Any) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _round_point(point: List[float]) -> List[float]:
    return [round(float(value), 4) for value in point[:3]]


def _safe(func: Any, default: Any = None) -> Any:
    try:
        return func()
    except Exception:
        return default
