# Allowing the RemoteCommand option

The configuration option `RemoteCommand` is not allowed by default in the central ssh configuration file. It would allow to execute arbitrary commands on any target host just by changing the configuration.

To allow the `RemoteCommand` option, you need to specify a whitelist of allowed commands.

| :information_source: Please note |
|---|
| This whitelist does not restrict users from executing commands on the server. It restricts the central ssh config from executing commands automatically. |

The whitelist is a list of rules where each rule has three fields: `user`, `hostname`, `command`.

|field|content|
|--|--|
|`user`|The remote username this rule applies for. May be `None` to allow the command for every target user.|
|`hostname`|The dns name of the target host. (not the host alias, if the `HostName` config is specified) May be `None` to allow the command on every target host.|
|`command`|The base command (command without options) that is allowed. For example, to base command of `ls -al` is just `ls`.|

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

|user|hostname|command|
|---|---|---|
|root|example.com|ls|

## Whitelist in csv file

When installing lssh using the `debian-systemwide-install` script, you can manage the whitelist in `/etc/lssh/remotecommand-whitelist.csv`. The same setup is also possible when installing manually, see [install-manually.md](./install-manually.md).

Example content of this csv file:

```csv
root,example.com,ls
```
