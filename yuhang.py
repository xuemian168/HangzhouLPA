#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
余杭区规划局文件爬虫
功能：自动下载、解压、整理规划文件
"""

import os
import re
import json
import time
import shutil
import logging
import zipfile
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import requests
from tqdm import tqdm

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False
    print("警告: rarfile 未安装，将跳过 RAR 文件解压。运行 'pip install rarfile' 安装。")


# ========== 配置管理 ==========

CONFIG = {
    'base_url': 'https://www.yuhang.gov.cn',
    'search_url': 'https://www.yuhang.gov.cn/module/xxgk/search.jsp',
    'list_url': 'http://www.yuhang.gov.cn/col/col1229191870/index.html?number=Y001C001',
    'infotype_id': 'Y001C001',
    'div_id': 'div1229106886',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Cookie': 'JSESSIONID=16C8B6FE3099D92E34BB4AD8DB1B489A;Path=/zwdt_public;HttpOnly',
        'Referer': 'https://www.yuhang.gov.cn/col/col1229191870/index.html?number=Y001C001',
        'Host': 'www.yuhang.gov.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"'
    },
    'output_dirs': {
        'projects': './yuhang_projects',  # 按项目组织的主目录
        'temp': './yuhang_temp',          # 临时文件目录
    },
    'encoding': 'utf-8',
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 2,
}


# ========== 日志配置 ==========

def setup_logging():
    """配置日志系统"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # 创建日志目录
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True)

    # 配置日志
    log_file = log_dir / f'yuhang_crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


logger = setup_logging()


# ========== 工具函数 ==========

def sanitize_filename(name: str, max_length: int = 200) -> str:
    """
    清理文件名中的非法字符

    Args:
        name: 原始文件名
        max_length: 最大长度限制

    Returns:
        清理后的文件名
    """
    # 移除非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    clean_name = re.sub(illegal_chars, '', name)

    # 移除首尾空格
    clean_name = clean_name.strip()

    # 限制长度
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length]

    return clean_name


def ensure_dir(path: Path) -> Path:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_metadata(project_dir: Path, metadata: Dict):
    """保存项目元信息"""
    metadata_file = project_dir / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


# ========== 网络请求函数 ==========

def create_session() -> requests.Session:
    """创建并配置 requests Session"""
    session = requests.Session()
    session.headers.update(CONFIG['headers'])
    return session


def download_with_retry(session: requests.Session, url: str,
                       max_retries: int = None) -> Optional[requests.Response]:
    """
    带重试机制的下载函数

    Args:
        session: requests.Session 对象
        url: 下载 URL
        max_retries: 最大重试次数

    Returns:
        Response 对象或 None（失败时）
    """
    if max_retries is None:
        max_retries = CONFIG['max_retries']

    for attempt in range(max_retries):
        try:
            requests.packages.urllib3.disable_warnings()
            response = session.get(url, timeout=CONFIG['timeout'], verify=False, allow_redirects=True)

            # 记录重定向信息
            if response.history:
                logger.debug(f"发生重定向: {url} -> {response.url}")

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            # 记录更详细的错误信息
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{e.__class__.__name__}: {e.response.status_code} - {e.response.reason}"
                if e.response.history:
                    redirect_chain = ' -> '.join([r.url for r in e.response.history])
                    error_msg += f" (重定向链: {redirect_chain} -> {e.response.url})"

            logger.warning(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {url[:100]}..., 错误: {error_msg}")

            if attempt < max_retries - 1:
                time.sleep(CONFIG['retry_delay'] ** attempt)  # 指数退避
            else:
                logger.error(f"下载彻底失败: {url[:100]}...")
                return None


# ========== 数据解析函数 ==========

def fetch_page_data(session: requests.Session, page: int) -> Optional[str]:
    """
    获取指定页面的 HTML 内容

    Args:
        session: requests.Session 对象
        page: 页码

    Returns:
        HTML 内容或 None
    """
    data = {
        'infotypeId': CONFIG['infotype_id'],
        'divid': CONFIG['div_id'],
        'currpage': str(page),
        'sortfield': ',compaltedate:0'
    }

    post_url = (
        f"{CONFIG['search_url']}?standardXxgk=1&isAllList=1&texttype=0&fbtime=-1"
        f"&vc_all=&vc_filenumber=&vc_title=&vc_number=&currpage={page}"
        f"&sortfield=,compaltedate:0"
    )

    try:
        response = session.post(post_url, data=data, timeout=CONFIG['timeout'])
        response.raise_for_status()
        return response.content.decode('utf-8')
    except Exception as e:
        logger.error(f"获取第 {page} 页数据失败: {e}")
        return None


def parse_project_list(html_content: str) -> List[Tuple[str, str]]:
    """
    解析 HTML 内容，提取项目名称和 URL

    Args:
        html_content: HTML 内容

    Returns:
        [(项目名称, 项目 URL)] 列表
    """
    pattern = r'<a title=\"([\d\D]*?)\" target=\"([\d\D]*?)\" href=\"([\d\D]*?)\">'
    matches = re.finditer(pattern, html_content, re.MULTILINE)

    projects = []
    for match in matches:
        project_name = match.group(1).strip()
        project_url = match.group(3).strip()
        projects.append((project_name, project_url))

    return projects


def fetch_project_list(session: requests.Session, pages: List[int]) -> List[Tuple[str, str]]:
    """
    获取多个页面的项目列表

    Args:
        session: requests.Session 对象
        pages: 页码列表

    Returns:
        [(项目名称, 项目 URL)] 列表
    """
    all_projects = []

    for page in tqdm(pages, desc="获取项目列表"):
        logger.info(f"正在获取第 {page} 页...")
        html_content = fetch_page_data(session, page)

        if html_content:
            projects = parse_project_list(html_content)
            all_projects.extend(projects)
            logger.info(f"第 {page} 页找到 {len(projects)} 个项目")
        else:
            logger.warning(f"第 {page} 页获取失败")

    return all_projects


# ========== 文件下载函数 ==========

def extract_file_urls(session: requests.Session, project_url: str) -> List[Tuple[str, str]]:
    """
    从项目页面提取文件下载链接

    Args:
        session: requests.Session 对象
        project_url: 项目页面 URL

    Returns:
        [(文件 URL, 文件后缀)] 列表
    """
    try:
        response = session.get(project_url, timeout=CONFIG['timeout'])
        response.raise_for_status()
        html_content = response.content.decode('utf-8')
    except Exception as e:
        logger.error(f"获取项目页面失败: {project_url}, 错误: {e}")
        return []

    # 修复：匹配完整的下载链接（包含文件扩展名）
    pattern = r'<a href=\"(\/module\/download[^\"]*?\.(zip|rar|pdf))\"'
    matches = re.finditer(pattern, html_content, re.MULTILINE | re.IGNORECASE)

    file_urls = []
    for match in matches:
        file_path = match.group(1)  # 完整路径（已包含扩展名）
        file_suffix = match.group(2).lower()  # 文件后缀
        file_url = f"{CONFIG['base_url']}{file_path}"
        file_urls.append((file_url, file_suffix))

    return file_urls


def download_file(session: requests.Session, url: str, save_path: Path) -> bool:
    """
    下载单个文件

    Args:
        session: requests.Session 对象
        url: 文件 URL
        save_path: 保存路径

    Returns:
        是否下载成功
    """
    response = download_with_retry(session, url)

    if response:
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"下载成功: {save_path.name}")
            return True
        except Exception as e:
            logger.error(f"保存文件失败: {save_path}, 错误: {e}")
            return False
    else:
        return False


# ========== 文件解压函数 ==========

def extract_archive(archive_path: Path, extract_to: Path) -> bool:
    """
    解压压缩文件（支持 ZIP 和 RAR）

    Args:
        archive_path: 压缩文件路径
        extract_to: 解压目标目录

    Returns:
        是否解压成功
    """
    ensure_dir(extract_to)

    try:
        if zipfile.is_zipfile(archive_path):
            # 解压 ZIP 文件
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # 检查是否有密码保护
                try:
                    zf.testzip()
                except RuntimeError as e:
                    if 'password' in str(e).lower():
                        logger.warning(f"ZIP 文件有密码保护，跳过: {archive_path.name}")
                        return False
                    raise

                # 解压所有文件
                for member in zf.namelist():
                    try:
                        zf.extract(member, extract_to)
                    except Exception as e:
                        logger.error(f"解压文件失败: {member}, 错误: {e}")

                logger.info(f"ZIP 解压成功: {archive_path.name}")
                return True

        elif RARFILE_AVAILABLE and rarfile.is_rarfile(archive_path):
            # 解压 RAR 文件
            try:
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extractall(extract_to)
                logger.info(f"RAR 解压成功: {archive_path.name}")
                return True
            except rarfile.PasswordRequired:
                logger.warning(f"RAR 文件有密码保护，跳过: {archive_path.name}")
                return False
            except Exception as e:
                logger.error(f"RAR 解压失败: {archive_path.name}, 错误: {e}")
                return False

        else:
            # 不是压缩文件，直接复制
            shutil.copy2(archive_path, extract_to / archive_path.name)
            logger.info(f"非压缩文件已复制: {archive_path.name}")
            return True

    except Exception as e:
        logger.error(f"处理文件失败: {archive_path.name}, 错误: {e}")
        return False


# ========== 项目处理函数 ==========

def process_project(session: requests.Session, project_name: str,
                   project_url: str, base_dir: Path) -> bool:
    """
    处理单个项目：下载文件、解压、整理

    Args:
        session: requests.Session 对象
        project_name: 项目名称
        project_url: 项目 URL
        base_dir: 基础目录

    Returns:
        是否处理成功
    """
    # 清理项目名称
    clean_name = sanitize_filename(project_name)
    if not clean_name:
        logger.warning(f"项目名称无效，跳过: {project_name}")
        return False

    # 创建项目目录结构
    project_dir = base_dir / clean_name
    raw_dir = project_dir / 'raw'
    docs_dir = project_dir / 'documents'

    ensure_dir(raw_dir)
    ensure_dir(docs_dir)

    # 保存元信息
    metadata = {
        'project_name': project_name,
        'project_url': project_url,
        'download_time': datetime.now().isoformat(),
        'files': []
    }

    # 提取文件链接
    file_urls = extract_file_urls(session, project_url)

    if not file_urls:
        logger.warning(f"项目无可下载文件: {project_name}")
        return False

    logger.info(f"项目 [{clean_name}] 找到 {len(file_urls)} 个文件")

    # 下载并处理文件
    success_count = 0
    for idx, (file_url, file_suffix) in enumerate(file_urls, 1):
        # 生成文件名
        file_name = f"{clean_name}_{idx}.{file_suffix}"
        file_path = raw_dir / file_name

        # 下载文件
        if download_file(session, file_url, file_path):
            # 记录文件信息
            metadata['files'].append({
                'filename': file_name,
                'url': file_url,
                'suffix': file_suffix,
                'size': file_path.stat().st_size
            })

            # 解压文件
            if file_suffix in ['zip', 'rar']:
                extract_archive(file_path, docs_dir)
            else:
                # 非压缩文件直接复制到 documents
                shutil.copy2(file_path, docs_dir / file_name)

            success_count += 1

    # 保存元信息
    metadata['success_count'] = success_count
    metadata['total_count'] = len(file_urls)
    save_metadata(project_dir, metadata)

    logger.info(f"项目 [{clean_name}] 处理完成: {success_count}/{len(file_urls)} 个文件成功")

    return success_count > 0


# ========== 主流程函数 ==========

def auto_mode(start_page: int = 1, end_page: int = 5):
    """
    自动模式：批量下载指定页码范围的所有项目

    Args:
        start_page: 起始页码
        end_page: 结束页码
    """
    logger.info(f"=== 自动模式启动 ===")
    logger.info(f"页码范围: {start_page} - {end_page}")

    # 创建输出目录
    base_dir = Path(CONFIG['output_dirs']['projects'])
    ensure_dir(base_dir)

    # 创建 Session
    session = create_session()

    # 获取项目列表
    pages = list(range(start_page, end_page + 1))
    projects = fetch_project_list(session, pages)

    if not projects:
        logger.warning("未找到任何项目")
        return

    logger.info(f"共找到 {len(projects)} 个项目，开始处理...")

    # 处理每个项目
    success_count = 0
    no_files_count = 0
    failed_count = 0

    for project_name, project_url in tqdm(projects, desc="处理项目"):
        try:
            result = process_project(session, project_name, project_url, base_dir)
            if result:
                success_count += 1
            elif result is False:
                failed_count += 1
        except Exception as e:
            logger.error(f"处理项目失败: {project_name}, 错误: {e}")
            failed_count += 1

    # 统计无文件项目
    no_files_count = len(projects) - success_count - failed_count

    logger.info(f"=== 处理完成 ===")
    logger.info(f"总计: {len(projects)} 个项目")
    logger.info(f"  ✓ 成功下载: {success_count} 个")
    logger.info(f"  ✗ 下载失败: {failed_count} 个")
    logger.info(f"  ⊘ 无可用文件: {no_files_count} 个")
    logger.info(f"  成功率: {success_count/len(projects)*100:.1f}%")


def manual_mode():
    """
    手动模式：指定页码下载
    """
    logger.info("=== 手动模式启动 ===")

    try:
        page_input = input("请输入页码（多个页码用逗号分隔，例如: 1,2,3）: ").strip()
        pages = [int(p.strip()) for p in page_input.split(',')]
    except ValueError:
        logger.error("页码输入无效")
        return

    # 创建输出目录
    base_dir = Path(CONFIG['output_dirs']['projects'])
    ensure_dir(base_dir)

    # 创建 Session
    session = create_session()

    # 获取项目列表
    projects = fetch_project_list(session, pages)

    if not projects:
        logger.warning("未找到任何项目")
        return

    logger.info(f"共找到 {len(projects)} 个项目，开始处理...")

    # 处理每个项目
    success_count = 0
    no_files_count = 0
    failed_count = 0

    for project_name, project_url in tqdm(projects, desc="处理项目"):
        try:
            result = process_project(session, project_name, project_url, base_dir)
            if result:
                success_count += 1
            elif result is False:
                failed_count += 1
        except Exception as e:
            logger.error(f"处理项目失败: {project_name}, 错误: {e}")
            failed_count += 1

    # 统计无文件项目
    no_files_count = len(projects) - success_count - failed_count

    logger.info(f"=== 处理完成 ===")
    logger.info(f"总计: {len(projects)} 个项目")
    logger.info(f"  ✓ 成功下载: {success_count} 个")
    logger.info(f"  ✗ 下载失败: {failed_count} 个")
    logger.info(f"  ⊘ 无可用文件: {no_files_count} 个")
    logger.info(f"  成功率: {success_count/len(projects)*100:.1f}%")


# ========== 主程序入口 ==========

def main():
    """主程序入口"""
    print("=" * 50)
    print("       余杭区规划局文件爬虫")
    print("=" * 50)
    print("  © XueMian168.Com")
    print("=" * 50)
    print()
    print("  1. 自动模式（批量下载 1-5 页）")
    print("  2. 手动模式（指定页码）")
    print()

    mode = input("请选择模式 (1/2): ").strip()

    if mode == "1":
        auto_mode(start_page=1, end_page=5)
    elif mode == "2":
        manual_mode()
    else:
        print("输入无效，退出程序")
        return

    # 完成后打开网站
    input('\n运行完毕，按下 Enter 键打开网站...')
    webbrowser.open_new('https://xuemian168.com')


if __name__ == '__main__':
    main()
