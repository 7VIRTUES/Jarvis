@echo off
setlocal
set "REPO_ROOT=%~dp0"

pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo Unable to use the Jarvis repository directory.
    exit /b 1
)

py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    py -3 "%REPO_ROOT%scripts\jarvis_launcher.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

python -c "import sys" >nul 2>&1
if not errorlevel 1 (
    python "%REPO_ROOT%scripts\jarvis_launcher.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

echo Python 3.10 or newer is required to run Jarvis. Install Python, then run this launcher again.
popd
exit /b 1
