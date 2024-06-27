#coding=utf-8
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；


AI玩法:颜色识别
功能:通过OpenCV调用摄像头识别卡片颜色（红绿蓝三色），如果颜色与预设的颜色相符，则驱动云台做出点头动作，否则做出摇头动作

'''

import cv2
import time
import threading
import numpy as np

import requests
from xr_pwm_servo import PWMServo
from xr_config import PWM_PIN_X, PWM_PIN_Y

from xr_command import STOP
from flask import Flask, Response

# from xrtsclient import XRTSClient
from xr_config import getStreamUrl

pwmX = PWMServo(PWM_PIN_X)
pwmY = PWMServo(PWM_PIN_Y)
color = 0
rR = 0
rG = 0
rB = 0

client = None
orgFrame = None
stream = None
bytes = bytes()
Running = False
get_image_ok = False
# flask推流处理
app = Flask(__name__)


@app.route('/video')  # 这个地址返回视频流响应
def video_feed():
    return Response(background_task(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def cv_continue():
    global stream
    global Running
    print(' CV颜色识别')
    if Running is False:
        # 开关一下连接
        if stream:
            stream.close()
        stream = requests.get(getStreamUrl(), stream=True)
        # # 执行动作组复位位置
        Running = True


def get_image():
    """获取图像视频流，并进行mjpeg视频解码
    """
    global Running
    global orgFrame
    global bytes
    global get_image_ok
    while True:
        if Running:
            try:
                if(stream.status_code == 200):
                    for chunk in stream.iter_content(chunk_size=1024):
                        bytes += chunk
                        a = bytes.find(b'\xff\xd8')#mjpeg格式视频流的开头为0xff 0xd8
                        b = bytes.find(b'\xff\xd9')#mjpeg格式视频流的结尾为0xff 0xd9
                        if a != -1 and b != -1:
                            jpg = bytes[a:b+2]
                            bytes = bytes[b+2:]
                            orgFrame = cv2.imdecode(np.frombuffer(   # 对图片进行解码
                                jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                            orgFrame = cv2.resize(
                                orgFrame, (480, 360), interpolation=cv2.INTER_LINEAR)  # 将图片缩放到
                            get_image_ok = True
            except Exception as e:
                print(e)
                continue
        else:
            time.sleep(0.01)


th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th1.start()

# 红绿蓝的HSV值字典
color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              }


def run_action(type):
    if type == 0:  # 摄像头回中
        pwmX.setAngle(90)
        time.sleep(0.1)
        pwmY.setAngle(0)
        time.sleep(0.1)
    elif type == 1:  # 点头
        pwmY.setAngle(90)
        time.sleep(0.2)
        pwmY.setAngle(0)
        time.sleep(0.2)
    elif type == 2:  # 摇头
        pwmX.setAngle(20)
        time.sleep(0.2)
        pwmX.setAngle(160)
        time.sleep(0.2)

color = ""
isRec = False # 筛选符合条件的识别结果

def loop_action():
    global color, isRec
    while True:
        if isRec:
            if color == 'red':
                print("red")
                run_action(1)
                run_action(1)
                run_action(0)
            elif color == 'blue':
                print("blue")
                run_action(2)
                run_action(2)
                run_action(0)
            elif color == 'green':
                print("green")
                run_action(2)
                run_action(2)
                run_action(0)
            else:
                run_action(0)


th2 = threading.Thread(target=loop_action)
th2.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th2.start()

def background_task():
    global orgFrame, get_image_ok, color, isRec
    cv_continue()
    
    run_action(0)
    while True:
        if orgFrame is not None and get_image_ok:
            frame = orgFrame
            res = cv2.GaussianBlur(
                frame, (5, 5), 0)  # 高斯模糊
            hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
            for i in color_dist:
                mask = cv2.inRange(
                    hsv, color_dist[i]['Lower'], color_dist[i]['Upper'])
                mask = cv2.erode(mask, None, iterations=2)
                # 膨胀
                mask = cv2.dilate(mask, None, iterations=2)
                # cv2.imshow('mask', mask)
                # 查找轮廓
                cnts = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                if len(cnts) > 0:
                    c = max(cnts, key=cv2.contourArea)
                    # 求出最小外接圆  原点坐标x, y  和半径
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    if radius >= 50:  # 半径大于50才算，然后在屏幕画圆
                        cv2.circle(res, (int(x), int(y)),
                                   int(radius), (0, 255, 255), 2)
                        color = i # 将识别到的颜色赋值给全局变量
                        isRec = True # 设置检测的标志位，交由后台线程做操作
                    else:
                        isRec = False
                        color = ""
                    # 在图片上添加当前的颜色值    
                    text = "color: {}".format(i)
                    cv2.putText(res, text, (int(x), int(y - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 125), 2)
            # cv2.imshow('cv_ball_frame', res)
            ret, buffer = cv2.imencode('.jpg', res)
            res = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + res + b'\r\n\r\n')
            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)

# xrtsc = XRTSClient()
if __name__ == '__main__':
    # xrtsc.run()
    try:
        app.run("0.0.0.0", 5052, debug=True)
    except KeyboardInterrupt:
        print("ctrl + c")
        # xrtsc.stop()
