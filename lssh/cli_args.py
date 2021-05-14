import argparse

parameterless_options = '46AaCfGgKkMNnqsTtVXxYy'
parameter_options = 'BbcDEeFIiJLlmOopQRSWw'

def parse_args():
    parser = argparse.ArgumentParser(prog='lssh')

    parser.add_argument('-r', '--replay', action='store_true', help='Watch a previously recored ssh session.')
    parser.add_argument('--timestamp', metavar='TIME', dest='time', help='The exact timestamp when the session recording was started, in the form YYYY-MM-DD_hh-mm-ss. (Implies --replay)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode. Enables printing the resulting ssh command line before connecting.')

    options_summary = [c for c in parameterless_options + parameter_options]
    options_summary.sort(key=lambda c: (str.lower(c), c))
    pass_through = parser.add_argument_group('ssh options', 'The following options are passed through to the ssh command: ' + "".join(options_summary) + ", see the ssh(1) man page for details.")
    for opt in parameterless_options:
        pass_through.add_argument('-' + opt, action='count', help=argparse.SUPPRESS)
    for opt in parameter_options:
        pass_through.add_argument('-' + opt, action='append', help=argparse.SUPPRESS)

    parser.add_argument('substring', metavar='[user@]substring', nargs='?', help='(Part of) the hostname to connect to, with an additional username if needed.')
    parser.add_argument('additional_substrings', metavar='substring', nargs='*', help='Additional parts of the hostname to connect to, which further restrict the search')

    return parser.parse_args()
