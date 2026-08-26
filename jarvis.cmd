@echo off
setlocal
set "REPO_ROOT=%~dp0"

pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo Unable to use the Jarvis repository directory.
    exit /b 1
)

:: 1. Check existing .venv
if exist "%REPO_ROOT%.venv\Scripts\python.exe" (
    "%REPO_ROOT%.venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        "%REPO_ROOT%.venv\Scripts\python.exe" "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
        set "EXIT_CODE=%ERRORLEVEL%"
        popd
        exit /b %EXIT_CODE%
    )
)

:: 2. Check py -3
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 (
    py -3 "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

:: 3. Check python on PATH
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 (
    python "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

:: 4. Check user local app data Python installations
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

:: 5. Python not found: attempt installation via winget
where winget >nul 2>&1
if not errorlevel 1 (
    echo ==================================================
    echo Python 3.10+ was not found on this system.
    echo Installing official Python 3.13 via Windows Package Manager (winget)...
    echo ==================================================
    winget install --id Python.Python.3.13 --scope user --exact --accept-package-agreements --accept-source-agreements
    
    :: Re-check after installation
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
        set "EXIT_CODE=%ERRORLEVEL%"
        popd
        exit /b %EXIT_CODE%
    )
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        python "%REPO_ROOT%scripts\jarvis_bootstrap.py" %*
        set "EXIT_CODE=%ERRORLEVEL%"
        popd
        exit /b %EXIT_CODE%
    )
)

echo ==================================================
echo Setup Blocked: Python 3.10 or newer is required to run Jarvis.
echo Please install Python from: https://www.python.org/downloads/windows/
echo Make sure to check "Add python.exe to PATH" during setup.
echo ==================================================
popd
exit /b 1
