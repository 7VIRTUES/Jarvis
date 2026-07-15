[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ShortcutName = 'Jarvis PC Local.lnk'
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

function Get-DesktopPath {
    $desktopPath = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if ([string]::IsNullOrWhiteSpace($desktopPath) -or -not (Test-Path -LiteralPath $desktopPath -PathType Container)) {
        Write-Failure 'The current user Windows Desktop could not be resolved. No shortcut was created.'
    }
    return (Resolve-Path -LiteralPath $desktopPath).Path
}

function Get-ShortcutArguments {
    param(
        [Parameter(Mandatory = $true)][string]$LauncherPath,
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

    $launcherCommand = '"{0}"' -f $LauncherPath
    if ($launcherArguments.Count -gt 0) {
        $launcherCommand = "$launcherCommand $($launcherArguments -join ' ')"
    }
    return '/d /c "{0}"' -f $launcherCommand
}

function New-JarvisDesktopShortcut {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$DesktopPath,
        [Parameter(Mandatory = $true)][bool]$DisableBrowser,
        [Parameter(Mandatory = $true)][int]$SelectedPort
    )

    $launcherPath = Join-Path -Path $RepositoryRoot -ChildPath 'jarvis.cmd'
    $shortcutPath = Join-Path -Path $DesktopPath -ChildPath $ShortcutName
    if (Test-Path -LiteralPath $shortcutPath) {
        [Console]::Error.WriteLine("$ShortcutName already exists: $shortcutPath")
        [Console]::Error.WriteLine('No changes were made. Delete or rename it manually, then rerun the shortcut creator if replacement is desired.')
        exit 1
    }

    $commandInterpreter = $env:ComSpec
    if ([string]::IsNullOrWhiteSpace($commandInterpreter) -or -not (Test-Path -LiteralPath $commandInterpreter -PathType Leaf)) {
        Write-Failure 'The Windows command interpreter could not be resolved. No shortcut was created.'
    }

    $arguments = Get-ShortcutArguments -LauncherPath $launcherPath -DisableBrowser $DisableBrowser -SelectedPort $SelectedPort
    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $commandInterpreter
        $shortcut.Arguments = $arguments
        $shortcut.WorkingDirectory = $RepositoryRoot
        $shortcut.Description = 'Start Jarvis PC Local from this repository'
        $shortcut.WindowStyle = 1
        $shortcut.Save()
    }
    catch [System.UnauthorizedAccessException] {
        Write-Failure 'Access was denied while creating the desktop shortcut. No shortcut was confirmed.'
    }
    catch {
        Write-Failure 'The Windows shortcut could not be created. Confirm Windows Script Host is available and try again.'
    }

    if (-not (Test-Path -LiteralPath $shortcutPath -PathType Leaf)) {
        Write-Failure 'The shortcut was not found after saving. No success was confirmed.'
    }

    Write-Output 'Jarvis PC Local desktop shortcut created.'
    Write-Output "Shortcut: $shortcutPath"
    Write-Output 'It launches the repository-local jarvis.cmd.'
    Write-Output "Port: $SelectedPort"
    if ($DisableBrowser) {
        Write-Output 'Browser opening: disabled.'
    }
    else {
        Write-Output 'Browser opening: enabled.'
    }
    Write-Output 'Jarvis was not started.'
}

try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        Write-Failure 'This shortcut creator is Windows-only. No shortcut was created.'
    }
    if ($Port -lt $MinimumPort -or $Port -gt $MaximumPort) {
        Write-Failure "Port must be an integer between $MinimumPort and $MaximumPort. No shortcut was created."
    }

    $repositoryRoot = Get-RepositoryRoot
    Test-RepositoryLayout -RepositoryRoot $repositoryRoot
    $desktopPath = Get-DesktopPath
    New-JarvisDesktopShortcut -RepositoryRoot $repositoryRoot -DesktopPath $desktopPath -DisableBrowser $NoBrowser.IsPresent -SelectedPort $Port
    exit 0
}
catch {
    Write-Failure 'The shortcut creator could not complete. No shortcut was confirmed.'
}
