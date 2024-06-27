#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-21 10:24:58
LastEditTime: 2022-04-09 09:54:46
LastEditors: Ceoifung
Description: 
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''

import os
import pigpio
import time
from xr_configparser import HandleConfig
path_data = os.path.dirname(os.path.realpath(__file__)) + '/data.ini'
cfgparser = HandleConfig(path_data)
import sys

class PWMServo():

    def __init__(self, pin=14):
        self.Pin = pin
        self.pi = pigpio.pi()
        if not self.pi.connected:
            os.system('echo "123456" | sudo -S pigpiod')
            self.pi = pigpio.pi()
        self.pi.set_PWM_frequency(self.Pin, 50)  # 设定14号引脚产生的pwm波形的频率为50Hz
        self.pi.set_PWM_range(self.Pin, 1800)

    def map(self, x, X_min, X_max, Y_min, Y_max):
        """
        Linear mapping between two ranges of values
        """
        X_range = X_max - X_min
        Y_range = Y_max - Y_min
        XY_ratio = X_range / Y_range
        y = ((x - X_min) / XY_ratio + Y_min) // 1
        return int(y)

    def setAngle(self, angle):
        print("设置舵机角度", angle)
        dutycycle = self.map(angle, 0, 180, 45, 225)  # 45:0.5ms对应舵机0度(0.5/20*1800) 225:2.5ms对应舵机180度(2.5/20*1800)
        self.pi.set_PWM_dutycycle(self.Pin, dutycycle)

    def move(self, start, end):
        for i in range(start,end):
            self.setAngle(i)

    def store(self, name, data):
        """
        存储舵机角度
        :return:
        """
        cfgparser.save_data("servo", name, data)

    def restore(self, name):
        """
        恢复舵机角度
        :return:
        """
        angle = cfgparser.get_data("servo", name)
        # print(type(angle))
        # print("angle: %s"%angle)
        self.setAngle(int(angle))
        return int(angle)


if __name__ == '__main__':
    pwmX = PWMServo(5)
    pwmY = PWMServo(6)
    try:
        pwmX.setAngle(int(sys.argv[1]))
        pwmY.setAngle(int(sys.argv[2]))
    except:
        print("请传入云台舵机的参数1和参数2")
