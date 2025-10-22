# install.ps1 — 一键安装 sqg for Windows

Write-Host "🔧 正在安装 sqg 工具..."

$installDir = "$env:USERPROFILE\sqg\bin"
$sqgUrl = "https://raw.githubusercontent.com/Melieahs/sqg/main/sqg"
$sqgPath = "$installDir\sqg"

# Step 1: 创建安装目录
if (!(Test-Path $installDir)) {
    Write-Host "📂 创建目录: $installDir"
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

# Step 2: 下载 sqg 脚本
Write-Host "📥 下载 sqg 脚本..."
Invoke-WebRequest -Uri $sqgUrl -OutFile $sqgPath

# Step 3: 检查 Git 是否安装
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "🚀 未检测到 Git，正在打开安装页面..."
    Start-Process "https://git-scm.com/download/win"
    [System.Windows.Forms.MessageBox]::Show("请安装 Git 并重新运行此脚本。", "Git 未安装", "OK", "Warning")
    exit
} else {
    Write-Host "✅ Git 已安装。"
}

# Step 4: 提示添加 PATH
$pathMessage = @"
请将以下目录添加到系统 PATH：
  $installDir

方法：
  控制面板 → 系统 → 环境变量 → 用户 PATH → 添加上述路径

完成后，请打开 Git Bash 并运行：
  sqg get hello
"@
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show($pathMessage, "📌 添加 PATH", "OK", "Information")

Write-Host "`n🎉 安装完成！"
Write-Host "👉 请打开 Git Bash 并运行：sqg get hello"
