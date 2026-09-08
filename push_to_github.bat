@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo   Pushing Analysis Tool to GitHub
echo   Target: https://github.com/naruto-sasuko/Analysis-Tool
echo ========================================================

REM Add installed Git and GH to Path for this session
set "PATH=%LOCALAPPDATA%\Programs\Git\cmd;%LOCALAPPDATA%\Programs\Git\bin;%PATH%"
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\GitHub.cli*") do (
    set "PATH=%%D\bin;%%D;!PATH!"
)

echo [1/3] Checking Git status...
git status -s

echo [2/3] Checking Remote configuration...
git remote -v

echo [3/3] Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Analysis Tool pushed to GitHub:
    echo   https://github.com/naruto-sasuko/Analysis-Tool
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   NOTE: If you see 'Repository not found' or authentication error:
    echo   1. Make sure you created the repo 'Analysis-Tool' at:
    echo      https://github.com/new
    echo   2. Run 'gh auth login' in your terminal or enter your GitHub credentials
    echo      when the Windows prompt appears.
    echo ========================================================
)

pause
