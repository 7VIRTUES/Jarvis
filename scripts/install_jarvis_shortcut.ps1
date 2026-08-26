[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [switch]$SkipPreparation,
    [int]$Port = 8000,
    [string]$DesktopPath,
    [string]$StartMenuProgramsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ShortcutName = 'Jarvis.lnk'
$DefaultPort = 8000
$MinimumPort = 1024
$MaximumPort = 65535

function Write-Failure {
    param([Parameter(Mandatory = $true)][string]$Message)

    [Console]::Error.WriteLine($Message)
    exit 1
}

function Get-RepositoryRoot {
    $rootCandidate = Join-Path -Path $PSScriptRoot -ChildPath '..'
    return (Resolve-Path -LiteralPath $rootCandidate).Path
}

function Test-RepositoryLayout {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $requiredPaths = @(
        (Join-Path -Path $RepositoryRoot -ChildPath 'jarvis.cmd'),
        (Join-Path -Path $RepositoryRoot -ChildPath 'scripts\jarvis_launcher.py')
    )
    $missingPaths = @($requiredPaths | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
    if ($missingPaths.Count -eq 0) {
        return
    }

    [Console]::Error.WriteLine("Jarvis repository structure was not found at: $RepositoryRoot")
    foreach ($missingPath in $missingPaths) {
        [Console]::Error.WriteLine("Expected file is missing: $missingPath")
    }
    exit 1
}

function Resolve-DesktopDirectory {
    param([string]$CustomPath)

    if ($CustomPath) {
        if (-not (Test-Path -LiteralPath $CustomPath -PathType Container)) {
            Write-Failure "Desktop path does not exist: $CustomPath"
        }
        return (Resolve-Path -LiteralPath $CustomPath).Path
    }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if (-not $desktop) {
        $desktop = Join-Path -Path $env:USERPROFILE -ChildPath 'Desktop'
    }
    if (-not (Test-Path -LiteralPath $desktop -PathType Container)) {
        Write-Failure "Desktop directory could not be resolved: $desktop"
    }
    return $desktop
}

function Resolve-StartMenuProgramsDirectory {
    param([string]$CustomPath)

    if ($CustomPath) {
        if (-not (Test-Path -LiteralPath $CustomPath -PathType Container)) {
            Write-Failure "Start Menu programs path does not exist: $CustomPath"
        }
        return (Resolve-Path -LiteralPath $CustomPath).Path
    }

    $programs = [Environment]::GetFolderPath([Environment+SpecialFolder]::Programs)
    if (-not $programs) {
        $programs = Join-Path -Path $env:APPDATA -ChildPath 'Microsoft\Windows\Start Menu\Programs'
    }
    if (-not (Test-Path -LiteralPath $programs -PathType Container)) {
        Write-Failure "Start Menu programs directory could not be resolved: $programs"
    }
    return $programs
}

function Get-LauncherArguments {
    param(
        [bool]$DisableBrowser,
        [int]$SelectedPort
    )

    $parts = @()
    if ($SelectedPort -ne $DefaultPort) {
        $parts += "--port $SelectedPort"
    }
    if ($DisableBrowser) {
        $parts += '--no-browser'
    }
    return ($parts -join ' ')
}

function Save-Shortcut {
    param(
        [Parameter(Mandatory = $true)][string]$ShortcutPath,
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [string]$Arguments,
        [string]$Description,
        [int]$WindowStyle = 7
    )

    $parentDir = Split-Path -Path $ShortcutPath -Parent
    if (-not (Test-Path -LiteralPath $parentDir -PathType Container)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    try {
        $wscriptShell = New-Object -ComObject WScript.Shell
        $shortcut = $wscriptShell.CreateShortcut($ShortcutPath)
        $shortcut.TargetPath = $TargetPath
        $shortcut.Arguments = $Arguments
        $shortcut.WorkingDirectory = $WorkingDirectory
        $shortcut.Description = $Description
        $shortcut.WindowStyle = $WindowStyle
        $shortcut.Save()
    }
    catch [System.UnauthorizedAccessException] {
        Write-Failure "Access was denied while creating shortcut: $ShortcutPath"
    }
    catch {
        Write-Failure "The Windows shortcut could not be created at: $ShortcutPath. Confirm Windows Script Host is available."
    }

    if (-not (Test-Path -LiteralPath $ShortcutPath -PathType Leaf)) {
        Write-Failure "The shortcut was not found after saving: $ShortcutPath"
    }
}

try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        Write-Failure 'This shortcut installer is Windows-only. No shortcut was created.'
    }
    if ($Port -lt $MinimumPort -or $Port -gt $MaximumPort) {
        Write-Failure "Port must be an integer between $MinimumPort and $MaximumPort. No shortcut was created."
    }

    $repositoryRoot = Get-RepositoryRoot
    Test-RepositoryLayout -RepositoryRoot $repositoryRoot

    $launcherPath = Join-Path -Path $repositoryRoot -ChildPath 'jarvis.cmd'
    $arguments = Get-LauncherArguments -DisableBrowser $NoBrowser.IsPresent -SelectedPort $Port

    # First-time preparation (unless explicitly skipped)
    if (-not $SkipPreparation.IsPresent) {
        Write-Output 'Running first-time Jarvis setup and preparation...'
        & $launcherPath --prepare-only --no-browser
        if ($LASTEXITCODE -ne 0) {
            Write-Failure 'Jarvis setup did not complete, so shortcuts were not installed.'
        }
    }

    # 1. Desktop shortcut
    $desktopDir = Resolve-DesktopDirectory -CustomPath $DesktopPath
    $desktopShortcutPath = Join-Path -Path $desktopDir -ChildPath $ShortcutName
    Save-Shortcut -ShortcutPath $desktopShortcutPath -TargetPath $launcherPath -WorkingDirectory $repositoryRoot -Arguments $arguments -Description 'Jarvis PC Local' -WindowStyle 7

    # 2. Start Menu shortcut
    $programsDir = Resolve-StartMenuProgramsDirectory -CustomPath $StartMenuProgramsPath
    $jarvisStartMenuDir = Join-Path -Path $programsDir -ChildPath 'Jarvis'
    if (-not (Test-Path -LiteralPath $jarvisStartMenuDir -PathType Container)) {
        New-Item -ItemType Directory -Path $jarvisStartMenuDir -Force | Out-Null
    }
    $startMenuShortcutPath = Join-Path -Path $jarvisStartMenuDir -ChildPath $ShortcutName
    Save-Shortcut -ShortcutPath $startMenuShortcutPath -TargetPath $launcherPath -WorkingDirectory $repositoryRoot -Arguments $arguments -Description 'Jarvis PC Local' -WindowStyle 7

    Write-Output 'Jarvis shortcuts installed successfully.'
    Write-Output ''
    Write-Output "Desktop:"
    Write-Output "  $desktopShortcutPath"
    Write-Output ''
    Write-Output "Start Menu:"
    Write-Output "  $startMenuShortcutPath"
    Write-Output ''
    Write-Output "Target:"
    Write-Output "  $launcherPath"
    Write-Output ''
    Write-Output "Working Directory:"
    Write-Output "  $repositoryRoot"
    Write-Output ''
    Write-Output "Landing page:"
    Write-Output "  http://127.0.0.1:$Port/assistant"
    Write-Output ''
    if ($NoBrowser.IsPresent) {
        Write-Output 'Browser auto-launch: disabled.'
    }
    else {
        Write-Output 'Browser auto-launch: enabled.'
    }
    exit 0
}
catch {
    Write-Failure "The shortcut installer could not complete: $_"
}
