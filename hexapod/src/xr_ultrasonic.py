#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-23 09:36:29
LastEditTime: 2022-02-26 09:54:41
LastEditors: Ceoifung
Description: 超声波避障
XiaoRGEEK All Rights Reserved, Powered by Ceoifung
深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

AI玩法:超声波跟随与避障
功能:使用超声波测量前方的障碍物距离，如果障碍物大于30cm并且小于50cm，则机器人前进，如果障碍物距离小于30cm，则后退
即实现了机器人跟随障碍物前后运动的效果
如果障碍物范围超过了50cm，则机器人处于停止状态
'''


from xr_command import BACKWARD, FORWARD, STOP
import time

import RPi.GPIO as GPIO
from xrtsclient import XRTSClient
import xr_config as Cfg

# 设置引脚模式
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 设置超声波引脚
TRIG = Cfg.TRIG  	# 超声波发射脚位
ECHO = Cfg.ECHO  	# 超声波接收脚位
# 超声波脚初始化使能
GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)  			# 超声波模块发射端管脚设置trig
GPIO.setup(ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  	# 超声波模块接收端管脚设置echo
DISTANCE = 0  			# 超声波测距值

class Ultrasonic(object):
	def __init__(self):
		pass

	def digital_write(self, gpio, status):
		"""
		设置gpio端口为电平
		参数：gpio为设置的端口，status为状态值只能为True(高电平)，False(低电平)
		"""
		GPIO.output(gpio, status)


	def digital_read(self, gpio):
		"""
		读取gpio端口的电平
		"""
		return GPIO.input(gpio)

	def get_distance(self):
		"""
		获取超声波距离函数,有返回值distance，单位cm
		"""
		global DISTANCE
		time_count = 0
		time.sleep(0.01)
		self.digital_write(TRIG, True)  # 拉高超声波Trig引脚
		time.sleep(0.000015)  # 发送10um以上高电平方波
		self.digital_write(TRIG, False)  # 拉低
		while not self.digital_read(ECHO):  # 等待Echo引脚由低电平变成高电平
			pass
		t1 = time.time()  # 记录Echo引脚高电平开始时间点
		while self.digital_read(ECHO):  # 等待Echo引脚由低电平变成低电平
			if time_count < 2000:  # 超时检测，防止死循环
				time_count = time_count + 1
				time.sleep(0.000001)
				pass
			else:
				print("NO ECHO receive! Please check connection")
				break
		t2 = time.time()  # 记录Echo引脚高电平结束时间点
		# Echo引脚高电平持续时间就是超声波由发射到返回的时间，即用时间x声波速度/2等于单程即超声波距物体距离值
		distance = (t2 - t1) * 340 / 2 * 100
		# t2-t1时间单位s,声波速度340m/s,x100将距离值单位m转换成cm
		# print("distance is %d" % distance)  # 打印距离值
		if distance < 500:  # 正常检测距离值
			# print("distance is %d"%distance)
			DISTANCE = round(distance, 2)
			return DISTANCE
		else:
			# print("distance is 0")  # 如果距离值大于5m,超出检测范围
			DISTANCE = 0
			return 0

if __name__ == "__main__":
	sonic = Ultrasonic()
	xrtsc = XRTSClient()
	xrtsc.run()
	try:
		while True:
			dis = sonic.get_distance()
			# print(dis)
			# 距离大于25cm,等于0的时候是远距离超过超声波测距范围
			if 50 < dis or dis == 0:
				print("---没有遇到障碍物---")
				xrtsc.sendData(STOP)
			else:
				if dis > 30:
					xrtsc.sendData(FORWARD)
				else:
					if dis > 0:
						xrtsc.sendData(BACKWARD)
			time.sleep(0.2)
	except KeyboardInterrupt:
		print("ctrl + c")
		xrtsc.stop()
