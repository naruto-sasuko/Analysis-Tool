@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo   Pushing Analysis Tool to Hugging Face Spaces
echo   Target: https://huggingface.co/spaces/naruto-sasuko/analysis-tool-saas
echo ========================================================

set "PATH=%LOCALAPPDATA%\Programs\Git\cmd;%LOCALAPPDATA%\Programs\Git\bin;%PATH%"

git remote | findstr /C:"space" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [1/3] Adding Hugging Face 'space' remote...
    git remote add space https://huggingface.co/spaces/naruto-sasuko/analysis-tool-saas
)

echo [2/3] Checking Hugging Face Token...
set "TOKEN=%HF_TOKEN%"
if "%TOKEN%"=="" (
    echo.
    echo Please enter your Hugging Face Token (Role: Write).
    echo Create one at: https://huggingface.co/settings/tokens
    set /p "TOKEN=Hugging Face Token: "
)

echo.
echo [3/3] Pushing to Hugging Face Space...
if not "!TOKEN!"=="" (
    git push --force https://naruto-sasuko:!TOKEN!@huggingface.co/spaces/naruto-sasuko/analysis-tool-saas main
) else (
    git push --force space main
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Analysis Tool pushed to Hugging Face Spaces:
    echo   https://huggingface.co/spaces/naruto-sasuko/analysis-tool-saas
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   Push failed. Ensure your Hugging Face token has
    echo   WRITE permissions for naruto-sasuko/analysis-tool-saas
    echo ========================================================
)

pause
