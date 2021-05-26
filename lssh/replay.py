import re, os, subprocess, sys
from lssh import tui_dialog, xdg_compat

def name_matches(name, substrings, timestamp):
    m = re.match('^([0-9\\-]+_[0-9\\-]+)_(.*)$', name)
    if not m:
        # If regex does not fit, it cannot be a recording
        return False
    t = m.group(1)
    if timestamp is not None and t != timestamp:
        # Timestamp does not fit
        return False
    name = m.group(2)
    # name might contain a trailing counter value, but this does not matter for substring match
    for sub in substrings:
        if sub not in name:
            # One substring does not match
            return False
    return True

def replay_recording(dirname):
    print("Replaying " + dirname + " ...")
    recording_path = xdg_compat.data_home() / 'lssh' / 'recordings' / dirname
    timing_file = str(recording_path / 'timing')
    output_file = str(recording_path / 'output')
    command = ['scriptreplay', '-t', timing_file, output_file]
    sys.exit(subprocess.run(command).returncode)

def replay(substrings, timestamp):
    recordings_basedir = xdg_compat.data_home() / 'lssh' / 'recordings'
    rec_files = os.listdir(recordings_basedir)
    matching_rec_files = [name for name in rec_files if name_matches(name, substrings, timestamp)]
    if len(matching_rec_files) == 0:
        print("No matching recording was found")
        sys.exit(1)
    elif len(matching_rec_files) == 1:
        replay_recording(matching_rec_files[0])
    else:
        matching_rec_files.sort()
        choice_idx = tui_dialog.flat_option_dialog(matching_rec_files, "Please choose a recording to replay")
        if choice_idx is None:
            print("No recording has been selected")
            sys.exit(1)
        choice = matching_rec_files[choice_idx]
        replay_recording(choice)
