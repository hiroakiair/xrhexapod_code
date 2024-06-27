#coding=utf-8
'''
Author: Ceoifung
Date: 2022-03-31 10:35:28
LastEditTime: 2022-04-13 14:18:40
LastEditors: Ceoifung
Description: 手柄控制机器人运动
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
'''
import os
import struct
import array
from fcntl import ioctl
import threading
import sys
import time
from xr_pwm_servo import PWMServo
from xrtsclient import XRTSClient
import xr_command as xrcmd
from xr_config import PWM_PIN_X, PWM_PIN_Y


class XRJoyUtils:
    """手柄操作数据读取类
    """
    def __init__(self, js='/dev/xrjoy', db=0):
        # 定义xrrobot按键
        # button
        self.joy_state = {'FLAG': 0,  # 是否有数据变更
                          'L1': 0, 'L2': 0, 'L2_PUSH': 0.0, 'R1': 0, 'R2': 0, 'R2_PUSH': 0.0,  # 侧面按键
                          'A': 0, 'B': 0, 'X': 0, 'Y': 0,  # 右侧按钮
                          'SELECT': 0, 'START': 0,  # 功能按钮
                          'LEFT': 0,'RIGHT': 0, 'UP': 0, 'DOWN': 0,
                          'LX_PUSH': 0, 'LY_PUSH': 0.0,
                          'RX_PUSH': 0, 'RY_PUSH': 0.0,
                          'LX_UP': 0, 'LX_DOWN': 0, 'LX_LEFT': 0, 'LX_RIGHT': 0,
                          'RX_UP': 0, 'RX_DOWN': 0, 'RX_LEFT': 0, 'RX_RIGHT': 0,
                          "LX_PRESSED": 0, "RX_PRESSED": 0}
        self.axis_names = {
            0x00: 'LX_PUSH',  # 左侧摇杆左右
            0x01: 'LY_PUSH',  # 左侧摇杆上下
            0x02: 'RX_PUSH',  # 右侧摇杆左右
            0x05: 'RY_PUSH',  # 右侧摇杆上下
            0x09: 'R2_PUSH',  # R2按下力度
            0x0a: 'L2_PUSH',  # L2按下力度
            0x10: 'LEFT_RIGHT',  # 左侧按键左右值
            0x11: 'UP_DOWN',    # 左侧按键上下值
        }
        # These constants were borrowed from linux/input.h
        self.button_names = {
            0x130: 'A',
            0x131: 'B',
            0x133: 'X',
            0x134: 'Y',
            0x136: 'L1',
            0x137: 'R1',
            0x138: 'L2',
            0x139: 'R2',
            0x13a: 'SELECT',
            0x13b: 'START',
            0x13d: 'LX_PRESSED',
            0x13e: 'RX_PRESSED'
        }
        self.axis_map = []
        self.button_map = []
        self.db = db  # 调试信息打印，1：打印，0：不打印

        if sys.version_info > (3, 0):  # 兼容python3.6
            self.py_v3 = True
        else:
            self.py_v3 = False
        # 1、搜寻打印设备信息
        self.find_js()
        # 2、Open the joystick device.
        self.js = js
        print('Opening %s...' % self.js)
        self.jsdev = open(self.js, 'rb')
        # 3、打印设备名称
        self.print_dev()
        time.sleep(0.1)
        self.setAsynRecv()
        time.sleep(2)
        # 防止数据错误
        self.joy_state["FLAG"] = 0


    def find_js(self):
        # Iterate over the joystick devices.
        print('Available devices:')
        for dev in os.listdir('/dev/input'):
            if dev.startswith('js'):
                print('  /dev/input/%s' % (dev))

    def print_dev(self):
        # Get the device name.
        # buf = bytearray(63)
        buf = array.array('B', [0] * 64)
        # JSIOCGNAME(len)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf)
        for i in range(buf.count(0)):
            buf.remove(0)
        js_name = ''.join('%s' % chr(i) for i in buf)
        print('Device name: %s' % js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf)  # JSIOCGAXES
        num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf)  # JSIOCGBUTTONS
        num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf)  # JSIOCGAXMAP

        for axis in buf[:num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf)  # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            # if btn in self.button_names.keys():
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)

        if self.db:  # 调试信息
            print('%d axes found: %s' % (num_axes, ', '.join(self.axis_map)))
            print('%d buttons found: %s' %
                  (num_buttons, ', '.join(self.button_map)))

    def setAsynRecv(self):
        if self.py_v3:
            self.analyThd = threading.Thread(
                target=self.joy_analy, daemon=True)
            print('py3 start joy_analy')
            self.analyThd.start()
        else:
            self.analyThd = threading.Thread(target=self.joy_analy)
            self.analyThd.setDaemon(True)
            print('py2 start joy_analy')
            self.analyThd.start()

    def joy_analy(self):
        # Main event loop
        while True:
            evbuf = self.jsdev.read(8)
            if evbuf:
                tim, value, type, number = struct.unpack(
                    'IhBB', evbuf)  # 图中标出的数字是指此处的 number，用来判断此数据是哪个按键的变化
                if self.db:  # 调试信息
                    print('value = 0x%02x, type= 0x%02x, number = 0x%02x ' %
                          (value, type, number))
                    if type & 0x80:
                        if self.db:  # 调试信息
                            print("(initial)")
                        else:
                            pass
                if type & 0x01:
                    self.joy_state['FLAG'] = 1
                    button = self.button_map[number]
                    # print(button, value)
                    if "unknown" not in button:
                        # fvalue = value
                        self.joy_state[button] = value
                        # print(button)
                    if self.db:  # 调试信息
                        button = self.button_map[number]
                        if button:
                            # button_states[button] = value
                            if value:
                                print("%s pressed" % (button))
                            elif value == 0:
                                print("%s released" % (button))

                if type & 0x02:
                    self.joy_state['FLAG'] = 1

                    axis = self.axis_map[number]

                    if axis and "unknown" not in axis:
                        
                        fvalue = 0
                        if value > 10000:
                            fvalue = value / 32767.0
                        elif value < -10000:
                            fvalue = value / 32767.0
                        if axis == "UP_DOWN":
                            self.joy_state["UP"] = 1 if fvalue < 0 else 0
                            self.joy_state["DOWN"] = 1 if fvalue > 0 else 0
                        if axis == "LEFT_RIGHT":
                            self.joy_state["LEFT"] = 1 if fvalue < 0 else 0
                            self.joy_state["RIGHT"] = 1 if fvalue > 0 else 0
                        if axis == "LX_PUSH":
                            self.joy_state["LX_LEFT"] = 1 if fvalue < 0 else 0
                            self.joy_state["LX_RIGHT"] = 1 if fvalue > 0 else 0
                        if axis == "LY_PUSH":
                            self.joy_state["LX_UP"] = 1 if fvalue < 0 else 0
                            self.joy_state["LX_DOWN"] = 1 if fvalue > 0 else 0
                        if axis == "RX_PUSH":
                            self.joy_state["RX_LEFT"] = 1 if fvalue < 0 else 0
                            self.joy_state["RX_RIGHT"] = 1 if fvalue > 0 else 0
                        if axis == "RY_PUSH":
                            self.joy_state["RX_UP"] = 1 if fvalue < 0 else 0
                            self.joy_state["RX_DOWN"] = 1 if fvalue > 0 else 0
                        self.joy_state[axis] = fvalue

                    if self.db:  # 调试信息
                        axis = self.axis_map[number]
                        if axis:
                            if value > 10000:
                                fvalue = value / 32767.0
                                # axis_states[axis] = fvalue
                                print("%s: %.3f" % (axis, fvalue))
                            elif value < -10000:
                                fvalue = value / 32767.0
                                # axis_states[axis] = fvalue
                                print("%s: %.3f" % (axis, fvalue))
                            elif value == 0:
                                print("%s released" % (axis))

if __name__ == "__main__":
    # 手柄操控类
    joy = XRJoyUtils("/dev/input/js0")
    xrtsc = XRTSClient()
    servoX = PWMServo(PWM_PIN_X)
    servoY = PWMServo(PWM_PIN_Y)
    preState = ""
    nowState = "s"
    xrtsc.run()
    angleX = 90
    angleY = 0
    isFastRun = False
    isClimbMode = False
    try:
        while True:
            if joy.joy_state["FLAG"]:
                buf = joy.joy_state.copy()
                joy.joy_state["FLAG"] = 0
                # if buf["L1"]:
                if buf["LX_UP"] and buf["LX_LEFT"]:
                    # print("左前")
                    nowState = 'fl'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.FORWARD_LEFT)
                elif buf["LX_UP"] and buf["LX_RIGHT"]:
                    # print("右前")
                    nowState = 'fr'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.FORWARD_RIGHT)
                elif buf["LX_DOWN"] and buf["LX_LEFT"]:
                    # print("左后")
                    nowState = 'bl'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.BACKWARD_LEFT)
                elif buf["LX_DOWN"] and buf["LX_RIGHT"]:
                    # print("右后")
                    nowState = 'br'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.BACKWARD_RIGHT)
                elif buf["LX_UP"]:
                    # print("前进")
                    nowState = 'f'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.FORWARD)
                elif buf["LX_DOWN"]:
                    # print("后退")
                    nowState = 'b'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.BACKWARD)
                elif buf["LX_LEFT"]:
                    # print("左平移")
                    nowState = 'sl'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.SHIFT_LEFT)
                elif buf["LX_RIGHT"]:
                    # print("右平移")
                    nowState = 'sr'
                    if preState != nowState:
                        preState = nowState
                        xrtsc.sendData(xrcmd.SHIFT_RIGHT)
                elif buf["L2"] and buf["UP"]:
                    if not isFastRun:
                        isFastRun = True
                        # print("快速前进")
                        xrtsc.sendData(xrcmd.FORWARD_FAST)

                elif buf["L2"] and buf["R1"] and buf["R2"] and buf["L1"]:
                    if not isFastRun:
                        isExhibitionMode = True
                        print("展厅模式")
                        xrtsc.sendData(xrcmd.EXHIBITION_MODE)

                elif buf["R2"] and buf["UP"]:
                    if not isClimbMode:
                    # print("匍匐前进")
                        xrtsc.sendData(xrcmd.CLIMB)
                elif buf["R1"] and buf["UP"]:
                    # print("高位前进")
                    xrtsc.sendData(xrcmd.CLIMB_FAST)
                elif buf["RX_PUSH"] != 0:
                    angleX = min(
                        180, max(0, (angleX + 5) if buf["RX_PUSH"] < 0 else (angleX - 5)))
                    # print(angleX)
                    servoX.setAngle(angleX)
                elif buf["RY_PUSH"] != 0:
                    angleY = min(
                        180, max(0, (angleY + 5) if buf["RY_PUSH"] < 0 else (angleY - 5)))
                    # print(angleY)
                    servoY.setAngle(angleY)
                elif buf["LX_PRESSED"]:
                    # print("保存舵机角度")
                    servoX.store("anglex", angleX)
                    servoY.store("angley", angleY)
                elif buf["RX_PRESSED"]:
                    angleX = servoX.restore("anglex")
                    angleY = servoY.restore("angley")
                else:
                    if buf["UP"]:
                        # print("前进")
                        xrtsc.sendData(xrcmd.FORWARD)
                    elif buf["DOWN"]:
                        # print("后退")
                        xrtsc.sendData(xrcmd.BACKWARD)
                    elif buf["LEFT"]:
                        # print("左转")
                        xrtsc.sendData(xrcmd.LEFT)
                    elif buf["RIGHT"]:
                        # print("右转")
                        xrtsc.sendData(xrcmd.RIGHT)
                    elif buf["Y"]:
                        # print("舞蹈动作1")
                        xrtsc.sendData(xrcmd.DANCING1)
                    elif buf["X"]:
                        # print("舞蹈动作2")
                        xrtsc.sendData(xrcmd.DANCING2)
                    elif buf["B"]:
                        # print("舞蹈动作3")
                        xrtsc.sendData(xrcmd.DANCING3)
                    elif buf["A"]:
                        # print("舞蹈动作4")
                        xrtsc.sendData(xrcmd.DANCING4)
                    else:
                        # print("停止")
                        nowState = 's'
                        preState = ''
                        isFastRun = False
                        isExhibitionMode = False
                        isClimbMode = False
                        xrtsc.sendData(xrcmd.STOP)
    except Exception as e:
        print(e)
    xrtsc.stop()
