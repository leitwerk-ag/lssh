import re, sys

ssh_config_filename = '/etc/ssh/ssh_config'
lssh_begin_line = '# == automatically added lssh config entries =='
lssh_include_entry = 'Include /var/local/lssh/hosts/*.txt'
lssh_end_line = '# == end of automatically added lssh config entries =='

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

def replace_lssh_config_section(lines):
    current = load_ssh_config_lines()
    begin_idx = [i for i in range(len(current)) if current[i] == lssh_begin_line]
    end_idx = [i for i in range(len(current)) if current[i] == lssh_end_line]
    def err(msg):
        print("Error: " + msg, file=sys.stderr)
        exit(1)
    if len(begin_idx) > 1:
        err("Found more than one lssh begin comment in " + ssh_config_filename + " - Failed to edit!")
    if len(end_idx) > 1:
        err("Found more than one lssh end comment in " + ssh_config_filename + " - Failed to edit!")
    if len(begin_idx) == 1 and len(end_idx) == 0:
        err("Found only the lssh begin comment but no end comment in " + ssh_config_filename + " - Failed to edit!")
    if len(begin_idx) == 0 and len(end_idx) == 1:
        err("Found only the lssh end comment but no begin comment in " + ssh_config_filename + " - Failed to edit!")
    if len(begin_idx) == 1 and begin_idx[0] > end_idx[0]:
        err("Found the lssh end comment before the lssh begin comment in " + ssh_config_filename + " - Failed to edit!")
    if len(begin_idx) == 0:
        # No lssh section in ssh_config yet, just append it
        new = current + lines
    else:
        # Replace the existing lssh section
        new = current[0:begin_idx[0]] + lines + current[end_idx[0]+1:]
    if new != current:
        save_config_lines(new)
    return len(begin_idx) == 1

def add_section():
    lines = [lssh_begin_line, "Host *", lssh_include_entry, lssh_end_line]
    replace_lssh_config_section(lines)

def remove_section():
    return replace_lssh_config_section([])
