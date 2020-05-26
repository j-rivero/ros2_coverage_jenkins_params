# Usage

## Get ROS package reverse dependencies

List of reverse dependencies (test+run) of quality list packages present in ros2.repos file
```
bash -e all_ros2_jobs.bash
```

## Get vcs format list from a file with a list of ROS2 packages

Convert from a separated line list of ROS2 packages to vcs format

```
./pkg_name_to_repo.py --packages_txt_file proposed_list.txt  < ros2.repos
```
