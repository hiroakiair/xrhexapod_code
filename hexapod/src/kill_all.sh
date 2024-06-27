#!/bin/sh
###
 # @Author: Ceoifung
 # @Date: 2023-09-22 09:58:47
 # @LastEditors: Ceoifung
 # @LastEditTime: 2023-12-25 10:05:03
 # @Description: XiaoRGEEK All Rights Reserved. Copyright © 2023
### 
#  结束掉python程序进程
pidnum=`ps -ef|grep xrts | grep -v grep|awk '{print $2}'`
if [ "$pidnum" != "" ]
	then
	for i in $pidnum
	do
    echo "start kill -9 $i"
    sudo kill -9 $i
	done
fi
# 结束手柄程序
pidnum=`ps -ef|grep xr_joyutils.py | grep -v grep|awk '{print $2}'`
if [ "$pidnum" != "" ]
	then
	for i in $pidnum
	do
    echo "start kill -9 $i"
    sudo kill -9 $i
	done
fi
# 结束语音程序
pidnum=`ps -ef|grep xr_voice.py | grep -v grep|awk '{print $2}'`
if [ "$pidnum" != "" ]
	then
	for i in $pidnum
	do
    echo "start kill -9 $i"
    sudo kill -9 $i
	done
fi

