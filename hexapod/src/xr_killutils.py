#coding=utf-8
'''
Author: Ceoifung
Date: 2022-02-15 15:13:18
LastEditTime: 2022-02-25 17:01:37
LastEditors: Ceoifung
Description: killer程序，服务于启动或结束python程序
XiaoRGEEK All Rights Reserved, Powered by Ceoifung

深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
商务合作：微信18126008008；电话：18588257008；

'''

from platform import platform
import psutil
import os

class KillUtils():
    def __init__(self) -> None:
        pass

    def kill(self, script):
        """结束python进程

        Args:
            script ([string]): python文件名称

        Returns:
            [bool]: 返回操作结果
        """
        pids = psutil.pids()
        hasProcess = False
        try:
            for pid in pids:
                p = psutil.Process(pid)
                
                if script in p.cmdline():
                    print(p.cmdline())
                    hasProcess = True
                    cmd = "echo '123456' | sudo -S kill -9 " + str(pid)
                    # if platform.system() == "Windows":
                    #     cmd = "taskkill /f /pid "+ str(pid)
                    print(cmd)
                    ret = os.system(cmd)
                    if ret == 0:
                        print("kill process successfully")
            if not hasProcess:
                print("找不到相关的进程")
            return hasProcess
        except Exception as e:
            print(e)
            return False


    def start(self, script):
        """启动python程序
        
        Args:
            script ([string]): 传入的python文件名称

        Returns:
            [bool]: 返回操作结果
        """
        try:
            ret = os.system("python " + script + " &")
            if ret == 0:
                print("运行script成功")
                return True
            else:
                print("运行失败")
                return False
        except Exception as e:
            print(e)
            return True

    def exec(self, script):
        """启动os命令行
        
        Args:
            script ([string]): 传入的linux命令

        Returns:
            [bool]: 返回操作结果
        """
        try:
            ret = os.system(script + " &")
            if ret == 0:
                print("运行script成功")
                return True
            else:
                print("运行失败")
                return False
        except Exception as e:
            print(e)
            return True
