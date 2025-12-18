@echo off
REM Windows 本地构建脚本

echo ==================================
echo 杭州爬虫本地构建脚本 (Windows)
echo ==================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt
pip install pyinstaller
echo.

REM 清理旧文件
echo 🧹 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

REM 构建
echo 🔨 开始构建...
pyinstaller --onefile --name hangzhou-windows hangzhou.py

if errorlevel 1 (
    echo.
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo.
echo ✅ 构建成功！
echo 📍 可执行文件位置: .\dist\hangzhou-windows.exe
echo.
echo 测试运行：
echo   .\dist\hangzhou-windows.exe
echo.
pause
