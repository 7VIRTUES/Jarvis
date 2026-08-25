[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [int]$Port = 8000,
    [string]$DesktopPath,
    [string]$StartMenuProgramsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$installer = Join-Path -Path $PSScriptRoot -ChildPath 'install_jarvis_shortcut.ps1'
$params = @{}
if ($NoBrowser.IsPresent) {
    $params['NoBrowser'] = $true
}
if ($Port -ne 8000) {
    $params['Port'] = $Port
}
if (-not [string]::IsNullOrWhiteSpace($DesktopPath)) {
    $params['DesktopPath'] = $DesktopPath
}
if (-not [string]::IsNullOrWhiteSpace($StartMenuProgramsPath)) {
    $params['StartMenuProgramsPath'] = $StartMenuProgramsPath
}

& $installer @params
exit $LASTEXITCODE
