# libHexapodR1.so使用说明

libHexapodR1是小R科技开发的六足控制库，已经安装在系统的`/usr/lib`目录下，使用步骤如下：

### 头文件说明

```c++
#include <hexapod/xr_hexapod_loop.h>
#include <hexapod/hexapod.h>
```

- **xr_hexapod_loop.h**内容如下：

```c++
void XR_Action_Speed(int);//设置速度
void XR_Factory_Setup(void);//出厂校准状态
void XR_Run_Action_loop(int);//动作循环
void XR_Servo_Test(void);//测试舵机
/**
 * @brief 让指定腿的指定关节旋转指定角度(leg范围0-5，joint范围0-2，angle范围0-180)
 * 
 * @param leg 从六足后面朝前看，右前方的腿为0，顺时针分别为0.1.2.3.4.5
 * @param angle0 身体(alpha)
 * @param angle1 中段(beta)
 * @param angle2 足尖(gamma)
 */
void XR_Set_Angle_For_Leg(int leg, float angle0,float angle1,float angle2);
//运动状态
enum XR_MovementMode
{
    XR_MOVEMENT_STANDBY = 0, //待机
    XR_MOVEMENT_FORWARD,     //前进
    XR_MOVEMENT_FORWARDFAST, //快速前进
    XR_MOVEMENT_BACKWARD,    //后退
    XR_MOVEMENT_TURNLEFT,    //左转
    XR_MOVEMENT_TURNRIGHT,   //右转
    XR_MOVEMENT_SHIFTLEFT,   //左平移
    XR_MOVEMENT_SHIFTRIGHT,  //右平移
    XR_MOVEMENT_CLIMB,       //高姿态爬行
    XR_MOVEMENT_CRAWL,       //匍匐爬行
    XR_MOVEMENT_ROTATEX,     //围绕X轴旋转跳舞
    XR_MOVEMENT_ROTATEY,     //围绕Y轴旋转跳舞
    XR_MOVEMENT_ROTATEZ,     //围绕Z轴旋转跳舞
    XR_MOVEMENT_TWIST,       //扭动
    XR_MOVEMENT_SHIFTLEFTFRONT,//左前方平移
    XR_MOVEMENT_SHIFTRIGHTFRONT,//右前方平移
    XR_MOVEMENT_SHIFTLEFTREAR,//左后方平移
    XR_MOVEMENT_SHIFTRIGHTREAR,//右后方平移
    XR_MOVEMENT_TOTAL,
};
```

- **hexapod.h**主要内容如下：

```c++
void calibrationSave(); // 参数保存到配置文件
void calibrationReset();// 重置所有参数
void calibrationSet(int legIndex, int partIndex, int offset, int scale);    // 更新舵机设置参数
```

### 简单示例

```cpp
#include <hexapod/xr_hexapod_loop.h>
#include <hexapod/hexapod.h>

#define PWM "PWM"   // PWM舵机
#define UART "Uart" //串行总线舵机

//机器人类型
#define XR_ROBOT_TYPE_HEXAPOD "XR_ROBOT_TYPE_HEXAPOD"     //六足
#define XR_ROBOT_TYPE_QUADRUPED "XR_ROBOT_TYPE_QUADRUPED" //四足
XR_MovementMode _mode = XR_MOVEMENT_STANDBY;              //默认为立正待机模式

int main(){
    hexapod::Hexapod.setRobotType(XR_ROBOT_TYPE_HEXAPOD); //设置机器人的模式为六足模式
    XR_Action_Speed(5);                                   //初始化速度为5
    hexapod::Hexapod.init(
        _mode == XR_MOVEMENT_STANDBY,
        "www.xiao-r.com by liuviking",
        UART,
        true); //六足核心驱动初始化，请勿修改参数!
    return 0;
}
```

### Makefile

一个标准的引用libHexapodR1.so的Makefile编写示例如下：

```shell
all:
	g++ -Wall -o app.out *.cpp -lHexapodR1

clean:
	rm -rf *.out *o *so
```

编译：**make**

成功后会在当前目录输出app.out可执行程序，`./app.out`即可运行查看效果