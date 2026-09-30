import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():

    sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value="True")
    map_file_arg = DeclareLaunchArgument("map_file", default_value="warehouse_map_sim.yaml")

    sim_f = LaunchConfiguration('use_sim_time')
    map_f = LaunchConfiguration('map_file')

    map_path = PathJoinSubstitution([
        get_package_share_directory("map_server"),
        "config",
        map_f,
    ])

    rviz_config_dir = os.path.join(get_package_share_directory('map_server'), 'rviz', 'map_display.rviz')

    map_node = Node(      
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': sim_f}, 
                        {'yaml_filename':map_path} 
                       ])

    lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_mapper',
            output='screen',
            parameters=[{'use_sim_time': sim_f},
                        {'autostart': True},
                        {'node_names': ['map_server']}])

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': sim_f}],
            output='screen')

    # create and return launch description object
    return LaunchDescription(
        [
            sim_time_arg,
            map_file_arg,
            map_node,
            lifecycle_manager_node,
            rviz_node,
        ]
    )