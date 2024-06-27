# coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-21 11:08:08
LastEditTime: 2023-12-25 09:46:48
LastEditors: Ceoifung
Description: 
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''

import eventlet
import socketio
import json
from xr_pwm_servo import PWMServo
from xr_killutils import KillUtils
import threading
from time import sleep
from xr_path_api import Api
import xr_command as xrcmd
from xr_config import PWM_PIN_X, PWM_PIN_Y
from xr_readutils import readConf

killer = KillUtils()

class XRTSEngine(threading.Thread):
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.pwmX = PWMServo(PWM_PIN_X)  # 云台的水平方向舵机
        self.pwmY = PWMServo(PWM_PIN_Y)  # 云台的竖直方向舵机
        self.pwmX.setAngle(90)  # 设置云台水平方向舵机默认角度为90度
        self.pwmY.setAngle(0)  # 设置云台竖直方向舵机默认角度为0度
        self.app = socketio.WSGIApp(self.sio, static_files={
            '/': {'content_type': 'text/html', 'filename': 'index.html'}
        })
        self.server = None

    def run(self):
        self.sio.on("connect", self.connect)
        self.sio.on("disconnected", self.disconnect)
        self.sio.on("ctl_message", self.ctl_message)
        try:
            # 在5051端口建立监听服务器，监听来自于APP或xrtsclient.py的消息
            eventlet.wsgi.server(eventlet.listen(('', 5051)), self.app)
        except:
            print("ctrl + c")
            self.sio.disconnect(self.sid)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def connect_error(self, data):
        print("The connection failed!", data)

    def connect(self, sid, environ):
        self.sid = sid
        print('connection established: ', sid)

    def disconnect(self, sid):
        print('disconnected', sid)

    def hexstring2bytes(self, cmd):
        """16进制字符串转bytes数组

        Args:
            cmd ([type]): 字符串

        Returns:
            [type]: bytes
        """
        data = []
        for i in range(int(len(cmd)/2)):
            i = i * 2
            data.append(int(cmd[0*i+i: i+2], 16))
        return data

    def ctl_message(self, id, data):  # 控制命令处理中心，所有来自于APP或AI玩法的命令，都会发到这里进行下一步处理
        msg = data
        try:
            if type(data) == str:
                msg = json.loads(data)
            if msg["type"] == "app":  # 如果控制命令来自于APP
                buf = self.hexstring2bytes(msg["data"])
                if buf[1] == 0x27:  # 0x27是云台舵机控制命令
                    self.pwmX.setAngle(buf[2])
                    # if buf[3] < 90:
                    #     buf[3] = 90
                    self.pwmY.setAngle(buf[3])
                elif buf[1] == 0x28:  # 0x28是云台舵机角度保存命令
                    self.pwmX.store("anglex", buf[2])
                    self.pwmY.store("angley", buf[3])
                elif buf[1] == 0x29:  # 0x29是云台舵机角度恢复命令
                    self.pwmX.restore("anglex")
                    self.pwmY.restore("angley")
            elif msg["type"] == "gui":  # '更多'玩法里面的命令
                print("gui message", msg)
                self.sio.emit("gui_message", json.dumps(data))
            elif msg["type"] == "control":  # 基本动作控制命令
                # print("bypass to control", msg["data"])
                # 将基本动作控制命令发送到res_message主题，然后转发到机器人底层驱动
                self.sio.emit("res_message", msg["data"])
            elif msg["type"] == 'config':
                try:
                    conf = readConf()
                    self.sio.emit("gui_message", {
                        "type": "config",
                        "data": conf
                    })
                except:
                    # 如果读取不到舵机校准配置文件，那么通知APP
                    self.sio.emit("gui_message", json.dumps({
                        "type": "gui",
                        "data": "Cannot read servo configuration"
                    }))

            elif msg["type"] == "ai":  # AI玩法命令
                # print(msg["data"])
                # 启用AI功能
                self.sio.emit("ctl_message", xrcmd.STOP)
                aidata = json.loads(msg["data"])
                status = aidata["status"]
                script = aidata["script"]
                if status and script != "default":
                    print(status)
                    killer.start(Api[script])
                else:
                    if script != "default":
                        killer.kill(Api[script])
        except Exception as e:
            print("数据解析报错", e)


if __name__ == '__main__':
    server = XRTSEngine()
    server.setDaemon(True)
    server.start()
    # 启用xrtsbase.out六足底层控制程序
    killer.exec(Api["xrtsbase"])
    killer.start(Api["xrjoy"])
    killer.start(Api["voice"])
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt as e:
        print("ctrl + c")
        # killer.kill(Api["xrtsbase"])
        # killer.kill(Api["xrjoy"])
        killer.exec(Api["killAll"])
        server.stop()
    server.join()
