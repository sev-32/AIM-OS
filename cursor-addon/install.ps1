# AIM-OS Cursor Add-on Installation Script
# This script installs the AIM-OS Cursor add-on for VS Code

Write-Host "Installing AIM-OS Cursor Add-on..." -ForegroundColor Green

# Check if VS Code is installed
$vscodePath = Get-Command code -ErrorAction SilentlyContinue
if (-not $vscodePath) {
    Write-Host "VS Code not found. Please install VS Code first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
$nodePath = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodePath) {
    Write-Host "Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

# Compile TypeScript
Write-Host "Compiling TypeScript..." -ForegroundColor Yellow
npm run compile

# Package the extension
Write-Host "Packaging extension..." -ForegroundColor Yellow
npx vsce package

# Install the extension
Write-Host "Installing extension..." -ForegroundColor Yellow
$packageFile = Get-ChildItem -Name "*.vsix" | Select-Object -First 1
if ($packageFile) {
    code --install-extension $packageFile
    Write-Host "Extension installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Package file not found. Please check the compilation." -ForegroundColor Red
    exit 1
}

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Please restart VS Code to activate the extension." -ForegroundColor Yellow
