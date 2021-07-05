# Installing lssh manually

# Dependencies

- **git**  
  If you want to share your host configuration using git, you will need git installed locally. But another vcs will also work.

- (optional) **sudo**  
  If you install lssh systemwide, you may need sudo to run config updates as a normal user.

## Needed python packages

- xdg
- py-cui

You can install them for example using the system package manager or via pip3.

# Installing

Before you start to install, you need to specify a few paths on your file system.
Placeholders are used in the rest of this guide that you need to replace with your actual chosen path.

- A bin directory where the lssh python script can be stored, called `$BIN`
- A place where the lssh directory with the main python code can be stored, called `$LIB`
- A local directory for the repository clone containing host entries, called `$HOST_REPO_CLONE`
- A local directory for the validated host entries, called `$HOSTS_VALIDATED`

## Installing python code

Copy the lssh directory from this repository to the `$LIB` directory.

For understanding: The python files must be located under `$LIB/lssh/*.py`

```bash
cp -r lssh $LIB/
```

## Clone the host configuration repository

Clone the repository that contains your ssh configuration files, to the location `$HOST_REPO_CLONE`, for example using git:

```bash
git clone _your-clone-url_ $HOST_REPO_CLONE
```

## Create a folder for validated host entries

Create an empty folder at `$HOSTS_VALIDATED`:

```bash
mkdir $HOSTS_VALIDATED
```

## Create the lssh executable file

Use the following template to create the executable script `$BIN/lssh` and customize it.

```python
#! /usr/bin/env python3

import sys

repo_clone = "<host repo clone>"
validated = "<hosts validated>"

def update_hosts():
    # Called when a user executes `lssh --update-hosts`
    import subprocess
    subprocess.run(["git", "pull"], cwd=repo_clone)
    subprocess.run(["lssh", "--load-from", repo_clone])

sys.path.append("<lib>")

from lssh import main
main.main(validated, update_hosts)
```

Replace `<hosts validated>` with your `$HOSTS_VALIDATED`, `<host repo clone>` with your `$HOST_REPO_CLONE` and `<lib>` with your `$LIB` in the template

Make the file executable:

```bash
chmod +x $BIN/lssh
```

## Include the ssh configuration files

In your ssh client configuration file (for example `/etc/ssh/ssh_config` or `~/.ssh/config`) add an include-entry using the following template:

```
Host *
Include <hosts validated>/*.txt
```

Replace `<hosts validated>` with your `$HOSTS_VALIDATED`.

Replace `example.com` with the actual alias hostname of your proxy in both lines.

## Setup bash completion

Put the following instruction into a bash startup file for example `~/.bashrc`

```bash
complete -o filenames -C 'lssh __complete__' lssh
```

# Optional settings

## General first proxy

You may specify a global proxy machine in the ssh client configuration. This proxy will always be used as a first connection step to the target machine.

To activate the proxy, add the settings using the following template below the include-instruction that you put in your ssh client configuration file:

```
Match originalhost !example.com,*
ProxyJump example.com
```

## Allow remote commands

For details what is needed to allow the automatic execution of remote commands, see [remote-command-whitelist.md](remote-command-whitelist.md). In the following, the setup of a whitelist is explained.

The lssh executable at `$BIN/lssh` contains the following last line:

```python
main.main(validated, update_hosts)
```

The function `main.main` accepts an optional third argument, `cmd_whitelist_func`. If specified, it must be a callable that returns a list of whitelist rules.

Each whitelist rule is a 3-tuple in the form `(user, hostname, command)`. For the meaning of these fields, see [remote-command-whitelist.md](remote-command-whitelist.md).

An example configuration may look like this:

```python
def build_cmd_whitelist():
    return [
        ("root", "example.com", "ls"),
    ]
main.main(validated, update_hosts, build_cmd_whitelist)
```

If you like to use a csv file instead (this is the configuration when running `debian-systemwide-install`), you may use the following code:

```python
def build_cmd_whitelist():
    from lssh import command_whitelist
    return command_whitelist.load("/etc/lssh/remotecommand-whitelist.csv")

main.main(hosts_dir, update_hosts, build_cmd_whitelist)
```
