import os, re

class HostEntry:
    def __init__(self, displayname):
        self.__displayname = displayname
        self.__keywords = set()

def load_config(path):
    entries = {}
    cur_host = None
    def handle_line(line):
        m = re.match('^\s*Host\s+([\S]+)\s*$', line)
        if m:
            hostname = m.group(1)
            if '*' not in hostname and '?' not in hostname:
                cur_host = hostname
                if hostname not in entries:
                    entries[hostname] = HostEntry(hostname)
    files = os.listdir(path)
    files.sort()
    for filename in files:
        name = path + "/" + filename
        if filename.endswith(".txt") and os.path.isfile(name):
            with open(name, "r") as f:
                for line in f:
                    handle_line(line)
    return entries
