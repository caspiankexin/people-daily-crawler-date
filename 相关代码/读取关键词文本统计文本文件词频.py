# 本知识来源：https://www.bilibili.com/video/BV1ue411s7Gv   https://github.com/Ericwang6/three_body
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
for i in range(5):   # 填入需要导出的前几位名单，若输入数字大于实际可以输出的排名数，会报错，但经测试，并不影响实际功能需求。
    writ.writerow(item[i])  # 将前几名写入表格，

print('统计结果输出成功')
