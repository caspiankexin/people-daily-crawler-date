# 人民日报爬虫

2021年8月3日更新

**之后人民日报的数据，我会每个月爬取一份，但github上一年更新一次，减少工作量。如需最新资料，可使用下方给的软件自己爬取或私信我。**

---

人民日报目前有电子版（[人民日报-人民网 (people.com.cn)](http://paper.people.com.cn/rmrb/html/2021-06/08/nbs.D110000renmrb_01.htm)），可以免费查看两年内的内容，可以通过爬虫爬取。同时，老资料网（[人民日报 - 人民日报1946-2003 - 老资料网 (laoziliao.net)](https://www.laoziliao.net/rmrb/)）有1946–2003年的人民日报数据，也可以通过爬虫爬取。

我爬取下来的数据放在release里，可以自行使用，**仅供学习，本人概不负责。**

---

分为两个程序来分别爬取“人民网”和“老资料网”

日期格式：20210101  ； 地址格式：E:\data   ；

### 人民网

打包好的爬虫软件：https://nebula.lanzoui.com/ieH5ijxmwub

代码：
```python
import requests
import bs4
import os
import datetime
import time

def fetchUrl(url):
    '''
    功能：访问 url 的网页，获取网页内容并返回
    参数：目标网页的 url
    返回：目标网页的 html 内容
    '''

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }

    r = requests.get(url,headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text

def getPageList(year, month, day):
    '''
    功能：获取当天报纸的各版面的链接列表
    参数：年，月，日
    '''
    url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/nbs.D110000renmrb_01.htm'
    html = fetchUrl(url)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    temp = bsobj.find('div', attrs = {'id': 'pageList'})
    if temp:
        pageList = temp.ul.find_all('div', attrs = {'class': 'right_title-name'})
    else:
        pageList = bsobj.find('div', attrs = {'class': 'swiper-container'}).find_all('div', attrs = {'class': 'swiper-slide'})
    linkList = []

    for page in pageList:
        link = page.a["href"]
        url = 'http://paper.people.com.cn/rmrb/html/'  + year + '-' + month + '/' + day + '/' + link
        linkList.append(url)

    return linkList

def getTitleList(year, month, day, pageUrl):
    '''
    功能：获取报纸某一版面的文章链接列表
    参数：年，月，日，该版面的链接
    '''
    html = fetchUrl(pageUrl)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    temp = bsobj.find('div', attrs = {'id': 'titleList'})
    if temp:
        titleList = temp.ul.find_all('li')
    else:
        titleList = bsobj.find('ul', attrs = {'class': 'news-list'}).find_all('li')
    linkList = []

    for title in titleList:
        tempList = title.find_all('a')
        for temp in tempList:
            link = temp["href"]
            if 'nw.D110000renmrb' in link:
                url = 'http://paper.people.com.cn/rmrb/html/'  + year + '-' + month + '/' + day + '/' + link
                linkList.append(url)

    return linkList

def getContent(html):
    '''
    功能：解析 HTML 网页，获取新闻的文章内容
    参数：html 网页内容
    '''
    bsobj = bs4.BeautifulSoup(html,'html.parser')

    # 获取文章 标题
    title = bsobj.h3.text + '\n' + bsobj.h1.text + '\n' + bsobj.h2.text + '\n'
    #print(title)

    # 获取文章 内容
    pList = bsobj.find('div', attrs = {'id': 'ozoom'}).find_all('p')
    content = ''
    for p in pList:
        content += p.text + '\n'
    #print(content)

    # 返回结果 标题+内容
    resp = title + content
    return resp

def saveFile(content, path, filename):
    '''
    功能：将文章内容 content 保存到本地文件中
    参数：要保存的内容，路径，文件名
    '''
    # 如果没有该文件夹，则自动生成
    if not os.path.exists(path):
        os.makedirs(path)

    # 保存文件
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content)

def download_rmrb(year, month, day, destdir):
    '''
    功能：爬取《人民日报》网站 某年 某月 某日 的新闻内容，并保存在 指定目录下
    参数：年，月，日，文件保存的根目录
    '''
    pageList = getPageList(year, month, day)
    for page in pageList:
        titleList = getTitleList(year, month, day, page)
        for url in titleList:

            # 获取新闻文章内容
            html = fetchUrl(url)
            content = getContent(html)

            # 生成保存的文件路径及文件名
            temp = url.split('_')[2].split('.')[0].split('-')
            pageNo = temp[1]
            titleNo = temp[0] if int(temp[0]) >= 10 else '0' + temp[0]
            path = destdir + '/' + year + month + day + '/'
            fileName = year + month + day + '-' + pageNo + '-' + titleNo + '.txt'

            # 保存文件
            saveFile(content, path, fileName)


def gen_dates(b_date, days):
    day = datetime.timedelta(days = 1)
    for i in range(days):
        yield b_date + day * i


def get_date_list(beginDate, endDate):
    """
    获取日期列表
    :param start: 开始日期
    :param end: 结束日期
    :return: 开始日期和结束日期之间的日期列表
    """

    start = datetime.datetime.strptime(beginDate, "%Y%m%d")
    end = datetime.datetime.strptime(endDate, "%Y%m%d")

    data = []
    for d in gen_dates(start, (end-start).days):
        data.append(d)

    return data


if __name__ == '__main__':
    '''
    主函数：程序入口
    '''
    # 输入起止日期，爬取之间的新闻
    beginDate = input('请输入开始日期:')
    endDate = input('请输入结束日期:')
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >=10 else '0' + str(d.month)
        day = str(d.day) if d.day >=10 else '0' + str(d.day)
        destdir = "E:/202001"

        download_rmrb(year, month, day, destdir)
        print("爬取完成：" + year + month + day)
#         time.Sleep(3)        # 怕被封 IP 爬一爬缓一缓，爬的少的话可以注释掉
```

### 老资料网

代码如下：

```python
'''
copyright @caspian
此程序为模仿@机灵鹤 的人民日报爬虫，改写的爬取‘老资料网-人民日报’资料的爬虫
采取的是先生成所有的日期列表，再循环执行日期列表的爬虫；
优点：可以准确爬取到日期，可以爬取老资料网的参考消息
缺点：容易被封ip，时间间隔太长，效率太低，太短，很快被封。
'''

import requests
import os
import datetime
import time
from lxml import etree
import random

def gen_dates(b_date, days):
    day = datetime.timedelta(days = 1)
    for i in range(days):
        yield b_date + day * i


def get_date_list(beginDate, endDate):
    """
    获取日期列表
    :param start: 开始日期
    :param end: 结束日期
    :return: 开始日期和结束日期之间的日期列表
    """

    start = datetime.datetime.strptime(beginDate, "%Y%m%d")
    end = datetime.datetime.strptime(endDate, "%Y%m%d")

    data = []
    for d in gen_dates(start, (end-start).days):
        data.append(d)

    return data

def header():      #随机选择header防止被禁
    headers_list = [
        'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
        'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',
        'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
        'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',
        'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11',
    ]
    header1 = random.choice(headers_list)
    headers = {"User-Agent": header1}
    return  headers


def saveFile(content, path, filename):
    '''
    功能：将文章内容 content 保存到本地文件中
    参数：要保存的内容，路径，文件名
    '''
    # 如果没有该文件夹，则自动生成
    if not os.path.exists(path):
        os.makedirs(path)
    # 保存文件
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content)

def fetchUrl(dataurl):
    '''
    功能：获取每天页面的每个版面的版面链接
    参数：目标日期的 url
    返回：每个版面的链接列表
    '''

    headers = header()
    r = requests.get(dataurl,headers=headers)
    text = r.text
    html = etree.HTML(text)
    ul = html.xpath('//ul')[0]
    lis = ul.xpath("//li[1]/a/@href")  # []内的是第几个元素，去掉[]是全部的，li[last()]是最后一个
    lis.remove('/')
    return lis


def gethtml(link1):
    headers = header()
    r = requests.get(link1, headers=headers)
    text = r.text
    html = etree.HTML(text)
    plist1 = html.xpath("//*[@class='article']/descendant-or-self::text()")  # 获取一个版面的所有文章内容
    content1 = ''
    for plist in plist1:
        content1 += plist
    return content1


if __name__ == '__main__':
    '''
    主函数：程序入口
    '''
    # 输入起止日期，爬取之间的新闻
    beginDate = input('请输入开始日期:')
    endDate = input('请输入结束日期:')
    destdir = input("请输入数据保存的地址：")
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >= 10 else '0' + str(d.month)
        day = str(d.day) if d.day >= 10 else '0' + str(d.day)
        destdir = destdir                                                     # 爬下来的文件的存储地方

        dataurl = 'https://www.laoziliao.net/rmrb/' + year + '-' + month + '-' + day
        for link1 in fetchUrl(dataurl):           #每一个版面的链接
            content = gethtml(link1)
            path = destdir + '/' + year + '年' + '/' + year + '年' + month + '月' + '/' + year + month + day + '/'
            n = link1.split('-')[3].split('#')[0]
            filename = year + month + day + '-' + n + '.txt'
            saveFile(content, path, filename)
#            time.sleep(2)
        print('爬取完成' + year + month + day)
        time.sleep(3)    
    print('全部爬取完成')

```

