[CmdletBinding()]
param(
    [switch]$NoBrowser,
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

    if (-not [string]::IsNullOrWhiteSpace($CustomPath)) {
        if (-not (Test-Path -LiteralPath $CustomPath -PathType Container)) {
            New-Item -ItemType Directory -Path $CustomPath -Force | Out-Null
        }
        return (Resolve-Path -LiteralPath $CustomPath).Path
    }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if ([string]::IsNullOrWhiteSpace($desktop) -or -not (Test-Path -LiteralPath $desktop -PathType Container)) {
        Write-Failure 'The current user Windows Desktop directory could not be resolved. No shortcut was created.'
    }
    return (Resolve-Path -LiteralPath $desktop).Path
}

function Resolve-StartMenuProgramsDirectory {
    param([string]$CustomPath)

    if (-not [string]::IsNullOrWhiteSpace($CustomPath)) {
        if (-not (Test-Path -LiteralPath $CustomPath -PathType Container)) {
            New-Item -ItemType Directory -Path $CustomPath -Force | Out-Null
        }
        return (Resolve-Path -LiteralPath $CustomPath).Path
    }

    $programs = [Environment]::GetFolderPath([Environment+SpecialFolder]::Programs)
    if ([string]::IsNullOrWhiteSpace($programs)) {
        $appData = [Environment]::GetFolderPath([Environment+SpecialFolder]::ApplicationData)
        if (-not [string]::IsNullOrWhiteSpace($appData)) {
            $programs = Join-Path -Path $appData -ChildPath 'Microsoft\Windows\Start Menu\Programs'
        }
    }
    if ([string]::IsNullOrWhiteSpace($programs) -or -not (Test-Path -LiteralPath $programs -PathType Container)) {
        Write-Failure 'The current user Windows Start Menu Programs directory could not be resolved. No shortcut was created.'
    }
    return (Resolve-Path -LiteralPath $programs).Path
}

function Get-LauncherArguments {
    param(
        [Parameter(Mandatory = $true)][bool]$DisableBrowser,
        [Parameter(Mandatory = $true)][int]$SelectedPort
    )

    $launcherArguments = @()
    if ($DisableBrowser) {
        $launcherArguments += '--no-browser'
    }
    if ($SelectedPort -ne $DefaultPort) {
        $launcherArguments += '--port'
        $launcherArguments += $SelectedPort.ToString()
    }
    return ($launcherArguments -join ' ')
}

function Save-Shortcut {
    param(
        [Parameter(Mandatory = $true)][string]$ShortcutPath,
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [AllowEmptyString()][string]$Arguments = '',
        [Parameter(Mandatory = $true)][string]$Description,
        [int]$WindowStyle = 7
    )

    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($ShortcutPath)
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
