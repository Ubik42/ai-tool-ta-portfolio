param(
    [ValidateSet("quick", "package", "ui", "animation", "unreal-animation", "unreal-animation-deep-facts", "character-calibration", "character-drilldown", "unreal-control-rig", "unreal-control-rig-fixture-authoring", "unreal-control-rig-face-skeleton-fixture", "unreal-control-rig-deformation-link", "unreal-control-rig-compile-status", "groom-export-inspector", "groom-unreal-readiness", "groom-alembic-payload", "groom-alembic-import-postcheck", "spatial-authoring", "spatial-drilldown", "unreal-socket", "unreal-socket-authoring-executor", "platform-variant", "platform-variant-unreal", "platform-variant-generation", "platform-variant-texture", "platform-variant-texture-payload", "platform-variant-executor", "platform-variant-executor-expansion", "platform-variant-staticmesh-postcheck", "blender", "max", "full")]
    [string]$Tier = "quick",
    [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    Write-Host "[validate:$Tier] $Name"
    & $Command
}

function Invoke-JsonCheck {
    param([string[]]$Paths)
    foreach ($Path in $Paths) {
        python -m json.tool $Path *> $null
    }
}

$MayaHost = Join-Path $Root "dcc-hosts\maya-auroraview-host"
$AnimationLab = Join-Path $Root "dcc-hosts\animation-continuity-lab"
$UnrealAnimationBridge = Join-Path $Root "dcc-hosts\unreal-animation-bridge"
$CharacterCalibration = Join-Path $Root "dcc-hosts\character-calibration-studio"
$UnrealControlRig = Join-Path $Root "dcc-hosts\unreal-control-rig-bridge"
$GroomExportInspector = Join-Path $Root "dcc-hosts\groom-export-inspector"
$SpatialAuthoring = Join-Path $Root "dcc-hosts\spatial-authoring-workbench"
$UnrealSocket = Join-Path $Root "dcc-hosts\unreal-socket-import-checker"
$PlatformVariant = Join-Path $Root "dcc-hosts\platform-variant-forge"
$BlenderAdapter = Join-Path $Root "dcc-hosts\blender-rule-adapter"
$MaxAdapter = Join-Path $Root "dcc-hosts\3dsmax-rule-adapter"
$PortfolioSite = Join-Path $Root "showcases\portfolio-site"
$MayapyCandidates = @(
    "C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe",
    "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe",
    "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe",
    "C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe",
    "D:\Program Files\Autodesk\Maya2026\bin\mayapy.exe",
    "D:\Program Files\Autodesk\Maya2025\bin\mayapy.exe",
    "D:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
)
$Mayapy = $MayapyCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Mayapy) {
    $MayapyCommand = Get-Command mayapy -ErrorAction SilentlyContinue
    if ($MayapyCommand) {
        $Mayapy = $MayapyCommand.Source
    }
}

$QuickPythonFiles = @(
    (Join-Path $MayaHost "ai_tool_ta_maya_host\api.py"),
    (Join-Path $MayaHost "ai_tool_ta_maya_host\external_control.py"),
    (Join-Path $MayaHost "scripts\send_maya_command.py"),
    (Join-Path $MayaHost "scripts\start_maya_command_bridge.py"),
    (Join-Path $BlenderAdapter "blender_rule_adapter\bpy_collector.py"),
    (Join-Path $BlenderAdapter "scripts\run_l3_smoke.py"),
    (Join-Path $MaxAdapter "max_rule_adapter\runtime_collector.py"),
    (Join-Path $MaxAdapter "scripts\run_l3_smoke.py"),
    (Join-Path $AnimationLab "animation_continuity_lab\contract.py"),
    (Join-Path $AnimationLab "animation_continuity_lab\maya_collector.py"),
    (Join-Path $AnimationLab "scripts\run_smoke.py"),
    (Join-Path $AnimationLab "scripts\run_l3_smoke.py"),
    (Join-Path $AnimationLab "scripts\run_maya_l3.py"),
    (Join-Path $UnrealAnimationBridge "unreal_animation_bridge\contract.py"),
    (Join-Path $UnrealAnimationBridge "unreal_animation_bridge\deep_facts.py"),
    (Join-Path $UnrealAnimationBridge "scripts\run_smoke.py"),
    (Join-Path $UnrealAnimationBridge "scripts\run_l3_smoke.py"),
    (Join-Path $UnrealAnimationBridge "scripts\run_import_l3_smoke.py"),
    (Join-Path $UnrealAnimationBridge "scripts\run_deep_facts.py"),
    (Join-Path $UnrealAnimationBridge "scripts\generate_maya_fbx_fixture.py"),
    (Join-Path $UnrealAnimationBridge "scripts\unreal_python\probe_animation_runtime.py"),
    (Join-Path $UnrealAnimationBridge "scripts\unreal_python\import_animsequence_fixture.py"),
    (Join-Path $UnrealAnimationBridge "scripts\unreal_python\collect_animsequence_deep_facts.py"),
    (Join-Path $CharacterCalibration "character_calibration_studio\contract.py"),
    (Join-Path $CharacterCalibration "character_calibration_studio\maya_collector.py"),
    (Join-Path $CharacterCalibration "character_calibration_studio\drilldown.py"),
    (Join-Path $CharacterCalibration "scripts\run_smoke.py"),
    (Join-Path $CharacterCalibration "scripts\run_l3_smoke.py"),
    (Join-Path $CharacterCalibration "scripts\run_maya_l3.py"),
    (Join-Path $CharacterCalibration "scripts\run_drilldown.py"),
    (Join-Path $UnrealControlRig "unreal_control_rig_bridge\contract.py"),
    (Join-Path $UnrealControlRig "unreal_control_rig_bridge\fixture_authoring.py"),
    (Join-Path $UnrealControlRig "unreal_control_rig_bridge\face_skeleton_fixture.py"),
    (Join-Path $UnrealControlRig "unreal_control_rig_bridge\deformation_link.py"),
    (Join-Path $UnrealControlRig "unreal_control_rig_bridge\compile_status.py"),
    (Join-Path $UnrealControlRig "scripts\run_smoke.py"),
    (Join-Path $UnrealControlRig "scripts\run_l3_smoke.py"),
    (Join-Path $UnrealControlRig "scripts\run_fixture_authoring.py"),
    (Join-Path $UnrealControlRig "scripts\run_face_skeleton_fixture.py"),
    (Join-Path $UnrealControlRig "scripts\run_deformation_link.py"),
    (Join-Path $UnrealControlRig "scripts\run_compile_status.py"),
    (Join-Path $UnrealControlRig "scripts\generate_face_skeleton_fbx.py"),
    (Join-Path $UnrealControlRig "scripts\unreal_python\probe_control_rig_bridge.py"),
    (Join-Path $UnrealControlRig "scripts\unreal_python\author_control_rig_fixture.py"),
    (Join-Path $UnrealControlRig "scripts\unreal_python\import_face_skeleton_fixture.py"),
    (Join-Path $UnrealControlRig "scripts\unreal_python\collect_control_rig_deformation_link.py"),
    (Join-Path $UnrealControlRig "scripts\unreal_python\collect_control_rig_compile_status.py"),
    (Join-Path $GroomExportInspector "groom_export_inspector\contract.py"),
    (Join-Path $GroomExportInspector "groom_export_inspector\maya_collector.py"),
    (Join-Path $GroomExportInspector "groom_export_inspector\unreal_readiness.py"),
    (Join-Path $GroomExportInspector "groom_export_inspector\alembic_payload.py"),
    (Join-Path $GroomExportInspector "groom_export_inspector\alembic_import_postcheck.py"),
    (Join-Path $GroomExportInspector "scripts\run_smoke.py"),
    (Join-Path $GroomExportInspector "scripts\run_l3_smoke.py"),
    (Join-Path $GroomExportInspector "scripts\run_maya_l3.py"),
    (Join-Path $GroomExportInspector "scripts\run_unreal_readiness.py"),
    (Join-Path $GroomExportInspector "scripts\run_alembic_payload.py"),
    (Join-Path $GroomExportInspector "scripts\run_alembic_import_postcheck.py"),
    (Join-Path $GroomExportInspector "scripts\run_maya_alembic_payload.py"),
    (Join-Path $GroomExportInspector "scripts\unreal_python\probe_groom_import_readiness.py"),
    (Join-Path $GroomExportInspector "scripts\unreal_python\probe_groom_alembic_import_postcheck.py"),
    (Join-Path $SpatialAuthoring "spatial_authoring_workbench\contract.py"),
    (Join-Path $SpatialAuthoring "spatial_authoring_workbench\maya_collector.py"),
    (Join-Path $SpatialAuthoring "spatial_authoring_workbench\drilldown.py"),
    (Join-Path $SpatialAuthoring "scripts\run_smoke.py"),
    (Join-Path $SpatialAuthoring "scripts\run_l3_smoke.py"),
    (Join-Path $SpatialAuthoring "scripts\run_maya_l3.py"),
    (Join-Path $SpatialAuthoring "scripts\run_drilldown.py"),
    (Join-Path $UnrealSocket "unreal_socket_import_checker\contract.py"),
    (Join-Path $UnrealSocket "unreal_socket_import_checker\controlled_executor.py"),
    (Join-Path $UnrealSocket "scripts\run_smoke.py"),
    (Join-Path $UnrealSocket "scripts\run_l3_smoke.py"),
    (Join-Path $UnrealSocket "scripts\run_socket_authoring_executor.py"),
    (Join-Path $UnrealSocket "scripts\unreal_python\probe_socket_import_checker.py"),
    (Join-Path $UnrealSocket "scripts\unreal_python\execute_socket_authoring.py"),
    (Join-Path $UnrealSocket "scripts\unreal_python\probe_socket_api_docs.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\contract.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\runtime_contract.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\generation_plan.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\texture_runtime.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\controlled_executor.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\executor_expansion.py"),
    (Join-Path $PlatformVariant "platform_variant_forge\staticmesh_postcheck.py"),
    (Join-Path $PlatformVariant "scripts\run_smoke.py"),
    (Join-Path $PlatformVariant "scripts\run_unreal_runtime_probe.py"),
    (Join-Path $PlatformVariant "scripts\run_generation_plan.py"),
    (Join-Path $PlatformVariant "scripts\run_texture_runtime_probe.py"),
    (Join-Path $PlatformVariant "scripts\run_texture_payload_probe.py"),
    (Join-Path $PlatformVariant "scripts\run_controlled_executor.py"),
    (Join-Path $PlatformVariant "scripts\run_executor_expansion.py"),
    (Join-Path $PlatformVariant "scripts\run_staticmesh_postcheck.py"),
    (Join-Path $PlatformVariant "scripts\unreal_python\probe_variant_runtime.py"),
    (Join-Path $PlatformVariant "scripts\unreal_python\collect_texture_runtime.py"),
    (Join-Path $PlatformVariant "scripts\unreal_python\execute_controlled_variant.py"),
    (Join-Path $PlatformVariant "scripts\unreal_python\collect_staticmesh_postcheck.py")
)

$CoreJsonFiles = @(
    (Join-Path $Root "public-case-package\dcc-first-package-manifest.json"),
    (Join-Path $Root "public-case-package\package-manifest.json")
)

Invoke-Step "python compile core files" {
    python -m py_compile @QuickPythonFiles
}

Invoke-Step "json manifests" {
    Invoke-JsonCheck $CoreJsonFiles
}

if ($Tier -in @("package", "full")) {
    Invoke-Step "maya presenter pack build smoke" {
        if (-not $Mayapy -or -not (Test-Path $Mayapy)) {
            throw "Maya mayapy not found. Searched: $($MayapyCandidates -join ', ')"
        }
        @"
import sys
sys.path.insert(0, r"$MayaHost")
from ai_tool_ta_maya_host.api import MayaPortfolioApi
pack = MayaPortfolioApi().dcc_presentation_build_pack(label="r49-groom-alembic-import-postcheck-presentation-pack")
summary = pack["summary"]
assert summary["present_evidence_files"] == 48, summary
assert summary["missing_required_files"] == 0, summary
assert summary["demo_route_steps"] == 38, summary
print(summary["package_id"], summary["package_version"], summary["present_evidence_files"], summary["missing_required_files"], summary["demo_route_steps"])
"@ | & $Mayapy -
        if ($LASTEXITCODE -ne 0) {
            throw "Maya presenter pack build smoke failed with exit code $LASTEXITCODE"
        }
    }
}

if ($Tier -in @("ui", "full")) {
    Invoke-Step "embedded ui build" {
        Push-Location $PortfolioSite
        try {
            npm run build
        }
        finally {
            Pop-Location
        }
    }
}

if ($Tier -in @("animation", "full")) {
    Invoke-Step "animation continuity contract smoke" {
        python (Join-Path $AnimationLab "scripts\run_smoke.py")
    }
}

if ($Tier -in @("unreal-animation", "full")) {
    Invoke-Step "unreal animation bridge contract smoke" {
        python (Join-Path $UnrealAnimationBridge "scripts\run_smoke.py")
    }
    Invoke-Step "unreal animation bridge import L3 harness" {
        python (Join-Path $UnrealAnimationBridge "scripts\run_import_l3_smoke.py")
    }
}

if ($Tier -in @("unreal-animation-deep-facts", "full")) {
    Invoke-Step "unreal animation deep facts" {
        python (Join-Path $UnrealAnimationBridge "scripts\run_deep_facts.py")
    }
}

if ($Tier -in @("character-calibration", "full")) {
    Invoke-Step "character calibration contract smoke" {
        python (Join-Path $CharacterCalibration "scripts\run_smoke.py")
    }
    Invoke-Step "character calibration Maya L3" {
        python (Join-Path $CharacterCalibration "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("character-drilldown", "full")) {
    Invoke-Step "character calibration drilldown" {
        python (Join-Path $CharacterCalibration "scripts\run_drilldown.py")
    }
}

if ($Tier -in @("unreal-control-rig", "full")) {
    Invoke-Step "unreal control rig bridge L3" {
        python (Join-Path $UnrealControlRig "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("unreal-control-rig-fixture-authoring", "full")) {
    Invoke-Step "unreal control rig fixture authoring" {
        python (Join-Path $UnrealControlRig "scripts\run_fixture_authoring.py")
    }
    Invoke-Step "unreal control rig bridge L3 after fixture authoring" {
        python (Join-Path $UnrealControlRig "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("unreal-control-rig-face-skeleton-fixture", "full")) {
    Invoke-Step "unreal control rig face skeleton fixture" {
        python (Join-Path $UnrealControlRig "scripts\run_face_skeleton_fixture.py")
    }
    Invoke-Step "unreal control rig bridge L3 after face skeleton fixture" {
        python (Join-Path $UnrealControlRig "scripts\run_l3_smoke.py")
    }
    Invoke-Step "unreal control rig deformation link after face skeleton fixture" {
        python (Join-Path $UnrealControlRig "scripts\run_deformation_link.py")
    }
}

if ($Tier -in @("unreal-control-rig-deformation-link", "full")) {
    Invoke-Step "unreal control rig deformation link" {
        python (Join-Path $UnrealControlRig "scripts\run_deformation_link.py")
    }
}

if ($Tier -in @("unreal-control-rig-compile-status", "full")) {
    Invoke-Step "unreal control rig compile status bridge" {
        python (Join-Path $UnrealControlRig "scripts\run_compile_status.py")
    }
}

if ($Tier -in @("groom-export-inspector", "full")) {
    Invoke-Step "groom export inspector contract smoke" {
        python (Join-Path $GroomExportInspector "scripts\run_smoke.py")
    }
    Invoke-Step "groom export inspector Maya L3" {
        python (Join-Path $GroomExportInspector "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("groom-unreal-readiness", "full")) {
    Invoke-Step "groom Unreal import readiness" {
        python (Join-Path $GroomExportInspector "scripts\run_unreal_readiness.py")
    }
}

if ($Tier -in @("groom-alembic-payload", "full")) {
    Invoke-Step "groom Alembic payload receipt" {
        python (Join-Path $GroomExportInspector "scripts\run_alembic_payload.py")
    }
}

if ($Tier -in @("groom-alembic-import-postcheck", "full")) {
    Invoke-Step "groom Alembic import/post-check readiness" {
        python (Join-Path $GroomExportInspector "scripts\run_alembic_import_postcheck.py")
    }
}

if ($Tier -in @("spatial-authoring", "full")) {
    Invoke-Step "spatial authoring contract smoke" {
        python (Join-Path $SpatialAuthoring "scripts\run_smoke.py")
    }
    Invoke-Step "spatial authoring Maya L3" {
        python (Join-Path $SpatialAuthoring "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("spatial-drilldown", "full")) {
    Invoke-Step "spatial authoring drilldown" {
        python (Join-Path $SpatialAuthoring "scripts\run_drilldown.py")
    }
}

if ($Tier -in @("unreal-socket", "full")) {
    Invoke-Step "unreal socket import checker L3" {
        python (Join-Path $UnrealSocket "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("unreal-socket-authoring-executor", "full")) {
    Invoke-Step "unreal socket authoring executor" {
        python (Join-Path $UnrealSocket "scripts\run_socket_authoring_executor.py")
    }
}

if ($Tier -in @("platform-variant", "full")) {
    Invoke-Step "platform variant forge contract smoke" {
        python (Join-Path $PlatformVariant "scripts\run_smoke.py")
    }
}

if ($Tier -in @("platform-variant-unreal", "full")) {
    Invoke-Step "platform variant unreal runtime probe" {
        python (Join-Path $PlatformVariant "scripts\run_unreal_runtime_probe.py")
    }
}

if ($Tier -in @("platform-variant-generation", "full")) {
    Invoke-Step "platform variant generation plan" {
        python (Join-Path $PlatformVariant "scripts\run_generation_plan.py")
    }
}

if ($Tier -in @("platform-variant-texture", "full")) {
    Invoke-Step "platform variant texture runtime probe" {
        python (Join-Path $PlatformVariant "scripts\run_texture_runtime_probe.py")
    }
}

if ($Tier -in @("platform-variant-texture-payload", "full")) {
    Invoke-Step "platform variant texture payload probe" {
        python (Join-Path $PlatformVariant "scripts\run_texture_payload_probe.py")
    }
}

if ($Tier -in @("platform-variant-executor", "full")) {
    Invoke-Step "platform variant controlled executor" {
        python (Join-Path $PlatformVariant "scripts\run_controlled_executor.py")
    }
}

if ($Tier -in @("platform-variant-executor-expansion", "full")) {
    Invoke-Step "platform variant executor expansion" {
        python (Join-Path $PlatformVariant "scripts\run_executor_expansion.py")
    }
}

if ($Tier -in @("platform-variant-staticmesh-postcheck", "full")) {
    Invoke-Step "platform variant StaticMesh post-check" {
        python (Join-Path $PlatformVariant "scripts\run_staticmesh_postcheck.py")
    }
}

if ($Tier -in @("blender", "full")) {
    Invoke-Step "blender runtime l3" {
        python (Join-Path $BlenderAdapter "scripts\run_l3_smoke.py")
    }
}

if ($Tier -in @("max", "full")) {
    Invoke-Step "3ds Max runtime l3" {
        python (Join-Path $MaxAdapter "scripts\run_l3_smoke.py") --run-runtime --timeout-seconds $TimeoutSeconds
    }
}

Write-Host "[validate:$Tier] complete"
