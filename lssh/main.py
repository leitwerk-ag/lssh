#! /usr/bin/env python3

# This module is executed when calling lssh and when using tab-completion.
# Tab-completion is time-critical.
# Load only necessary modules to minimize the reaction time when user presses tab
# Especially do not load cli when called for completion

import sys

DEFAULT = {}
def main(hosts_dir, update_hosts, cmd_whitelist_func = DEFAULT, attributes={}):
    if len(sys.argv) >= 2 and sys.argv[1] == '__complete__':
        from lssh import tabcomplete
        tabcomplete.main(hosts_dir)
    else:
        if cmd_whitelist_func is not DEFAULT:
            print("Warning: The third argument of main, cmd_whitelist_func, is no longer in use. (removed in version 0.5.0)", file=sys.stderr)
            print("Please update your lssh executable and remove this argument, otherwise this will become a hard error in future versions.", file=sys.stderr)
        from lssh import cli
        cli.main(hosts_dir, update_hosts, attributes)
