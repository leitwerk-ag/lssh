ssh_config_filename = '/etc/ssh/ssh_config'
lssh_include_entry = 'Include /var/local/lssh/hosts/*.txt # automatically added by lssh installer'

def load_ssh_config_lines():
    with open(ssh_config_filename, "r") as f:
        data = f.read()
    lines = data.split("\n")
    if len(lines) > 0 and lines[-1] == "":
        lines = lines[:-1]
    return lines

def save_config_lines(lines):
    content = "".join([l+"\n" for l in lines])
    with open(ssh_config_filename, "w") as f:
        f.write(content)

def add_include_entry():
    lines = load_ssh_config_lines()
    # Check if there is already an entry
    if len([l for l in lines if l == lssh_include_entry]) > 0:
        return
    lines.append(lssh_include_entry)
    save_config_lines(lines)

def remove_include_entry():
    current = load_ssh_config_lines()
    new = [l for l in current if l != lssh_include_entry]
    if len(new) < len(current):
        save_config_lines(new)
        return True
    return False
