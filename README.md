# lssh - Leitwerk SSH Wrapper

This wrapper-tool is suitable to be used in organizations for accessing ssh hosts.

A central git repository contains the ssh configuration for all your hosts and will be accessed by all users of lssh.

## Features

- Searching hosts by specifying keywords (matching hostname, or the filename that contains the host)
- Possibility to specify multiple keywords for filtering hosts
- A tui dialog to choose one of the hosts matching the given keywords
- Checks additional keywords that are given in your central configuration (per file or per host)
- Automatic session recording of each ssh session in the home directory of the calling user with a replay command option
- SSH command options are passed through
- Tab-completion for Bash
- Automatically starts and uses an ssh-agent if not already started
- The ssh configuration of the git repository is included in the official ssh configuration file, so all hosts are also accessible using ssh, without the wrapper.
- The include of the ssh configuration is protected by a security validation to prevent code execution.

## Install

### Debian

For the debian linux distribution, there is an install-script that installs lssh for all users and must be run as root:  
`./install/debian-systemwide-install <git_repo_url>`  
Replace `<git_repo_url>` with the clone url of your ssh configuration repository, that must be formatted as described in [SSH config format](./docs/ssh_config_format.md)

There is also a corresponding uninstaller:  
`./install/debian-systemwide-uninstall`

### Other distributions

If you use another distribution or want custom settings, you can also install and configure lssh manually.  
See [Installing lssh manually](./docs/install-manually.md).

## Using lssh

After successful installation, run `lssh --help` to see the possible commands and options.
