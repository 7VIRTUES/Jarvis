[CmdletBinding()]
param(
    [string]$DesktopPath,
    [string]$StartMenuProgramsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Failure {
    param([Parameter(Mandatory = $true)][string]$Message)

    [Console]::Error.WriteLine($Message)
    exit 1
}

function Resolve-DesktopDirectory {
    param([string]$CustomPath)

    if (-not [string]::IsNullOrWhiteSpace($CustomPath)) {
        if (Test-Path -LiteralPath $CustomPath -PathType Container) {
            return (Resolve-Path -LiteralPath $CustomPath).Path
        }
        return $CustomPath
    }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if ([string]::IsNullOrWhiteSpace($desktop) -or -not (Test-Path -LiteralPath $desktop -PathType Container)) {
        return $null
    }
    return (Resolve-Path -LiteralPath $desktop).Path
}

function Resolve-StartMenuProgramsDirectory {
    param([string]$CustomPath)

    if (-not [string]::IsNullOrWhiteSpace($CustomPath)) {
        if (Test-Path -LiteralPath $CustomPath -PathType Container) {
            return (Resolve-Path -LiteralPath $CustomPath).Path
        }
        return $CustomPath
    }

    $programs = [Environment]::GetFolderPath([Environment+SpecialFolder]::Programs)
    if ([string]::IsNullOrWhiteSpace($programs)) {
        $appData = [Environment]::GetFolderPath([Environment+SpecialFolder]::ApplicationData)
        if (-not [string]::IsNullOrWhiteSpace($appData)) {
            $programs = Join-Path -Path $appData -ChildPath 'Microsoft\Windows\Start Menu\Programs'
        }
    }
    if ([string]::IsNullOrWhiteSpace($programs) -or -not (Test-Path -LiteralPath $programs -PathType Container)) {
        return $null
    }
    return (Resolve-Path -LiteralPath $programs).Path
}

try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        Write-Failure 'This shortcut uninstaller is Windows-only.'
    }

    $removed = @()

    # 1. Desktop shortcut(s)
    $desktopDir = Resolve-DesktopDirectory -CustomPath $DesktopPath
    if ($desktopDir -and (Test-Path -LiteralPath $desktopDir -PathType Container)) {
        foreach ($name in @('Jarvis.lnk', 'Jarvis PC Local.lnk')) {
            $candidate = Join-Path -Path $desktopDir -ChildPath $name
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                Remove-Item -LiteralPath $candidate -Force
                $removed += $candidate
            }
        }
    }

    # 2. Start Menu shortcut(s)
    $programsDir = Resolve-StartMenuProgramsDirectory -CustomPath $StartMenuProgramsPath
    if ($programsDir -and (Test-Path -LiteralPath $programsDir -PathType Container)) {
        $jarvisFolder = Join-Path -Path $programsDir -ChildPath 'Jarvis'
        if (Test-Path -LiteralPath $jarvisFolder -PathType Container) {
            foreach ($name in @('Jarvis.lnk', 'Jarvis PC Local.lnk')) {
                $candidate = Join-Path -Path $jarvisFolder -ChildPath $name
                if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                    Remove-Item -LiteralPath $candidate -Force
                    $removed += $candidate
                }
            }
            # Clean up folder if empty
            $remaining = @(Get-ChildItem -LiteralPath $jarvisFolder -Force)
            if ($remaining.Count -eq 0) {
                Remove-Item -LiteralPath $jarvisFolder -Force
            }
        }
        # Also check root of programs if shortcut was placed directly
        $directCandidate = Join-Path -Path $programsDir -ChildPath 'Jarvis.lnk'
        if (Test-Path -LiteralPath $directCandidate -PathType Leaf) {
            Remove-Item -LiteralPath $directCandidate -Force
            $removed += $directCandidate
        }
    }

    if ($removed.Count -gt 0) {
        Write-Output 'Jarvis shortcuts removed successfully.'
        Write-Output ''
        Write-Output 'Removed:'
        foreach ($path in $removed) {
            Write-Output "  $path"
        }
    }
    else {
        Write-Output 'No Jarvis shortcuts were found to remove.'
    }
    exit 0
}
catch {
    Write-Failure "The shortcut uninstaller could not complete: $_"
}
