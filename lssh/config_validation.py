import re

instruction_whitelist = {
    'addkeystoagent',
    'addressfamily',
    'batchmode',
    'bindaddress',
    'bindinterface',
    'canonicaldomains',
    'canonicalizefallbacklocal',
    'canonicalizehostname',
    'canonicalizemaxdots',
    'canonicalizepermittedcnames',
    'casignaturealgorithms',
    'certificatefile',
    'challengeresponseauthentication',
    'ciphers',
    'clearallforwardings',
    'compression',
    'connectionattempts',
    'connecttimeout',
    'controlmaster',
    'controlpath',
    'controlpersist',
    'dynamicforward',
    'enablesshkeysign',
    'escapechar',
    'exitonforwardfailure',
    'fingerprinthash',
    'gatewayports',
    'globalknownhostsfile',
    'gssapiauthentication',
    'gssapiclientidentity',
    'gssapikeyexchange',
    'gssapirenewalforcesrekey',
    'gssapiserveridentity',
    'gssapitrustdns',
    'host',
    'hostbasedauthentication',
    'hostbasedkeytypes',
    'hostkeyalgorithms',
    'hostname',
    'identitiesonly',
    'identityagent',
    'identityfile',
    'ignoreunknown',
    'ipqos',
    'kbdinteractiveauthentication',
    'kbdinteractivedevices',
    'kexalgorithms',
    'localforward',
    'loglevel',
    'macs',
    'nohostauthenticationforlocalhost',
    'numberofpasswordprompts',
    'passwordauthentication',
    'pkcs11provider',
    'port',
    'preferredauthentications',
    'proxyjump',
    'pubkeyacceptedkeytypes',
    'pubkeyauthentication',
    'rekeylimit',
    'remoteforward',
    'requesttty',
    'revokedhostkeys',
    'serveralivecountmax',
    'serveraliveinterval',
    'setenv',
    'streamlocalbindmask',
    'streamlocalbindunlink',
    'syslogfacility',
    'tcpkeepalive',
    'tunnel',
    'tunneldevice',
    'user',
}

# The following entries are intentionally not listed on the instruction_whitelist:
# Match:
#   Match exec ... allows an attacker to specify arbitrary commands
# ForwardAgent:
#   An attacker could enable agent forwarding and then misuse the agent of a victim.
# ForwardX11, ForwardX11Timeout, ForwardX11Trusted:
#   An attacer could enable X11 forwarding and misuse the display connection of a victim.
# GSSAPIDelegateCredentials:
#   An attacker controlling the target server could steal credentials when enabling this option.
# HashKnownHosts:
#   This is a client-side security setting. An attacker could disable hashing, resulting in worse security.
# CheckHostIP, HostKeyAlias, StrictHostKeyChecking, UpdateHostKeys, UserKnownHostsFile, VerifyHostKeyDNS, VisualHostKey:
#   Hostkeys are security-critical. An attacker could effectively bypass hostkey checking, resulting in
#   victims connecting to the wrong server without noticing.
# Include:
#   An attacker could include unwanted files (needs to be owned by root, but there might be a way to do so).
#   This would bypass all the other security measures.
# LocalCommand, PermitLocalCommand, ProxyCommand, ProxyUseFdpass, RemoteCommand, XAuthLocation:
#   An attacker could specify arbitrary commands
# SendEnv:
#   Environment variables should generally not contain secrets. But to be completely sure, sending
#   these variables is disallowed.

def check_line(line, nr):
    if re.match('^\\s*$', line):
        # line is empty
        return None
    if re.match('^\\s*#.*', line):
        # line just contains a comment
        return None
    m = re.match('^\\s*([a-zA-Z]+) (.*)$', line)
    if m:
        # found an instruction
        instruction = m.group(1)
        if instruction.lower() in instruction_whitelist:
            # allowed setting
            return None
        # disallowed setting
        return "Option " + instruction + " (line " + str(nr) + ") is not whitelisted."
    # could not parse this line
    return "Line " + str(nr) + " could not be parsed by the validator."

def check_ssh_config_safety(content):
    '''
    Check if the given ssh config file content is valid and safe.
    The content is given as a single string.
    A config is not safe, if it contains instructions that may cause harm to the user.
    An example is executing commands via 'Match exec ...'

    An array of error messages is returned. If it is empty, the check was successful.
    '''
    lines = content.split("\n")
    line_nr = 1
    errors = []
    for line in lines:
        error = check_line(line, line_nr)
        if error is not None:
            errors.append(error)
        line_nr += 1
    return errors
