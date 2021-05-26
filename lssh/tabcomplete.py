from json import load
from os import environ
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
            option_val = part == '--timestamp'
        else:
            substrings.append(part)
    if len(substrings) > 0:
        idx = substrings[0].find('@')
        if idx != -1:
            substrings[0] = substrings[0][idx+1:]
    return substrings

def contains_all_substrings(keywords, substrings):
    for substr in substrings:
        contained = False
        for keyword in keywords:
            if substr in keyword:
                contained = True
                break
        if not contained:
            return False
    return True

def timestamp_completions(substrings):
    def matches(entry):
        return contains_all_substrings(entry[2], substrings)
    return [entry[1] for entry in recordings.find_recording_files() if matches(entry)]

def parse_hosts(hosts_dir):
    from json import dump
    from lssh.hostlist import load_config

    config = load_config(hosts_dir)
    names = [h.display_name for h in config.values()]
    return names

def host_cache_path():
    return xdg_cache_home() / 'lssh' / 'hosts.json'

def main(hosts_dir):
    if len(argv) < 5:
        return
    current_arg = argv[3]
    previous_arg = argv[4]

    if previous_arg == '--timestamp':
        # timestamp completion
        choices = timestamp_completions(find_substrings())
    elif current_arg.startswith('-'):
        # option completion
        choices = ['--help', '--replay', '--timestamp', '--update-hosts', '--verbose']
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
            keyword_choices = {keyword for h in host_choices for keyword in hosts[h]}
            choices = host_choices | keyword_choices
        except FileNotFoundError:
            choices = []
    result = [x for x in choices if x.startswith(current_arg)]
    print("\n".join(result))
