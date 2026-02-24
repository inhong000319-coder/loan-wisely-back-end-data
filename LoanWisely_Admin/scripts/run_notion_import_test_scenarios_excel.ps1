param(
    [string]$DatabaseId = $env:NOTION_TEST_DB_ID,
    [string]$ExcelPath = "C:\workspace\Django_Spring\CCKSY_LW_TC_260220.xlsx",
    [string]$SheetName = "???????",
    [bool]$SkipExisting = $false
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($env:NOTION_TOKEN)) {
    Write-Host '[ERROR] NOTION_TOKEN environment variable is not set.' -ForegroundColor Red
    Write-Host 'Set it first (current session):' -ForegroundColor Yellow
    Write-Host '  $env:NOTION_TOKEN="<token>"'
    exit 1
}

if ([string]::IsNullOrWhiteSpace($DatabaseId)) {
    Write-Host '[ERROR] Test database id is missing.' -ForegroundColor Red
    Write-Host 'Set NOTION_TEST_DB_ID or pass -DatabaseId <id>.' -ForegroundColor Yellow
    exit 1
}

Push-Location $PSScriptRoot
try {
    $argsList = @('notion_import_test_scenarios_excel.py', '--database-id', $DatabaseId, '--xlsx-path', $ExcelPath, '--sheet-name', $SheetName)
    if ($SkipExisting) { $argsList += '--skip-existing' }

    Write-Host "[RUN] python $($argsList -join ' ')" -ForegroundColor Cyan
    & python @argsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
