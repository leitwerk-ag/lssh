from pathlib import Path

import xdg
if not hasattr(xdg, 'xdg_cache_home'):
    from xdg import BaseDirectory as xdg # Fallback for old xdg version (debian)

def cache_home():
    if type(xdg.xdg_cache_home) is str:
        return Path(xdg.xdg_cache_home)
    return xdg.xdg_cache_home()

def config_home():
    if type(xdg.xdg_config_home) is str:
        return Path(xdg.xdg_config_home)
    return xdg.xdg_config_home()

def data_home():
    if type(xdg.xdg_data_home) is str:
        return Path(xdg.xdg_data_home)
    return xdg.xdg_data_home()
