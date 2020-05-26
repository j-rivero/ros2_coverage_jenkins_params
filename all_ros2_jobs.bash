#!/bin/bash -e

ROS2_REPOS_URL=https://raw.githubusercontent.com/ros2/ros2/master/ros2.repos
ROS2_QUALITY_LEVELS_PKGS_FILE=quality_level.list
ROS2_QUALITY_LEVELS_PKGS=$(cat ${ROS2_QUALITY_LEVELS_PKGS_FILE})
TMP_DIR=$(mktemp -d)

remove_string_dups()
{
    local string=${1}

    sed 's/ /\n/g' <<< $string | sort | uniq | tr '\n' ' '
}

pushd "$TMP_DIR" 2> /dev/null
mkdir src
wget -q ${ROS2_REPOS_URL}
vcs import src < ros2.repos
ALL_ROS2_PKGS=$(colcon list --names-only)

# Check that all packages in ROS2_QUALITY_LEVELS_PKGS 
# are in the workspace
for pkg in ${ROS2_QUALITY_LEVELS_PKGS}; do
    if [[ ${ALL_ROS2_PKGS/$pkg/} == ${ALL_ROS2_PKGS} ]]; then
	echo " $pkg not found in workspace"
	exit 1
    fi
done

final_test_list=
# Go over ALL_ROS2_PKGS to check which one interacts with any of the packages
# in ROS2_QUALITY_LEVELS_PKGS
for pkg in ${ALL_ROS2_PKGS}; do
    echo " * Processing $pkg "
    # if the package is in our quality level list, add it automatically and
    # continue with the next
    if [[ ${ROS2_QUALITY_LEVELS_PKGS/$pkg/} != ${ROS2_QUALITY_LEVELS_PKGS} ]];
    then
	# if pkg is in quality levels add it automatically
	echo "    + selected because in ROS2_QUALITY_LEVELS_PKGS"
	final_test_list="${final_test_list} ${pkg}"
	continue
    fi
    # check the run and test dependencies of the package
    echo -n "     - check reverse test deps: "
    #run_deps=$(colcon info ${pkg} | grep 'run: ' | sed 's/.*run: //')
    test_deps=$(colcon info ${pkg} | grep 'test: ' | sed 's/.*test: //')
    total_deps=$(remove_string_dups "$test_deps")
    echo "${total_deps}"

    testing_set=
    # Check if among the deps we have a package in ROS2_QUALITY_LEVELS_PKGS
    # if that is the case, we are interested in this package since it uses
    # somehow our packages under testing
    for dep in ${total_deps}; do
    	if [[ ${ROS2_QUALITY_LEVELS_PKGS/$dep/} != ${ROS2_QUALITY_LEVELS_PKGS} ]]; then
	    echo "        + selected because uses ${dep}"
	    testing_set=$(remove_string_dups  "${testing_set} ${pkg}")
	    # break
	fi
    done

    # compute test list
    final_test_list="${final_test_list} ${testing_set}"
    final_test_list=$(remove_string_dups "${final_test_list}")
done

echo "PROPOSED LIST:"
echo $final_test_list
echo

# Final filtering to leave only packages present in ALL_ROS2_PKGS
echo "Packages proposed not in QUALITY_LEVEL list:"
echo
for pkg in ${final_test_list}; do
  if [[ ${ROS2_QUALITY_LEVELS_PKGS/$pkg/} == ${ROS2_QUALITY_LEVELS_PKGS} ]]; then
      echo "${pkg}"
  fi
done

popd 2> /dev/null
