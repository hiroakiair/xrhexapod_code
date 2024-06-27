# coding=utf-8
'''
Author: Ceoifung
Date: 2022-09-24 15:48:10
LastEditTime: 2023-09-22 09:33:35
LastEditors: Ceoifung
Description: 读取python文件键值
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
'''
import json
from os import getcwd, path

def readConf(filename="xrhexapodr1"):
    cfgPath = f"{path.abspath(getcwd())}/../build/{filename}.conf"
    print(f"servo offset config file path: {cfgPath}")
    with open(cfgPath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# if __name__=="__main__":
#     data = readConf()
#     print(data)
