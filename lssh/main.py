#! /usr/bin/env python3

# This module is executed when calling lssh and when using tab-completion.
# Tab-completion is time-critical.
# Load only necessary modules to minimize the reaction time when user presses tab
# Especially do not load cli when called for completion

import sys

def main(hosts_dir, update_hosts):
    if len(sys.argv) >= 2 and sys.argv[1] == '__complete__':
        from lssh import tabcomplete
        tabcomplete.main(hosts_dir)
    else:
        from lssh import cli
        cli.main(hosts_dir, update_hosts)
