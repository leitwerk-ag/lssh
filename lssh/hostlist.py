import csv, json, os, pathlib, re, sys

from lssh import config_validation
from lssh.command_whitelist import load_default_paths
from lssh.tabcomplete import host_cache_path

class HostEntry:
    def __init__(self, display_name, customer):
        self.display_name = display_name
        self.customer = customer
        self.keywords = set()
        self.jumphost = None
    def add_customer_as_keyword(self):
        self.keywords.add(self.customer)

def update_display_name_cache(entries, newest_timestamp, suppress_errors):
    try:
        cache_stat = os.stat(host_cache_path())
        need_update = cache_stat.st_mtime < newest_timestamp
    except FileNotFoundError:
        need_update = True
    if need_update:
        cache = {}
        for display_name in entries:
            cache[display_name] = list(entries[display_name].keywords)
        try:
            os.makedirs(host_cache_path().parent, exist_ok=True)
            with open(host_cache_path(), "w") as f:
                json.dump(cache, f)
        except Exception as e:
            if not suppress_errors:
                print("Warning: failed to create hostlist cache file: " + str(e), file=sys.stderr)

def load_config(path, suppress_errors=False):
    entries = {}
    displaynames = {}
    cur_host = [None] # array is used to make the value mutable for the handle_line function
    file_displayname = [None]
    def handle_line(line, customer, file_keywords, file_hosts):
        m = re.match('^\\s*Host\\s+([\\S]+)\\s*$', line, re.IGNORECASE)
        if m:
            hostname = m.group(1)
            if '*' not in hostname and '?' not in hostname:
                cur_host[0] = HostEntry(hostname, customer)
                if hostname not in entries:
                    entries[hostname] = cur_host[0]
                file_hosts.append(cur_host[0])
        m = re.match('^\\s*proxyjump\\s+([\\S]+)\\s*$', line, re.IGNORECASE)
        if m and cur_host[0] is not None and cur_host[0].jumphost is None:
            cur_host[0].jumphost = m.group(1)
        m = re.match('^\\s*#\\s*lssh:(file)?keywords\\s(.*)$', line, re.IGNORECASE)
        if m:
            keywords_str = m.group(2)
            keywords = {k.strip() for k in keywords_str.split(',')}
            if m.group(1) == 'file':
                # keywords for the entire file
                file_keywords |= keywords
            elif cur_host[0] is not None:
                # keywords only for this host
                cur_host[0].keywords |= keywords
        m = re.match('^\\s*#\\s*lssh:displayname\\s+(\\S.*)$', line, re.IGNORECASE)
        if m and file_displayname[0] is None:
            file_displayname[0] = m.group(1)
        m = re.match('^\\s*#\\s*lssh:assignedcustomer\\s+(\\S.*)$', line, re.IGNORECASE)
        if m and cur_host[0] is not None:
            name = m.group(1)
            # allow both: with or without file ending .txt
            if name.endswith(".txt"):
                name = name[0:-4]
            cur_host[0].customer = name
    files = os.listdir(path)
    files.sort()
    newest_timestamp = os.stat(path).st_mtime
    for filename in files:
        name = path + "/" + filename
        if filename.endswith(".txt") and os.path.isfile(name):
            basename = filename[0:-4]
            with open(name, "r") as f:
                cur_host[0] = None
                file_keywords = {basename}
                file_hosts = []
                file_displayname = [None]
                for line in f:
                    handle_line(line, basename, file_keywords, file_hosts)
                # add the file keywords to all hosts of this file
                for host in file_hosts:
                    host.keywords |= file_keywords
                # store the displayname
                if file_displayname[0] is not None:
                    displaynames[basename] = file_displayname[0]
            stat = os.stat(name)
            newest_timestamp = max(newest_timestamp, stat.st_mtime)
    for entry in entries.values():
        entry.add_customer_as_keyword()
    update_display_name_cache(entries, newest_timestamp, suppress_errors)

    return (entries, displaynames)

def import_new_config(srcpath, dstpath, general_proxy):
    srcpath = pathlib.Path(srcpath)
    dstpath = pathlib.Path(dstpath)
    srcfiles = [name for name in os.listdir(srcpath) if name.endswith(".txt") and os.path.isfile(srcpath / name)]
    srcfiles.sort()
    dstfiles = [name for name in os.listdir(dstpath) if name.endswith(".txt") and os.path.isfile(dstpath / name)]

    contents = {}
    error_files = set()
    errors = []
    cmd_whitelist = load_default_paths()

    for name in srcfiles:
        with open(srcpath / name, "r") as f:
            content = f.read()
        file_errors, content = config_validation.transform_config(content, cmd_whitelist, general_proxy)
        if len(file_errors) > 0:
            error_files.add(name)
            errors += [name + ": " + e for e in file_errors]
        else:
            contents[name] = "".join([line + "\n" for line in content])
    if len(errors) > 0:
        for error in errors:
            print(error, file=sys.stderr)
        print("Could not completely import the new config because of " + ("this error" if len(errors) == 1 else "these errors"), file=sys.stderr)
        print("Files containing errors will not be updated.", file=sys.stderr)

    # Write new config to destination dir
    for name in srcfiles:
        if name not in error_files:
            try:
                with open(dstpath / name, "r+") as f:
                    # First check, if the file did actually change
                    # Simply overwriting would change the file's modification date, resulting in cache-rebuilds
                    content = f.read()
                    if content != contents[name]:
                        f.seek(0)
                        f.truncate()
                        f.write(contents[name])
            except FileNotFoundError:
                # File does not exist yet, just create it
                with open(dstpath / name, "w") as f:
                    f.write(contents[name])

    # Delete files from destination that were removed in source
    for name in set(dstfiles) - set(srcfiles):
        os.unlink(dstpath / name)

    if len(errors) > 0:
        exit(1)
    exit(0)

def validate_config(srcdir, general_proxy):
    srcpath = pathlib.Path(srcdir)
    srcfiles = [name for name in os.listdir(srcpath) if name.endswith(".txt") and os.path.isfile(srcpath / name)]
    srcfiles.sort()

    errors = []
    cmd_whitelist = load_default_paths()

    for name in srcfiles:
        with open(srcpath / name, "r") as f:
            content = f.read()
        file_errors, _ = config_validation.transform_config(content, cmd_whitelist, general_proxy)
        errors += [name + ": " + e for e in file_errors]
    if len(errors) > 0:
        for error in errors:
            print(error, file=sys.stderr)
        exit(1)
    exit(0)
