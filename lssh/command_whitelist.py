import csv, sys
from lssh import xdg_compat

def convert_field(value):
    if value == "*":
        return None
    return value

def convert_row(row):
    user, hostname, command = row
    return convert_field(user), convert_field(hostname), command

def load(filename):
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            result = []
            i = 1
            for row in reader:
                if len(row) != 3:
                    print("Warning: Line " + str(i) + " in " + filename + " is invalid - expected 3 columns but found " + str(len(row)), file=sys.stderr)
                else:
                    result.append(convert_row(row))
                i += 1
            return result
    except FileNotFoundError:
        return []

def load_default_paths():
    global_path = "/etc/lssh/remotecommand-whitelist.csv"
    local_path = xdg_compat.config_home() / "lssh" / "remotecommand-whitelist.csv"
    return load(global_path) + load(local_path)
