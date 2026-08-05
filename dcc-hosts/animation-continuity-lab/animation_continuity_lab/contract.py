"""Headless animation continuity contract.

The contract captures the business checks before a take moves between Maya,
MotionBuilder and Unreal: identity, time, channel ownership, sub-frame keys,
root motion and unsupported animation layers.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "animation-continuity-contract@0.1.0"
NORMALIZED_SCHEMA = "animation-continuity-input@0.1.0"
FIXTURE_SCHEMA = "synthetic-animation-continuity-scene@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    return build_facts_from_assets(
        scene=fixture.get("scene", {}),
        assets=fixture.get("assets", []),
        source_dcc="Fixture",
        runtime_collected=False,
    )


def build_facts_from_assets(
    scene: Dict[str, Any],
    assets: List[Dict[str, Any]],
    source_dcc: str,
    runtime_collected: bool,
) -> Dict[str, Any]:
    rows = [_build_asset_facts(asset, scene, source_dcc) for asset in assets]
    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": source_dcc,
            "unit": scene.get("unit"),
            "timeUnit": scene.get("timeUnit"),
            "fps": scene.get("fps"),
            "playbackStart": scene.get("playbackStart"),
            "playbackEnd": scene.get("playbackEnd"),
            "assetCount": len(rows),
            "runtimeCollected": runtime_collected,
        },
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    scene = facts.get("scene", {})
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row, scene))
    return {
        "schema": "animation-continuity-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "fixPreview": _build_fix_preview(evaluations),
    }


def build_report(fixture_path: str | Path) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Animation Continuity Lab",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2",
        "l3Status": "contract_fixture_collected",
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "animation-continuity",
            "name": "Animation Continuity Lab",
            "methodSource": "Lightbox animation export / MotionBuilder handoff / Unreal animation import continuity",
            "protocolCarrier": "animation continuity protocol + take metadata + keyed channel facts",
            "boundary": {
                "mutation": "contract_validation_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": _reviewer_claims(),
    }


def _build_asset_facts(asset: Dict[str, Any], scene: Dict[str, Any], source_dcc: str) -> Dict[str, Any]:
    protocol = asset.get("protocol", {})
    channels = asset.get("channels", [])
    channel_rows = [_channel_fact(asset, channel) for channel in channels]
    identities = [row["identity"] for row in channel_rows]
    identity_counts = Counter(identities)
    duplicate_identities = sorted(identity for identity, count in identity_counts.items() if count > 1)
    required_channels = [str(channel) for channel in protocol.get("requiredChannels", [])]
    actual_identities = sorted(set(identities))
    missing_channels = sorted(set(required_channels) - set(actual_identities))
    sub_frame_keys = [
        {"identity": row["identity"], "frame": key["frame"]}
        for row in channel_rows
        for key in row["keys"]
        if not _is_integral_frame(key["frame"])
    ]
    start_frame = float(protocol.get("startFrame", 0.0))
    end_frame = float(protocol.get("endFrame", 0.0))
    keys_outside_range = [
        {"identity": row["identity"], "frame": key["frame"]}
        for row in channel_rows
        for key in row["keys"]
        if key["frame"] < start_frame or key["frame"] > end_frame
    ]
    root_node = str(asset.get("rootNode", "Hips"))
    root_motion_channels = [
        row for row in channel_rows if row["identity"] in {f"{root_node}.translateX", f"{root_node}.translateZ"}
    ]
    root_motion_delta = sum(abs(_curve_delta(row)) for row in root_motion_channels)
    scale_drift = max([_scale_drift(row) for row in channel_rows if row["attr"].startswith("scale")] or [0.0])
    additive_layers = [
        layer
        for layer in asset.get("animationLayers", [])
        if str(layer.get("mode", "")).lower() == "additive" and not bool(layer.get("muted"))
    ]
    first_key = min([key["frame"] for row in channel_rows for key in row["keys"]] or [start_frame])
    last_key = max([key["frame"] for row in channel_rows for key in row["keys"]] or [end_frame])

    return {
        "assetId": asset.get("id"),
        "assetLabel": asset.get("label"),
        "sourceDcc": source_dcc,
        "normalizedSchema": NORMALIZED_SCHEMA,
        "protocolCarrier": "animation continuity protocol + take metadata + keyed channel facts",
        "sourceFields": {
            "rigIdentity": "root.aiToolTaRigId + root.aiToolTaSkeletonFingerprint",
            "take": "root.aiToolTaAnimProtocol takeName/start/end/sampleRate",
            "channels": "animCurve target node + attr + key frames",
            "subFrame": "keyframe time values",
            "rootMotion": "root translateX/translateZ curve deltas",
            "layers": "animation layer payload",
        },
        "normalized": {
            "animation.protocol.schema": protocol.get("schema"),
            "character.rigId": asset.get("actualRigId"),
            "character.expectedRigId": protocol.get("expectedRigId"),
            "character.skeletonFingerprint": asset.get("actualSkeletonFingerprint"),
            "character.expectedSkeletonFingerprint": protocol.get("expectedSkeletonFingerprint"),
            "take.name": protocol.get("takeName"),
            "take.startFrame": protocol.get("startFrame"),
            "take.endFrame": protocol.get("endFrame"),
            "take.actualFirstKey": first_key,
            "take.actualLastKey": last_key,
            "take.sampleRate": protocol.get("sampleRate"),
            "scene.fps": scene.get("fps"),
            "take.allowSubFrameKeys": protocol.get("allowSubFrameKeys", False),
            "channels.requiredCount": len(required_channels),
            "channels.actualCount": len(actual_identities),
            "channels.missing": missing_channels,
            "channels.duplicates": duplicate_identities,
            "keys.subFrameCount": len(sub_frame_keys),
            "keys.outsideRangeCount": len(keys_outside_range),
            "rootMotion.policy": protocol.get("rootMotion"),
            "rootMotion.delta": root_motion_delta,
            "scale.maxDrift": scale_drift,
            "animationLayers.additiveActive": len(additive_layers),
            "animationLayers.additiveWithoutOwner": sum(1 for layer in additive_layers if not layer.get("owner")),
        },
        "raw": {
            "namespace": asset.get("namespace"),
            "rootNode": root_node,
            "requiredChannels": required_channels,
            "channelIdentities": identities,
            "duplicateChannelIdentities": duplicate_identities,
            "missingChannels": missing_channels,
            "subFrameKeys": sub_frame_keys,
            "keysOutsideRange": keys_outside_range,
            "rootMotionChannels": [row["identity"] for row in root_motion_channels],
            "animationLayers": asset.get("animationLayers", []),
            "channels": channel_rows,
        },
    }


def _channel_fact(asset: Dict[str, Any], channel: Dict[str, Any]) -> Dict[str, Any]:
    node = str(channel.get("node"))
    namespace = str(channel.get("namespace", asset.get("namespace", "")))
    attr = str(channel.get("attr"))
    keys = [
        {
            "frame": float(key.get("frame")),
            "value": float(key.get("value", 0.0)),
        }
        for key in channel.get("keys", [])
    ]
    keys.sort(key=lambda key: key["frame"])
    return {
        "node": node,
        "fullNode": f"{namespace}:{node}" if namespace else node,
        "attr": attr,
        "identity": f"{node}.{attr}",
        "keyCount": len(keys),
        "keys": keys,
    }


def _evaluate_asset(row: Dict[str, Any], scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    normalized = row.get("normalized", {})
    raw = row.get("raw", {})
    root_policy = normalized.get("rootMotion.policy")
    root_delta = float(normalized.get("rootMotion.delta") or 0.0)
    root_motion_ok = root_delta > 0.001 if root_policy == "required" else root_delta <= 0.001
    additive_without_owner = int(normalized.get("animationLayers.additiveWithoutOwner") or 0)
    additive_active = int(normalized.get("animationLayers.additiveActive") or 0)
    additive_allowed = not additive_active or additive_without_owner == 0

    return [
        _eval(
            asset_id,
            "protocol-carrier",
            normalized.get("animation.protocol.schema") == "animation-continuity@dcc-r23",
            "error",
            "Animation protocol carrier",
            "Animation take must expose animation-continuity@dcc-r23 before handoff.",
            str(normalized.get("animation.protocol.schema")),
            "Write continuity protocol on the take root before export.",
        ),
        _eval(
            asset_id,
            "rig-identity",
            normalized.get("character.rigId") == normalized.get("character.expectedRigId")
            and normalized.get("character.skeletonFingerprint") == normalized.get("character.expectedSkeletonFingerprint"),
            "error",
            "Rig identity / skeleton fingerprint",
            "Retargeting is only deterministic when rig id and skeleton fingerprint match the declared take.",
            "rig=%s expected=%s skeleton=%s"
            % (
                normalized.get("character.rigId"),
                normalized.get("character.expectedRigId"),
                normalized.get("character.skeletonFingerprint"),
            ),
            "Re-export from the approved rig or attach a retarget owner waiver.",
        ),
        _eval(
            asset_id,
            "sample-rate",
            float(normalized.get("take.sampleRate") or 0.0) == float(scene.get("fps") or 0.0),
            "error",
            "Sample rate",
            "Take sample rate must match scene FPS so MotionBuilder and Unreal do not resample silently.",
            "sampleRate=%s sceneFps=%s" % (normalized.get("take.sampleRate"), scene.get("fps")),
            "Resample curves to scene FPS and re-export the take receipt.",
        ),
        _eval(
            asset_id,
            "required-channel-coverage",
            not raw.get("missingChannels"),
            "error",
            "Required channel coverage",
            "Gameplay-critical channels must be present after retarget/export.",
            ",".join(raw.get("missingChannels", [])) or "-",
            "Restore missing channels or mark the take owner-held.",
        ),
        _eval(
            asset_id,
            "channel-identity",
            not raw.get("duplicateChannelIdentities"),
            "error",
            "Channel identity collision",
            "Two curves cannot resolve to the same normalized joint.attr identity.",
            ",".join(raw.get("duplicateChannelIdentities", [])) or "-",
            "Resolve namespace/source merge before export.",
        ),
        _eval(
            asset_id,
            "sub-frame-boundary",
            bool(normalized.get("take.allowSubFrameKeys")) or int(normalized.get("keys.subFrameCount") or 0) == 0,
            "error",
            "Sub-frame key boundary",
            "Sub-frame keys must be explicit because game import can quantize them differently.",
            str(raw.get("subFrameKeys", [])),
            "Bake or document sub-frame keys with owner approval.",
        ),
        _eval(
            asset_id,
            "curve-range",
            int(normalized.get("keys.outsideRangeCount") or 0) == 0,
            "warning",
            "Curve range",
            "Keys outside declared take range can leak poses into neighboring clips.",
            str(raw.get("keysOutsideRange", [])),
            "Trim keys to take range or split the take.",
        ),
        _eval(
            asset_id,
            "root-motion-contract",
            root_motion_ok,
            "error",
            "Root motion contract",
            "Root motion policy must match root translate curve evidence.",
            "policy=%s delta=%.4f" % (root_policy, root_delta),
            "Bake root motion into the approved root or remove it from in-place clips.",
        ),
        _eval(
            asset_id,
            "scale-clean",
            float(normalized.get("scale.maxDrift") or 0.0) <= 0.001,
            "warning",
            "Scale clean",
            "Animated scale usually indicates retarget or rig compensation leakage.",
            "%.4f" % float(normalized.get("scale.maxDrift") or 0.0),
            "Remove scale curves or route the exception to rig owner review.",
        ),
        _eval(
            asset_id,
            "animation-layer-boundary",
            additive_allowed,
            "warning",
            "Animation layer boundary",
            "Active additive layers need owner attribution before deterministic export.",
            str(raw.get("animationLayers", [])),
            "Bake approved layers or add owner attribution to the handoff packet.",
        ),
    ]


def _eval(
    asset_id: str,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    reason: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (asset_id, rule_id),
        "assetId": asset_id,
        "ruleId": rule_id,
        "label": label,
        "status": "pass" if passed else fail_status,
        "reason": reason,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    asset_ids = sorted({row["assetId"] for row in rows})
    blocked_assets = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review_assets = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked_assets))
    ready_assets = sorted(set(asset_ids) - set(blocked_assets) - set(review_assets))
    gate = "Blocked" if blocked_assets else "Review" if review_assets else "Ready"
    return {
        "gate": gate,
        "assetCount": len(asset_ids),
        "readyAssets": len(ready_assets),
        "reviewAssets": len(review_assets),
        "blockedAssets": len(blocked_assets),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready_assets,
        "reviewAssetIds": review_assets,
        "blockedAssetIds": blocked_assets,
    }


def _build_fix_preview(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "fix:%s" % row["id"],
            "assetId": row["assetId"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "mutationScope": "owner_required" if row["status"] == "error" else "manual_only",
            "preview": row["fixPreview"],
        }
        for row in evaluations
        if row["status"] != "pass"
    ]


def _curve_delta(row: Dict[str, Any]) -> float:
    keys = row.get("keys", [])
    if len(keys) < 2:
        return 0.0
    return float(keys[-1]["value"]) - float(keys[0]["value"])


def _scale_drift(row: Dict[str, Any]) -> float:
    return max([abs(float(key["value"]) - 1.0) for key in row.get("keys", [])] or [0.0])


def _is_integral_frame(frame: float) -> bool:
    return math.isclose(float(frame), round(float(frame)), abs_tol=0.0001)


def _reviewer_claims() -> List[str]:
    return [
        "Animation Continuity Lab turns take handoff into explicit business facts: rig identity, skeleton fingerprint, sample rate, channel ownership, sub-frame keys and root motion.",
        "The fixture includes one ready locomotion take and one intentionally blocked retargeted take, exposing the exact failure modes a TA must catch before engine import.",
        "The contract pass is public-safe and performs no production scene, asset or engine writes.",
    ]
