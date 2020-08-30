# “语象观察”-爬取人民日报并统计词频

> “语象观察”是之前看过的钱钢老师做的一项社会学研究，由于之前用于发布的“尽知天下事”公众号被封，导致目前无法再看到老师的相关研究成果（或许这个项目已经停止了），便有了自己尝试来研究。
> 钱钢老师的文章示例：[https://sourl.cn/idh34d](https://sourl.cn/idh34d)

## 一、确定整体思路

![](https://i.loli.net/2020/08/30/XvFLU136qGszcjp.png)

## 二、实际操作部分

作为技术初学者（和小白差不多），所有的操作都是以目的为导向，并不追求操作的完美型，只求在最少涉及技术的情况下实现要求。

本次所用程序主要由python实现。（python3.8，windows 10 环境下进行的测试）

### 1、爬取人民日报的数据

此处特别感谢CSDN用户@机灵鹤的[博客文章](https://blog.csdn.net/wenxuhonghe/article/details/90047081)，我在他的代码上进行了一丢丢的更改，直接上代码

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
    beginDate = input('请输入开始日期:') # 日期格式20200101
    endDate = input('请输入结束日期:')
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >=10 else '0' + str(d.month)
        day = str(d.day) if d.day >=10 else '0' + str(d.day)
        destdir = "E:/date"  #此处选择爬取下来文件的存储路径

        download_rmrb(year, month, day, destdir)
        print("爬取完成：" + year + month + day)
#         time.sleep(3)        # 怕被封 IP 爬一爬缓一缓，爬的少的话可以注释掉
# 不建议一次爬取太多天的数据，如果报错，可能是被封ip，稍等一会再进行即可
```

### 2、整理爬取的数据

第一步爬虫爬下来的是将每天所有文章保存在一个文件夹下，需要将所有文章合并为一个txt文件。

此处代码感谢CSDN用户@yunzifengqing的[博客文章](https://blog.csdn.net/yunzifengqing/article/details/82465794?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522159852148519724839240101%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=159852148519724839240101&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v3~pc_rank_v4-1-82465794.first_rank_ecpm_v3_pc_rank_v4&utm_term=python+%E5%90%88%E5%B9%B6+%E5%AD%90%E6%96%87%E4%BB%B6%E5%A4%B9+txt&spm=1018.2118.3001.4187)

```python
# 本知识来源于：https://sourl.cn/LR2N5W
# 本程序支持合并文件夹及其子文件中txt的合并

import os

# 运行Python过程中输入文件夹路径及合并后的文件路径及名称
# rootdir = raw_input("the old path: ")
# newfile = raw_input("the new path and filename: ")
rootdir = r'E:\date'   # 输入需要合并文件的文件夹路径
newfile = r'E:\date\合并后文档.txt'  # 输入合并后文件的存储路径
paths = []   # 存放文件夹（含子文件夹）下所有文件的路径及名称

# 获取文件夹（含子文件夹）下所有文件的路径及名称
for root, dirs, files in os.walk(rootdir):
    for file in files:
        paths.append(os.path.join(root, file).encode('utf-8')) # 支持中文名称

# 创建新的文件
f = open(newfile,'w',encoding='utf-8')
# 将之前获取到的文件夹（含子文件夹）下所有文件的路径及名称里的内容写进新建的文件里
for i in paths:
    for line in open(i,encoding='utf-8'):
        f.writelines(line)
f.close()   # 保存并关闭新建的文件
```

### 3、统计关键词的出现次数

搜索关键词虽是日常生活中最常用到的操作，但是花费是精力是最大的。由于合并后文本的字数非常大，且需要搜索的关键词很多，如果是通过软件搜索那工作量太大了，此外网上有很多的python搜索关键词的代码，但是大多是需要我在程序中输入需要搜索的关键词，不适合关键词很多的情况。

此外，作为python小白，之前走错路查了非常多的自然语言处理，但是最后还是查找资料找到了想要的程序。

---

实现此项目的首先需要创建关键词文件，这个根据具体需要进行更换，关键词的整理或许还需要爬虫的支持，我暂时还未涉及，如果不多可以手动输入。还有为了考虑项目的实际需要，选择在程序中指定关键词和文本路径，以便减少后续操作的更改量。

此代码统计次数部分感谢B站用户@Deustchlands的[视频](https://www.bilibili.com/video/BV1ue411s7Gv)，关键次文件和需统计文本的路径知识感谢CSDN用户@Scarlett2045的[博客文章](https://blog.csdn.net/weixin_43507682/article/details/103078816)，将统计结果输出为csv文件知识感谢CSDN用户@Aaran123的[博客文章](https://blog.csdn.net/weixin_44298385/article/details/104392226)，还很感谢无数网友的乐于分享帮助解决了很多问题。

> **注意：**
> 1、`with   open（）`里的路径是‘`\`’,`Excel = open（）`里的路径是‘`/`’
> 2、关键词名单为txt文件，每个关键词为一行。
> 3、本程序其实具有两个部分，打印出统计结果，和输出有统计结果的csv文件
> 4、倒数第三行和第七行中的数字分别代表打印和输出排名的前多少位，输出的排名必需小于或等于可以输出的排名，例如10个关键词只有7个出现过可以被搜到，那输出的排名智只能小于等于7。

```python
# 本知识来源：https://www.bilibili.com/video/BV1ue411s7Gv 
#  https://github.com/Ericwang6/three_body
# https://sourl.cn/jKeQYH      https://sourl.cn/cDP8HR

import jieba
import csv

# 打开准备好的关键词名单
with open(file=r"E:\OneDrive\projects\语象观察—人民日报\相关代码\词频统计\中国政要名单.txt",encoding='UTF-8') as f:
    nameList = f.read().split('\n')

# 打开要进行词频统计的文本
with open(file=r"E:\date\合并后文档.txt",encoding='UTF-8') as f:
    txt = f.read()

# 向jieba库中加入人名，防止jieba在分词时将人名当作两个词拆分掉
for name in nameList:
    jieba.add_word(name)

# 打开表格文件，若表格文件不存在则创建
# 输出的文件路径也是可以设置的，和之前的修改估计一样
# 直接输入要存入的路径即可，不过路径中不是“\”而是“/”
Excel = open("E:/date/本月中国政要出现次数.csv", 'w', newline='')
writ = csv.writer(Excel)  # 创建一个csv的writer对象用于写每一行内容
writ.writerow(['名称', '出现次数'])  # 写表格表头

# 分词
txt = jieba.lcut(txt)

# 创建一个字典，用于对词出现次数的统计，键表示词，值表示对应的次数
counts = {}
for item in txt:
    for name in nameList:
        if item == name:
            counts[name] = counts.get(name, 0) + 1  # 在字典中查询若该字返回次数加一

# 排序并输出结果
count = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
for item in count[:20]:  # 选择打印输出前多少的数据
    print(item)  # 会显示在控制面板上，但不会保存到本地

item = list(counts.items())  # 将字典转化为列表格式
item.sort(key=lambda x: x[1], reverse=True)  # 对列表按照第二列进行排序
for i in range(5):   # 要确保设置导出的数小于等于可以导出数的最大值
    writ.writerow(item[i])  # 将前几名写入表格，
print('统计结果输出成功')
```

### 4、后续操作

如果想要全自动，可以直接将这几段代码按顺序合并在一起，便能自动执行相应的功能。

在输出统计结果之后，可以按照自己的需求进行相应操作。可视化和社科研究就不在这里考虑了。

---

2020年8月30日更新

- 将涉及的代码全部放到“相关代码”文件夹内

- 创建关键词文件夹目录，存在用来统计的关键词，持续更新关键词文件

---

2020年8月22日更新

- 上传新的代码文件“代码（第二版）.py”


---

2020-07-31更新

没有想到人民日报在七月份更改了他们的版面，导致原来的爬虫无法爬取2020年7月1日以后的内容了，不过之前的内容还是可以爬取的。之后我会将新的爬虫上传。

---

- 爬虫的代码是程序.py，源于网络，我已经使用很久了，可以正常使用，不过速度不是很快，如果要一次性大量爬取不建议使用这个。

- 此外，从2019年开始，我会每月爬取一次人民日报的文章，也会把爬下来的内容放到仓库里，压缩包里是txt文件，按月分类。如有需要可以直接下载使用。

爬取人民日报内容是源于之前看的"语像观察"被封了，所以想着自己模仿也进行类似的研究，但是发现作为各方面小白，如果想要做成还是有很大的难度的，所以只能暂时搁置，先定期把人民日报的数据保存下来，以便之后使用。

---
> 如果我发布的内容算侵权的话，请告知，我会删

> 爬虫代码和爬取下来的人民日报数据可以随意使用，但利用这些创作的内容概不负责。
