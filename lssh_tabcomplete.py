import sys

# To activate tab completion in bash:
# complete -C 'lssh __complete__' lssh

def main():
    if len(sys.argv) < 5:
        return
    current_arg = sys.argv[3]
    previous_arg = sys.argv[4]

    if previous_arg == '--timestamp':
        # timestamp completion
        choices = []
    elif current_arg.startswith('-'):
        # option completion
        choices = ['--help', '--replay', '--timestamp', '--verbose']
    else:
        choices = []
    result = [x for x in choices if x.startswith(current_arg)]
    print("\n".join(result))
