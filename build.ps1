<#
easyDesktop build script (PowerShell, ASCII-only to avoid encoding issues on Windows PowerShell 5.1)

Adds:
  - Build exeIconGet.exe for frozen runtime (ICON_GETTER = ['exeIconGet.exe'])
  - Run unit tests before packaging
#>

[CmdletBinding()]
param(
  [string]$ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path),
  [string]$VenvDir = "ed",
  [string]$EntryScript = "easyDesktop.py",
  [string]$InstallerScript = "easyDesktop_Installer.py",
  [string]$IconPath = "favicon.ico",
  [string]$HelperScript = "exeIconGet.py",
  [string]$PythonCmd = "py -3.12",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

function Assert-Path([string]$Path, [string]$Hint) {
  if (-not (Test-Path -LiteralPath $Path)) { throw "$Hint`nPath: $Path" }
}

Write-Host "== easyDesktop build ==" -ForegroundColor Cyan
Set-Location -LiteralPath $ProjectRoot

if ($Clean) {
  if (Test-Path ".\build") { Remove-Item -Recurse -Force ".\build" }
  if (Test-Path ".\dist")  { Remove-Item -Recurse -Force ".\dist" }
  Get-ChildItem "." -Filter "*.spec" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
}

Assert-Path (Join-Path $ProjectRoot $EntryScript) "Missing entry script"
Assert-Path (Join-Path $ProjectRoot $InstallerScript) "Missing installer script"
Assert-Path (Join-Path $ProjectRoot $IconPath) "Missing icon file"
Assert-Path (Join-Path $ProjectRoot $HelperScript) "Missing helper script (exeIconGet.py)"

$venvPath = Join-Path $ProjectRoot $VenvDir
if (-not (Test-Path $venvPath)) { Invoke-Expression "$PythonCmd -m venv $VenvDir" }

$activate = Join-Path $venvPath "Scripts\Activate.ps1"
Assert-Path $activate "Missing venv activate script"
. $activate

python -m pip install -U pip

$reqTxt = Join-Path $ProjectRoot "requirements.txt"
$reqIn  = Join-Path $ProjectRoot "requirements.in"
if (Test-Path $reqTxt) {
  python -m pip install -r $reqTxt
} elseif (Test-Path $reqIn) {
  python -m pip install -r $reqIn
}

python -m pip install "pywebview==6.1" "pyinstaller~=6.0" "pythonnet"

python -m unittest discover -s tests -p "test*.py"

$distRoot = Join-Path $ProjectRoot "dist\easyDesktop"

$addData = "$VenvDir/Lib/site-packages/pythonnet/runtime;pythonnet/runtime"
$argsMain = @(
  "-w", "-i", $IconPath, $EntryScript,
  "--add-data", $addData,
  "--hidden-import", "clr",
  "--hidden-import", "tkinter",
  "--hidden-import", "System",
  "--hidden-import", "System.Runtime",
  "--hidden-import=webview.platforms.win32",
  "--hidden-import=webview"
)
& pyinstaller @argsMain

$argsHelper = @(
  "-F", "-w",
  "--name", "exeIconGet",
  "--distpath", $distRoot,
  $HelperScript
)
& pyinstaller @argsHelper
Assert-Path (Join-Path $distRoot "exeIconGet.exe") "Missing exeIconGet.exe in dist output"

$internal = Join-Path $distRoot "_internal"
if (-not (Test-Path $internal)) { New-Item -ItemType Directory -Path $internal -Force | Out-Null }

if (Test-Path ".\resources") { Copy-Item -Recurse -Force ".\resources" (Join-Path $internal "resources") }
if (Test-Path ".\theme")     { Copy-Item -Recurse -Force ".\theme" (Join-Path $internal "theme") }
if (Test-Path ".\easyFileDesk.html") { Copy-Item -Force ".\easyFileDesk.html" $internal }
if (Test-Path ".\ed_logo.png") {
  Copy-Item -Force ".\ed_logo.png" $internal
  Copy-Item -Force ".\ed_logo.png" $distRoot
}
if (Test-Path ".\favicon.ico") { Copy-Item -Force ".\favicon.ico" $internal }

$resDir = Join-Path $ProjectRoot "res"
if (-not (Test-Path $resDir)) { New-Item -ItemType Directory -Path $resDir -Force | Out-Null }
$zipPath = Join-Path $resDir "easyDesktop.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path $distRoot -DestinationPath $zipPath -Force

$argsInstaller = @("-F","-w","-i",$IconPath,"--add-data","res;res",$InstallerScript)
& pyinstaller @argsInstaller

Write-Host "Done." -ForegroundColor Green
Write-Host "dist\easyDesktop\"
Write-Host "res\easyDesktop.zip"
Write-Host "dist\easyDesktop_Installer.exe"

