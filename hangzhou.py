#!/usr/bin/env python3
"""
杭州市规划和自然资源局项目爬虫 (优化版)
遵循 SOLID、DRY、KISS、YAGNI 原则
"""

import os
import re
import time
import csv
import webbrowser
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin
import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Config:
    """配置类 - 单一职责：集中管理所有配置"""
    BASE_URL = 'https://ghzy.hangzhou.gov.cn'
    API_URL = f'{BASE_URL}/api-gateway/jpaas-publish-server/front/page/build/unit'
    API_PARAMS = {
        'parseType': 'bulidstatic',
        'webId': '3390',
        'tplSetId': 'gNNXQnJhGbgHJoFMLtgED',
        'pageType': 'column',
        'tagId': '当前栏目list',
        'editType': 'null',
        'pageId': '1228968050'
    }
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    OUTPUT_DIR = './jpg'
    REQUEST_TIMEOUT = 15
    DOWNLOAD_TIMEOUT = 30
    RATE_LIMIT_DELAY = 0.5
    MAX_FILENAME_LENGTH = 100


class HttpClient:
    """HTTP 客户端 - 单一职责：统一管理所有网络请求"""

    def __init__(self):
        os.environ['NO_PROXY'] = '*'
        self._session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        """创建禁用代理的会话"""
        session = requests.Session()
        session.trust_env = False
        return session

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """统一的 GET 请求方法 - DRY 原则"""
        try:
            kwargs.setdefault('headers', Config.HEADERS)
            kwargs.setdefault('timeout', Config.REQUEST_TIMEOUT)
            response = self._session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"  ✗ 请求失败: {e}")
            return None


class ProjectParser:
    """项目解析器 - 单一职责：解析 HTML/JSON 数据"""

    @staticmethod
    def parse_project_list(html: str) -> List[Dict[str, str]]:
        """从 HTML 中提取项目列表"""
        pattern = r'<a[^>]*href="(/col/col1228968050/art/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)

        return [
            {'name': name.strip(), 'url': urljoin(Config.BASE_URL, url)}
            for url, name in matches
        ]

    @staticmethod
    def parse_image_url(html: str) -> Optional[str]:
        """从 HTML 中提取设计图 URL - DRY 原则"""
        patterns = [
            r'href="(/cms_files/filemanager/[^"]+\.jpg)"',
            r'src="(/cms_files/filemanager/[^"]+\.jpg)"'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                return urljoin(Config.BASE_URL, matches[0])

        return None


class ProjectScraper:
    """项目爬虫 - 单一职责：协调爬取流程"""

    def __init__(self, client: HttpClient, parser: ProjectParser):
        self.client = client
        self.parser = parser

    def get_project_list(self) -> List[Dict[str, str]]:
        """获取所有页面的项目列表（支持翻页）"""
        print("正在获取项目列表...")
        all_projects = []
        seen_urls = set()  # 用于检测重复项目
        page = 1
        page_size = 15

        while True:
            print(f"  正在获取第 {page} 页...")

            # 使用正确的分页参数格式
            params = Config.API_PARAMS.copy()
            params['paramJson'] = f'{{"pageNo":{page},"pageSize":"{page_size}"}}'

            response = self.client.get(Config.API_URL, params=params)
            if not response:
                print(f"  ✗ 第 {page} 页获取失败")
                break

            data = response.json()
            if not data.get('success'):
                print(f"  ✗ 第 {page} 页 API 返回失败: {data.get('message', '未知错误')}")
                break

            projects = self.parser.parse_project_list(data['data']['html'])

            if not projects:
                print(f"  ✓ 第 {page} 页无数据，已获取所有页面")
                break

            # 检查是否有新项目（去重）
            new_projects = []
            for project in projects:
                if project['url'] not in seen_urls:
                    new_projects.append(project)
                    seen_urls.add(project['url'])

            if not new_projects:
                print(f"  ✓ 第 {page} 页无新项目，已获取所有页面")
                break
            else:
                print(f"  ✓ 第 {page} 页找到 {len(new_projects)} 个新项目")
                all_projects.extend(new_projects)

            page += 1

            # 短暂延迟，避免请求过快
            time.sleep(0.5)

        print(f"\n✓ 总共找到 {len(all_projects)} 个项目（跨 {page-1} 页）\n")
        return all_projects

    def get_image_url(self, project_url: str) -> Optional[str]:
        """获取项目设计图 URL"""
        response = self.client.get(project_url)
        return self.parser.parse_image_url(response.text) if response else None


class ImageDownloader:
    """图片下载器 - 单一职责：下载和保存图片"""

    def __init__(self, client: HttpClient, output_dir: str = Config.OUTPUT_DIR):
        self.client = client
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ 创建输出目录: {self.output_dir}\n")

    def download(self, img_url: str, project_name: str) -> bool:
        """下载图片到本地"""
        file_path = self._get_safe_file_path(project_name)

        response = self.client.get(
            img_url,
            timeout=Config.DOWNLOAD_TIMEOUT,
            verify=False
        )

        if not response:
            return False

        try:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
        except IOError as e:
            print(f"  ✗ 写入文件失败: {e}")
            return False

    def _get_safe_file_path(self, project_name: str) -> str:
        """生成安全的文件路径 - 清理非法字符"""
        safe_name = re.sub(r'[<>:"/\\|?*]', '', project_name)
        safe_name = safe_name[:Config.MAX_FILENAME_LENGTH]
        return os.path.join(self.output_dir, f'{safe_name}.jpg')


class CSVExporter:
    """CSV 导出器 - 单一职责：导出数据到 CSV"""

    @staticmethod
    def save(data: List[List[str]], filename: str):
        """保存数据到 CSV 文件"""
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['项目名称', '项目URL', '设计图URL'])
                writer.writerows(data)
            print(f"\n✓ 数据已保存到: {filename}")
        except IOError as e:
            print(f"\n✗ 保存 CSV 失败: {e}")


class Application:
    """应用程序主类 - 协调所有组件"""

    def __init__(self):
        # 依赖注入 - 依赖倒置原则 (SOLID-D)
        self.client = HttpClient()
        self.parser = ProjectParser()
        self.scraper = ProjectScraper(self.client, self.parser)
        self.downloader = ImageDownloader(self.client)
        self.exporter = CSVExporter()

    def run(self):
        """运行主程序"""
        self._print_header()
        self._show_disclaimer()

        # 获取项目列表
        projects = self.scraper.get_project_list()
        if not projects:
            print("没有找到项目，程序退出")
            return

        # 处理每个项目
        results = self._process_projects(projects)

        # 保存结果
        self._save_results(results)

        # 打印总结
        self._print_summary(results)

    def _process_projects(
        self, projects: List[Dict[str, str]]
    ) -> List[Tuple[Dict, Optional[str], bool]]:
        """处理所有项目 - 返回 (项目, 图片URL, 是否成功)"""
        results = []
        total = len(projects)

        print(f"开始处理 {total} 个项目...\n")

        for i, project in enumerate(projects, 1):
            print(f"[{i}/{total}] {project['name']}")

            # 获取设计图 URL
            img_url = self.scraper.get_image_url(project['url'])
            success = False

            if img_url:
                print("  ✓ 找到设计图")
                # 下载设计图
                if self.downloader.download(img_url, project['name']):
                    print("  ✓ 下载成功")
                    success = True
            else:
                print("  ✗ 未找到设计图")

            results.append((project, img_url, success))

            # 限流
            time.sleep(Config.RATE_LIMIT_DELAY)

        return results

    def _save_results(self, results: List[Tuple[Dict, Optional[str], bool]]):
        """保存结果到 CSV"""
        csv_data = [
            [
                project['name'],
                project['url'],
                img_url or '未找到设计图'
            ]
            for project, img_url, _ in results
        ]

        filename = f'公示图_{int(time.time())}.csv'
        self.exporter.save(csv_data, filename)

    def _print_summary(self, results: List[Tuple[Dict, Optional[str], bool]]):
        """打印执行总结"""
        total = len(results)
        success = sum(1 for _, _, s in results if s)

        print("\n" + "=" * 50)
        print(f"处理完成！成功下载 {success}/{total} 个设计图")
        print("=" * 50)

    @staticmethod
    def _print_header():
        """打印程序头部"""
        print("=" * 50)
        print("杭州市规划和自然资源局项目爬虫")
        print("=" * 50)
        print("© XueMian168.Com")
        print()

    @staticmethod
    def _show_disclaimer():
        """显示免责声明并要求用户确认"""
        print("⚠️  重要免责声明")
        print("=" * 50)
        print("本工具仅供学习、研究和实验目的使用")
        print()
        print("1. 下载的数据必须在 24 小时内删除")
        print("2. 仅用于技术学习和研究,不得商业使用")
        print("3. 使用者需遵守相关法律法规和网站服务条款")
        print("4. 使用本工具的风险由使用者自行承担")
        print("5. 请尊重数据版权,不得擅自传播或出售")
        print()
        print("使用本工具即表示您已阅读并同意上述声明")
        print("=" * 50)
        print()

        response = input("是否同意并继续? (y/n): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("\n程序已取消")
            exit(0)
        print()


def main():
    """程序入口"""
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠ 程序被用户中断")
    except Exception as e:
        print(f"\n\n✗ 程序出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 打开网站
        print("\n正在打开网站...")
        webbrowser.open('https://www.ict.run')
        input('\n按回车键退出...')


if __name__ == '__main__':
    main()
