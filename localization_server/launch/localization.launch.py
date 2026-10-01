import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression


def generate_launch_description():

    map_file_arg = DeclareLaunchArgument(
        "map_file",
        default_value="warehouse_map_sim.yaml"
    )

    map_f = LaunchConfiguration("map_file")

    # True for simulation map, False for real map
    sim_f = PythonExpression([
        "'True' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else 'False'"
    ])

    # sim config file for simulation map, real config file for for real map
    amcl_config_f = PythonExpression([
        "'amcl_config_sim.yaml' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else ' amcl_config_real.yaml'"
    ])

    map_path = PathJoinSubstitution([
        get_package_share_directory("map_server"),
        "config",
        map_f,
    ])

    amcl_config_path = PathJoinSubstitution([
        get_package_share_directory("localization_server"),
        "config",
        amcl_config_f,
    ])

    rviz_config_dir = os.path.join(
        get_package_share_directory("localization_server"),
        "rviz",
        "localization_display.rviz"
    )

    map_node = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"use_sim_time": sim_f},
            {"yaml_filename": map_path}
        ]
    )

    amcl_node = Node(package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                    amcl_config_path,
                    {"use_sim_time": sim_f}
            ]
    )

    lifecycle_manager_node = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {"use_sim_time": sim_f},
            {'bond_timeout':0.0},
            {"autostart": True},
            {"node_names": ["map_server", "amcl"]}
        ]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_dir],
        parameters=[
            {"use_sim_time": sim_f}
        ],
        output="screen"
    )

    return LaunchDescription([
        map_file_arg,
        map_node,
        amcl_node,
        lifecycle_manager_node,
        rviz_node,
    ])
