#!/bin/bash
# 本地构建脚本 - 用于在发布前本地测试

echo "=================================="
echo "杭州爬虫本地构建脚本"
echo "=================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"

# 检查并安装依赖
echo ""
echo "📦 安装依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# 清理旧的构建文件
echo ""
echo "🧹 清理旧文件..."
rm -rf build dist *.spec

# 构建
echo ""
echo "🔨 开始构建..."

# 检测系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        OUTPUT_NAME="hangzhou-macos-arm64"
    else
        OUTPUT_NAME="hangzhou-macos-intel"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    OUTPUT_NAME="hangzhou-linux"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

pyinstaller --onefile --name "$OUTPUT_NAME" hangzhou.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 构建成功！"
    echo "📍 可执行文件位置: ./dist/$OUTPUT_NAME"
    echo ""
    echo "测试运行："
    echo "  ./dist/$OUTPUT_NAME"
else
    echo ""
    echo "❌ 构建失败"
    exit 1
fi
