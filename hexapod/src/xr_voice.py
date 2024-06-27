#!/usr/bin/env python
# coding:utf-8
'''
Author: Ceoifung
Date: 2023-12-19 17:54:03
LastEditors: Ceoifung
LastEditTime: 2023-12-25 10:16:16
Description: XiaoRGEEK All Rights Reserved. Copyright © 2023
'''
import serial
import time
import threading
# import signal
# import sys
from xrtsclient import XRTSClient
import xr_command as xrcmd

xrts = None
class Voice(object):
    def __init__(self, port="/dev/ttyAMA1", baud=115200):
        self.ser = serial.Serial(port, baud)    # /dev/ttyUSB0
        # signal.signal(signal.SIGINT, self.signal_handler)
        self.running = True

    def voice_start(self):
        print("run voice_start")
        while self.running:
            while self.ser.inWaiting() > 0:
                time.sleep(0.05)
                n = self.ser.inWaiting()
                myout = self.ser.read(n)
                self.get_voice(myout)
            time.sleep(0.5)

    # def signal_handler(self, signal, frame):
    #     print("ctrl+c")
    #     self.running = False
    #     self.ser.close()
    #     self.send_data(xrcmd.STOP)
    #     pass

    def get_voice(self, data):
        if len(data) < 3:  # 不符合接收长度标准
            print('data len %d:'%len(data))
        if data[0] == 0xff and data[len(data)-1] == 0xff:  # 如果包头和包尾是0xff则符合小二科技通信协议
            # print("data[1]=",data[1])
            if data[1] == 0x00:
                print("normal mode")
                self.send_data(xrcmd.STOP)
            elif data[1] == 0x01:
                print("go forward")
                self.send_data(xrcmd.FORWARD)
            elif data[1] == 0x02:
                print("go backward")
                self.send_data(xrcmd.BACKWARD)
            elif data[1] == 0x03:
                print("turn left")
                self.send_data(xrcmd.LEFT)

            elif data[1] == 0x04:
                print("turn right")
                self.send_data(xrcmd.RIGHT)
            elif data[1] == 0x05:
                print("forward left")
                self.send_data(xrcmd.FORWARD_LEFT)
            elif data[1] == 0x06:
                print("forward right")
                self.send_data(xrcmd.FORWARD_RIGHT)
            elif data[1] == 0x07:
                print("backward left")
                self.send_data(xrcmd.BACKWARD_LEFT)
            elif data[1] == 0x08:
                print("backward right")
                self.send_data(xrcmd.BACKWARD_RIGHT)
            elif data[1] == 0x09:
                print("shift left")
                self.send_data(xrcmd.SHIFT_LEFT)
            elif data[1] == 0x0a:
                print("shift right")
                self.send_data(xrcmd.SHIFT_RIGHT)
    

    def send_data(self, key):
        if xrtsc:
            xrtsc.sendData(key)
            time.sleep(1)
            xrtsc.sendData(xrcmd.STOP)

    def release(self):
        self.ser.close()

if __name__ == "__main__":
    ser = Voice()
    th1 = threading.Thread(target=ser.voice_start)
    th1.setDaemon(True)
    th1.start()
    xrtsc = XRTSClient()
    xrtsc.run()
    try:
        while True:
            time.sleep(1)
    except:
        print("down...")
        xrtsc.sendData(xrcmd.STOP)
    th1.join()
    xrtsc.stop()

    # while True:
    #     ser.voice_start()
