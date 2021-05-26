import json, os, re, socket, subprocess

import xdg
if not hasattr(xdg, 'xdg_cache_home'):
    from xdg import BaseDirectory as xdg # Fallback for old xdg version (debian)

def ssh_agent_config_filename():
    return xdg.xdg_cache_home() / 'lssh' / 'ssh_agent.config'

def load_config():
    try:
        with open(ssh_agent_config_filename(), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def valid_config(config):
    sock_path = config['SSH_AUTH_SOCK']
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(sock_path)
        s.close()
        return True
    except (FileNotFoundError, ConnectionRefusedError):
        return False

def start_agent():
    completed = subprocess.run(['ssh-agent', '-c'], capture_output=True)
    output = completed.stdout.decode()
    lines = output.split("\n")
    env_vars = {}
    for line in lines:
        m = re.match('^setenv ([^ ]+) (.*);$', line)
        if m:
            env_vars[m.group(1)] = m.group(2)
    os.makedirs(ssh_agent_config_filename().parent, exist_ok=True)
    with open(ssh_agent_config_filename(), 'w') as f:
        json.dump(env_vars, f)
    return env_vars

def apply_config(config):
    output = os.environ.copy()
    output.update(config)
    return output

def get_environment():
    if os.environ.get('SSH_AUTH_SOCK') is not None:
        # agent already started by user or system, do not start another one
        return os.environ.copy()
    ssh_agent_config = load_config()
    if ssh_agent_config is None:
        # No valid config found, start a new agent
        new_config = start_agent()
        return apply_config(new_config)
    if valid_config(ssh_agent_config):
        # Agent was previously started by lssh, use its settings
        return apply_config(ssh_agent_config)
    # Agent is no longer running, start a new one
    new_config = start_agent()
    return apply_config(new_config)
