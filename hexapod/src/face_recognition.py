#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-22 09:32:04
LastEditTime: 2022-03-03 15:06:37
LastEditors: Ceoifung
Description: 人脸检测
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；


AI玩法:人脸识别
功能:通过OpenCV调用摄像头识别人脸，并驱动云台跟随人脸移动

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
    print('CV云台人脸识别')
    if Running is False:
        # 开关一下连接
        if stream:
            stream.close()
        stream = requests.get(getStreamUrl(), stream=True)
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
    global orgFrame, get_image_ok
    cv_continue(0, 0)
    # 初始化舵机角度
    pwmX.setAngle(90)
    pwmY.setAngle(0)
    # 实例化一个X轴坐标的PID算法PID参数：第一个代表pid的P值，二代表I值,三代表D值
    X_pid = PID(0.03, 0.09, 0.0005)
    X_pid.setSampleTime(0.005)  # 设置PID算法的周期
    # 设置PID算法的预值点，即目标值，这里160指的是屏幕框的x轴中心点，x轴的像素是480，一半是160
    X_pid.setPoint(240)

    # 实例化一个X轴坐标的PID算法PID参数：第一个代表pid的P值，二代表I值,三代表D值
    Y_pid = PID(0.035, 0.08, 0.002)
    Y_pid.setSampleTime(0.005)  # 设置PID算法的周期
    # 设置PID算法的预值点，即目标值，这里160指的是屏幕框的y轴中心点，y轴的像素是360，一半是160
    Y_pid.setPoint(160)
    angle_X = 90
    angle_Y = 90
    face_cascade = cv2.CascadeClassifier('/home/pi/work/hexapod/src/face.xml')
    while True:
        # get_color = False
        if orgFrame is not None and get_image_ok:
            res = orgFrame
            # 要先将每一帧先转换成灰度图，在灰度图中进行查找
            gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray)  # 查找人脸
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # if the contour is not sufficiently large, ignore it
                    # 参数分别是“目标帧”，“矩形”，“矩形大小”，“线条颜色”，“宽度”
                    cv2.rectangle(res, (x, y), (x + h, y + w), (0, 255, 0), 2)
                    result = (x, y, w, h)
                    x_middle = result[0] + w / 2  # x轴中心
                    y_middle = result[1] + h / 2  # y轴中心
                    # cnt = max(cnts, key=cv2.contourArea)
                    # (x, y), radius = cv2.minEnclosingCircle(cnt)
                    # cv2.circle(res, (int(x), int(y)), int(
                    #     radius), (255, 0, 255), 2)  # 画出一个圆
                    X_pid.update(x_middle)  # 将X轴数据放入pid中计算输出值
                    Y_pid.update(y_middle)  # 将Y轴数据放入pid中计算输出值
                    # print("X_pid.output==%d"%X_pid.output)		#打印X输出
                    # print("Y_pid.output==%d"%Y_pid.output)		#打印Y输出
                    angle_X = math.ceil(
                        angle_X + 1 * X_pid.output)  # 更新X轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                    angle_Y = math.ceil(
                        angle_Y + 0.8 * Y_pid.output)  # 更新Y轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度

                    # 限制X轴最大角度为0-180
                    angle_X = min(180, max(0, angle_X))
                    # 限制Y轴最大角度为0-180
                    angle_Y = min(180, max(0, angle_Y))
                    # print("angle_X---->> %d" % angle_X)  # 打印X轴舵机角度
                    # print("angle_Y---->> %d" % angle_Y)  # 打印Y轴舵机角度
                    pwmX.setAngle(angle_X)
                    pwmY.setAngle(angle_Y)

            # 打开视频画面
            ret, buffer = cv2.imencode('.jpg', res)
            res = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + res + b'\r\n\r\n')
            # cv2.imshow('cv_ball_frame', res)
            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)


if __name__ == '__main__':
    app.run("0.0.0.0", 5052, debug=True)
