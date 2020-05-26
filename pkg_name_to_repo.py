#!/usr/bin/python3

from rosdistro import get_distribution_cache
from rosdistro import get_index
from rosdistro.manifest_provider import get_release_tag
from rosdistro.repository_specification import RepositorySpecification
from vcstool.executor import ansi
from vcstool.commands.import_ import get_repositories
from vcstool.streams import set_streams
from vcstool.commands.validate import get_parser
from vcstool.commands.command import add_common_arguments

import yaml
import argparse
import sys


def get_proposed_packages_repo_names(pkg_name_list):
    index = get_index('https://raw.githubusercontent.com/ros/rosdistro/master/index.yaml')
    dist_cache = get_distribution_cache(index, 'foxy')
    dist_file = dist_cache.distribution_file

    repositories = []
    for pkg_name in pkg_name_list:
        if not pkg_name:
            continue
        try:
            repo_name = dist_file.release_packages[pkg_name].repository_name
            release_repo = dist_file.repositories[repo_name].source_repository.get_url_parts()[1]
        except KeyError:
            if pkg_name.startswith('rosbag2_'):
                release_repo = 'ros2/rosbag2'
            elif pkg_name.startswith('test_launch_ros'):
                release_repo = 'ros2/launch_ros'
            elif pkg_name.startswith('test_'):
                release_repo = 'ros2/system_tests'
            elif pkg_name.startswith('tf2_'):
                release_repo = 'ros2/geometry2'
            elif pkg_name.startswith('libstatistics_collector') or pkg_name.startswith('statistics_'):
                release_repo = 'ros-tooling/libstatistics_collector'
            elif pkg_name.startswith('rmw_dds_common'):
                release_repo = 'ros2/rmw_dds_common'
            elif pkg_name.startswith('rosidl_runtime_c'):
                release_repo = 'ros2/rosidl'
            elif pkg_name.startswith('rmw_cyclonedds'):
                release_repo = 'ros2/rmw_cyclonedds'
            elif pkg_name.startswith('rmw_connext'):
                release_repo = 'ros2/rmw_connext'
            elif pkg_name.startswith('rmw_fastcdr'):
                release_repo = 'eProsima/Fast-CDR'
            else:
                raise Exception("package " + pkg_name + " not found in foxy release. Might need to add code manually")
        repositories.append(release_repo)
    return list(dict.fromkeys(repositories))


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    parser = get_parser()
    add_common_arguments(
        parser, skip_nested=True, path_nargs=False)
    parser.add_argument('--packages_txt_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    pkg_name_list = args.packages_txt_file.read().split('\n')

    try:
        ros2_repos = get_repositories(args.input)
    except RuntimeError as e:
        print(ansi('redf') + str(e) + ansi('reset'), file=sys.stderr)
        return 1

    vcs_format_repo_list = {}
    for repo_name in get_proposed_packages_repo_names(pkg_name_list):
        vcs_format_repo_list[repo_name] = ros2_repos[repo_name]

    print(yaml.dump(vcs_format_repo_list))


if __name__ == "__main__":
    main()
