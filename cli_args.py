import argparse

parser = argparse.ArgumentParser(prog='lssh')

parser.add_argument('-r', '--replay', action='store_true', help='Watch a previously recored ssh session.')
parser.add_argument('--timestamp', dest='TIME', help='The exact timestamp when the session recording was started, in the form YYYY-MM-DD_hh-mm-ss. (Implies --replay)')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode. Enablkes printing the resulting ssh command line before connecting.')

parser.add_argument('substring', metavar='[user@]substring', nargs='?', help='(Part of) the hostname to connect to, with an additional username if needed.')

parser.parse_known_args()
