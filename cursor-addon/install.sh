#!/bin/bash

# AIM-OS Cursor Add-on Installation Script
# This script installs the AIM-OS Cursor add-on for VS Code

echo "Installing AIM-OS Cursor Add-on..."

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "VS Code not found. Please install VS Code first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Compile TypeScript
echo "Compiling TypeScript..."
npm run compile

# Package the extension
echo "Packaging extension..."
npx vsce package

# Install the extension
echo "Installing extension..."
PACKAGE_FILE=$(ls *.vsix | head -n 1)
if [ -n "$PACKAGE_FILE" ]; then
    code --install-extension "$PACKAGE_FILE"
    echo "Extension installed successfully!"
else
    echo "Package file not found. Please check the compilation."
    exit 1
fi

echo "Installation complete!"
echo "Please restart VS Code to activate the extension."
