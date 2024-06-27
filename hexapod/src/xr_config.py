#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-25 16:28:03
LastEditTime: 2022-03-11 11:29:26
LastEditors: Ceoifung
Description: 
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''
import platform

# 设置超声波引脚,BCM编码
TRIG = 9  	# 超声波发射脚位
ECHO = 10  	# 超声波接收脚位
# pwm云台舵机引脚,BCM编码
PWM_PIN_X = 5
PWM_PIN_Y = 6
# socket.io server address
SOCTET_HOST = "http://localhost:5051"

def getStreamUrl():
    '''
    获取视频流，如果处于windows系统，那么使用测试的视频流，否则使用树莓派系统的mjpeg视频流
    '''
    if platform.system() == "Windows":
        return "http://192.168.88.100:8081/?action=stream"
    else:
        return "http://127.0.0.1:8080/?action=stream"
