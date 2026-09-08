# PowerShell script to push Analysis Tool to GitHub
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Pushing Analysis Tool to GitHub" -ForegroundColor Cyan
Write-Host "  Target: https://github.com/naruto-sasuko/Analysis-Tool" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$gitCmd = "$env:LOCALAPPDATA\Programs\Git\cmd"
$gitBin = "$env:LOCALAPPDATA\Programs\Git\bin"
if ($env:Path -notlike "*$gitCmd*") {
    $env:Path = "$gitCmd;$gitBin;$env:Path"
}

git status -s
git remote -v

Write-Host "`nExecuting: git push -u origin main..." -ForegroundColor Yellow
git push -u origin main
