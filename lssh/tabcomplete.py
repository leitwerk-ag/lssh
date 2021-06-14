from json import load
from os import environ
from pathlib import Path
from sys import argv

try:
    from xdg import xdg_cache_home
except ImportError:
    from xdg.BaseDirectory import xdg_cache_home # Fallback for old xdg version (debian)

from lssh import recordings

# To activate tab completion in bash:
# complete -C 'lssh __complete__' lssh

def find_substrings():
    if 'COMP_LINE' not in environ:
        return []
    # very rudimentary parsing of a bash commandline
    parts = environ['COMP_LINE'].split(' ')[1:]
    option_val = False
    substrings = []
    for part in parts:
        if option_val:
            option_val = False
        elif part.startswith('-'):
            option_val = part in ('--timestamp', '--load-from')
        else:
            substrings.append(part)
    if len(substrings) > 0:
        idx = substrings[0].find('@')
        if idx != -1:
            substrings[0] = substrings[0][idx+1:]
    # Cut off the currently typed substring, it should not restrict current completion
    return substrings[0:-1]

def contains_substring(keywords, substring):
    for keyword in keywords:
        if substring in keyword:
            return True
    return False

def contains_all_substrings(keywords, substrings):
    for substr in substrings:
        if not contains_substring(keywords, substr):
            return False
    return True

def timestamp_completions(substrings):
    def matches(entry):
        return contains_all_substrings(entry[2], substrings)
    return [entry[1] for entry in recordings.find_recording_files() if matches(entry)]

def parse_hosts(hosts_dir):
    from json import dump
    from lssh.hostlist import load_config

    config, _ = load_config(hosts_dir, suppress_errors=True)
    hosts = {}
    for display_name in config:
        hosts[display_name] = list(config[display_name].keywords)
    return hosts

def host_cache_path():
    if type(xdg_cache_home) is str:
        cache = Path(xdg_cache_home)
    else:
        cache = xdg_cache_home()
    return cache / 'lssh' / 'hosts.json'

# Check if the given new_keyword reduces the given hosts in host_choices
# True, if there is at least one host that does not match the new_keyword
def restricts(new_keyword, host_choices, host_keyword_map):
    for host in host_choices:
        if not contains_substring([host] + host_keyword_map[host], new_keyword):
            return True
    return False

def main(hosts_dir):
    if len(argv) < 5:
        return
    current_arg = argv[3]
    previous_arg = argv[4]

    if previous_arg == '--timestamp':
        # timestamp completion
        choices = timestamp_completions(find_substrings())
    elif previous_arg == '--load-from':
        from shlex import quote
        from subprocess import run
        from sys import exit
        compgen_cmd = "compgen -d -- " + quote(current_arg)
        exit(run(["bash", "-c", compgen_cmd]).returncode)
    elif current_arg.startswith('-'):
        # option completion
        choices = ['--help', '--load-from', '--replay', '--timestamp', '--update-hosts', '--verbose', '--version']
    else:
        # substring completion
        try:
            try:
                with open(host_cache_path(), 'r') as f:
                    hosts = load(f)
            except FileNotFoundError:
                hosts = parse_hosts(hosts_dir)
            substrings = find_substrings()
            host_choices = {h for h in hosts if contains_all_substrings([h] + hosts[h], substrings)}
            if len(host_choices) == 1 and list(host_choices)[0] in substrings:
                # Only one host remaining and this host is already given explicitly. No further suggestions for the tab-completion
                choices = []
            else:
                keyword_options = {keyword for h in host_choices for keyword in hosts[h]}
                keyword_choices = {keyword for keyword in keyword_options if restricts(keyword, host_choices, hosts)}
                choices = host_choices | keyword_choices
        except FileNotFoundError:
            choices = []
    result = [x for x in choices if x.startswith(current_arg)]
    print("\n".join(result))
