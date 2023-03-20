import os
from typing import Optional

AUTOJINJA_DEFAULT_FILENAME   = "__jinja__.py"
AUTOJINJA_DEFAULT_TAG        = "autojinja"
AUTOJINJA_DEFAULT_COG_OPEN   = "[[["
AUTOJINJA_DEFAULT_COG_CLOSE  = "]]]"
AUTOJINJA_DEFAULT_COG_END    = "end"
AUTOJINJA_DEFAULT_EDIT_OPEN  = "<<["
AUTOJINJA_DEFAULT_EDIT_CLOSE = "]>>"
AUTOJINJA_DEFAULT_EDIT_END   = "end"

AUTOJINJA_DEBUG          = "AUTOJINJA_DEBUG"
AUTOJINJA_REMOVE_MARKERS = "AUTOJINJA_REMOVE_MARKERS"
AUTOJINJA_SILENT         = "AUTOJINJA_SILENT"
AUTOJINJA_SUMMARY        = "AUTOJINJA_SUMMARY"
AUTOJINJA_THIS_DIRPATH   = "THIS_DIRPATH"

def osenviron_debug(env: Optional[os._Environ] = None) -> int:
    env = env or os.environ
    if AUTOJINJA_DEBUG not in env:
        return 0
    value = env[AUTOJINJA_DEBUG]
    is_valid = True
    if len(value) != 1:
        is_valid = False
    elif value != "0" and value != "1":
        is_valid = False
    if not is_valid:
        raise Exception(f"Expected 0 or 1 for environment variable '{AUTOJINJA_DEBUG}'")
    return 1 if value == "1" else 0

def osenviron_remove_markers(env: Optional[os._Environ] = None) -> int:
    env = env or os.environ
    if AUTOJINJA_REMOVE_MARKERS not in env:
        return 0
    value = env[AUTOJINJA_REMOVE_MARKERS]
    is_valid = True
    if len(value) != 1:
        is_valid = False
    elif value != "0" and value != "1":
        is_valid = False
    if not is_valid:
        raise Exception(f"Expected 0 or 1 for environment variable '{AUTOJINJA_REMOVE_MARKERS}'")
    return 1 if value == "1" else 0

def osenviron_silent(env: Optional[os._Environ] = None) -> int:
    env = env or os.environ
    if AUTOJINJA_SILENT not in env:
        return 0
    value = env[AUTOJINJA_SILENT]
    is_valid = True
    if len(value) != 1:
        is_valid = False
    elif value != "0" and value != "1":
        is_valid = False
    if not is_valid:
        raise Exception(f"Expected 0 or 1 for environment variable '{AUTOJINJA_SILENT}'")
    return 1 if value == "1" else 0

def osenviron_summary(env: Optional[os._Environ] = None) -> str:
    env = env or os.environ
    if AUTOJINJA_SUMMARY not in env:
        return "1"
    value = env[AUTOJINJA_SUMMARY]
    is_valid = True
    if len(value) != 1 and len(value) != 3:
        is_valid = False
    else:
        for c in value:
            if c != "0" and c != "1":
                is_valid = False
                break
    if not is_valid:
        raise Exception(f"Expected 0, 1 or flags for environment variable '{AUTOJINJA_SUMMARY}'")
    return value

def osenviron_this_dirpath(env: Optional[os._Environ] = None) -> Optional[str]:
    env = env or os.environ
    return env.get(AUTOJINJA_THIS_DIRPATH)
