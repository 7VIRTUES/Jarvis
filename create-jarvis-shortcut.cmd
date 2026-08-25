@echo off
setlocal
set "REPO_ROOT=%~dp0"
call "%REPO_ROOT%install-jarvis-shortcut.cmd" %*
exit /b %ERRORLEVEL%
