# PowerShell script to push Analysis Tool to Hugging Face Spaces
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Pushing Analysis Tool to Hugging Face Spaces" -ForegroundColor Cyan
Write-Host "  Target: https://huggingface.co/spaces/naruto-sasuko/analysis-tool-saas" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$gitCmd = "$env:LOCALAPPDATA\Programs\Git\cmd"
$gitBin = "$env:LOCALAPPDATA\Programs\Git\bin"
if ($env:Path -notlike "*$gitCmd*") {
    $env:Path = "$gitCmd;$gitBin;$env:Path"
}

# Ensure Hugging Face Space remote is configured
$spaceUrl = "https://huggingface.co/spaces/naruto-sasuko/analysis-tool-saas"
$existingRemote = git remote | Where-Object { $_ -eq "space" }
if (-not $existingRemote) {
    Write-Host "Configuring 'space' remote..." -ForegroundColor Yellow
    git remote add space $spaceUrl
}

$token = $env:HF_TOKEN
if (-not $token) {
    Write-Host "`nTo push to Hugging Face, a Write Token is required." -ForegroundColor Yellow
    Write-Host "Get one at: https://huggingface.co/settings/tokens (Role: Write)`n" -ForegroundColor Gray
    $tokenInput = Read-Host "Enter Hugging Face Token (or press Enter to use Git Credential Manager)"
    if ($tokenInput) {
        $token = $tokenInput.Trim()
    }
}

if ($token) {
    Write-Host "`nPushing to Hugging Face Spaces using provided token..." -ForegroundColor Cyan
    $pushUrl = "https://naruto-sasuko:$token@huggingface.co/spaces/naruto-sasuko/analysis-tool-saas"
    git push --force -u $pushUrl main
} else {
    Write-Host "`nPushing to Hugging Face Spaces using Git credentials..." -ForegroundColor Cyan
    git push --force -u space main
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS! Deployed to Hugging Face Space: $spaceUrl" -ForegroundColor Green
} else {
    Write-Host "`nPush failed. Please ensure your token has WRITE permissions on naruto-sasuko/analysis-tool-saas" -ForegroundColor Red
}
