import cli_args, hostlist, os, subprocess, sys, tui_dialog, xdg

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

def matches_substring(display_name, substring):
    return substring in display_name

def matches_all_substrings(display_name, substring, additional_substrings):
    if not matches_substring(display_name, substring):
        return False
    for substr in additional_substrings:
        if not matches_substring(display_name, substr):
            return False
    return True

def ensure_no_usernames(substrings):
    for substr in substrings:
        if '@' in substr:
            print("Only the first substring may contain a username")
            sys.exit(1)

def split_user_from_substring(s):
    idx = s.find('@')
    if idx == -1:
        # contains no username
        return (None, s)
    return (s[0:idx], s[idx+1:])

def main():
    args = cli_args.parse_args()
    hosts = hostlist.load_config(os.environ['HOME'] + '/.local/share/lssh/hosts')

    user, substring = split_user_from_substring(args[0].substring)
    additional_substrings = args[0].additional_substrings
    ensure_no_usernames(additional_substrings)
    if substring is None:
        matched_hosts = hosts
    else:
        matched_hosts = {}
        for display_name in hosts:
            if matches_all_substrings(display_name, substring, additional_substrings):
                matched_hosts[display_name] = hosts[display_name]

    if len(matched_hosts) == 0:
        print("No matching hosts for substring `" + substring + "' found")
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

    print(selected)
    user_prefix = "" if user is None else user + "@"
    sys.exit(subprocess.run(["ssh", user_prefix + selected]).returncode)
