# Post-tool execution hook — runs self_heal on recently edited files
param([string]$FilePath)

$ErrorActionPreference = "SilentlyContinue"
$script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if (-not $FilePath) { exit 0 }

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$validExts = @(".py", ".ts", ".tsx", ".dart")
if ($ext -notin $validExts) { exit 0 }

$py = "py"
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
    $py = "python3"
    if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
        $py = "python"
    }
}

& $py -m farewell_assistant.cli self-heal --file "$FilePath" --project "$script:ROOT_DIR"
exit $LASTEXITCODE
