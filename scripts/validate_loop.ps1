param(
    [ValidateSet("quick", "package", "ui", "animation", "unreal-animation", "blender", "max", "full")]
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
    (Join-Path $UnrealAnimationBridge "scripts\run_smoke.py"),
    (Join-Path $UnrealAnimationBridge "scripts\run_l3_smoke.py"),
    (Join-Path $UnrealAnimationBridge "scripts\unreal_python\probe_animation_runtime.py")
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
pack = MayaPortfolioApi().dcc_presentation_build_pack(label="r24-unreal-animation-bridge-presentation-pack")
summary = pack["summary"]
assert summary["present_evidence_files"] == 21, summary
assert summary["missing_required_files"] == 0, summary
print(summary["package_id"], summary["package_version"], summary["present_evidence_files"], summary["missing_required_files"])
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
