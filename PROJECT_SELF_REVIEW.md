# ROS2 差速机器人项目自我总结与巩固路线

## 1. 项目自我描述

这个项目是我基于 ROS2 搭建的差速移动机器人仿真与导航工程。项目目前主要集中在 `my_robot_description` 功能包中，完成了机器人模型描述、Gazebo 仿真、ros2_control 控制器、SLAM 建图、地图保存与 Nav2 自主导航配置。

通过这个项目，我已经从“只知道 ROS2 概念”推进到“能够把机器人模型、传感器、控制器、仿真环境、建图和导航串成完整流程”的阶段。这个工程不是单纯写一个节点，而是一个偏系统集成的机器人项目，重点在于理解各个模块之间的数据流、TF 关系和参数匹配。

## 2. 当前项目结构

```text
src/my_robot_description/
├── CMakeLists.txt
├── package.xml
├── READ.MD
├── config/
│   ├── controllers.yaml
│   ├── nav2.yaml
│   └── slam.yaml
├── launch/
│   ├── display.launch.py
│   ├── navigation.launch.py
│   └── slam.launch.py
├── maps/
│   ├── my_map.pgm
│   └── my_map.yaml
├── rviz/
│   └── robot.rviz
├── urdf/
│   ├── base_core.xacro
│   ├── robot_properties.xacro
│   ├── base_body.xacro
│   ├── drive_wheel.xacro
│   ├── caster_wheel.xacro
│   ├── sensor_lidar.xacro
│   ├── sensor_camera.xacro
│   ├── gazebo_plugin.xacro
│   └── materials.xacro
└── worlds/
    ├── my_world.world
    └── model/
```

当前工程没有自定义 Python/C++ 节点源码，主要能力由 ROS2 标准包、Gazebo 插件、控制器配置、Xacro 模型和 Nav2 参数共同完成。

## 3. 我已经掌握的核心知识

### 3.1 ROS2 功能包与安装规则

我已经理解 `ament_cmake` 功能包的基本结构：

- `package.xml` 描述包名、依赖和构建类型。
- `CMakeLists.txt` 通过 `install(DIRECTORY ...)` 把 `launch`、`urdf`、`rviz`、`config`、`worlds`、`maps` 等资源安装到 `share/my_robot_description`。
- Launch 文件中通过 `FindPackageShare("my_robot_description")` 获取安装后的资源路径。

巩固要求：

1. 能解释为什么修改 `urdf`、`launch`、`config` 后通常需要重新 `colcon build`。
2. 能说清楚源码目录和 `install/share` 目录的关系。
3. 能独立补全 `package.xml` 中缺失的运行依赖。

### 3.2 Xacro 模块化机器人建模

我已经把机器人模型拆成多个 Xacro 文件：

- `base_core.xacro` 是总入口。
- `robot_properties.xacro` 管理尺寸、质量和惯量宏。
- `base_body.xacro` 定义 `base_footprint`、`base_link`、`upper_base_link`。
- `drive_wheel.xacro` 用宏生成左右驱动轮。
- `caster_wheel.xacro` 用宏生成前后支撑轮。
- `sensor_lidar.xacro` 定义雷达。
- `sensor_camera.xacro` 定义相机和 `camera_optical_link`。
- `gazebo_plugin.xacro` 接入 Gazebo、ros2_control、雷达和相机插件。

我已经掌握的关键点：

- `link` 表示刚体，`joint` 表示连接关系。
- `visual` 管显示，`collision` 管碰撞，`inertial` 管物理仿真。
- 差速轮是 `continuous` joint，支撑轮和传感器是 `fixed` joint。
- `base_footprint` 适合作为导航平面基准，`base_link` 表示机器人主体。
- Xacro 宏可以减少重复建模代码。

巩固要求：

1. 手画 TF 树：`base_footprint -> base_link -> upper_base_link -> lidar_link/camera_link`。
2. 独立解释 `wheel_radius`、`wheel_separation`、`base_frame_id` 对控制和导航的影响。
3. 修改一个参数，例如底盘半径或轮距，并同步更新控制器和 Nav2 参数。

### 3.3 Gazebo 仿真与传感器插件

我已经在 `gazebo_plugin.xacro` 中完成：

- `gazebo_ros2_control` 控制接口。
- 左右轮速度控制接口。
- 轮子摩擦参数。
- 万向轮低摩擦设置。
- 激光雷达 `LaserScan` 输出到 `/scan`。
- 相机输出 `image_raw` 和 `camera_info`。

我已经理解：

- Gazebo 插件负责把仿真世界中的物理对象转换成 ROS2 话题和控制接口。
- 雷达参数必须和 SLAM/Nav2 中的扫描参数匹配。
- 相机光学坐标系需要 `camera_optical_link`，否则后续视觉算法可能坐标方向不一致。

巩固要求：

1. 用 `ros2 topic list` 找到 `/scan`、`/camera/image_raw`、`/camera/camera_info`。
2. 用 `ros2 topic echo /scan --once` 检查雷达数据。
3. 用 RViz 同时显示 RobotModel、LaserScan、TF。

### 3.4 ros2_control 与差速控制

我已经通过 `controllers.yaml` 配置：

- `joint_state_broadcaster`
- `diff_drive_controller`
- 左右轮 joint 名称
- 轮距 `0.36`
- 轮半径 `0.06`
- 里程计坐标系 `odom`
- 机器人基坐标系 `base_footprint`
- `/diff_drive_controller/cmd_vel_unstamped` 速度输入

我已经理解：

- 控制器通过左右轮速度计算机器人运动。
- `diff_drive_controller` 会发布里程计和 TF。
- Nav2 默认发 `/cmd_vel`，而当前控制器订阅 `/diff_drive_controller/cmd_vel_unstamped`，所以需要 `topic_tools relay` 转发。

巩固要求：

1. 能解释 `/cmd_vel -> /diff_drive_controller/cmd_vel_unstamped -> wheel joints -> odom` 的链路。
2. 用命令手动控制机器人：

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}" -r 10
```

3. 用 `ros2 topic echo /diff_drive_controller/odom` 检查里程计是否变化。

### 3.5 Launch 启动流程

当前有三个启动文件：

- `display.launch.py`：启动 Gazebo、RViz、robot_state_publisher、机器人生成、控制器、cmd_vel 转发、SLAM。
- `slam.launch.py`：单独启动 slam_toolbox。
- `navigation.launch.py`：启动 Nav2 bringup、cmd_vel 转发和 RViz。

我已经掌握：

- `Command(["xacro ", xacro_path])` 会把 Xacro 转成 `robot_description`。
- `robot_state_publisher` 根据 `robot_description` 发布静态/动态 TF。
- `spawn_entity.py` 从 `robot_description` 生成 Gazebo 实体。
- 控制器启动需要等待 Gazebo 和 controller_manager 准备好。
- Nav2 可以通过 IncludeLaunchDescription 复用官方 bringup。

巩固要求：

1. 按顺序说出 `display.launch.py` 启动后发生了什么。
2. 分别解释 `TimerAction` 和 `RegisterEventHandler(OnProcessExit)` 的作用。
3. 能独立判断一个节点启动失败时应该看哪个终端日志。

### 3.6 SLAM 建图

`slam.yaml` 使用 `slam_toolbox`，主要配置：

- `map_frame: map`
- `odom_frame: odom`
- `base_frame: base_link`
- `scan_topic: /scan`
- `mode: mapping`
- 雷达最大距离 `8.0`
- 差速运动模型噪声参数

我已经理解：

- SLAM 依赖 `/scan`、`odom` 和 TF。
- 建图时机器人运动越稳定，地图质量越好。
- 雷达范围、更新频率、里程计噪声会影响建图效果。

巩固要求：

1. 启动仿真和 SLAM 后，在 RViz 中观察 `/map` 是否更新。
2. 通过手柄或 `/cmd_vel` 控制机器人慢速绕场地运动。
3. 建图完成后保存地图，并确认 `my_map.yaml` 与 `my_map.pgm` 能被 Nav2 加载。

### 3.7 Nav2 自主导航

`nav2.yaml` 已经覆盖 Nav2 主要模块：

- AMCL 定位
- BT Navigator 行为树导航
- DWB 局部规划器
- Local Costmap
- Global Costmap
- Map Server
- Planner Server
- Smoother Server
- Behavior Server
- Waypoint Follower
- Velocity Smoother

我已经理解：

- AMCL 负责在已有地图中定位。
- Global Planner 负责规划全局路径。
- DWB Local Planner 负责生成局部速度。
- Costmap 把地图、障碍物、膨胀区转换成规划可用的代价。
- Velocity Smoother 限制速度和加速度，使机器人运动更平滑。

巩固要求：

1. 能解释 `map -> odom -> base_footprint -> base_link` 的导航 TF 链路。
2. 能解释局部代价地图和全局代价地图的区别。
3. 能根据机器人半径调整 `robot_radius` 和 `inflation_radius`。
4. 能根据机器人运动表现调整 DWB 的速度、加速度和评分器权重。

## 4. 推荐运行流程

### 第一步：编译工程

```bash
cd ~/ros2_robot/ros2_ws
colcon build
source install/setup.bash
```

### 第二步：启动仿真、模型、控制器和 SLAM

```bash
ros2 launch my_robot_description display.launch.py
```

确认：

- Gazebo 中出现机器人和地图环境。
- RViz 中显示机器人模型。
- `/scan` 有数据。
- `/diff_drive_controller/odom` 有数据。
- TF 树连续。

### 第三步：手动控制机器人建图

手柄方式：

```bash
ros2 run joy joy_node --ros-args -p device:=/dev/input/js0 -p deadzone:=0.06
```

```bash
ros2 run teleop_twist_joy teleop_node --ros-args \
  -p axis_linear.x:=1 \
  -p axis_angular.yaw:=0 \
  -p require_enable_button:=false \
  -p enable_button:=0 \
  -p scale_linear:=0.6 \
  -p scale_angular:=1.5
```

### 第四步：保存地图

```bash
ros2 run nav2_map_server map_saver_cli -f src/my_robot_description/maps/my_map
```

### 第五步：启动导航

```bash
ros2 launch my_robot_description navigation.launch.py
```

确认：

- RViz 可以设置 Initial Pose。
- AMCL 粒子云能收敛。
- 点击 Nav2 Goal 后机器人能规划路径并移动。
- `/cmd_vel` 能通过 relay 到达控制器输入话题。

## 5. 我需要重点巩固的调试能力

### 5.1 话题检查

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/odom --once
```

目标：判断传感器、速度指令、里程计是否正常。

### 5.2 TF 检查

```bash
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo map base_footprint
ros2 run tf2_ros tf2_echo odom base_footprint
```

目标：判断 TF 是否断开、frame 名称是否不一致。

### 5.3 控制器检查

```bash
ros2 control list_controllers
ros2 control list_joints
ros2 control list_hardware_interfaces
```

目标：判断控制器是否加载、joint 名称是否匹配、接口是否存在。

### 5.4 Nav2 状态检查

```bash
ros2 lifecycle nodes
ros2 topic echo /amcl_pose --once
ros2 topic echo /plan --once
```

目标：判断 Nav2 生命周期节点是否激活、定位是否正常、全局路径是否生成。

## 6. 逐步掌握路线

### 阶段 1：看懂模型

目标：不运行项目，也能从 Xacro 读出机器人长什么样。

要掌握：

- link/joint
- visual/collision/inertial
- fixed/continuous joint
- Xacro property/macro/include
- base_footprint/base_link 区别

验收标准：

- 能手画机器人结构图。
- 能说出每个 Xacro 文件负责什么。
- 能改一个尺寸并预测模型变化。

### 阶段 2：跑通仿真

目标：机器人能在 Gazebo 中正常出现并被控制。

要掌握：

- Gazebo world
- spawn_entity
- robot_state_publisher
- gazebo_ros2_control
- diff_drive_controller

验收标准：

- Gazebo 中机器人不飞、不陷地、不抖动。
- `/cmd_vel` 能让机器人前进和转向。
- `/odom` 正常发布。

### 阶段 3：掌握传感器

目标：雷达和相机能稳定输出数据。

要掌握：

- LaserScan 参数
- Camera topic
- frame_name
- RViz 可视化

验收标准：

- RViz 能看到雷达点云/扫描线。
- 相机图像能打开。
- 能解释雷达最大距离、角度范围、频率对建图和避障的影响。

### 阶段 4：完成 SLAM

目标：用机器人运动生成可用地图。

要掌握：

- map/odom/base_link 的关系
- slam_toolbox 输入输出
- 地图保存
- 建图质量影响因素

验收标准：

- 能生成 `my_map.yaml` 和 `my_map.pgm`。
- 地图边界清楚，没有严重重影。
- 能解释为什么机器人运动太快会影响建图。

### 阶段 5：完成 Nav2 导航

目标：机器人能在已有地图中定位、规划和移动。

要掌握：

- AMCL
- Nav2 lifecycle
- Global Planner
- DWB Local Planner
- Costmap
- Recovery Behavior
- Velocity Smoother

验收标准：

- Initial Pose 后粒子云收敛。
- Nav2 Goal 后能生成路径。
- 机器人能避障并到达目标附近。
- 能根据表现调整 `nav2.yaml`。

### 阶段 6：面向实车迁移

目标：把仿真理解迁移到真实机器人。

要掌握：

- Gazebo 插件和真实硬件驱动的区别。
- 仿真中的 `/scan` 对应真实雷达驱动。
- 仿真中的 `diff_drive_controller` 对应真实底盘驱动或 STM32 通信节点。
- 真实机器人需要处理编码器、IMU、电机控制、串口通信和急停安全。

验收标准：

- 能画出实车数据链路：STM32 编码器/电机 -> ROS2 底盘节点 -> odom/TF -> Nav2。
- 能说明哪些参数可以直接复用，哪些参数必须实测。

## 7. 当前项目可继续完善的点

1. `package.xml` 中 description 和 license 还是 TODO，可以补充。
2. `slam.yaml` 使用 `base_frame: base_link`，而控制器和 Nav2 多数使用 `base_footprint`，建议后续统一检查 TF 和定位表现。
3. `display.launch.py` 已经包含 SLAM，`slam.launch.py` 是独立启动 SLAM 的轻量版本，可以明确两者使用场景。
4. `display.launch.py` 中部分注释和实际延时不完全一致，例如注释写 5 秒，实际 `period=3.0`。
5. 后续如果接入真实 STM32 底盘，需要新增硬件通信节点或 ros2_control 硬件接口。

## 8. 我的复盘问题清单

每次复习这个项目时，我应该能回答：

1. 机器人模型从哪个 Xacro 文件开始加载？
2. `robot_description` 是谁生成的，谁使用它？
3. Gazebo 中机器人是怎么被生成出来的？
4. 左右轮 joint 名称在哪里定义，在哪里被控制器引用？
5. `/cmd_vel` 为什么要转发？
6. `/scan` 是哪个插件发布的？
7. SLAM 需要哪些输入？
8. Nav2 导航需要哪些核心 TF？
9. AMCL、Planner、Controller、Costmap 分别负责什么？
10. 如果机器人不动，应该按什么顺序排查？

## 9. 一句话总结

这个项目让我系统掌握了 ROS2 移动机器人从模型描述、Gazebo 仿真、差速控制、雷达建图到 Nav2 自主导航的完整链路。下一步的重点不是继续堆功能，而是反复运行、调参、排错，把 TF、话题、控制器和 Nav2 参数之间的关系真正变成自己的工程直觉。
