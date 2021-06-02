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
    'hostbasedauthentication',
    'hostbasedkeytypes',
    'hostkeyalgorithms',
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
# CheckHostIP, StrictHostKeyChecking, UpdateHostKeys, UserKnownHostsFile, VerifyHostKeyDNS, VisualHostKey:
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

class HostSection():
    def __init__(self):
        self.reset(None, None)
    def reset(self, hostname, line_nr):
        self.__hostname = hostname
        self.__heading_line_nr = line_nr
        self.__connectname_set = False
        self.__connectname_line = None
        self.__alias_set = False
        self.__alias_line = None
    def register_connectname(self, line_nr):
        if self.__hostname is None:
            return "Option HostName is not allowed on line " + str(line_nr) + ", only allowed in an explicit Host section (one host, no wildcards)"
        elif self.__connectname_set:
            return "Option HostName is only allowed once per host block. (Appeared in line " + str(self.__connectname_line) + " and " + str(line_nr) + ")"
        else:
            self.__connectname_set = True
            self.__connectname_line = line_nr
            return None
    def set_hostkeyalias(self, alias, line_nr):
        if self.__hostname is None:
            return "Option HostKeyAlias is not allowed on line " + str(line_nr) + ", only allowed in an explicit Host section (one host, no wildcards)"
        elif self.__alias_set:
            return "Option HostKeyAlias is only allowed once per host block. (Appeared in line " + str(self.__alias_line) + " and " + str(line_nr) + ")"
        elif alias != self.__hostname:
            self.__alias_set = True
            return "The value of the HostKeyAlias field on line " + str(line_nr) + " must match the host keyword of this host block (`" + self.__hostname + "')"
        else:
            self.__alias_set = True
            self.__alias_line = line_nr
            return None
    def validate(self):
        if self.__connectname_set and not self.__alias_set:
            return "Host section beginning at line " + str(self.__heading_line_nr) + " must contain a `HostKeyAlias " + self.__hostname + "' because it contains a custom HostName setting."

def check_line(section, line, nr):
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
        instruction_l = instruction.lower()
        if instruction_l in instruction_whitelist:
            # allowed setting
            return None
        elif instruction_l == 'host':
            # A new section begins here. First validate the previous section (Ensure no fields are missing)
            validation = section.validate()
            # Now reset for a new section
            name = m.group(2)
            if '*' in name or '?' in name or ' ' in name.strip():
                section.reset(None, None)
            else:
                section.reset(m.group(2), nr)
            return validation
        elif instruction_l == 'hostname':
            # If HostName is set, HostKeyAlias must also be set.
            return section.register_connectname(nr)
        elif instruction_l == 'hostkeyalias':
            return section.set_hostkeyalias(m.group(2), nr)
        # disallowed setting
        return "Option `" + instruction + "' (line " + str(nr) + ") is not whitelisted."
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
    section = HostSection()
    for line in lines:
        error = check_line(section, line, line_nr)
        if error is not None:
            errors.append(error)
        line_nr += 1
    section.validate()
    return errors
