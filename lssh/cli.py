import itertools, os, shlex, subprocess, sys, time
from lssh import cli_args, hostlist, replay, ssh_agent, tui_dialog, xdg_compat

def group_options_by_customer(hosts):
    map_customer = {}
    for hostname in hosts:
        customer = hosts[hostname].customer
        if customer not in map_customer:
            map_customer[customer] = []
        map_customer[customer].append(hosts[hostname].display_name)
    customers = list(map_customer.keys())
    customers.sort()
    def make_option(customer):
        values = map_customer[customer]
        values.sort()
        return (customer, values)
    return [make_option(c) for c in customers]

def matches_substring(host, substring):
    if substring in host.display_name:
        return True
    for keyword in host.keywords:
        if substring in keyword:
            return True
    return False

def matches_all_substrings(host, substring, additional_substrings):
    if not matches_substring(host, substring):
        return False
    for substr in additional_substrings:
        if not matches_substring(host, substr):
            return False
    return True

def ensure_no_usernames(substrings):
    for substr in substrings:
        if '@' in substr:
            print("Only the first substring may contain a username")
            sys.exit(1)

def split_user_from_substring(s):
    if s is None:
        return (None, None)
    idx = s.find('@')
    if idx == -1:
        # contains no username
        return (None, s)
    return (s[0:idx], s[idx+1:])

def create_recording_directory(hostname):
    recordings_basedir = xdg_compat.data_home() / 'lssh' / 'recordings'
    os.makedirs(recordings_basedir, exist_ok=True)
    name = time.strftime("%Y-%m-%d_%H-%M-%S") + '_' + hostname
    try:
        d = recordings_basedir / name
        os.mkdir(d)
        return d
    except FileExistsError:
        for i in itertools.count(2):
            try:
                d = recordings_basedir / (name + '_' + str(i))
                os.mkdir(d)
                return d
            except FileExistsError:
                pass

def main(hosts_dir, update_hosts):
    args = cli_args.parse_args()

    user, substring = split_user_from_substring(args.substring)
    additional_substrings = args.additional_substrings
    ensure_no_usernames(additional_substrings)
    if args.update:
        update_hosts()
    elif args.load is not None:
        hostlist.import_new_config(args.load, hosts_dir)
    elif args.replay or args.time is not None:
        if substring is None:
            all_substrings = []
        else:
            all_substrings = [substring] + additional_substrings
        replay.replay(all_substrings, args.time)
    else:
        connect(args, user, substring, additional_substrings, hosts_dir)

def select_host(substring, additional_substrings, hosts_dir):
    hosts = hostlist.load_config(hosts_dir)
    if substring is None:
        matched_hosts = hosts
    else:
        matched_hosts = {}
        for display_name in hosts:
            host = hosts[display_name]
            if matches_all_substrings(host, substring, additional_substrings):
                matched_hosts[display_name] = hosts[display_name]

    if len(matched_hosts) == 0:
        if len(hosts) == 0:
            print("No hosts defined in the configuration")
        elif len(additional_substrings) == 0:
            print("No matching hosts for substring `" + substring + "' found")
        else:
            print("No matching hosts for the given substrings found")
        sys.exit(1)
    elif len(matched_hosts) == 1:
        selected = list(matched_hosts.keys())[0]
    else:
        options = group_options_by_customer(matched_hosts)
        choice = tui_dialog.hierarchical_option_dialog(options, 'select customer', 'select host')
        if choice is None:
            print("No host has been selected")
            sys.exit(1)
        selected = options[choice[0]][1][choice[1]]
    return selected

def connect(args, user, substring, additional_substrings, hosts_dir):
    selected = select_host(substring, additional_substrings, hosts_dir)

    options_dict = vars(args)
    command = ['ssh']
    for opt in cli_args.parameterless_options:
        count = options_dict[opt]
        if count is not None:
            command.append('-' + count * opt)
    for opt in cli_args.parameter_options:
        parameters = options_dict[opt]
        if parameters is not None:
            for param in parameters:
                command += ['-' + opt, param]
    if args.verbose is not None:
        command.append('-' + args.verbose * 'v')
    user_prefix = "" if user is None else user + "@"
    command.append(user_prefix + selected)
    rec_dir = create_recording_directory(selected)
    ssh_commandline = ' '.join([shlex.quote(arg) for arg in command])
    if args.verbose is not None:
        print("executing command: " + ssh_commandline)
    script_command = ['script', '-t'+str(rec_dir / 'timing'), rec_dir / 'output', '-c', ssh_commandline]
    sys.exit(subprocess.run(script_command, env=ssh_agent.get_environment()).returncode)
