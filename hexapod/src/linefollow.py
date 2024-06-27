#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-22 09:32:46
LastEditTime: 2022-03-03 15:15:21
LastEditors: Ceoifung
Description: 摄像头巡线
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；


AI玩法:视觉巡线
功能:通过OpenCV调用摄像头，对视频画面中的黑线进行识别，并根据黑线在画面位置的偏移量，进行方向修正，最终实现通过摄像头跟随黑线行进的功能
'''

import cv2
import numpy as np
import time

import threading
import signal
import requests
import platform

import xr_command as xrcmd
from xr_pwm_servo import PWMServo
from xrtsclient import XRTSClient
from flask import Flask, Response
from xr_config import PWM_PIN_X, PWM_PIN_Y, getStreamUrl

app = Flask(__name__)

@app.route('/video')  # 这个地址返回视频流响应
def video_feed():
    return Response(background_task(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

last_turn = None
stream = None
# socket.io 客户端
xrtsc = XRTSClient()
# bytes = ''
bytes = bytes()
orgFrame = None
Running = False
get_image_ok = False
cv_ok = False
# 角度因子
angle_factor = 0.125
line_out = False
# 三个区域的加权值   从上到下
weight = [0, 0.5, 0.5]
weight_sum = 0
for w in range(len(weight)):
    weight_sum += weight[w]

# 机器人应该转的角度
deflection_angle = 0

# 暂停信号的回调
def cv_stop(signum, frame):
    global Running

    print("cv_ball_color_Stop")
    if Running is True:
        Running = False
    cv2.destroyWindow('cv_ball_frame')
    cv2.destroyAllWindows()


# 继续信号的回调
def cv_continue(signum, frame):
    global stream
    # global bytes
    global Running
    print("巡线")
    if Running is False:
        # 开关一下连接
        if stream:
            stream.close()
        stream = requests.get(getStreamUrl(), stream=True)
        # # 执行动作组复位位置
        Running = True


#   注册信号回调
if platform.system() != "Windows":
    print("当前不是window系统")
    signal.signal(signal.SIGTSTP, cv_stop)
    signal.signal(signal.SIGCONT, cv_continue)


# 要识别的颜色字典
color_dist = {'red': {'Lower': np.array([0, 50, 50]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'cyan': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              'black': {'Lower': np.array([0, 0, 0]), 'Upper': np.array([180, 255, 95])},
              }


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


# 显示图像线程
th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th1.start()


def get_x(img):
    '''
    范围区域图像内色块的中心坐标X
    :param img:
    :return:
    '''
    x = 0
    # 高斯模糊
    gs_frame = cv2.GaussianBlur(img, (5, 5), 0)
    # 转换颜色空间
    hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)
    # 查找颜色
    mask = cv2.inRange(hsv, color_dist['black']['Lower'], color_dist['black']['Upper'])
    # 腐蚀
    mask = cv2.erode(mask, None, iterations=2)
    # 膨胀
    mask = cv2.dilate(mask, None, iterations=2)
    # 查找轮廓
    # cv2.imshow('mask', mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts):
        c = max(cnts, key=cv2.contourArea)  # 找出最大的区域
        area = cv2.contourArea(c)
        # 获取最小外接矩形
        rect = cv2.minAreaRect(c)
        if area >= 500:
            xy = rect[0]
            xy = int(xy[0]), int(xy[1])
            cv2.circle(img, (xy[0], xy[1]), 3, (0, 255, 0), -1)
            x = xy[0]
            # box = cv2.cv.BoxPoints(rect)
            box = cv2.boxPoints(rect)
            # 数据类型转换
            box = np.int0(box)
            # 绘制轮廓
            cv2.drawContours(img, [box], 0, (0, 255, 255), 1)
    return x

def line():
    global cv_ok
    global deflection_angle
    global line_count, line_flag
    global last_turn
    global line_out
    while True:
        if cv_ok:
            # 如果偏角范围在-20 到 20之间，那么前进
            if -20 <= deflection_angle <= 20:
                xrtsc.sendData(xrcmd.FORWARD)
                print("ST")
            else:
                # 如果偏角范围除以15 < 0，说明中心线向左偏移，
                # 那么车子也就需要向左偏移，保持黑线处于屏幕中间
                if (deflection_angle / 15) < 0:
                    print("trun left")
                    xrtsc.sendData(xrcmd.LEFT)
                else:
                    print("turn right")
                    xrtsc.sendData(xrcmd.RIGHT)
                # 休眠0.15s，保证向左或向右的范围不要过大
                time.sleep(0.15)
            cv_ok = False
        else:
            if line_out:
                if last_turn == 'R':
                    print("last_turn")
                    xrtsc.sendData(xrcmd.RIGHT)
                    time.sleep(0.05)
                elif last_turn == 'L':
                    print("last_turn")
                    xrtsc.sendData(xrcmd.LEFT)
                    time.sleep(0.05)
                line_out = False
            else:
                time.sleep(0.05)


th2 = threading.Thread(target=line)
th2.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th2.start()


def camera_pos_init():#视觉巡线功能要求摄像头看着地面黑线，所以进入功能后，需要设定云台的角度
    pwmX = PWMServo(PWM_PIN_X)
    pwmY = PWMServo(PWM_PIN_Y)
    print("set pan servo 1")
    pwmX.setAngle(90)
    time.sleep(0.2)
    print("set pan servo 2")
    pwmY.setAngle(0)
    time.sleep(0.2)

def background_task():
    global orgFrame, get_image_ok, last_turn, line_out, deflection_angle
    global cv_ok, line_count, line_flag
    cv_continue(0, 0)
    line_center = 0.0
    camera_pos_init()
    while True:
        if orgFrame is not None and get_image_ok:
            t1 = cv2.getTickCount()
            f = orgFrame
            # 获取总图像的大小
            img_h, img_w = f.shape[:2]
            # 获取黑线的顶部，底部以及中部区间
            up_frame = f[0:65, 0:480]
            center_frame = f[145:210, 0:480]
            down_frame = f[290:355, 0:480]

            up_x = get_x(up_frame)
            center_x = get_x(center_frame)
            down_x = get_x(down_frame)

            if down_x != 0:
                line_center = down_x
                # print('c_x', deflection_angle)
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'

                d_line = line_center - img_w / 2
                # 计算直线偏角
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif center_x != 0:
                line_center = center_x
                # print('d_x', deflection_angle)
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'

                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x != 0 and down_x != 0:
                line_center = (up_x + down_x) / 2
                # print('ud_x', deflection_angle)
                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x != 0:
                line_center = up_x
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'
                # print('u_x', deflection_angle)
                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x == 0 and down_x == 0 and center_x == 0:
                line_out = True

            # 画屏幕中心十字
            cv2.line(f, (220, 180), (260, 180), (255, 255, 0), 1)
            cv2.line(f, (240, 160), (240, 200), (255, 255, 0), 1)
            # cv2.namedWindow("cv_ball_frame", cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('cv_ball_frame', f)
            cv2.waitKey(1)
            get_image_ok = False
            t2 = cv2.getTickCount()
            time_r = (t2 - t1) / cv2.getTickFrequency() * 1000
            # print("%sms" % time_r)
            # 打开视频画面
            ret, buffer = cv2.imencode('.jpg', f)
            f = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + f + b'\r\n\r\n')
        else:
            time.sleep(0.01)

if __name__ == '__main__':
    xrtsc.run() 
    try:
        app.run("0.0.0.0", 5052, debug=True)
    except KeyboardInterrupt:
        xrtsc.stop()

