import json, os, re

from lssh.tabcomplete import host_cache_path

class HostEntry:
    def __init__(self, display_name, customer):
        self.display_name = display_name
        self.customer = customer
        self.keywords = {customer}

def update_display_name_cache(entries, newest_timestamp):
    try:
        cache_stat = os.stat(host_cache_path())
        need_update = cache_stat.st_mtime < newest_timestamp
    except FileNotFoundError:
        need_update = True
    if need_update:
        cache = {}
        for display_name in entries:
            cache[display_name] = list(entries[display_name].keywords)
        with open(host_cache_path(), "w") as f:
            json.dump(cache, f)

def load_config(path):
    entries = {}
    cur_host = [None] # array is used to make the value mutable for the handle_line function
    def handle_line(line, customer, file_keywords, file_hosts):
        m = re.match('^\s*Host\s+([\S]+)\s*$', line)
        if m:
            hostname = m.group(1)
            if '*' not in hostname and '?' not in hostname:
                cur_host[0] = HostEntry(hostname, customer)
                if hostname not in entries:
                    entries[hostname] = cur_host[0]
                file_hosts.append(cur_host[0])
        m = re.match('^\s*#\s*lssh:(file)?keywords\s(.*)$', line)
        if m:
            keywords_str = m.group(2)
            keywords = {k.strip() for k in keywords_str.split(',')}
            if m.group(1) == 'file':
                # keywords for the entire file
                file_keywords |= keywords
            elif cur_host[0] is not None:
                # keywords only for this host
                cur_host[0].keywords |= keywords
    files = os.listdir(path)
    files.sort()
    newest_timestamp = 0
    for filename in files:
        name = path + "/" + filename
        if filename.endswith(".txt") and os.path.isfile(name):
            basename = filename[0:-4]
            with open(name, "r") as f:
                cur_host[0] = None
                file_keywords = {basename}
                file_hosts = []
                for line in f:
                    handle_line(line, basename, file_keywords, file_hosts)
                # add the file keywords to all hosts of this file
                for host in file_hosts:
                    host.keywords |= file_keywords
            stat = os.stat(name)
            newest_timestamp = max(newest_timestamp, stat.st_mtime)
    update_display_name_cache(entries, newest_timestamp)

    return entries
