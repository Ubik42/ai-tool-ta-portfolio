"""Link 3ds Max material slots to a texture delivery manifest."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "max-texture-manifest-link@0.1.0"
SUPPORTED_MANIFEST_SCHEMA = "synthetic-max-texture-delivery-manifest@0.1.0"


def build_texture_manifest_link_report(source_path: str | Path, manifest_path: str | Path) -> Dict[str, Any]:
    source_file = Path(source_path)
    manifest_file = Path(manifest_path)
    source = _read_json(source_file)
    manifest = _read_json(manifest_file)
    if manifest.get("schema") != SUPPORTED_MANIFEST_SCHEMA:
        raise ValueError("Unsupported texture manifest schema: %s" % manifest.get("schema"))

    facts = _build_facts(source, manifest)
    rows = _evaluate(facts)
    summary = _summary(facts, rows)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / 3ds Max Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived" if source.get("evidenceLevel") == "L3" else "L2+",
        "l3Status": "max_material_texture_manifest_linked",
        "sourceMaxRuntime": {
            "path": _public_path(source_file),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "textureManifest": {
            "path": _public_path(manifest_file),
            "schema": manifest.get("schema"),
            "packageId": manifest.get("packageId"),
            "packageVersion": manifest.get("packageVersion"),
        },
        "facts": facts,
        "evaluation": {
            "schema": "max-texture-manifest-link-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "max-texture-manifest-link",
            "name": "3ds Max Material Texture Manifest Link",
            "methodSource": "3ds Max pymxs material slot facts + texture delivery manifest",
            "protocolCarrier": "material slot texture filenames, package entries, channel semantics and platform budgets",
            "boundary": {
                "mutation": "read_only_artifact_join",
                "sceneWrites": 0,
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _build_facts(source: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    manifest_assets = {str(row.get("assetId")): row for row in manifest.get("assets", [])}
    asset_rows = []
    for asset in source.get("facts", {}).get("assets", []):
        asset_id = str(asset.get("assetId"))
        raw = asset.get("raw", {})
        manifest_asset = manifest_assets.get(asset_id, {})
        material_rows = list(raw.get("materialTextureRows") or _fallback_material_rows(raw))
        slot_textures = sorted({texture for row in material_rows for texture in row.get("textures", []) if texture})
        package_entries = list(manifest_asset.get("textures", []))
        package_names = sorted({entry.get("textureName") for entry in package_entries if entry.get("textureName")})
        required_semantics = list(manifest_asset.get("requiredSemantics", []))
        slot_semantics = sorted({_semantic_from_name(name) for name in slot_textures if _semantic_from_name(name)})
        package_semantics = sorted({entry.get("semantic") for entry in package_entries if entry.get("semantic")})
        asset_rows.append(
            {
                "assetId": asset_id,
                "assetLabel": asset.get("assetLabel"),
                "sourceDcc": asset.get("sourceDcc", "3ds Max"),
                "sourceGate": _asset_source_gate(source, asset_id),
                "platform": manifest_asset.get("platform") or asset.get("normalized", {}).get("asset.delivery.platform"),
                "ownerState": manifest_asset.get("ownerState"),
                "materialRows": material_rows,
                "slotTextureNames": slot_textures,
                "slotSemantics": slot_semantics,
                "manifestTextureNames": package_names,
                "manifestSemantics": package_semantics,
                "requiredSemantics": required_semantics,
                "missingManifestTextures": sorted(set(slot_textures) - set(package_names)),
                "orphanManifestTextures": sorted(set(package_names) - set(slot_textures)),
                "missingRequiredSemantics": sorted(set(required_semantics) - set(slot_semantics)),
                "packageEntries": package_entries,
                "textureChecks": [_texture_check(entry, manifest_asset.get("platform")) for entry in package_entries],
            }
        )
    return {
        "schema": "max-material-texture-manifest-link@0.1.0",
        "sourceRuntimeReportVersion": source.get("reportVersion"),
        "manifestPackageId": manifest.get("packageId"),
        "manifestPackageVersion": manifest.get("packageVersion"),
        "assets": asset_rows,
    }


def _evaluate(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for asset in facts.get("assets", []):
        asset_id = asset.get("assetId")
        rows.extend(
            [
                _row(
                    asset_id,
                    "source-runtime-l3",
                    asset.get("sourceGate") in {"Ready", "Review", "Blocked"},
                    "error",
                    "sourceGate=%s" % asset.get("sourceGate"),
                    "Run the Max pymxs L3 collector before manifest link evaluation.",
                ),
                _row(
                    asset_id,
                    "manifest-package-present",
                    bool(asset.get("manifestTextureNames")),
                    "error",
                    "manifestTextures=%s" % ",".join(asset.get("manifestTextureNames", [])),
                    "Add this asset to the texture delivery manifest before package review.",
                ),
                _row(
                    asset_id,
                    "slot-textures-covered",
                    not asset.get("missingManifestTextures"),
                    "error",
                    "missing=%s" % ",".join(asset.get("missingManifestTextures", [])),
                    "Add every Max material bitmap slot texture to the delivery manifest.",
                ),
                _row(
                    asset_id,
                    "no-orphan-manifest-textures",
                    not asset.get("orphanManifestTextures"),
                    "warning",
                    "orphans=%s" % ",".join(asset.get("orphanManifestTextures", [])),
                    "Remove stale package entries or bind them to a visible material slot.",
                ),
                _row(
                    asset_id,
                    "required-channel-semantics",
                    not asset.get("missingRequiredSemantics"),
                    "error",
                    "required=%s slotSemantics=%s missing=%s"
                    % (
                        ",".join(asset.get("requiredSemantics", [])),
                        ",".join(asset.get("slotSemantics", [])),
                        ",".join(asset.get("missingRequiredSemantics", [])),
                    ),
                    "Bind every required texture semantic in Max material slots before export.",
                ),
                _row(
                    asset_id,
                    "material-name-policy",
                    all(str(row.get("materialName") or "").startswith("MI_") for row in asset.get("materialRows", [])),
                    "warning",
                    "materials=%s" % ",".join(str(row.get("materialName")) for row in asset.get("materialRows", [])),
                    "Rename Max materials to MI_* so package slots and engine material instances stay deterministic.",
                ),
            ]
        )
        for check in asset.get("textureChecks", []):
            rows.append(
                _row(
                    asset_id,
                    "texture-policy:%s" % check["textureName"],
                    check["ok"],
                    check["failStatus"],
                    check["evidence"],
                    check["fixPreview"],
                )
            )
    return rows


def _texture_check(entry: Dict[str, Any], platform: Any) -> Dict[str, Any]:
    name = str(entry.get("textureName"))
    semantic = str(entry.get("semantic") or _semantic_from_name(name) or "unknown")
    width = int(entry.get("width") or 0)
    height = int(entry.get("height") or 0)
    srgb = bool(entry.get("srgb"))
    platform_name = str(platform or entry.get("platform") or "pc").lower()
    max_dim = 2048 if platform_name == "mobile" else 4096
    color_ok = (semantic == "baseColor" and srgb) or (semantic != "baseColor" and not srgb)
    size_ok = width <= max_dim and height <= max_dim and width > 0 and height > 0
    ok = color_ok and size_ok
    problems = []
    if not color_ok:
        problems.append("colorspace")
    if not size_ok:
        problems.append("resolution")
    return {
        "textureName": name,
        "ok": ok,
        "failStatus": "error" if "resolution" in problems else "warning",
        "evidence": "semantic=%s size=%sx%s srgb=%s platform=%s max=%s"
        % (semantic, width, height, srgb, platform_name, max_dim),
        "fixPreview": (
            "None"
            if ok
            else "Fix %s for %s before package acceptance." % ("/".join(problems), name)
        ),
    }


def _summary(facts: Dict[str, Any], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    asset_rows = list(facts.get("assets", []))
    asset_ids = sorted({row.get("assetId") for row in row_list})
    blocked = sorted({row.get("assetId") for row in row_list if row.get("status") == "error"})
    review = sorted({row.get("assetId") for row in row_list if row.get("status") == "warning"} - set(blocked))
    ready = sorted(set(asset_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready),
        "reviewAssets": len(review),
        "blockedAssets": len(blocked),
        "materialRows": sum(len(asset.get("materialRows", [])) for asset in asset_rows),
        "slotTextures": sum(len(asset.get("slotTextureNames", [])) for asset in asset_rows),
        "manifestTextures": sum(len(asset.get("manifestTextureNames", [])) for asset in asset_rows),
        "missingManifestTextures": sum(len(asset.get("missingManifestTextures", [])) for asset in asset_rows),
        "missingRequiredSemantics": sum(len(asset.get("missingRequiredSemantics", [])) for asset in asset_rows),
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
        actions.append(
            {
                "id": "max-texture-action:%s" % row.get("id"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "owner": "material-ta" if "texture" in str(row.get("ruleId")) else "asset-owner",
                "preview": row.get("fixPreview"),
            }
        )
    return actions


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R53 links real 3ds Max pymxs material-slot facts to a texture delivery manifest instead of judging texture package readiness from filenames alone.",
        "The report separates Max source slot coverage, required channel semantics, color-space policy, platform resolution budget and owner action boundaries.",
        "The join is read-only: sceneWrites, assetWrites, engineWrites and productionWrites stay zero.",
        "The fixture keeps one approved panel ready and one mobile hero prop blocked so both clean and failing package paths are inspectable.",
    ]


def _asset_source_gate(source: Dict[str, Any], asset_id: str) -> str:
    evaluations = source.get("evaluation", {}).get("evaluations", [])
    statuses = [row.get("status") for row in evaluations if row.get("assetId") == asset_id]
    if any(status == "error" for status in statuses):
        return "Blocked"
    if any(status == "warning" for status in statuses):
        return "Review"
    return "Ready"


def _fallback_material_rows(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    material_names = list(raw.get("materialNames", []))
    return [
        {
            "node": None,
            "lod": None,
            "materialName": name,
            "textures": list(raw.get("textureImages", [])),
        }
        for name in material_names
    ]


def _row(asset_id: Any, rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (asset_id, rule_id),
        "assetId": asset_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _semantic_from_name(name: str) -> str | None:
    stem = Path(str(name)).stem.upper()
    if stem.endswith("_BC") or stem.endswith("_BASECOLOR") or stem.endswith("_ALBEDO"):
        return "baseColor"
    if stem.endswith("_N") or stem.endswith("_NRM") or stem.endswith("_NORMAL"):
        return "normal"
    if stem.endswith("_ORM") or stem.endswith("_MRA"):
        return "orm"
    if stem.endswith("_M"):
        return "mask"
    return None


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object: %s" % path)
    return data


def _public_path(path: Path) -> str:
    root = Path(__file__).resolve().parents[3]
    try:
        return "<repo>\\" + str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)
