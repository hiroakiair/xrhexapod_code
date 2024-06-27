/**
 * @file xrtsbase.cpp
 * @author ceoifung (ccf19960919@163.com)
 * @brief xiaorgeek socket.io client
 * @version 0.1
 * @date 2022-02-17
 *深圳市小二极客科技有限公司（小R科技）版权所有；您可以任意修改本代码，并应用于个人作品，但禁止用于商业盈利目的，小R科技保留诉诸法律追责的权利！
 *商务合作：微信18126008008；电话：18588257008；
 * @copyright Copyright (c) 2022
 *
 */
#include <iostream>
#include <sio_client.h>
#include <stdio.h>
#include "hexutils.h"
#include <hexapod/xr_hexapod_loop.h>
#include <hexapod/hexapod.h>
#include "custom.h"

using namespace std;

sio::client h;
string host = "http://127.0.0.1:5051";
bool is_custom_mode = false;
#define PWM "PWM"   // PWM舵机
#define UART "Uart" //串行总线舵机
char *buffer; //解析出来的串口数据
int len; //数据长度
bool recvData = false; //判断数据接收标志位

//机器人类型
#define XR_ROBOT_TYPE_HEXAPOD "XR_ROBOT_TYPE_HEXAPOD"     //六足
#define XR_ROBOT_TYPE_QUADRUPED "XR_ROBOT_TYPE_QUADRUPED" //四足
XR_MovementMode _mode = XR_MOVEMENT_STANDBY;              //默认为立正待机模式

/**
 * @brief Create a Message object
 *
 * @param type 数据类型
 * @param data 实际要传递的数据
 * @return sio::message::ptr 对象
 */
sio::message::ptr createMessage(string type, string data)
{
    sio::message::ptr send_data(sio::object_message::create());
    map<string, sio::message::ptr> &map = send_data->get_map();
    map.insert(make_pair("type", sio::string_message::create(type)));
    map.insert(make_pair("data", sio::string_message::create(data)));
    return send_data;
}

/**
 * @brief 解析通信协议
 *
 * @param buffer 接收到的通信数据
 * @param len 数据长度
 */
void *decodeData(/*const char *buffer, int len*/ void *m)
{
    while (1)
    {
        if (recvData)
        {
            recvData = false;
            if (buffer[0] == 0xff && buffer[len - 1] == 0xff)
            {
                // cout << "通信协议正确" << endl;

                if (buffer[1] == 0x18)
                {
                    is_custom_mode = false;
                    switch (buffer[2])
                    {
                    case 0x00:
                        cout << "XR_MOVEMENT_STANDBY" << endl;
                        _mode = XR_MOVEMENT_STANDBY;
                        break;
                    case 0x01:
                        cout << "XR_MOVEMENT_FORWARD" << endl;
                        _mode = XR_MOVEMENT_FORWARD;
                        break;
                    case 0x02:
                        cout << "XR_MOVEMENT_BACKWARD" << endl;
                        _mode = XR_MOVEMENT_BACKWARD;
                        break;
                    case 0x03:
                        cout << "XR_MOVEMENT_TURNLEFT" << endl;
                        _mode = XR_MOVEMENT_TURNLEFT;
                        break;
                    case 0x04:
                        cout << "XR_MOVEMENT_TURNRIGHT" << endl;
                        _mode = XR_MOVEMENT_TURNRIGHT;
                        break;
                    case 0x05:
                        cout << "XR_MOVEMENT_SHIFTLEFTFRONT" << endl;
                        _mode = XR_MOVEMENT_SHIFTLEFTFRONT;
                        break;
                    case 0x06:
                        cout << "XR_MOVEMENT_SHIFTLEFTREAR" << endl;
                        _mode = XR_MOVEMENT_SHIFTLEFTREAR;
                        break;
                    case 0x07:
                        cout << "XR_MOVEMENT_SHIFTRIGHTFRONT" << endl;
                        _mode = XR_MOVEMENT_SHIFTRIGHTFRONT;
                        break;
                    case 0x08:
                        cout << "XR_MOVEMENT_SHIFTRIGHTREAR" << endl;
                        _mode = XR_MOVEMENT_SHIFTRIGHTREAR;
                        break;
                    case 0x09:
                        cout << "XR_MOVEMENT_CRAWL" << endl;
                        _mode = XR_MOVEMENT_CRAWL;
                        break;
                    case 0x0A:
                        cout << "XR_MOVEMENT_ROTATEX" << endl;
                        _mode = XR_MOVEMENT_ROTATEX;
                        break;
                    case 0x0B:
                        cout << "XR_MOVEMENT_ROTATEY" << endl;
                        _mode = XR_MOVEMENT_ROTATEY;
                        break;
                    case 0x0C:
                        cout << "XR_MOVEMENT_ROTATEZ" << endl;
                        _mode = XR_MOVEMENT_ROTATEZ;
                        break;
                    case 0x0D:
                        cout << "XR_MOVEMENT_TWIST" << endl;
                        _mode = XR_MOVEMENT_TWIST;
                        break;
                    case 0xE1:
                        cout << "XR_MOVEMENT_FORWARDFAST" << endl;
                        _mode = XR_MOVEMENT_FORWARDFAST;
                        break;
                    case 0xE3:
                        cout << "XR_MOVEMENT_SHIFTLEFT" << endl;
                        _mode = XR_MOVEMENT_SHIFTLEFT;
                        break;
                    case 0xE4:
                        cout << "XR_MOVEMENT_SHIFTRIGHT" << endl;
                        _mode = XR_MOVEMENT_SHIFTRIGHT;
                        break;
                    case 0xE9:
                        cout << "XR_MOVEMENT_CLIMB" << endl;
                        _mode = XR_MOVEMENT_CLIMB;
                        break;
                    default:
                        _mode = XR_MOVEMENT_STANDBY;
                        break;
                    }
                }
                else if (buffer[1] == 0x19)
                {
                    is_custom_mode = true;
                    cout << "send msg" << endl;
                    switch (buffer[2])
                    {
                    case 0x00:
                        cout << "Action:XR_HexapodAction_Hello" << endl;
                        XR_HexapodAction_Hello();
                        break;
                    case 0x01:
                        cout << "Action:XR_HexapodAction_Bye" << endl;
                        XR_HexapodAction_Bye();
                        break;
                    case 0x02:
                        cout << "Action:XR_HexapodAction_Defense" << endl;
                        XR_HexapodAction_Defense();
                        break;
                    case 0x03:
                        cout << "Action:XR_HexapodAction_FortuneCat" << endl;
                        XR_HexapodAction_FortuneCat();
                        break;
                    case 0x04:
                        cout << "Action:XR_HexapodAction_Surrender" << endl;
                        XR_HexapodAction_Surrender();
                        break;
                    case 0x05:
                        cout << "Action:XR_HexapodAction_Provocation" << endl;
                        XR_HexapodAction_Provocation();
                        break;
                    case 0x06:
                        cout << "Action:XR_HexapodAction_Stretch" << endl;
                        XR_HexapodAction_Stretch();
                        break;
                    case 0x07:
                        cout << "Action:XR_HexapodAction_Warmup" << endl;
                        XR_HexapodAction_Warmup();
                        break;
                    case 0x08:
                        cout << "Action:XR_HexapodAction_Bench" << endl;
                        XR_HexapodAction_Bench();
                        break;
                    case 0x09:
                        cout << "Action:XR_HexapodAction_NoNoNo" << endl;
                        XR_HexapodAction_NoNoNo();
                        break;
                    case 0x0A:
                        cout << "Action:XR_HexapodAction_Respect" << endl;
                        XR_HexapodAction_Respect();
                        break;
                    case 0x0B:
                        cout << "Action:XR_HexapodAction_PlayDead" << endl;
                        XR_HexapodAction_PlayDead();
                        break;
                    default:
                        _mode = XR_MOVEMENT_STANDBY;
                        break;
                    }
                    _mode = XR_MOVEMENT_STANDBY;
                    is_custom_mode = false;
                    // if (h.socket() != null)
                    h.socket()->emit("ctl_message", createMessage("gui", "done"));
                }
                else if (buffer[1] == 0x20)
                {
                    is_custom_mode = false;
                    /* code */
                    cout << "设置单条腿" << endl;
                    XR_Set_Angle_For_Leg(buffer[2], buffer[3], buffer[4], buffer[5]);
                }
                else if (buffer[1] == 0x21)
                {
                    cout << "参数校准" << endl;
                    hexapod::Hexapod.calibrationSet(buffer[2], buffer[3], buffer[4], buffer[5]);
                }
                else if (buffer[1] == 0x22)
                {
                    cout << "参数保存" << endl;
                    hexapod::Hexapod.calibrationSave();
                }
                else if (buffer[1] == 0x23)
                {
                    cout << "恢复默认的出厂参数" << endl;
                    hexapod::Hexapod.calibrationReset();
                }
                else if (buffer[1] == 0x25)
                {
                    cout << "调整六足高度" << endl;
                    int gain = buffer[2] - 10;
                    if (gain > 15)
                        gain = 15;
                    if (gain < -15)
                        gain = -15;
                    hexapod::Hexapod.setHightGain(gain);
                }
                else if (buffer[1] == 0x26)
                {
                    cout << "调整六足速度" << endl;
                    int speed = buffer[2];
                    if (speed > 120)
                        speed = 120;
                    if (speed < 5)
                        speed = 5;

                    XR_Action_Speed(speed);
                }
                else if (buffer[1] == 0xA0)//展厅模式，自动循环执行一些动作
                {
                    XR_HexapodAction_Exhibition_Mode();
                }
            }
            else
            {
                cout << "通信协议解析错误，请检查包头包尾以及数据长度是否为7" << endl;
            }
        }
    }
}

/**
 * @brief 监听res_message消息
 *
 * @param ev event
 */
void onNewMessage(sio::event &ev)
{
    auto data = ev.get_message();
    auto cmd = data->get_string();
    cout << "监听到消息: " << cmd << endl;
    if (cmd.length() % 2 != 0)
    {
        cout << "通信协议长度异常，已返还结果给app" << endl;
        h.socket()->emit("ctl_message", createMessage("gui", "length of command error"));
    }
    else
    {
        // char *buf = hexstringToBytes(cmd);
        buffer = hexstringToBytes(cmd);
        len = int(cmd.length() / 2);
        recvData = true;
        // decodeData(hexstringToBytes(cmd), int(cmd.length() / 2));
    }
}

/**
 * @brief 客户端重连事件
 *
 * @param test1
 * @param test2
 */
void onClientReconnect(unsigned test1, unsigned test2)
{
    cout << "reconnect socket:" << test1 << ":" << test2 << endl;
}

/**
 * @brief 客户端断开连接事件
 *
 * @param nsp
 */
void onClientDisconnect(string const &nsp)
{
    cout << "close socket:" << nsp << endl;
    // h.socket()->off_all();
}

/**
 * @brief 客户端成功反馈
 *
 * @param nsp
 */
void onClientConnected(string const &nsp)
{
    cout << "open socket:" << nsp << endl;
}

/**
 * @brief 循环运行六足机器人动作
 *
 * @param m
 * @return void*
 */
void *loop_action(void *m)
{
    printf("----run action loop----\n");
    while (1)
    {
        if (!is_custom_mode)
        {
            XR_Run_Action_loop(_mode);
        }
    }
}

int main()
{
    h.socket()->on("res_message", &onNewMessage);
    h.set_socket_open_listener(&onClientConnected);
    h.set_socket_close_listener(&onClientDisconnect);
    h.set_reconnect_listener(&onClientReconnect);
    h.connect(host);

    hexapod::Hexapod.setRobotType(XR_ROBOT_TYPE_HEXAPOD);//设置机器人的模式为六足模式
    XR_Action_Speed(20);                                   //初始化速度为5
    hexapod::Hexapod.init(
        _mode == XR_MOVEMENT_STANDBY,
        "www.xiao-r.com by liuviking",
        UART,
        true);//六足核心驱动初始化，请勿修改参数!
    pthread_t *msg = (pthread_t *)malloc(2 * sizeof(pthread_t));
    pthread_create(&msg[0], NULL, loop_action, (void *)0);
    pthread_create(&msg[1], NULL, decodeData, (void *)0);

    while (1)
    {
        /* code */
	//std::cout << "Running Code" << std::endl;
	XR_Run_Action_loop(XR_MOVEMENT_FORWARD);
    }
    h.socket()->off_all();
    h.socket()->close();
    free(msg);
    return 0;
}
