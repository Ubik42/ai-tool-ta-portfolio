$ErrorActionPreference = "Stop"

$HostRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PortfolioRoot = Resolve-Path (Join-Path $HostRoot "..\..")
$FrontendRoot = Join-Path $PortfolioRoot "showcases\portfolio-site"

Push-Location $FrontendRoot
try {
  if (-not (Test-Path -LiteralPath "node_modules")) {
    npm install
  }
  npm run build
  $IndexPath = Join-Path $FrontendRoot "dist\index.html"
  if (-not (Test-Path -LiteralPath $IndexPath)) {
    throw "Frontend build did not create dist\index.html"
  }
  Get-Item -LiteralPath $IndexPath | Select-Object FullName, Length, LastWriteTime
}
finally {
  Pop-Location
}
