#!/usr/bin/env python3
'''
============================================================
文件: navigation.launch.py
功能: 启动Nav2导航系统 + RViz可视化
适配: my_robot_description 差速机器人
============================================================
'''
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, 
    DeclareLaunchArgument,
    SetEnvironmentVariable
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ============================================================
    # 1. 定位功能包路径
    # ============================================================
    # ⭐ 修改为你的功能包名
    my_robot_nav_dir = get_package_share_directory('my_robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    # ============================================================
    # 2. 声明参数
    # ============================================================
    # 使用仿真时间（Gazebo仿真必须为true）
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # ⭐ 地图文件路径（修改成你的地图名）
    map_yaml_path = LaunchConfiguration(
        'map',
        default=os.path.join(my_robot_nav_dir, 'maps', 'my_map.yaml')
    )

    # ⭐ Nav2参数文件路径
    nav2_param_path = LaunchConfiguration(
        'params_file',
        default=os.path.join(my_robot_nav_dir, 'config', 'nav2.yaml')
    )

    # ⭐ RViz配置文件路径（可以用自己的，也可以用nav2默认的）
    # rviz_config_dir = os.path.join(
    #     my_robot_nav_dir, 'rviz', 'robot.rviz'
    # )
    # 如果没有自己的rviz配置，用默认的：
    rviz_config_dir = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    # ============================================================
    # 3. 声明可修改的启动参数（命令行传入）
    # ============================================================
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='使用Gazebo仿真时间'
    )

    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=map_yaml_path,
        description='地图文件路径'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_param_path,
        description='Nav2参数文件路径'
    )

    # ============================================================
    # 4. 启动 Nav2 主服务
    # ⭐ 关键：加入 cmd_vel 话题重映射
    # ============================================================
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_path,
            'use_sim_time': use_sim_time,
            'params_file': nav2_param_path,
        }.items(),
    )

    # ============================================================
    # 5. ⭐ cmd_vel 话题重映射（关键！）
    # Nav2默认发布到 /cmd_vel
    # 你的机器人订阅 /diff_drive_controller/cmd_vel_unstamped
    # 用 topic_tools 做话题转发
    # ============================================================
    cmd_vel_relay = Node(
        package='topic_tools',
        executable='relay',
        name='cmd_vel_relay',
        arguments=['/cmd_vel', '/diff_drive_controller/cmd_vel_unstamped'],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # ============================================================
    # 6. RViz可视化
    # ============================================================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # ============================================================
    # 7. 返回LaunchDescription
    # ============================================================
    return LaunchDescription([
        # 参数声明
        declare_use_sim_time_cmd,
        declare_map_cmd,
        declare_params_file_cmd,
        # 启动节点
        nav2_bringup_launch,
        cmd_vel_relay,       # ⭐ 话题转发
        rviz_node,
    ])