import json, os, pathlib, re, sys

from lssh import config_validation
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
        os.makedirs(host_cache_path().parent, exist_ok=True)
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

def import_new_config(srcpath, dstpath):
    srcpath = pathlib.Path(srcpath)
    dstpath = pathlib.Path(dstpath)
    srcfiles = [name for name in os.listdir(srcpath) if name.endswith(".txt") and os.path.isfile(srcpath / name)]
    srcfiles.sort()
    dstfiles = [name for name in os.listdir(dstpath) if name.endswith(".txt") and os.path.isfile(dstpath / name)]

    contents = {}
    errors = []
    for name in srcfiles:
        with open(srcpath / name, "r") as f:
            content = f.read()
            # Store the content in ram to prevent race-conditions (no extra read needed for copying)
            contents[name] = content
        errors += [name + ": " + e for e in config_validation.check_ssh_config_safety(content)]
    if len(errors) > 0:
        for error in errors:
            print(error, file=sys.stderr)
        print("Could not import the new config because of " + ("this error" if len(errors) == 1 else "these errors"), file=sys.stderr)
        sys.exit(1)

    # Write new config to destination dir
    for name in srcfiles:
        with open(dstpath / name, "w") as f:
            f.write(contents[name])

    # Delete files from destination that were removed in source
    for name in set(dstfiles) - set(srcfiles):
        os.unlink(dstpath / name)
