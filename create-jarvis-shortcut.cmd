@echo off
setlocal
set "REPO_ROOT=%~dp0"

pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo Unable to use the Jarvis repository directory.
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -Command "exit 0" >nul 2>&1
if not errorlevel 1 (
    powershell.exe -NoLogo -NoProfile -File "%REPO_ROOT%scripts\create_jarvis_shortcut.ps1" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

pwsh.exe -NoLogo -NoProfile -Command "exit 0" >nul 2>&1
if not errorlevel 1 (
    pwsh.exe -NoLogo -NoProfile -File "%REPO_ROOT%scripts\create_jarvis_shortcut.ps1" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

echo Windows PowerShell or PowerShell 7 is required only to create the desktop shortcut.
echo Jarvis itself can still be started with .\jarvis.
popd
exit /b 1
