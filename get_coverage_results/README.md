# Coverage calculator for ROS2 packages in ROS2 buildfarm

Script to get results from a `ci.ros2.org` coverage build through json and
calculate the covarage rate from all the listed entries corresponding to
unit testing.

## Usage

```
  $ ./get_coverage_ros2_pkg.py <jenkins_build_url> <ros2_package_name>

Example:
  $ ./get_coverage_ros2_pkg.py https://ci.ros2.org/job/nightly_linux_coverage/879 rclcpp
```