#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-22 09:32:04
LastEditTime: 2022-03-03 15:18:03
LastEditors: Ceoifung
Description: 颜色追踪
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

AI玩法:颜色追踪
功能:通过OpenCV调用摄像头识别颜色卡片，并驱动云台跟随卡片转动
'''

import cv2
import time
import threading
import numpy as np
import requests
import math
from xr_pid import PID
from xr_pwm_servo import PWMServo
from flask import Flask, Response
from xr_config import PWM_PIN_X, PWM_PIN_Y, getStreamUrl

img_w = 480
img_h = 360

orgFrame = None
stream = None
bytes = bytes()
Running = False
get_image_ok = False

pwmX = PWMServo(PWM_PIN_X)
pwmY = PWMServo(PWM_PIN_Y)

app = Flask(__name__)


@app.route('/video')  # 这个地址返回视频流响应
def video_feed():
    return Response(background_task(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def cv_stop(signum, frame):
    global Running

    print("cv_ball_color_Stop")
    if Running is True:
        Running = False
    cv2.destroyWindow('cv_ball_frame')
    cv2.destroyAllWindows()


def cv_continue(signum, frame):
    global stream
    global Running
    print('CV云台颜色追踪')
    if Running is False:
        # 开关一下连接
        if stream:
            stream.close()
        # stream = urllib.urlopen(
        #     "http://127.0.0.1:8080/?action=stream?dummy=param.mjpg")
        # bytes = ''
        stream = requests.get(getStreamUrl(), stream=True)
        # # 执行动作组复位位置
        Running = True


def get_image():
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


def background_task():
    global get_image_ok, orgFrame
    cv_continue(0, 0)
    pwmX.setAngle(90)
    pwmY.setAngle(0)
    # 实例化一个X轴坐标的PID算法PID参数：第一个代表pid的P值，二代表I值,三代表D值
    X_pid = PID(0.03, 0.09, 0.0005)
    X_pid.setSampleTime(0.005)  # 设置PID算法的周期
    # 设置PID算法的预值点，即目标值，这里160指的是屏幕框的x轴中心点，x轴的像素是320，一半是160
    X_pid.setPoint(160)

    # 实例化一个X轴坐标的PID算法PID参数：第一个代表pid的P值，二代表I值,三代表D值
    Y_pid = PID(0.035, 0.08, 0.002)
    Y_pid.setSampleTime(0.005)  # 设置PID算法的周期
    # 设置PID算法的预值点，即目标值，这里160指的是屏幕框的y轴中心点，y轴的像素是320，一半是160
    Y_pid.setPoint(160)
    angle_X = 90
    angle_Y = 90

    while True:
        if orgFrame is not None and get_image_ok:
            
            # res = orgFrame
            res = cv2.GaussianBlur(
                orgFrame, (5, 5), 0)                     # 高斯模糊
            hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(
                hsv, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
            mask = cv2.erode(mask, None, iterations=2)
            # 膨胀
            mask = cv2.dilate(mask, None, iterations=2)
            # cv2.imshow('mask', mask)
            # 查找轮廓
            cnts = cv2.findContours(
                mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            # center_x = 240.0
            # center_y = 180.0
            if len(cnts) > 0:
                for c in cnts:
                    # if the contour is not sufficiently large, ignore it
                    area = cv2.contourArea(c)
                    if area < 1600:  # 获取形状块的面积大小，过滤小面积
                        continue
                    else:
                        cnt = max(cnts, key=cv2.contourArea)
                        (x, y), radius = cv2.minEnclosingCircle(cnt)
                        cv2.circle(res, (int(x), int(y)), int(
                            radius), (255, 0, 255), 2)  # 画出一个圆
                        X_pid.update(x)  # 将X轴数据放入pid中计算输出值
                        Y_pid.update(y)  # 将Y轴数据放入pid中计算输出值
                        # print("X_pid.output==%d"%X_pid.output)		#打印X输出
                        # print("Y_pid.output==%d"%Y_pid.output)		#打印Y输出
                        angle_X = math.ceil(
                            angle_X + 1 * X_pid.output)  # 更新X轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                        angle_Y = math.ceil(
                            angle_Y + 0.8 * Y_pid.output)  # 更新Y轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度

                        # 限制X轴最大角度为0-180
                        angle_X = min(max(angle_X, 0), 180)
                        # 限制Y轴最大角度为0-180
                        angle_Y = min(max(angle_Y, 0), 180)
                        # print("angle_X---->> %d" % angle_X)  # 打印X轴舵机角度
                        # print("angle_Y---->> %d" % angle_Y)  # 打印Y轴舵机角度
                        pwmX.setAngle(angle_X)
                        pwmY.setAngle(angle_Y)
            # 在屏幕中心画十字
            cv2.line(res, (220, 180),
                     (260, 180), (255, 255, 0), 1)
            cv2.line(res, (240, 160),
                     (240, 200), (255, 255, 0), 1)
            # 打开视频画面
            # cv2.imshow('cv_ball_frame', res)
            ret, buffer = cv2.imencode('.jpg', res)
            res = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + res + b'\r\n\r\n')
            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)

if __name__ == '__main__':
    app.run("0.0.0.0", 5052, debug=True)
