import os
import re
import time
import webbrowser

import requests


def getproject(select):
    basicurl = 'http://ghzy.hangzhou.gov.cn/col/col1228968050/index.html?uid=6897088&pageNum='
    r = requests.get(basicurl)
    test_str = r.content.decode('utf8')
    regex2 = r' <a href=\"([\d\D]*?)\" target=\"([\d\D]*?)\" title=\"([\d\D]*?)"'
    matches = re.finditer(regex2, test_str, re.MULTILINE)
    write = open('temp.txt', 'w')
    writename = open('projectname.txt', 'w')
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(2, 3):
            groupNum = groupNum + 1
            projectname = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
            if select == "1" or select == "2":
                print(projectname)
        for groupNum in range(1):
            groupNum = groupNum + 1
            urls = "http://ghzy.hangzhou.gov.cn""{group}".format(groupNum=groupNum, group=match.group(groupNum))
            if select == "2":
                print(urls)
            elif select == "3":
                print(urls, file=write)
                print(projectname, file=writename)
    return True


pass


def getjpg():
    read = open('temp.txt', 'r')
    writejpg = open('jpgtemp.txt', 'w')
    writeurl = open('jpgtemp2.txt', 'w')
    print("项目名称,公示图地址", file=writejpg)
    while True:
        line = read.readline()  # 包括换行符
        line = line[:-1]  # 去掉换行符
        if line:
            jurl = line
        else:
            break
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52'}
        regex = r'<p><a href=\"([\d\D]*?)\" target=\"([\d\D]*?)\"'
        r = requests.get(jurl, headers=header)
        test_str = r.content.decode('utf8')
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(1):
                regextitle = r'<title>([\d\D]*?)<'
                title = re.findall(regextitle, test_str)
                groupNum = groupNum + 1
                jpgurl0 = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
                jpgurl1 = "http://ghzy.hangzhou.gov.cn{jpgurl0}".format(jpgurl0=jpgurl0)
                r2 = requests.get(jpgurl1, headers=header, verify=False, allow_redirects=False)
                new_url = r2.headers["Location"]
                print("{title}\t{url}".format(title=title, url=new_url))
                result = "{title},{url}".format(title=title, url=new_url)
                print(result, file=writejpg)
                print(new_url, file=writeurl)


def downloadjpg():
    readurl = open('jpgtemp2.txt', 'r', encoding='ANSI')
    num = 0
    readname = open('projectname.txt', 'r', encoding='ANSI')
    while 1:
        line = readurl.readline()
        name = readname.readline()
        if not line:
            break
        elif not name:
            break
        print("正在下载第{num}份，项目名为{name}".format(num=num, name=name))
        num += 1
        image_url = line
        ima = image_url.replace('\n', '')
        try:
            requests.packages.urllib3.disable_warnings()
            r = requests.get(ima, verify=False)  # 创建响应对象
            # path = re.sub(
            #     "http://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3390/site/picture/0/",
            #     "./jpg/{name}".format(name=name), line)
            name = name.replace('/', '')  # 防止斜杠导致的写入失败
            path = re.sub('\n', '', "./jpg/" + name + ".jpg")  # 删除path末尾的换行符'\n'
            f = open(path, "wb")
            f.write(r.content)
            f.close()
        except Exception as e:
            print('无法下载，%s' % e)
            continue
    readurl.close()


def writecsv():
    print("写入CSV")
    import csv
    # 1. 读取数据
    data = []
    with open('jpgtemp.txt', 'r', encoding='ANSI') as f:
        for line in f:
            data.append(list(line.strip().split(',')))
    # 2. 创建文件对象
    f = open('公示图{time}.csv'.format(time=time.time()), 'w', encoding='utf_8_sig', newline='')
    # 3. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 4. 写入csv文件内容
    csv_writer.writerows(data)
    # 5. 关闭文件
    f.close()


def clean():
    if os.path.exists('temp.txt'):
        if os.path.exists('jpgtemp.txt'):
            if os.path.exists('jpgtemp2.txt'):
                if os.path.exists('projectname.txt'):
                    os.remove('temp.txt')
                    os.remove('jpgtemp.txt')
                    os.remove('jpgtemp2.txt')
                    os.remove('projectname.txt')
                    pass


if __name__ == '__main__':
    clean()
    if os.path.exists('./jpg'):
        print('运行环境正常')
    else:
        os.mkdir('./jpg/')
        print('已新建文件夹"jpg"用于存储\n')
    print(" 杭州市规划局文件爬虫")
    print("===================")
    print(" © XueMian168.Com  ")
    print("1.获取最新项目名")
    print("2.获取最新项目URL及名称")
    print("3.获取最新项目设计图")
    select = input("请输入：")
    if select == "3":
        if getproject("3"):
            print("写入完成")
            getjpg()
        else:
            print("出了点问题")
    if select != "1" and select != "2" and select != "3":
        print("输入有误请重新输入")
    getproject(select)
    if select == "3":
        writecsv()
        downloadjpg()
        clean()
    webbrowser.open_new('https://xuemian168.com')
    input('\n运行完毕，按下“回车(Enter)关闭程序...”')
