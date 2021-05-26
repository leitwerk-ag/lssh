import os, re
from lssh import xdg_compat

def find_recording_files():
    recordings_basedir = xdg_compat.data_home() / 'lssh' / 'recordings'
    rec_files = os.listdir(recordings_basedir)
    file_entries = []
    for file_name in rec_files:
        m = re.match('^([0-9\\-]+_[0-9\\-]+)_(.*)$', file_name)
        if not m:
            # If regex does not fit, it cannot be a recording
            continue
        t = m.group(1)
        name = m.group(2)
        file_entries.append((file_name, t, name))
    return file_entries
