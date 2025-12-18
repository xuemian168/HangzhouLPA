#!/bin/bash
# 杭州规划爬虫套件本地构建脚本

echo "================================================"
echo "      杭州规划爬虫套件本地构建脚本"
echo "================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python 3，请先安装 Python"
    exit 1
fi

echo "[信息] Python 版本: $(python3 --version)"

# 检查并安装依赖
echo ""
echo "[步骤 1/3] 安装依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

# 清理旧的构建文件
echo ""
echo "[步骤 2/3] 清理旧文件..."
rm -rf build dist *.spec

# 检测系统
echo ""
echo "[步骤 3/3] 开始构建..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        SUFFIX="macos-arm64"
        echo "[信息] 检测到 macOS (Apple Silicon)"
    else
        SUFFIX="macos-intel"
        echo "[信息] 检测到 macOS (Intel)"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    SUFFIX="linux"
    echo "[信息] 检测到 Linux"
else
    echo "[错误] 不支持的操作系统: $OSTYPE"
    exit 1
fi

# 构建杭州爬虫
echo ""
echo "[构建] hangzhou-$SUFFIX..."
pyinstaller --onefile --name "hangzhou-$SUFFIX" hangzhou.py

if [ $? -ne 0 ]; then
    echo "[错误] 杭州爬虫构建失败"
    exit 1
fi

# 构建余杭爬虫
echo ""
echo "[构建] yuhang-$SUFFIX..."
pyinstaller --onefile --name "yuhang-$SUFFIX" yuhang.py

if [ $? -ne 0 ]; then
    echo "[错误] 余杭爬虫构建失败"
    exit 1
fi

# 设置可执行权限
chmod +x ./dist/hangzhou-$SUFFIX
chmod +x ./dist/yuhang-$SUFFIX

echo ""
echo "================================================"
echo "                 构建成功！"
echo "================================================"
echo ""
echo "可执行文件位置："
echo "  - ./dist/hangzhou-$SUFFIX"
echo "  - ./dist/yuhang-$SUFFIX"
echo ""
echo "测试运行："
echo "  ./dist/hangzhou-$SUFFIX"
echo "  ./dist/yuhang-$SUFFIX"
echo ""
