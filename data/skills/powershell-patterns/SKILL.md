---
name: powershell-patterns
description: PowerShell scripting patterns, error handling, module management, API calls, pipeline operations, and best practices for Windows automation.
metadata:
  origin: farewell-assistant
---

# PowerShell Patterns

Idiomatic PowerShell 5.1+ patterns, best practices, and conventions for building robust, maintainable automation scripts.

## When to Activate

- Writing new PowerShell scripts (.ps1, .psm1, .psd1)
- Refactoring existing automation scripts
- Fixing bugs in PowerShell code
- Reviewing PowerShell code quality

### When NOT to Use

- Pure bash/Unix scripting → use `golang-patterns` or other shell skills
- Python automation → use `python-patterns`
- Node.js scripts → use `backend-patterns`

## Error Handling

### Always Set Error Action Preference

```powershell
# Explicit preference per script (recommended)
$ErrorActionPreference = "Stop"

# Or per command for specific cases
Get-ChildItem -Path $path -ErrorAction SilentlyContinue
```

### Try/Catch for Critical Operations

```powershell
try {
    $result = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
} catch {
    Write-Error "API call failed: $($_.Exception.Message)"
    # Log context, don't swallow
    throw
}
```

### Pipeline Error Handling

```powershell
# Don't use $ErrorActionPreference = "Continue" in pipelines
# Instead, use explicit error action per cmdlet
Get-ChildItem -Path $path -ErrorAction Stop | ForEach-Object {
    # If one item fails, the pipeline stops (correct behavior)
}
```

## Module Management

### Import Modules

```powershell
# Always check if module exists before importing
if (Get-Module -ListAvailable -Name $ModuleName) {
    Import-Module $ModuleName -Force
} else {
    Write-Warning "Module $ModuleName not found. Install with: Install-Module -Name $ModuleName"
}
```

### Module Structure

```powershell
# Module manifest (.psd1)
@{
    RootModule        = 'MyModule.psm1'
    ModuleVersion     = '1.0.0'
    GUID              = 'your-guid-here'
    Author            = 'Your Name'
    FunctionsToExport = @('Get-Something', 'Set-Something')
    CmdletsToExport  = @()
    VariablesToExport  = @()
    AliasesToExport    = @()
}
```

## API Calls

### Invoke-RestMethod (Preferred)

```powershell
# GET request
$response = Invoke-RestMethod -Uri "https://api.example.com/data" -Method GET -Headers @{
    "Authorization" = "Bearer $token"
    "Accept"        = "application/json"
}

# POST with JSON body
$body = @{
    name  = "test"
    value = 123
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod -Uri "https://api.example.com/submit" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
```

### Error Handling for APIs

```powershell
try {
    $response = Invoke-RestMethod -Uri $url -Method $method -ContentType "application/json" -TimeoutSec 30
} catch [System.Net.WebException] {
    $statusCode = [int]$_.Exception.Response.StatusCode
    switch ($statusCode) {
        401 { Write-Error "Unauthorized - check API key" }
        403 { Write-Error "Forbidden - insufficient permissions" }
        404 { Write-Error "Not found - check endpoint" }
        429 { Write-Error "Rate limited - wait before retrying" }
        500 { Write-Error "Server error - try again later" }
        default { Write-Error "HTTP $statusCode - $($_.Exception.Message)" }
    }
} catch {
    Write-Error "Request failed: $($_.Exception.Message)"
}
```

## Pipeline Patterns

### ForEach-Object

```powershell
# Parallel execution (PowerShell 7+)
$items | ForEach-Object -Parallel {
    # Process each item in parallel
    $_ | Process-Item
} -ThrottleLimit 5

# Sequential (PowerShell 5.1 compatible)
$items | ForEach-Object {
    Process-Item -Input $_
}
```

### Filtering

```powershell
# Where-Object (pipeline filter)
$items | Where-Object { $_.Status -eq "active" } | Select-Object Name, Status

# Filter operator (faster for simple comparisons)
$items | Where-Object Status -eq "active"
```

### Sorting

```powershell
# Sort by property
$items | Sort-Object -Property CreatedAt -Descending | Select-Object -First 10

# Multi-property sort
$items | Sort-Object -Property @{Expression={$_.Category}}, @{Expression={$_.Name}}
```

## File Operations

### Safe File Handling

```powershell
# Read with error handling
if (Test-Path $filePath) {
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
} else {
    Write-Warning "File not found: $filePath"
    return
}

# Write with backup
$backupPath = "$filePath.bak"
if (Test-Path $filePath) {
    Copy-Item -Path $filePath -Destination $backupPath -Force
}
$content | Set-Content -Path $filePath -Encoding UTF8 -Force
```

### JSON Operations

```powershell
# Read JSON
$json = Get-Content -Path $path -Raw | ConvertFrom-Json

# Write JSON
$json | ConvertTo-Json -Depth 10 | Set-Content -Path $path -Encoding UTF8

# Modify and save
$json | ConvertTo-Json -Depth 10 -Compress
```

## PowerShell Best Practices

### Naming Conventions

```powershell
# Functions: Verb-Noun (approved verbs)
function Get-ProjectStatus { }
function Set-Configuration { }

# Variables: camelCase
$projectName = "my-project"
$apiEndpoint = "https://api.example.com"

# Parameters: PascalCase
param(
    [string]$ProjectPath,
    [switch]$Force
)

# Constants: UPPER_SNAKE_CASE
$MAX_RETRY_COUNT = 3
$DEFAULT_TIMEOUT = 30
```

### Script Structure

```powershell
# 1. Header comment (purpose, usage)
# Script: MyScript.ps1
# Usage: .\MyScript.ps1 -Path "C:\project" -Force

# 2. Parameters
param(
    [string]$Path = (Get-Location).Path,
    [switch]$Force
)

# 3. Strict mode
Set-StrictMode -Version Latest

# 4. Error action
$ErrorActionPreference = "Stop"

# 5. Constants
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# 6. Functions
function Invoke-MainLogic {
    # Implementation
}

# 7. Main execution
try {
    Invoke-MainLogic
} catch {
    Write-Error "Script failed: $($_.Exception.Message)"
    exit 1
}
```

### Avoid Common Pitfalls

```powershell
# DON'T: Use Write-Host for output (use Write-Output or return)
Write-Host "This is bad"  # Bad
Write-Output "This is good"  # Good

# DON'T: Use aliases in scripts (only in interactive)
Get-ChildItem  # Good in scripts
ls             # Bad in scripts

# DON'T: Use $input (reserved word)
function Get-Data {
    param([string]$FilePath)  # Good
}

# DON'T: Silently continue errors
try { Something } catch { }  # Bad - swallows errors

# DON'T: Hardcode paths
$path = "C:\Users\me\project"  # Bad
$path = Join-Path $env:USERPROFILE "project"  # Good
```

## Testing PowerShell

### Unit Tests (Pester)

```powershell
Describe "Get-ProjectStatus" {
    It "returns correct status for active project" {
        $result = Get-ProjectStatus -Path "C:\active-project"
        $result.Status | Should -Be "active"
    }

    It "throws when path does not exist" {
        { Get-ProjectStatus -Path "C:\nonexistent" } | Should -Throw
    }
}
```

### Integration Tests

```powershell
Describe "API Integration" {
    BeforeAll {
        # Setup test environment
    }

    It "creates and retrieves item" {
        $item = New-Item -Name "test" -Value 123
        $item.Id | Should -Not -BeNullOrEmpty
    }

    AfterAll {
        # Cleanup
    }
}
```
