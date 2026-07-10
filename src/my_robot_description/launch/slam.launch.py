from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # xacro 路径
    xacro_path = PathJoinSubstitution([
        FindPackageShare("my_robot_description"),
        "urdf",
        "base_core.xacro"
    ])      

    # robot_description
    robot_description = ParameterValue(
        Command(["xacro ", xacro_path]),
        value_type=str
    )

    # slam_toolbox 配置
    slam_yaml = PathJoinSubstitution([
        FindPackageShare("my_robot_description"),
        "config",
        "slam.yaml"
    ])

        # slam_toolbox 节点
    slam_toolbox = Node(

        package="slam_toolbox",

        executable="async_slam_toolbox_node",

        name="slam_toolbox",

        parameters=[

            slam_yaml,

            {"use_sim_time": True}

        ],

        output="screen"

    )

    return LaunchDescription([
        slam_toolbox
    ])