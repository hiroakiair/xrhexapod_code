#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-22 11:05:00
LastEditTime: 2022-03-03 15:15:48
LastEditors: Ceoifung
Description: 二维码识别
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；


AI玩法:二维码识别
功能：通过OpenCV和pyzbar库，调用摄像头对特定的二维码图片进行识别，并根据识别结果发送命令给机器人底层执行动作
'''
import cv2
import time
import threading
import numpy as np
import requests
import pyzbar.pyzbar as pyzbar
from xr_config import getStreamUrl
from xrtsclient import XRTSClient
import xr_command as xrcmd

from flask import Flask, Response


img_w = 480
img_h = 360

orgFrame = None
stream = None
bytes = bytes()
Running = False
get_image_ok = False
BARCODE_DATE = None		# 二维码识别数据
BARCODE_TYPE = None		# 二维码识别数据类型
# socket.io 客户端
xrtsc = XRTSClient()

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
    print('CV二维码识别')
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

isRec = False # 识别到二维码的标志位
# 如果要处理自己识别到的内容，可以在这里编写自定义的动作
def loop_action():
    global BARCODE_DATE, isRec
    while True:#根据识别到的二维码结果，发送控制命令到xrtsengine.py进行处理
        if isRec and BARCODE_DATE != None:
            # print("处理相关动作")
            if BARCODE_DATE == "forward":
                print("go forward")
                xrtsc.sendData(xrcmd.FORWARD)
            elif BARCODE_DATE == "back":
                print("go back")
                xrtsc.sendData(xrcmd.BACKWARD)
            elif BARCODE_DATE == "left":
                print("turn left")
                xrtsc.sendData(xrcmd.LEFT)
            elif BARCODE_DATE == "right":
                print("turn right")
                xrtsc.sendData(xrcmd.RIGHT)
            elif BARCODE_DATE == "shiftLeft":
                print("shift left")
                xrtsc.sendData(xrcmd.SHIFT_LEFT)
            elif BARCODE_DATE == "shiftRight":
                print("shift right")
                xrtsc.sendData(xrcmd.SHIFT_RIGHT)
            elif BARCODE_DATE == "forwardLeft":
                print("forward left")
                xrtsc.sendData(xrcmd.FORWARD_LEFT)
            elif BARCODE_DATE == "forwardRight":
                print("forward right")
                xrtsc.sendData(xrcmd.FORWARD_RIGHT)
            elif BARCODE_DATE == "backwardLeft":
                print("backward left")
                xrtsc.sendData(xrcmd.BACKWARD_LEFT)
            elif BARCODE_DATE == "backwardRight":
                print("backward right")
                xrtsc.sendData(xrcmd.BACKWARD_RIGHT)
            else:
                pass
            time.sleep(2)
            xrtsc.sendData(xrcmd.STOP)
        time.sleep(0.01)

th2 = threading.Thread(target=loop_action)
th2.setDaemon(True)
th2.start()

def decodeDisplay(image):
    """识别二维码

    Args:
        image ([type]): 传递的摄像头画面

    Returns:
        [type]: 贴图后的摄像头图案
    """
    global BARCODE_DATE, BARCODE_TYPE, isRec
    barcodes = pyzbar.decode(image)
    if barcodes == [] :
        isRec = False
        BARCODE_DATE = None
        BARCODE_TYPE = None
    else:
        for barcode in barcodes:
            isRec = True
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            BARCODE_DATE = barcode.data.decode("utf-8")
            BARCODE_TYPE = barcode.type
            text = "{} ({})".format(BARCODE_DATE, BARCODE_TYPE)
            cv2.putText(image, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 125), 2)
    return image


def background_task():
    global orgFrame,  get_image_ok
    cv_continue(0, 0)
    while True:
        if orgFrame is not None and get_image_ok:
            res = orgFrame
            # 要先将每一帧先转换成灰度图，在灰度图中进行查找
            gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)  # 转为灰度图像
            img = decodeDisplay(gray)  # 识别二维码
            get_image_ok = False
            cv2.waitKey(1)
            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
        else:
            time.sleep(0.01)


if __name__ == '__main__':
    xrtsc.run()
    try:
        app.run("0.0.0.0", 5052, debug=True)
    except KeyboardInterrupt:
        print("ctrl + c")
        xrtsc.stop()
    
    
