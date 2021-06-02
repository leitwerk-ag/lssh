# Installing lssh manually

Before you start to install, you need to specify a few paths on your file system.
Placeholders are used in the rest of this guide that you need to replace with your actual chosen path.

- A bin directory where the lssh python script can be stored, called `$BIN`
- A place where the lssh directory with the main python code can be stored, called `$LIB`
- A path for the repository containing host entries, called `$HOST_REPO`
- A path for the validated host entries, called `$HOSTS`

## Installing python code

Copy the lssh directory from this repository to the `$LIB` directory.

For understanding: The python files must be located under `$LIB/lssh/*.py`

```bash
cp -r lssh $LIB/
```

## Clone the host configuration repository

Clone the repository that contains your ssh configuration files, to the location `$HOST_REPO`, for example using git:

```bash
git clone _your-clone-url_ $HOST_REPO
```

## Create the lssh executable file

Use the following template to create the executable script `$BIN/lssh` and customize it.

```python
#! /usr/bin/env python3

import sys

hosts_dir = "<hosts dir>"

def update_hosts():
    # Called when a user executes `lssh --update-hosts`
    import subprocess
    subprocess.run(["git", "pull"], cwd=hosts_dir)
    subprocess.run(["lssh", "--load-from", "<host repo>"])

sys.path.append("<lib>")

from lssh import main
main.main(hosts_dir, update_hosts)
```

Replace `<hosts dir>` with your `$HOSTS`, `<host repo>` with your `$HOST_REPO` and `<lib>` with your `$LIB` in the template

Make the file executable:

```bash
chmod +x $BIN/lssh
```

## Include the ssh configuration files

In your ssh client configuration file (for example `/etc/ssh/ssh_config` or `~/.ssh/config`) add an include-entry using the following template:

```
Include <hosts dir>/*.txt
```

Replace `<hosts dir>` with your `$HOSTS`.

## Setup bash completion

Put the following instruction into a bash startup file for example `~/.bashrc`

```bash
complete -o filenames -C 'lssh __complete__' lssh
```
