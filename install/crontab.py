import random, re, subprocess

def load_crontab_lines():
    proc = subprocess.run(["crontab", "-l"], capture_output=True)
    if proc.returncode == 1:
        # No crontab
        return []
    proc.check_returncode()
    lines = proc.stdout.decode().split("\n")
    if len(lines) > 0 and lines[-1] == "":
        lines = lines[:-1]
    return lines

def save_crontab_lines(lines):
    content = ("".join([l+"\n" for l in lines])).encode()
    subprocess.run(["crontab", "-"], input=content).check_returncode()

def is_pull_entry(line):
    return re.match('^([^#\\s]+\\s+){5}/var/local/lssh/pull.sh # automatically added by lssh installer$', line) is not None

def add_pull_entry():
    lines = load_crontab_lines()
    # Check if there is already an entry
    if len([l for l in lines if is_pull_entry(l)]) > 0:
        return
    # Choose a random minute to distribute the load
    minute = random.randrange(0, 60)
    lines.append(str(minute) + " * * * * /var/local/lssh/pull.sh # automatically added by lssh installer")
    save_crontab_lines(lines)

def remove_pull_entry():
    current = load_crontab_lines()
    new = [l for l in current if not is_pull_entry(l)]
    if len(new) < len(current):
        save_crontab_lines(new)
        return True
    return False
