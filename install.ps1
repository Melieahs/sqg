# install.ps1 — Windows 安装脚本 for sqg

Write-Host "🔧 Starting sqg installation for Windows..."

$installDir = "$env:USERPROFILE\sqg\bin"
$sqgUrl = "https://raw.githubusercontent.com/Melieahs/sqg/main/sqg"
$sqgPath = "$installDir\sqg"

# Step 1: Create install directory
if (!(Test-Path $installDir)) {
    Write-Host "📂 Creating install directory at $installDir"
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

# Step 2: Download sqg script
Write-Host "📥 Downloading sqg script..."
Invoke-WebRequest -Uri $sqgUrl -OutFile $sqgPath

# Step 3: Make it executable (for Git Bash)
Write-Host "🔒 Setting executable permissions (if using Git Bash)..."
bash -c "chmod +x '$sqgPath'" 2>$null

# Step 4: Check Git installation
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "🚀 Git not found. Opening Git installer page..."
    Start-Process "https://git-scm.com/download/win"
    Write-Host "❗ Please install Git manually, then re-run this script."
    exit
} else {
    Write-Host "✅ Git is installed."
}

# Step 5: Prompt to add to PATH
Write-Host "`n📌 To finish setup:"
Write-Host "👉 Add '$installDir' to your system PATH:"
Write-Host "   Control Panel → System → Environment Variables → User PATH → Add: $installDir"
Write-Host "`n💡 Then open Git Bash and run: sqg get hello"

Write-Host "`n🎉 Installation complete!"
