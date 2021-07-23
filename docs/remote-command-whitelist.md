# Allowing the RemoteCommand option

The configuration option `RemoteCommand` is not allowed by default in the central ssh configuration file. It would allow to execute arbitrary commands on any target host just by changing the configuration.

To allow the `RemoteCommand` option, you need to specify a whitelist of allowed commands.

| :information_source: Please note |
|---|
| This whitelist does not restrict users from executing commands on the server. It restricts the central ssh config from executing commands automatically. |

The whitelist is a csv file (one rule per row) with the columns: `user`, `hostname`, `command`.

|field|content|
|--|--|
|`user`|The remote username this rule applies for. May be `None` to allow the command for every target user.|
|`hostname`|The dns name of the target host. (not the host alias, if the `HostName` config is specified) May be `None` to allow the command on every target host.|
|`command`|The base command (command without options) that is allowed. For example, to base command of `ls -al` is just `ls`.|

There are two locations, where this csv file is loaded from. (If both exist, they are combined.)

- `/etc/lssh/remotecommand-whitelist.csv`
- `~/.config/lssh/remotecommand-whitelist.csv`  
  (If the environment variable `XDG_CONFIG_HOME` is set, `$XDG_CONFIG_HOME/lssh/remotecommand-whitelist.csv` is used instead.)

Note that lssh might run as root when updating the configuration, depending on your setup. In this case, the user-specific config file will not be read.

## Example

When connecting to `root@example.com`, we want to automatically execute `ls -t`.

The following ssh configuration may be used to achieve this:

```
Host examplehost
    HostName example.com
    User root
    RemoteCommand ls -t
```

Now a whitelist is needed on every lssh installation, otherwise lssh will refuse to import the above configuration.

Example content of this csv file:

```csv
root,example.com,ls
```
