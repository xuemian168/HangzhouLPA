# 杭州市规划和自然资源局项目爬虫

[![GitHub release](https://img.shields.io/github/v/release/yourusername/HangzhouLPA-1)](https://github.com/yourusername/HangzhouLPA-1/releases)
[![License](https://img.shields.io/github/license/yourusername/HangzhouLPA-1)](LICENSE)

自动抓取杭州市规划和自然资源局的建设项目批前公示信息和设计图。

## ✨ 特性

- 🚀 自动获取最新项目列表
- 📥 批量下载项目设计图
- 📊 生成 CSV 格式的项目数据
- 🎯 支持多平台（Windows、macOS、Linux）
- 🔒 无需额外配置，开箱即用
- 🧩 遵循 SOLID、DRY、KISS 设计原则

## 📦 下载

访问 [Releases 页面](https://github.com/yourusername/HangzhouLPA-1/releases) 下载最新版本：

- **Windows**: `hangzhou-windows.exe`
- **macOS (Intel)**: `hangzhou-macos-intel`
- **macOS (Apple Silicon)**: `hangzhou-macos-arm64`
- **Linux**: `hangzhou-linux`

## 🚀 快速开始

### 使用可执行文件（推荐）

1. 下载对应系统的可执行文件
2. 双击运行（Windows）或在终端中运行（macOS/Linux）

**macOS/Linux**:
```bash
# 添加执行权限
chmod +x hangzhou-macos-arm64

# 运行
./hangzhou-macos-arm64
```

**Windows**:
直接双击 `hangzhou-windows.exe`

### 使用 Python 源码

**前置要求**:
- Python 3.8+
- pip

**安装依赖**:
```bash
pip install -r requirements.txt
```

**运行**:
```bash
python hangzhou.py
```

## 📖 使用说明

程序运行后会自动：

1. ✓ 获取最新的项目列表
2. ✓ 显示找到的项目数量
3. ✓ 逐个下载设计图到 `./jpg` 目录
4. ✓ 生成包含项目信息的 CSV 文件

**输出文件**:
- `./jpg/项目名称.jpg` - 下载的设计图
- `公示图_时间戳.csv` - 项目数据（项目名称、URL、设计图地址）

## 🛠️ 开发

### 本地构建

**macOS/Linux**:
```bash
chmod +x build.sh
./build.sh
```

**Windows**:
```cmd
build.bat
```

### 项目结构

```
├── hangzhou.py          # 主程序（优化版）
├── yuhang.py           # 余杭区规划局脚本
├── requirements.txt    # Python 依赖
├── build.sh           # Unix 构建脚本
├── build.bat          # Windows 构建脚本
├── RELEASE.md         # 发布指南
└── .github/
    └── workflows/
        └── release.yml # GitHub Actions 工作流
```

### 代码架构

遵循 SOLID 原则的面向对象设计：

- `Config` - 配置管理
- `HttpClient` - HTTP 请求封装
- `ProjectParser` - HTML/JSON 解析
- `ProjectScraper` - 爬取流程协调
- `ImageDownloader` - 图片下载
- `CSVExporter` - 数据导出
- `Application` - 应用主控制器

## 📝 更新日志

### v1.0.0 (2025-12-18)
- ✅ 完全重构代码，遵循 SOLID、DRY、KISS 原则
- ✅ 适配新版网站 API
- ✅ 优化错误处理和用户反馈
- ✅ 添加类型注解提升代码质量
- ✅ 支持多平台自动构建发布

## ⚠️ 重要免责声明

**本工具仅供学习、研究和实验目的使用，请严格遵守以下条款：**

1. **24小时删除要求**: 下载的数据和程序必须在24小时内删除，不得长期保存或用于其他用途
2. **仅供学习研究**: 本工具仅用于技术学习、研究和实验，不得用于商业用途或违法活动
3. **遵守法律法规**: 使用本工具即表示您同意遵守所在地区的法律法规及目标网站的服务条款
4. **风险自负**: 使用本工具产生的任何法律责任和风险由使用者自行承担，开发者不承担任何责任
5. **尊重版权**: 请尊重数据版权和隐私，不得擅自传播、出售或用于其他非法目的

**使用本工具即表示您已阅读并同意上述免责声明**

详细免责条款请参阅 [DISCLAIMER.md](DISCLAIMER.md)

## ⚠️ 注意事项

1. **合法使用**: 仅用于学习和合法用途
2. **频率限制**: 程序内置 0.5 秒延迟，避免频繁请求
3. **网络要求**: 需要稳定的网络连接
4. **存储空间**: 确保有足够空间存储设计图（每张约 5-40MB）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

## 👤 作者

© XueMian168.Com

---

**免责声明**: 本工具仅供学习交流使用，请遵守相关网站的服务条款和 robots.txt 规则。
