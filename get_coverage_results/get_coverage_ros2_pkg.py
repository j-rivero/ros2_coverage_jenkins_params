#!/usr/bin/env python3

import json
from pprint import pprint
import requests
import sys

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + '<jenkins_coverage_build>' + '<ros_package>')

input_url = sys.argv[1]
input_pkg = sys.argv[2]

r = requests.get(url=input_url + '/cobertura/api/json?depth=3')
if r.status_code != 200:
    print("Wrong input URL")
    sys.exit(-1)

coverage_entries = r.json()['results']['children']

total_lines_under_testing = 0
total_lines_tested = 0

for e in coverage_entries:
    if e['name'] == '.':
        continue
    # e has children, elements or name
    entry_name = e['name'].replace("'","")
    lines_coverage = e['elements'][2]
    assert lines_coverage['name'] == 'Lines', 'Error expecting lines coverage2'
    name_parts = entry_name.split('.')
    if len(name_parts) == 1:
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('build') or name_parts[0].startswith('test'):
        package_under_cov = name_parts[1]
    elif name_parts[0].startswith('launch'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('ros2'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('sros2'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('tracetools'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('topic_monitor'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('demo_nodes_py'):
        package_under_cov = name_parts[0]
    elif name_parts[0].startswith('install'):
        # integration/system testing, out by now
        continue
    elif name_parts[0].startswith('src'):
        if len(name_parts) > 4:
            package_under_cov = name_parts[3]
        else:
            package_under_cov = name_parts[2]
    else:
        print('UNEXPECTED: ' + name_parts[0])
        pprint(name_parts)
        continue

    found = False
    if package_under_cov == input_pkg:
        found = True
    else:
        # Try other metrics to fidn it
        if name_parts[0].startswith('src') and '.' + input_pkg + '.' in entry_name:
            found = True

    if found:
        total_lines_under_testing += lines_coverage['denominator']
        total_lines_tested += lines_coverage['numerator']
        print(" * %s [%04.2f] -- %i/%i" % (
              entry_name,
              lines_coverage['ratio'],
              lines_coverage['numerator'],
              lines_coverage['denominator']))


if (total_lines_under_testing == 0):
    print("Package not found: " + input_pkg)
    sys.exit(-1)

print("\nCombined unit testing for %s: %04.2f%% %i/%i" % (
    input_pkg,
    total_lines_tested / total_lines_under_testing * 100,
    total_lines_tested,
    total_lines_under_testing))
