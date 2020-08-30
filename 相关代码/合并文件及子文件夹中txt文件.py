# 本知识来源于：https://sourl.cn/LR2N5W
# 本程序支持合并文件夹及其子文件中txt的合并

import os

#运行Python过程中输入文件夹路径及合并后的文件路径及名称
#rootdir = raw_input("the old path: ")
#newfile = raw_input("the new path and filename: ")
rootdir = r'D:\系统自带文件夹\新建文件夹 (5)\python合并txt文件\20190101'   #输入需要合并文件的文件夹路径
newfile = r'D:\系统自带文件夹\新建文件夹 (5)\python合并txt文件\合并后文档.txt'  #输入合并后文件的存储路径
paths = []   #存放文件夹（含子文件夹）下所有文件的路径及名称

#获取文件夹（含子文件夹）下所有文件的路径及名称
for root, dirs, files in os.walk(rootdir):
    for file in files:
        paths.append(os.path.join(root, file).encode('utf-8')) #支持中文名称

#创建新的文件
f = open(newfile,'w',encoding='utf-8')
# 将之前获取到的文件夹（含子文件夹）下所有文件的路径及名称里的内容写进新建的文件里
for i in paths:
    for line in open(i,encoding='utf-8'):
        f.writelines(line)
f.close()   #保存并关闭新建的文件
