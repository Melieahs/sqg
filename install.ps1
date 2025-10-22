# install.ps1 — 一键安装 sqg.exe 到系统 PATH

$exeName = "sqg.exe"
$installDir = "$env:USERPROFILE\sqg\bin"
$exeUrl = "https://github.com/Melieahs/sqg/releases/latest/download/sqg.exe"
$exePath = Join-Path $installDir $exeName

Write-Host "🔧 正在安装 sqg 到 $installDir..."

# Step 1: 创建安装目录
if (!(Test-Path $installDir)) {
    Write-Host "📂 创建目录: $installDir"
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

# Step 2: 下载 sqg.exe
Write-Host "📥 正在从 GitHub 下载 sqg.exe..."
try {
    Invoke-WebRequest -Uri $exeUrl -OutFile $exePath -UseBasicParsing
    Write-Host "✅ 下载完成: $exePath"
} catch {
    Write-Host "❌ 下载失败，请检查网络或链接是否有效"
    exit 1
}

# Step 3: 添加安装目录到用户 PATH（如果尚未添加）
$existingPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($existingPath -notlike "*$installDir*") {
    Write-Host "📌 添加安装目录到用户 PATH..."
    $newPath = "$existingPath;$installDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✅ 已添加到 PATH"
} else {
    Write-Host "ℹ️ 安装目录已在 PATH 中，无需重复添加"
}

# Step 4: 提示用户重启终端
Write-Host "`n🎉 安装完成！"
Write-Host "👉 请关闭并重新打开 PowerShell 或 CMD，然后运行：sqg get hello"
