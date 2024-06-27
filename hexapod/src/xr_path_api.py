#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-21 14:57:05
LastEditTime: 2023-12-25 09:46:21
LastEditors: Ceoifung
Description: 脚本路径
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''
from os import getcwd

path = getcwd()+"/"
Api = {
    "xrtsbase": path + "../build/xrtsbase.out",
    "colorTrack": path + "color_track.py",
    "sonic": path + "xr_ultrasonic.py",
    "colorRecognition": path + "color_recognition.py",
    "lineFollow": path + "linefollow.py",
    "qrcodeRecognition": path + "qrcode_recognition.py",
    "faceRecognition": path + "face_recognition.py",
    "xrjoy": path + "xr_joyutils.py",
    "killAll": path +"kill_all.sh",
    "voice": path + "xr_voice.py"
}
