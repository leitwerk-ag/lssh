# SSH config format

The lssh tool expects to find your ssh host configuration in a git repository. In the top-level directory of your repository, each file ending with `.txt` is read as an ssh configuration file.

Here is an example, how an ssh configuration file may look like:

```
Host example.com
    User root

Host a.example.com
    Port 4444

Host fileserver
    HostName ftp.central.example.com
    User ftp
```

These files are included in the configuration of ssh and must therefore be valid ssh_config syntax. But lssh puts further restrictions on the allowed configurations for security reasons. (For example to disallow code execution)

## Disallowed ssh_config options

For security reasons, the following options cannot be configured via the central git repository:

- Match
- ForwardAgent
- ForwardX11
- ForwardX11Timeout
- ForwardX11Trusted
- GSSAPIDelegateCredentials
- HashKnownHosts
- HostKeyAlias
- CheckHostIP
- StrictHostKeyChecking
- UpdateHostKeys
- UserKnownHostsFile
- VerifyHostKeyDNS
- VisualHostKey
- Include
- LocalCommand
- PermitLocalCommand
- ProxyCommand
- ProxyUseFdpass
- RemoteCommand
- XAuthLocation
- SendEnv

If one of these options appears in the git repository, lssh refuses to update its machine-local configuration and shows an error message when executing `lssh --update-hosts`.

## Additional lssh attributes

In each configuration file the options `#lssh:displayname` and `#lssh:filekeywords` can be specified once per file, see the following example:

```
#lssh:displayname example.com Hosts
#lssh:filekeywords demo, unreal

Host fileserver
    #lssh:keywords transfer, storage
    HostKeyAlias fileserver
    HostName ftp.central.example.com
    User ftp
```

The hash character makes this line a comment for ssh, but lssh reads these settings.

### `#lssh:displayname`

The value of this options tells lssh how to display this file (typically associated with one customer) in the tui dialog. If not given, the filename is used instead.

### `#lssh:filekeywords`

The comma-separated keywords of this options are associated with all hosts of this file. If one of the filekeywords or a substring of them is given on the lssh commandline, it will match all hosts of this file.

### `#lssh:keywords`

Keywords must be specified inside of a host block. If one of the given keywords or a substring is given on the lssh call, it will match this specific host.
