<#
Simple helper to create a GitHub repo and push the current folder.
You must provide a GitHub Personal Access Token (PAT) with 'repo' scope.

Usage: Run in PowerShell:
  .\push_to_github.ps1

This script will ask for a repo name and PAT, create a repo under your account,
add a remote `origin`, commit all files and push to GitHub's main branch.
#>

Param()

function Read-Secret($prompt) {
    Write-Host $prompt -NoNewline
    $sec = Read-Host -AsSecureString
    return [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
}

$repo = Read-Host 'GitHub repository name to create (e.g. my-psycho-app)'
if (-not $repo) { Write-Error 'Repository name required'; exit 1 }

$pat = Read-Secret 'Enter your GitHub Personal Access Token (PAT): '
if (-not $pat) { Write-Error 'PAT required'; exit 1 }

Write-Host "Creating repo $repo using your token..."

$body = @{ name = $repo } | ConvertTo-Json

$resp = Invoke-RestMethod -Method Post -Uri https://api.github.com/user/repos -Headers @{ Authorization = "token $pat"; 'User-Agent'='ps' } -Body $body -ContentType 'application/json'
if (-not $resp) { Write-Error 'Failed to create repo'; exit 1 }

$cloneUrl = $resp.clone_url
Write-Host "Repo created: $cloneUrl"

git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin $cloneUrl
git push -u origin main

Write-Host 'Push complete. The GitHub Actions workflow should run and build the APK. Check Actions tab on GitHub.'
