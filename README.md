# 通过python来实现"语象观察"

> “语象观察”是钱刚老师之前在做的一个研究项目，之前曾经在公众号“尽知天下事”（现已被封）上发布。我对这种通过数据来发掘有价值的内容的数据新闻很感兴趣，算是弥补自己文笔不行还想从事新闻传媒的曲线救国道路吧。

不过作为一个对电脑方面感兴趣但很小白的我来说，所有的步骤想起来都很简单，但实操起来无从下手，不过决心还是很坚定的，决定要做到现在基本完成将近10个月。

![](https://cdn.jsdelivr.net/gh/caspiankexin/tuchuang/PIC-img/57BD8C52-E76A-45B2-BB9D-D8385B786E90.jpeg)

一步步找问题，找解决办法，和一次次试验。念念不忘，必有回响。目前我已经实现了所有我最初的设想功能。

---

# 一：获取人民日报的数据

分析数据，第一步是要获取人民日报的数据。利用爬虫每月爬取人民日报当月内容为txt文件，爬虫这部分代码来源于CSDN用户@机灵鹤，帮助我解决了最难的变成问题，非常感谢。

## 1、代码如下：

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
    destdir = input("请输入数据保存的地址：")
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >=10 else '0' + str(d.month)
        day = str(d.day) if d.day >=10 else '0' + str(d.day)
        destdir = destdir  # 爬下来的文件的存储地方

        download_rmrb(year, month, day, destdir)
        print("爬取完成：" + year + month + day)
        time.sleep(3)        # 怕被封 IP 爬一爬缓一缓，爬的少的话可以注释掉

print("本月数据爬取完成！")
```

## 2、⚠️注意：

### ①本爬虫只能爬取人民日报网页版上可查看的日期的内容，具体范围，参考原网站：[http://paper.people.com.cn/rmrb](http://paper.people.com.cn/rmrb/html/2021-01/01/nbs.D110000renmrb_01.htm)

### ②开始日期和结束日期格式为：20200101    20200102（这样保存的是2020年1月1日的内容）

###③由于反爬原因，本程序并不能保证每次都会顺利全部爬取下来，这个概率很小

##3、其他方案

考虑到很多朋友对程序更小白，不习惯使用代码来操作。提供两种备选方案。

①、我已经将上述代码封装成了exe文件，在Windows电脑上可以直接运行这个爬虫，自主选择需要爬取的范围。

下载地址：[https://nebula.lanzous.com/ieH5ijxmwub](https://nebula.lanzous.com/ieH5ijxmwub)

②我已经把我爬取下来的人民日报txt文件打包分享了，每月更新一次，有需要的，可以直接下载使用。

下载地址：Github：[https://github.com/caspiankexin/people-daily-crawler-date](https://github.com/caspiankexin/people-daily-crawler-date)

# 二：对人民日报的内容进行数据提取

“语象观察”需要的数据非常简单，就是统计一个关键词在文章中出现了几次。难度再于“语象观察”分析的文章字数经常会在十万和百万级，关键词上百个，还得是对多个文件进行操作，传统方法无法应付。


## 1、准备关键词名单

关键词名单的准备一定程度上属于非技术难题，这里需要的是看你要统计文章中哪个词语出现的次数，可以是国家各级领导人的名单，也可以是要研究对比的政治性术语，名单的制作看个人需要制作。当然一些关键词名单还是需要爬虫来实现更加方便，但这不属于本项目的教学范围，不进行讨论。

我在这里准备了两个关键词名单来作说明：“中国省份名单.txt”,“外国政要名单.txt”，关键词名单内容格式为每行一个。如图所示：

![%E9%80%9A%E8%BF%87python%E6%9D%A5%E5%AE%9E%E7%8E%B0%20%E8%AF%AD%E8%B1%A1%E8%A7%82%E5%AF%9F%20d2883b8ae080443eaf3a207092e5adda/Untitled%201.png](https://cdn.jsdelivr.net/gh/caspiankexin/tuchuang/PIC-img/Untitled%201.png)

🔔**提醒**：建议将需要统计的关键词名单存放在同一个文件夹下，方便下一步的操作。

## 2、合并并统计关键词出现的次数并输出为csv

数据提取操作的前期准备工作，为了使操作便利，将程序设计为只需输入一个项目地址便能自动运行。但这就需要一些准备工作。

### ①整理项目文件夹

 创建一个文件夹并按下图创建存放相关文件：

![](https://cdn.jsdelivr.net/gh/caspiankexin/tuchuang/PIC-img/%E7%AE%A1%E7%90%86%E9%83%A8%E9%97%A8.png)

### ②确定需要统计的日期和关键词名单

如：需要统计2019年和2020年的数据；以及中国政要名单和外国政要名单；下图所示

![](https://cdn.jsdelivr.net/gh/caspiankexin/tuchuang/PIC-img/image-20210102144453988.png)

### ③运行代码：

```python
import os
import jieba
import csv


fuji = input("请输入项目地址：") #例如我的项目地址：E:\onedrive\project\语象观察人民日报

#xuhebingliebiao = input("请输入需合并的所有文件夹名称的列表txt文件：")
#xuhebingfuji = input("请输入需合并的文件夹所在的父级地址：")
#cunchuhebinghoufuji = input("请输入合并后文件的存储地址：")

xuhebing = fuji+"\\实际操作\\需合并文件的列表.txt"

with open(xuhebing, 'r', encoding='UTF-8') as f:
    lines1 = [line1.strip() for line1 in f.readlines()]

for line1 in lines1:
    newstr = fuji+"\\原始数据\\"+line1 #需要合并的每一个文件夹
    newfile = fuji+"\\实际操作\\合并后的文件\\"+line1+"合并后文档.txt" # 输入合并后文件的存储路径
    paths = []  # 存放文件夹（含子文件夹）下所有文件的路径及名称
    for root, dirs, files in os.walk(newstr):
        for file in files:
            paths.append(os.path.join(root, file).encode('utf-8'))  # 支持中文名称

    # 创建新的文件
    f = open(newfile, 'w', encoding='utf-8')
    # 将之前获取到的文件夹（含子文件夹）下所有文件的路径及名称里的内容写进新建的文件里
    for i in paths:
        for line in open(i, encoding='utf-8'):
            f.writelines(line)
    f.close()  # 保存并关闭新建的文件

print("所有文件夹都已合并完成。")

#打开需要统计的已经合并后的txt文件的汇总好的文件地址的txt列表
with open(xuhebing, 'r', encoding='UTF-8') as f:   #这里的open的使用方式看对不对，对比下面na g
    lines = [line.strip() for line in f.readlines()]

guanjianci = fuji+"\\实际操作\\关键词名单列表.txt"
with open(guanjianci, 'r', encoding='UTF-8') as f:
    lines2 = [line2.strip() for line2 in f.readlines()]

guanjiancifuji = fuji+"\\关键词名单" #关键词文件父级地址
xutongjiwenjianfuji = fuji+"\\实际操作\\合并后的文件" #需要统计的文件所在的文件夹地址
cunchuwenjianfuji = fuji+"\\实际操作\\统计后输出" #统计后输出的文件所在的文件夹地址

for line in lines:
   line = line+"合并后文档" #注意这里的，看是否会有问题
   for line2 in lines2:
            with open(file=guanjiancifuji+"\\"+line2+".txt", encoding='UTF-8') as f:
                nameList = f.read().split('\n')

            newaddress = xutongjiwenjianfuji +"\\"+ line + ".txt"
            newfileaddress = cunchuwenjianfuji+"\\"+line+line2+".csv"  # 输入合并后文件的存储路径
            paths = []  # 存放文件夹（含子文件夹）下所有文件的路径及名称
            oldfile = newaddress  # 输入需要统计的文档的路径
            newfile = newfileaddress  # 统计后数据的保存路径
            with open(file=oldfile, encoding='UTF-8') as f:
                txt = f.read()

            # 向jieba库中加入人名，防止jieba在分词时将人名当作两个词拆分掉
            for name in nameList:
                jieba.add_word(name)

            # 打开表格文件，若表格文件不存在则创建
            # 输出的文件路径也是可以设置的，和之前的修改估计一样
            # 直接输入要存入的路径即可，不过路径中不是“\”而是“/”
            Excel = open(newfile, 'w', newline='')
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
            for item in count[:15]:  # 选择打印输出前多少的数据
                print(item)  # 会显示在控制面板上，但不会保存到本地

            item = list(counts.items())  # 将字典转化为列表格式
            item.sort(key=lambda x: x[1], reverse=True)  # 对列表按照第二列进行排序
            for i in item:  # 要确保设置导出的数小于等于可以导出数的最大值！！！！！！这个得解决！！！
             writ.writerow(i)  # 将前几名写入表格，
            print(line+line2+'统计结果输出成功')



print("所有文件都已经统计并输出完成。")
```

### ④查看结果：

最终输出的结果如下

![](https://cdn.jsdelivr.net/gh/caspiankexin/tuchuang/PIC-img/image-20210102145340909.png)


#三：数据分析

通过第二步将数据从众多文章中提取出来后，就需要分析数据，“语象观察”作为一个社科项目，分析数据才是核心所在。可以研究每一时间短内某个名词的出现次数，或某个名词在多个时间段出现次数的变化等来进行，推荐大家多看钱钢老师之前的“语象观察”的文章（自行搜索）来了解相关的语料分析。

#四：后记

自己做“语象观察”，最初只是出自无奈，无奈于钱钢被封杀，和“语象观察”这个项目所用到资源的不对外开放。没有办法在巨人肩膀上前行，只能自己从头开始造车轮，甚至造的还是很落后的车轮。这方面，确实很希望有能力的人能够多多的将知识和工具予以扩散，让更多的人能够在前辈基础上创造新的价值。

同时，在确定自己做之后，我也享受挑战，我虽然是编程小白，但是我有信心自己的网络能力能解决这些问题，也是检验自己电脑玩的到底行不行的机会。从刚开始的完全没有头脑到慢慢的分拆问题，解决问题；从最初的查资料都查偏了，到最后直接靠自己感觉去修改代码，这些都是在完善这个项目时不断进步的。在这个项目中，我也了解了更多的python知识，实践中学习学的比较牢靠。

此外，我在学习过程中也意识到，我为“语象观察”弄的程序也适合于其他的统计某个“词语”出现次数的需求上，最典型的就是统计一下考研大纲词汇在考研真题中的出现次数，其他肯定还会有很多的。

之后的后续，我也会在有时间的时候继续思考，争取能够做出高质量的“语象观察”类的文章。
