# 杭州规划爬虫套件

[![GitHub release](https://img.shields.io/github/v/release/yourusername/HangzhouLPA-1)](https://github.com/yourusername/HangzhouLPA-1/releases)
[![License](https://img.shields.io/github/license/yourusername/HangzhouLPA-1)](LICENSE)

自动抓取杭州市规划和自然资源局及余杭区规划局的建设项目批前公示信息和设计图。

## 项目简介

本套件包含两个独立的爬虫工具：

### 1. 杭州市规划局爬虫 (hangzhou.py)
- 自动获取杭州市规划和自然资源局的最新项目列表
- 批量下载项目设计图
- 生成 CSV 格式的项目数据
- 支持多平台运行

### 2. 余杭区规划局爬虫 (yuhang.py) - v2.0 全新重构
- 自动下载余杭区规划局公开文件
- 按项目名智能整理文件夹结构
- 支持 ZIP/RAR 自动解压
- tqdm 进度条实时显示
- 网络异常自动重试机制
- 详细的操作日志记录
- 保存项目元信息（JSON）

## 特性

### 杭州市爬虫
- 自动获取最新项目列表
- 批量下载项目设计图
- 生成 CSV 格式的项目数据
- 支持多平台（Windows、macOS、Linux）
- 无需额外配置，开箱即用
- 遵循 SOLID、DRY、KISS 设计原则

### 余杭区爬虫
- 自动下载并按项目名整理文件
- 支持 ZIP/RAR 自动解压（需系统安装 UnRAR）
- 进度条实时显示下载和解压进度
- 网络异常自动重试（最多3次）
- 详细日志记录到文件
- 生成项目元信息 JSON 文件
- 统一 UTF-8 编码，避免乱码

## 下载

访问 [Releases 页面](https://github.com/yourusername/HangzhouLPA-1/releases) 下载最新版本：

### 杭州市规划局爬虫
- **Windows**: `hangzhou-windows.exe`
- **macOS**: `hangzhou-macos-arm64` (仅支持 Apple Silicon M1/M2/M3)
- **Linux**: `hangzhou-linux`

### 余杭区规划局爬虫
- **Windows**: `yuhang-windows.exe`
- **macOS**: `yuhang-macos-arm64` (仅支持 Apple Silicon M1/M2/M3)
- **Linux**: `yuhang-linux`

**注意**: Intel Mac 用户请使用 Python 源码运行。

## 快速开始

### 使用可执行文件（推荐）

#### 杭州市爬虫

**macOS/Linux**:
```bash
# 添加执行权限
chmod +x hangzhou-macos-arm64

# 运行
./hangzhou-macos-arm64
```

**Windows**:
直接双击 `hangzhou-windows.exe`

#### 余杭区爬虫

**macOS/Linux**:
```bash
# 添加执行权限
chmod +x yuhang-macos-arm64

# 运行
./yuhang-macos-arm64
```

**Windows**:
直接双击 `yuhang-windows.exe`

### 使用 Python 源码

**前置要求**:
- Python 3.8+
- pip

**安装依赖**:
```bash
pip install -r requirements.txt
```

**运行杭州市爬虫**:
```bash
python hangzhou.py
```

**运行余杭区爬虫**:
```bash
python yuhang.py
```

## 使用说明

### 杭州市爬虫

程序运行后会自动：

1. 获取最新的项目列表
2. 显示找到的项目数量
3. 逐个下载设计图到 `./jpg` 目录
4. 生成包含项目信息的 CSV 文件

**输出文件**:
- `./jpg/项目名称.jpg` - 下载的设计图
- `公示图_时间戳.csv` - 项目数据（项目名称、URL、设计图地址）

### 余杭区爬虫

程序运行后：

1. 选择模式：
   - **模式 1**: 自动批量下载 1-5 页的所有项目
   - **模式 2**: 手动指定页码下载（支持多页，如：1,2,3）

2. 自动处理：
   - 获取项目列表（显示进度）
   - 下载文件到各项目的 `raw/` 目录
   - 自动解压到 `documents/` 目录
   - 保存项目元信息到 `metadata.json`

**输出结构**:
```
yuhang_projects/
├── 项目名称1/
│   ├── raw/              # 原始下载文件
│   │   ├── 项目名称1_1.zip
│   │   └── 项目名称1_2.pdf
│   ├── documents/        # 解压后的文档
│   │   ├── 文件1.dwg
│   │   └── 文件2.pdf
│   └── metadata.json     # 项目元信息
├── 项目名称2/
└── ...

logs/                     # 日志目录
└── yuhang_crawler_YYYYMMDD_HHMMSS.log
```

## 依赖说明

### 通用依赖
- requests - HTTP 请求库
- urllib3 - HTTP 连接池

### 余杭区爬虫额外依赖
- tqdm - 进度条显示
- rarfile - RAR 文件解压支持

### RAR 解压要求（仅余杭区爬虫）

余杭区爬虫的 RAR 解压功能需要系统安装 UnRAR：

**macOS**:
```bash
brew install unrar
```

**Ubuntu/Debian**:
```bash
sudo apt-get install unrar
```

**Windows**:
安装 WinRAR 或 UnRAR

## 开发

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

构建脚本会自动构建两个爬虫的可执行文件。

### 项目结构

```
├── hangzhou.py          # 杭州市规划局爬虫
├── yuhang.py           # 余杭区规划局爬虫
├── requirements.txt    # Python 依赖
├── build.sh           # Unix 构建脚本
├── build.bat          # Windows 构建脚本
├── RELEASE.md         # 发布指南
├── yuhang_README.md   # 余杭爬虫详细文档
└── .github/
    └── workflows/
        └── release.yml # GitHub Actions 工作流
```

### 代码架构

#### 杭州市爬虫
遵循 SOLID 原则的面向对象设计：

- `Config` - 配置管理
- `HttpClient` - HTTP 请求封装
- `ProjectParser` - HTML/JSON 解析
- `ProjectScraper` - 爬取流程协调
- `ImageDownloader` - 图片下载
- `CSVExporter` - 数据导出
- `Application` - 应用主控制器

#### 余杭区爬虫
模块化函数设计，应用 SOLID、DRY、KISS 原则：

- `CONFIG` - 集中配置管理
- `setup_logging()` - 日志系统
- `fetch_project_list()` - 项目列表获取
- `download_file()` - 文件下载（带重试）
- `extract_archive()` - 统一解压接口
- `process_project()` - 项目处理流程
- `auto_mode()` / `manual_mode()` - 用户界面

## 更新日志

### v2.0.0 (2025-01-18) - 余杭区爬虫全新重构
- 修复文件覆盖严重 Bug
- 新增按项目智能整理功能
- 完善 RAR 解压支持
- 添加进度显示和日志系统
- 统一 UTF-8 编码
- 添加重试机制和错误处理
- 代码重构，消除 90% 重复代码

### v1.1.2 (2025-12-18) - 杭州市爬虫
- 修复无限分页 Bug
- 改进分页逻辑，添加去重
- 增强项目数据检索

### v1.0.0 (2025-12-18) - 杭州市爬虫
- 完全重构代码，遵循 SOLID、DRY、KISS 原则
- 适配新版网站 API
- 优化错误处理和用户反馈
- 添加类型注解提升代码质量
- 支持多平台自动构建发布

## 重要免责声明

**本工具仅供学习、研究和实验目的使用，请严格遵守以下条款：**

1. **24小时删除要求**: 下载的数据和程序必须在24小时内删除，不得长期保存或用于其他用途
2. **仅供学习研究**: 本工具仅用于技术学习、研究和实验，不得用于商业用途或违法活动
3. **遵守法律法规**: 使用本工具即表示您同意遵守所在地区的法律法规及目标网站的服务条款
4. **风险自负**: 使用本工具产生的任何法律责任和风险由使用者自行承担，开发者不承担任何责任
5. **尊重版权**: 请尊重数据版权和隐私，不得擅自传播、出售或用于其他非法目的

**使用本工具即表示您已阅读并同意上述免责声明**

详细免责条款请参阅 [DISCLAIMER.md](DISCLAIMER.md)

## 注意事项

1. **合法使用**: 仅用于学习和合法用途
2. **频率限制**: 程序内置延迟，避免频繁请求
3. **网络要求**: 需要稳定的网络连接
4. **存储空间**: 确保有足够空间存储设计图和文档

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

## 作者

© XueMian168.Com

---

**免责声明**: 本工具仅供学习交流使用，请遵守相关网站的服务条款和 robots.txt 规则。
