import re, shlex

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
# HostKeyAlias
#   This field is automatically added for each host that contains a HostName setting.
#   It is needed for security reasons and must not be set manually.
# Include:
#   An attacker could include unwanted files (needs to be owned by root, but there might be a way to do so).
#   This would bypass all the other security measures.
# LocalCommand, PermitLocalCommand, ProxyCommand, ProxyUseFdpass, RemoteCommand, XAuthLocation:
#   An attacker could specify arbitrary commands
# SendEnv:
#   Environment variables should generally not contain secrets. But to be completely sure, sending
#   these variables is disallowed.

def parse_escaped_command(command):
    remaining = command
    main_command = ""
    main_command_finished = False
    while remaining != "":
        m = re.match('( |"\'"|\'[^\']+\')(.*)$', remaining)
        if m:
            part = m.group(1)
            if part == " ":
                if main_command != "":
                    main_command_finished = True
            elif not main_command_finished:
                main_command += part
            remaining = m.group(2)
            continue
        m = re.match('([^ \'"]+)(.*)$', remaining)
        if m:
            part = m.group(1)
            if not shlex.quote(part) == part:
                return None
            if not main_command_finished:
                main_command += part
            remaining = m.group(2)
            continue
        return None
    return main_command

class HostSection():
    def __init__(self, cmd_whitelist):
        self.__cmd_whitelist = cmd_whitelist
        self.__hostname = None
        self.reset(None, None)
    def reset(self, hostname, line_nr):
        result = self.validate()
        self.__hostname = hostname
        self.__username = None
        self.__username_line = None
        self.__command = None
        self.__command_linenr = None
        self.__heading_line_nr = line_nr
        self.__connectname = None
        self.__connectname_line = None
        return result
    def current_host(self):
        return self.__hostname
    def register_connectname(self, name, line_nr):
        if self.__hostname is None:
            return "Option HostName is not allowed on line " + str(line_nr) + ", only allowed in an explicit Host section (one host, no wildcards)"
        elif self.__connectname is not None:
            return "Option HostName is only allowed once per host block. (Appeared in line " + str(self.__connectname_line) + " and " + str(line_nr) + ")"
        else:
            self.__connectname = name
            self.__connectname_line = line_nr
            return None
    def register_username(self, user, line_nr):
        if self.__hostname is not None and self.__username is not None:
            return "Option User is only allowed once per host block. (Appeared in line " + str(self.__username_line) + " and " + str(line_nr) + ")"
        self.__username = user
        self.__username_line = line_nr
    def register_command(self, command, line_nr):
        if self.__hostname is None:
            return "Option RemoteCommand is not allowed on line " + str(line_nr) + ", only allowed in an explicit Host section (one host, no wildcards)"
        elif self.__command is not None:
            return "Option RemoteCommand is only allowed once per host block. (Appeared in line " + str(self.__command_linenr) + " and " + str(line_nr) + ")"
        else:
            self.__command = command
            self.__command_linenr = line_nr
            return None
    def validate(self):
        if self.__hostname is None:
            # No specific block, nothing to check
            return None
        if self.__command is None:
            # valid, accept
            return None
        cmdtarget_hostname = self.__connectname if self.__connectname is not None else self.__hostname
        for user, hostname, command in self.__cmd_whitelist:
            if command == self.__command and (user is None or user == self.__username) and (hostname is None or hostname == cmdtarget_hostname):
                # command is whitelisted
                return None
        display_username = self.__username if self.__username is not None else "<any user>"
        return "Command `" + self.__command + "' (line " + str(self.__command_linenr) + ") is not whitelisted for " + display_username + "@" + cmdtarget_hostname

def validate_line(section, line, nr, output_lines):
    if re.match('^\\s*$', line):
        # line is empty
        return None
    if re.match('^\\s*#.*', line):
        # line just contains a comment
        return None
    m = re.match('^(\\s*)([a-zA-Z]+) (.*)$', line)
    if m:
        # found an instruction
        instruction = m.group(2)
        instruction_l = instruction.lower()
        if instruction_l in instruction_whitelist:
            # allowed setting
            return None
        elif instruction_l == 'host':
            # Reset for a new section
            name = m.group(3)
            if '*' in name or '?' in name or ' ' in name.strip():
                return section.reset(None, None)
            elif not re.match('^[a-zA-Z0-9\\.\\-_]+$', name.strip()):
                return "The hostname " + name.strip() + " (line " + str(nr) + ") contains invalid characters."
            else:
                return section.reset(m.group(3), nr)
        elif instruction_l == 'hostname':
            # If HostName is set, HostKeyAlias must also be set.
            result = section.register_connectname(m.group(3), nr)
            if result is None:
                output_lines.append(m.group(1) + "HostKeyAlias " + section.current_host())
            return result
        elif instruction_l == 'user':
            return section.register_username(m.group(3), nr)
        elif instruction_l == 'remotecommand':
            full_command = m.group(3)
            program = parse_escaped_command(full_command)
            if program is None:
                parts = [p for p in full_command.split(" ") if p != ""]
                suggestion = " ".join([shlex.quote(p) for p in parts])
                return "The command on line " + str(nr) + " looks not properly escaped, suggested replacement (but use with care, might be wrong): " + suggestion
            return section.register_command(program, nr)
        # disallowed setting
        return "Option `" + instruction + "' (line " + str(nr) + ") is not whitelisted."
    # could not parse this line
    return "Line " + str(nr) + " could not be parsed by the validator."

def check_ssh_config_safety(content, cmd_whitelist):
    '''
    Check if the given ssh config file content is valid and safe.
    The content is given as a single string.
    A config is not safe, if it contains instructions that may cause harm to the user.
    An example is executing commands via 'Match exec ...'

    An array of error messages is returned. If it is empty, the check was successful.
    '''
    lines = content.split("\n")
    output_lines = []
    line_nr = 1
    errors = []
    section = HostSection(cmd_whitelist)
    for line in lines:
        output_lines.append(line)
        error = validate_line(section, line, line_nr, output_lines)
        if error is not None:
            errors.append(error)
        line_nr += 1
    error = section.validate()
    if error is not None:
        errors.append(error)
    return (errors, output_lines)
