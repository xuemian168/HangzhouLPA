@echo off
REM 杭州规划爬虫套件本地构建脚本 (Windows)

echo ================================================
echo      杭州规划爬虫套件本地构建脚本
echo ================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo [信息] Python 已安装
echo.

REM 安装依赖
echo [步骤 1/3] 安装依赖...
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo.

REM 清理旧文件
echo [步骤 2/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

REM 构建
echo [步骤 3/3] 开始构建...
echo.

echo [构建] hangzhou-windows.exe...
pyinstaller --onefile --name hangzhou-windows hangzhou.py
if errorlevel 1 (
    echo [错误] 杭州爬虫构建失败
    pause
    exit /b 1
)
echo.

echo [构建] yuhang-windows.exe...
pyinstaller --onefile --name yuhang-windows yuhang.py
if errorlevel 1 (
    echo [错误] 余杭爬虫构建失败
    pause
    exit /b 1
)

echo.
echo ================================================
echo                 构建成功！
echo ================================================
echo.
echo 可执行文件位置：
echo   - .\dist\hangzhou-windows.exe
echo   - .\dist\yuhang-windows.exe
echo.
echo 测试运行：
echo   .\dist\hangzhou-windows.exe
echo   .\dist\yuhang-windows.exe
echo.
pause
