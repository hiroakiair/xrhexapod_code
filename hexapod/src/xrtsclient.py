#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-18 16:59:43
LastEditTime: 2022-04-01 17:15:37
LastEditors: Ceoifung
Description: socket.io client
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''

from time import sleep

import sys
import json
import socketio
from xr_config import SOCTET_HOST

class XRTSClient():
    """socket.io 客户端,AI玩法通过这个类把命令发到xrtsengine.py
    """
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.running = True
        self.sio = None
        

    def run(self):
        self.sio = socketio.Client()
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("connect_error", self.connect_error)
        self.sio.connect(SOCTET_HOST)

    def stop(self):
        self.running = False
        self.sio.disconnect()

    def connect_error(self, data):
        print("The connection failed!", data)

    def connect(self):
        print('connection established: ', self.sio.sid)

    def disconnect(self):
        print('disconnected from server')

    def sendData(self, cmd):
        if self.sio:
            self.sio.emit("ctl_message", cmd)

    def getDefault(self):
        return self.sio

if __name__ == "__main__":
    client = XRTSClient()
    client.run()
    ########################################################################
    # 注意：以下程序不要做任何改动，这关乎USB-monitor检测摄像头热插拔，消息发送处理
    # Attention: Do not modify any code, 'cause usb monitor will use it
    try:
        client.sendData(json.loads(sys.argv[1]))
    except:
        print("请传入至少一个参数")
    sleep(0.2)
    client.stop()
    #########################################################################
    # 不要在这里添加任何代码
    # Do no add any code here
