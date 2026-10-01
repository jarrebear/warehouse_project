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
        "' == 'warehouse_map_sim.yaml' else 'amcl_config_real.yaml'"
    ])

    # sim planner config file for simulation map, real planner config file for for real map
    nav2_config_f = PythonExpression([
        "'planner_sim.yaml' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else 'planner_real.yaml'"
    ])

    # sim controller config file for simulation map, real controller config file for for real map
    controller_config_f = PythonExpression([
        "'controller_sim.yaml' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else 'controller_real.yaml'"
    ])

    # sim bt_navigator config file for simulation map, real bt_navigator config file for for real map
    bt_navigator_config_f = PythonExpression([
        "'bt_navigator_sim.yaml' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else 'bt_navigator_real.yaml'"
    ])

    # sim recovery config file for simulation map, real recovery config file for for real map
    recovery_config_f = PythonExpression([
        "'recoveries_sim.yaml' if '",
        map_f,
        "' == 'warehouse_map_sim.yaml' else 'recoveries_real.yaml'"
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
        get_package_share_directory("path_planner_server"),
        "rviz",
        "navigation.rviz"
    )

    nav2_yaml = PathJoinSubstitution([
        get_package_share_directory("path_planner_server"),
        "config",
        nav2_config_f,
    ])

    controller_yaml = PathJoinSubstitution([
        get_package_share_directory("path_planner_server"),
        "config",
        controller_config_f,
    ])

    bt_navigator_yaml = PathJoinSubstitution([
        get_package_share_directory("path_planner_server"),
        "config",
        bt_navigator_config_f,
    ])
    
    recovery_yaml = PathJoinSubstitution([
        get_package_share_directory("path_planner_server"),
        "config",
        recovery_config_f,
    ])
    
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

    planner_server = Node(package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_yaml,
             {"use_sim_time": sim_f}])


    control_server = Node(name='controller_server',
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[controller_yaml,
             {"use_sim_time": sim_f}])


    bt_navigator = Node(package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_yaml,
             {"use_sim_time": sim_f}])
            
    behavior_server = Node(package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[recovery_yaml,
             {"use_sim_time": sim_f}],
            output='screen')

    lifecycle_manager_node = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            {"use_sim_time": sim_f},
            {'bond_timeout':0.0},
            {"autostart": True},
            {"node_names": ["map_server", "amcl", 'planner_server',
                         'controller_server', 'bt_navigator',
                          'recoveries_server']}
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
        planner_server,
        control_server,
        bt_navigator,
        behavior_server,
        lifecycle_manager_node,
        rviz_node,
    ])
