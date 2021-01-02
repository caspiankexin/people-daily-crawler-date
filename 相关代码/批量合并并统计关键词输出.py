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