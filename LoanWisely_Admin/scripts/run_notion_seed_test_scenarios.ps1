param(
    [string]$DatabaseId = $env:NOTION_TEST_DB_ID,
    [string]$Owner,
    [bool]$SkipExisting = $true
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

$env:NOTION_TEST_DB_ID = $DatabaseId

Push-Location $PSScriptRoot
try {
    $argsList = @('notion_seed_test_scenarios.py', '--database-id', $DatabaseId)
    if ($SkipExisting) {
        $argsList += '--skip-existing'
    }
    if (-not [string]::IsNullOrWhiteSpace($Owner)) {
        $argsList += @('--owner', $Owner)
    }

    Write-Host "[RUN] python $($argsList -join ' ')" -ForegroundColor Cyan
    & python @argsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
