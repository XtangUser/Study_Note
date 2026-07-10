1. 分两个终端运行（推荐，方便看日志）
终端 1：joy 读取手柄硬件
bash
运行
ros2 run joy joy_node --ros-args -p device:=/dev/input/js0 -p deadzone:=0.06
deadzone 消除摇杆轻微漂移，数值 0.05~0.1 之间可调
终端 2：摇杆转 /cmd_vel 速度指令
bash
运行
ros2 run teleop_twist_joy teleop_node --ros-args \
-p axis_linear.x:=1 \
-p axis_angular.yaw:=0 \
-p require_enable_button:= false \
-p enable_button:=0 \
-p scale_linear:=0.6 \
-p scale_angular:=1.5
参数说明：
axis_linear.x=1 左摇杆上下控制前进后退
axis_angular.yaw=0 左摇杆左右控制转向
enable_button=0 A 键按住才生效
scale 数值越大车辆速度越快