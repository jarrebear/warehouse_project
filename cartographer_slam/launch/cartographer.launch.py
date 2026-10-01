import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression

def generate_launch_description():

    cartographer_config_dir = os.path.join(get_package_share_directory('cartographer_slam'), 'config')
    rviz_config_dir = os.path.join(get_package_share_directory('cartographer_slam'), 'rviz', 'mapping.rviz')

    sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="True"
    )

    sim_f = LaunchConfiguration("use_sim_time")

    # True for simulation map, False for real map
    cartographer_config_f = PythonExpression([
        "'cartographer_sim.lua' if '",
        sim_f,
        "' == 'True' else 'cartographer_real.lua'"
    ])

    cartographer_node = Node(
            package='cartographer_ros', 
            executable='cartographer_node', 
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': sim_f}],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', cartographer_config_f]

    )

    occupancy_grid_node = Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            output='screen',
            name='occupancy_grid_node',
            parameters=[{'use_sim_time': sim_f}],
            arguments=['-resolution', '0.05', '-publish_period_sec', '1.0']

    )

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
            cartographer_node,
            occupancy_grid_node,
            rviz_node,

        ]
    )