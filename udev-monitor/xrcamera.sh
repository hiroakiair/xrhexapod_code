#! /bin/sh
###
 # @Author: Ceoifung
 # @Date: 2022-03-30 14:48:27
 # @LastEditTime: 2022-04-01 16:30:30
 # @LastEditors: Ceoifung
 # @Description: 启动mjpg-streamer
 # XiaoRGEEK All Rights Reserved, Powered by Ceoifung
### 
#set -e
case $1 in
    "start")
    _pid=$(netstat -anp|grep 8080|awk '{printf $7}'|cut -d/ -f1)
    if [ ! -n "$_pid" ]; then
        echo "no such process"
    else
        printf "mjpg-streamer pid is %s\n" "$_pid"
        kill -9 $_pid
        echo "mjpg-streamer is stopped"
    fi
    sleep 0.5
    cd /home/pi/work/mjpg-streamer-master/mjpg-streamer-experimental/
    ./start.sh &
    ;;
    "stop")
    _pid=$(netstat -anp|grep 8080|awk '{printf $7}'|cut -d/ -f1)
    if [ ! -n "$_pid" ]; then
        echo "no such process"
    else
        printf "mjpg-streamer pid is %s\n" "$_pid"
        kill -9 $_pid
        echo "mjpg-streamer is stopped"
    fi
    ;;
    *)
    exit 1;
esac


