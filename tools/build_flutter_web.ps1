# Build the Flutter web bundle for the AMORA UI.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# Flutter 3.38 runs a "native assets" build hook for `objective_c` (an Apple-only
# transitive dependency that arrives via `path_provider_foundation`) even for web
# builds. That hook shells out with UNQUOTED paths, so if the project path OR the
# pub cache path contains a space, the build dies with:
#
#     'C:\Users\ARUL' is not recognized as an internal or external command
#     Building native assets for package:objective_c failed.
#
# The fix is to build from a staging directory and a pub cache that have no spaces
# in them, then copy the finished bundle back into the project. The build output is
# self-contained, so this produces a byte-identical result.
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\build_flutter_web.ps1

$ErrorActionPreference = "Stop"

$ProjectDir = Join-Path $PSScriptRoot "..\frontend\flutter_app"
$ProjectDir = (Resolve-Path $ProjectDir).Path

$StageRoot = "C:\amof_build"
$StageCache = "C:\pubcache"
$PubCache   = "C:\pubcache"

Write-Host "Project : $ProjectDir"
Write-Host "Staging : $StageRoot  (no spaces required)"
Write-Host ""

# ── 1. Copy sources to the staging directory ────────────────────────────────
if (Test-Path $StageRoot) { Remove-Item $StageRoot -Recurse -Force }
New-Item -ItemType Directory -Path $StageRoot | Out-Null

$null = robocopy $ProjectDir $StageRoot /E /XD build .dart_tool .idea android `
        /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }

# ── 2. Resolve dependencies against a space-free pub cache ─────────────────
if (-not (Test-Path $PubCache)) { New-Item -ItemType Directory -Path $PubCache | Out-Null }
$env:PUB_CACHE = $PubCache
Push-Location $StageRoot
try {
    Write-Host "Resolving dependencies (PUB_CACHE=$PubCache)..."
    flutter pub get
    if ($LASTEXITCODE -ne 0) { throw "flutter pub get failed" }

    # ── 3. Compile ─────────────────────────────────────────────────────────
    Write-Host "Building web release bundle..."
    flutter build web --release --base-href /app/
    if ($LASTEXITCODE -ne 0) { throw "flutter build web failed" }
}
finally { Pop-Location }

# ── 4. Copy the bundle back into the project ───────────────────────────────
$Dest = Join-Path $ProjectDir "build\web"
if (Test-Path $Dest) { Remove-Item $Dest -Recurse -Force }
$null = robocopy (Join-Path $StageRoot "build\web") $Dest /E /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "robocopy of build output failed" }

$Size = [math]::Round((Get-ChildItem $Dest -Recurse -File |
          Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ""
Write-Host "Done. $Size MB written to $Dest"
Write-Host "Start the backend and open http://localhost:8000/app"
