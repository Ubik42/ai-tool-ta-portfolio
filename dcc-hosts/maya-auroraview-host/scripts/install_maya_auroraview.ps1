param(
  [string]$MayaVersion = "2024",
  [string]$MayapyPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $MayapyPath) {
  $MayapyPath = "C:\Program Files\Autodesk\Maya$MayaVersion\bin\mayapy.exe"
}

if (-not (Test-Path -LiteralPath $MayapyPath)) {
  throw "mayapy.exe not found: $MayapyPath"
}

& $MayapyPath -m pip install --upgrade "auroraview[qt]>=0.5.10"
& $MayapyPath -c "import auroraview; print('auroraview', auroraview.__version__, 'qt', getattr(auroraview, '_HAS_QT', None), 'core_error', getattr(auroraview, '_CORE_IMPORT_ERROR', None))"
