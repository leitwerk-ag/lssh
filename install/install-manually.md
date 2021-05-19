# Installing lssh manually

Before you start to install, you need to specify a few paths on your file system.
Placeholders are used in the rest of this guide that you need to replace with your actual chosen path.

- A bin directory where the lssh python script can be stored, called `$BIN`
- A place where the lssh directory with the main python code can be stored, called `$LIB`
- A path for the repository containing host entries, called `$HOSTS`

## Installing python code

Copy the lssh directory from this repository to the `$LIB` directory.

For understanding: The python files must be located under `$LIB/lssh/*.py`

```bash
cp -r lssh $LIB/
```

## Clone the host configuration repository

Clone the repository that contains your ssh configuration files, to the location `$HOSTS`, for example using git:

```bash
git clone _your-clone-url_ $HOSTS
```

## Create the lssh executable file

Use the following template to create the executable script `$BIN/lssh` and customize it.

```python
#! /usr/bin/env python3

import sys

hosts_dir = "$HOSTS"

def update_hosts():
    import subprocess
    subprocess.run(["git", "pull"], cwd=hosts_dir)

sys.path.append("$LIB")

from lssh import main
main.main(hosts_dir, update_hosts)
```

Replace `$HOSTS` and `$LIB` in the template

The function `update_hosts()` is called when a user executes `lssh --update-hosts`. You may adapt the pull command to other version control systems and/or use sudo rules. For details on command execution, see https://docs.python.org/3/library/subprocess.html

Make the file executable:

```bash
chmod +x $BIN/lssh
```

## Setup bash completion

Put the following instruction into a bash startup file

```bash
complete -C 'lssh __complete__' lssh
```
