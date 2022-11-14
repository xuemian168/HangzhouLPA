import os
import re
import webbrowser
import requests


def auto():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        "Cookie": "JSESSIONID = 16C8B6FE3099D92E34BB4AD8DB1B489A;Path = / zwdt_public;HttpOnly",
        'Referer': 'https://www.yuhang.gov.cn/col/col1229191870/index.html?number=Y001C001',
        'Host': 'www.yuhang.gov.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"'
    }
    url = 'http://www.yuhang.gov.cn/col/col1229191870/index.html?number=Y001C001'
    for page in range(1, 6):
        data = {
            "infotypeId": 'Y001C001',
            'divid': 'div1229106886',
            "currpage": '{page}'.format(page=page),
            "sortfield": ',compaltedate:0'
        }
        posturl = 'https://www.yuhang.gov.cn/module/xxgk/search.jsp?standardXxgk=1&isAllList=1&texttype=0&fbtime=-1&vc_all=&vc_filenumber=&vc_title=&vc_number=&currpage={page}&sortfield=,compaltedate:0'.format(
            page=page)
        print("当前正在第{page}页：".format(page=page))
        regular = r'<a title=\"([\d\D]*?)" target=\"([\d\D]*?)\" href=\"([\d\D]*?)\">'
        html = requests.post(posturl, data=data, headers=header)
        code = html.content.decode('utf-8')
        write = open('yuhangnames.txt', f'w')
        writeurl = open('yuhangurls.txt', f'w')
        matches = re.finditer(regular, code, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, 1):
                groupNum = groupNum + 1
                projectname = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
            for groupNum in range(2, 3):
                groupNum = groupNum + 1
                projecturl = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
            print(projectname, file=write)
            print(projecturl, file=writeurl)


def shoudong():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        "Cookie": "JSESSIONID = 16C8B6FE3099D92E34BB4AD8DB1B489A;Path = / zwdt_public;HttpOnly",
        'Referer': 'https://www.yuhang.gov.cn/col/col1229191870/index.html?number=Y001C001',
        'Host': 'www.yuhang.gov.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"'

    }
    page = input("请输入页码：")
    data = {
        "infotypeId": 'Y001C001',
        'divid': 'div1229106886',
        "currpage": '{page}'.format(page=page),
        "sortfield": ',compaltedate:0'
    }
    posturl = 'https://www.yuhang.gov.cn/module/xxgk/search.jsp?standardXxgk=1&isAllList=1&texttype=0&fbtime=-1&vc_all=&vc_filenumber=&vc_title=&vc_number=&currpage={page}&sortfield=,compaltedate:0'.format(
        page=page)
    print("当前正在第{page}页：".format(page=page))
    regular = r'<a title=\"([\d\D]*?)" target=\"([\d\D]*?)\" href=\"([\d\D]*?)\">'
    html = requests.post(posturl, data=data, headers=header)
    code = html.content.decode('utf-8')
    write = open('yuhangnames.txt', f'w')
    writeurl = open('yuhangurls.txt', f'w')
    matches = re.finditer(regular, code, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, 1):
            groupNum = groupNum + 1
            projectname = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
        for groupNum in range(2, 3):
            groupNum = groupNum + 1
            projecturl = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
        print(projectname, file=write)
        print(projecturl, file=writeurl)
    return "完成"


def getzipurl():
    print("正在获取ZIP/RAR地址")
    read = open('yuhangurls.txt', 'r')
    writeurl = open('yuhangurls2.txt', 'w')
    writesuffix = open('yuhangsuffix.txt', 'w')
    urlprefix = "https://www.yuhang.gov.cn"
    while True:
        line = read.readline()  # 包括换行符
        line = line[:-1]  # 去掉换行符
        if line:
            zipurl1 = line
        else:
            break
        regux = r'<a href=\"(\/module\/download[\d\D]*?)+(zip|rar|pdf):?\">'
        html = requests.get(zipurl1)
        code = html.content.decode('utf-8')
        matches = re.finditer(regux, code, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, 1):
                groupNum = groupNum + 1
                projectname = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
                suffix = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
            for groupNum in range(1, 2):
                groupNum = groupNum + 1
                suffix = "{group}".format(groupNum=groupNum, group=match.group(groupNum))
            print('{prefix}{url}{suffix}'.format(prefix=urlprefix, suffix=suffix, url=projectname), file=writeurl)
            print(suffix, file=writesuffix)


def downloadzip():
    readurl = open('yuhangurls2.txt', 'r', encoding='ANSI')
    num = 0
    readname = open('yuhangnames.txt', 'r', encoding='ANSI')
    readsuffix = open('yuhangsuffix.txt', 'r', encoding='ANSI')
    while 1:
        line = readurl.readline()
        name = readname.readline()
        suffix = readsuffix.readline()
        if not line:
            break
        elif not name:
            break
        num += 1
        print("正在下载第{num}份，项目名为{name}".format(num=num, name=name))
        image_url = line
        ima = image_url.replace('\n', '')
        try:
            requests.packages.urllib3.disable_warnings()
            r = requests.get(ima, verify=False)  # 创建响应对象
            # path = re.sub(
            #     "http://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3390/site/picture/0/",
            #     "./jpg/{name}".format(name=name), line)
            name = name.replace('/', '')  # 防止斜杠导致的写入失败
            path = re.sub('\n', '', "./yuhang/" + name + '.' + suffix)  # 删除path末尾的换行符'\n'
            f = open(path, "wb")
            f.write(r.content)
            f.close()
        except Exception as e:
            print('无法下载，%s' % e)
            continue
    readurl.close()


def un_zip():
    import zipfile
    import rarfile
    src = './yuhang/'
    dst = './yh/'
    filenames = os.listdir(src)
    for filename in filenames:
        if zipfile.is_zipfile(src + filename):
            fz = zipfile.ZipFile(src + filename, 'r')
            for file in fz.namelist():
                if os.path.exists(dst + filename.replace("#", '')):
                    print("正在解压ZIP：", file)
                    fz.extract(file, dst + filename.replace("#", '') + "/")
                else:
                    os.mkdir(dst + filename.replace('#', ''))
            fz.close()
        elif rarfile.is_rarfile(src + filename):
            # rz = rarfile.RarFile(src + filename, mode='r')
            # for file in rz.namelist():
            #     if os.path.exists(dst + filename):
            #         print("正在解压RAR:", filename, file)
            #         rz.extract(file, dst + filename)
            #     else:
            #         os.mkdir(dst + filename)
            # rz.close()
            print(filename,"是RAR文件，不支持解压")
        else:
            print(filename, "is not zip")
            return False


if __name__ == '__main__':
    if os.path.exists("./yuhang/"):
        print('当前环境正常')
    else:
        os.mkdir('./yuhang/')
    if os.path.exists("./yh/"):
        print('当前环境正常')
    else:
        os.mkdir('./yh/')
    print(" 余杭区规划局文件爬虫 ")
    print("===================")
    print(" © XueMian168.Com  ")
    print("  1.自动模式")
    print("  2.手动模式")
    mode = input("请选择模式：")
    if mode == "1":
        auto()
    if mode == "2":
        print(shoudong())
    else:
        print("输入有误")
    getzipurl()
    downloadzip()
    un_zip()
    input('\n运行完毕，按下“回车(Enter)关闭程序...”')
    webbrowser.open_new('https://xuemian168.com')
