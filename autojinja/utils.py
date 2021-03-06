from . import defaults
from . import parser
from . import path

import os
import sys

def file_tagged(filepath, tag = defaults.AUTOJINJA_DEFAULT_TAG, encoding = None):
    """ Returns True if the file at the given filepath is tagged with the given tag.
        The file's first line must contain this tag (ex: '### autojinja ###').
        Raises an error if the file can't be read.
    """
    with open(filepath, 'r', encoding = encoding or "utf-8") as file:
        return tag in file.readline()

def generate_file(filepath, new_content, old_content = None, encoding = None, newline = None):
    """ Generates the given content to the given filepath.
        Only writes the content to the file if the content is new.
        The previous content can be directly provided to avoid reading the file.
        Raises an error if the file can't be read/write.
    """
    assert filepath != None, "output filepath parameter can't be None"
    ### Compare old content
    filepath = path(filepath).abspath
    created = not filepath.isfile
    if not created and not old_content:
        with open(filepath, 'r', encoding = encoding or "utf-8") as file:
            old_content = file.read()
    ### Save new generation
    changed = new_content != old_content
    if created or changed:
        with open(filepath, 'w', encoding = encoding or "utf-8", newline = newline) as file:
            file.write(new_content)
    print(f"[autojinja]  {'  new  ' if created else 'changed' if changed else '-------'}  {filepath}  (from {path.no_antislash(sys.argv[0])})")

def parse_file(filepath, settings = None, encoding = None):
    """ Parses the given file and return the parsing result.
        Returns an empty dictionary if the file doesn't exist.
        Raises an error if the file can't be read.
    """
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r', encoding = encoding or (settings.encoding if settings else None) or "utf-8") as file:
        return parse_string(file.read(), settings)

def parse_string(string, settings = None):
    """ Parses the given string and returns the parsing result.
    """
    try:
        object = parser.Parser(string, settings or parser.ParserSettings())
        object.parse()
        return object
    except BaseException as e:
        raise e.with_traceback(None)

def edit_markers_from_file(filepath, settings = None, encoding = None):
    """ Returns a dictionary with all edit markers in the given file.
        Returns an empty dictionary if the file doesn't exist.
        Raises an error if the file can't be read.
    """
    object = parse_file(filepath, settings, encoding)
    return object.edit_markers

def edit_markers_from_string(string, settings = None):
    """ Returns a dictionary with all edit markers in the given string.
    """
    object = parse_string(string, settings)
    return object.edit_markers

def edits_from_file(filepath, settings = None, encoding = None):
    """ Returns a dictionary with all manual edits in the given file.
        Returns an empty dictionary if the file doesn't exist.
        Raises an error if the file can't be read.
    """
    object = parse_file(filepath, settings, encoding)
    return object.edits

def edits_from_string(string, settings = None):
    """ Returns a dictionary with all manual edits in the given string.
    """
    object = parse_string(string, settings)
    return object.edits

def parse_envvars(env, values):
    """ Loads the given environment variables to the given environment dictionary.
        Variable format must be 'name=value', otherwise considered as an environment file.
    """
    for arg in values:
        if '=' in arg: # Environment variable
            splits = arg.split('=', 1)
            env[splits[0].strip()] = evaluate_env(env, splits[1].strip())
        else: # Environment file
            parse_envfile(env, arg)

def parse_envfile(env, envfile):
    """ Loads the given environment file and appends all environment variables to the given environment dictionary.
        The special environment variable ${THIS_DIRPATH} can be used to refer to the environment file location.
    """
    with open(envfile, encoding = "utf-8") as file:
        lines = [line.split('#', 1)[0].strip() for line in file.readlines()] # Remove comments
        lines = [line for line in lines if line] # Remove empty lines
        for line in lines:
            splits = line.split('=', 1)
            name = splits[0].strip()
            if len(splits) == 1:
                env[name] = "" # No value defined
            else:
                exists = defaults.AUTOJINJA_THIS_DIRPATH in env
                if not exists:
                    env[defaults.AUTOJINJA_THIS_DIRPATH] = path(envfile).abspath.dirpath[:-1]
                value = evaluate_env(env, splits[1].strip())
                env[name] = value.strip()
                if not exists:
                    del env[defaults.AUTOJINJA_THIS_DIRPATH]

def evaluate_env(env, value):
    """ Evaluates the given string with the appropriate environment variables' value.
        /dir1/${VAR1}/file.txt -> /dir1/dir2/file.txt
    """
    old_env = os.environ
    try:
        os.environ = env
        return os.path.expandvars(value)
    finally:
        os.environ = old_env

def os_pathsep(value):
    """ Returns the appropriate path separator based the given value and the host OS.
    """
    if os.name != "nt": # Unix
        return ':' if ':' in value else ';'
    else: # Windows
        return ';'
