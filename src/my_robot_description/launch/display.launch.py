from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessExit


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

    # rviz 配置
    rviz_config = PathJoinSubstitution([
        FindPackageShare("my_robot_description"),
        "rviz",
        "robot.rviz"
    ])

    # 控制器yaml路径
    controllers_yaml = PathJoinSubstitution([
        FindPackageShare("my_robot_description"),
        "config",
        "controllers.yaml"
    ])

    # robot_state_publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description},
            {"use_sim_time": True}
        ]
    )

    # rviz2
    rviz2 = Node(
        package="rviz2",
        executable="rviz2",
        parameters=[{"use_sim_time": True}],
        arguments=["-d", rviz_config]
    )

    # gazebo 仿真环境
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"),
                "launch",
                "gazebo.launch.py"
            ])
        ),
        launch_arguments={
            "world": PathJoinSubstitution([
                FindPackageShare("my_robot_description"),
                "worlds",
                "my_world.world"
            ]),
            "use_sim_time": "true"
        }.items()
    )

    # 5秒后生成机器人实体
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
                    "-topic", "robot_description",
                    "-entity", "my_robot",
                    "-z", "0.1"  # 设置机器人在z轴上的初始位置，避免与地面碰撞
                ],
                output="screen"
            )
        ]
    )

    # --------------------------控制器启动逻辑重构--------------------------
    # 1. 延时6s启动关节状态广播器，传入控制器配置文件
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "60"
        ],
        output="screen"
    )

    delayed_broadcaster = TimerAction(
        period=6.0,
        actions=[joint_state_broadcaster_spawner]
    )

    # 2. 广播器退出后再启动差速控制器，单独新建节点，不复用对象
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "60"
        ],
        output="screen"
    )
    # 3. 创建一个cmd_vel的relay节点，将/cmd_vel话题转发到/diff_drive_controller/cmd_vel_unstamped
    cmd_vel_relay = Node(
    package="topic_tools",
    executable="relay",
    name="cmd_vel_relay",
    arguments=["/cmd_vel", "/diff_drive_controller/cmd_vel_unstamped"],
    output="screen",
    parameters=[{"use_sim_time": True}]
    )

    # 监听广播器完成，自动启动差速控制器
    trigger_diff_drive = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_spawner]
        )
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
        robot_state_publisher,
        rviz2,
        gazebo,
        spawn_robot,
        delayed_broadcaster,
        trigger_diff_drive,
        cmd_vel_relay,
        slam_toolbox
    ])