@echo off
setlocal
set "REPO_ROOT=%~dp0"

pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo Unable to use the Jarvis repository directory.
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%scripts\remove_jarvis_shortcut.ps1" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
