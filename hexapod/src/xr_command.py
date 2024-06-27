#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-21 09:24:45
LastEditTime: 2022-03-31 17:09:20
LastEditors: Ceoifung
Description: 控制hexapod的命令
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''
STOP = {
    "type": "control",
    "data": "FF1800000000FF"
}

FORWARD = {
    "type": "control",
    "data": "FF1801000000FF"
}
BACKWARD = {
    "type": "control",
    "data": "FF1802000000FF"
}
LEFT = {
    "type": "control",
    "data": "FF1803000000FF"
}
RIGHT = {
    "type": "control",
    "data": "FF1804000000FF"
}
# 左前
FORWARD_LEFT = {
    "type": "control",
    "data": "FF1805000000FF"
}
# 左后
BACKWARD_LEFT = {
    "type": "control",
    "data": "FF1806000000FF"
}
# 右前
FORWARD_RIGHT = {
    "type": "control",
    "data": "FF1807000000FF"
}
# 右后
BACKWARD_RIGHT = {
    "type": "control",
    "data": "FF1808000000FF"
}
# 快速前进
FORWARD_FAST = {
    "type": "control",
    "data": "FF18E1000000FF"
}
# 展厅模式
# showroom mode
EXHIBITION_MODE = {
    "type": "control",
    "data": "FFA001000000FF"
}
# 左平移
SHIFT_LEFT = {
    "type": "control",
    "data": "FF18E3000000FF"
}
# 右平移
SHIFT_RIGHT = {
    "type": "control",
    "data": "FF18E4000000FF"
}
# 匍匐前进
# 這って進む
CLIMB = {
    "type": "control",
    "data": "FF1809000000FF"
}
# 高姿态前进
CLIMB_FAST = {
    "type": "control",
    "data": "FF18E9000000FF"
}
# 舞蹈动作

DANCING1 = {
    "type": "control",
    "data": "FF180A000000FF"
}
DANCING2 = {
    "type": "control",
    "data": "FF180B000000FF"
}

DANCING3 = {
    "type": "control",
    "data": "FF180C000000FF"
}
DANCING4 = {
    "type": "control",
    "data": "FF180D000000FF"
}
