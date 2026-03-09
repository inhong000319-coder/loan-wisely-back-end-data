param(
    [ValidateSet('all','hub-page','test-db','troubleshooting-page','troubleshooting-page-detailed')]
    [string]$Mode = 'all',
    [string]$Prefix = 'LOAN WISELY',
    [string]$ParentPageId = $env:NOTION_PARENT_PAGE_ID
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($env:NOTION_TOKEN)) {
    Write-Host '[ERROR] NOTION_TOKEN environment variable is not set.' -ForegroundColor Red
    Write-Host 'Set it first (current session):' -ForegroundColor Yellow
    Write-Host '  $env:NOTION_TOKEN="<token>"'
    exit 1
}

if ([string]::IsNullOrWhiteSpace($ParentPageId)) {
    Write-Host '[ERROR] Parent page id is missing.' -ForegroundColor Red
    Write-Host 'Set NOTION_PARENT_PAGE_ID or pass -ParentPageId <id>.' -ForegroundColor Yellow
    exit 1
}

$env:NOTION_PARENT_PAGE_ID = $ParentPageId

Push-Location $PSScriptRoot
try {
    $argsList = @('notion_seed_templates.py', '--mode', $Mode, '--prefix', $Prefix, '--parent-page-id', $ParentPageId)
    Write-Host "[RUN] python $($argsList -join ' ')" -ForegroundColor Cyan
    & python @argsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
