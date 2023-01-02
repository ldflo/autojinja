"""
Visits directories and executes python scripts to perform content generation

Usage
-----
autojinja [OPTIONS] (PYTHON_SCRIPT | DIRECTORY)...

Examples
--------
autojinja script1.py script2.py
autojinja -a .

Arguments
---------
PYTHON_SCRIPT:
    Python script to execute
    The filepath must end with '.py' extension

DIRECTORY:
    Directory to visit
    Only works if '--search-filename' or '--search-tag' is enabled

OPTIONS:
    -f, --search-filename         Searches for python scripts named '__jinja__.py' in visited directories
    -t, --search-tag              Searches for python scripts tagged 'autojinja' in visited directories
    -r, --recursive               Recursively visits subdirectories of visited directories
    -a, --all                     All above options simultaneously (equivalent to '-ftr')
    --filename=FILENAME           Filename searched by '--search-filename'. Default value is '__jinja__.py'
    --tag=TAG                     Tag searched by '--search-tag'. Default value is 'autojinja'
                                  Python scripts' first line must contain this tag (ex: '### autojinja ###')
    -e, --env=NAME=VALUE/FILE     Additional environment variable or .env file
    -i, --includes=DIRECTORIES    Additional import directories for executed python scripts
                                  Directory list separated by ':' (Unix only) or ';' (Windows and Unix)
                                  Appended to environment variable 'PYTHONPATH'
    --remove-markers=ENABLE       Removes markers from generated outputs
                                  Default value is '0' or environment variable 'AUTOJINJA_REMOVE_MARKERS'
                                  Overrides environment variable 'AUTOJINJA_REMOVE_MARKERS'
    --silent                      Prevents executed python scripts from writing to stdout/stderr
                                  Enabled if environment variable 'AUTOJINJA_SILENT' == 1
                                  Overrides environment variable 'AUTOJINJA_SILENT'
    --debug                       enhances stacktraces for exceptions raised from Jinja context variables
                                  Enabled if environment variable 'AUTOJINJA_DEBUG' == 1
                                  Overrides environment variable 'AUTOJINJA_DEBUG'
    ---summary=VALUE/FLAGS        Enables notifications for generated files to stdout
                                  Overrides environment variable 'AUTOJINJA_SUMMARY'
                                  Default value is '1':
                                      0: nothing
                                      1: [autojinja]  -------  <abs_path>  (from <abs_path>)
                                  Also accepts 3 flags instead:
                                      100
                                      ^------ show (1) / hide (0) executing script path
                                              0: [autojinja]  -------  <path>
                                              1: [autojinja]  -------  <path>  (from <path>)
                                      010
                                       ^------ use absolute (1) / relative (0) paths
                                              0: [autojinja]  -------  <rel_path>  (from <rel_path>)
                                              1: [autojinja]  -------  <abs_path>  (from <abs_path>)
                                      001
                                        ^------ notification when changed only (1)
                                              0: [autojinja]  -------  <path>  (from <path>)
                                              1: [autojinja]  changed  <path>  (from <path>)
"""

from .defaults import *
from . import path
from . import utils

import argparse
import os.path
import subprocess
import sys

this_module = sys.modules[__name__]

def main(*arguments):
    ### Parse arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Visits directories and executes python scripts to perform content generation")
    parser.add_argument("arguments",
                        nargs="+",
                        help="PYTHON_SCRIPT:\n"
                             "    Python script to execute\n"
                             "    The filepath must end with '.py' extension\n\n"
                             "DIRECTORY:\n"
                             "    Directory to visit\n"
                             "    Only works if '--search-filename' or '--search-tag' is enabled")
    parser.add_argument("-f",
                        "--search-filename",
                        action="store_true",
                        help=f"searches for python scripts named '{AUTOJINJA_DEFAULT_FILENAME}' in visited directories")
    parser.add_argument("-t",
                        "--search-tag",
                        action="store_true",
                        help=f"searches for python scripts tagged '{AUTOJINJA_DEFAULT_TAG}' in visited directories")
    parser.add_argument("-r",
                        "--recursive",
                        action="store_true",
                        help="recursively visits subdirectories of visited directories")
    parser.add_argument("-a",
                        "--all",
                        action="store_true",
                        help="all above options simultaneously (equivalent to '-ftr')")
    parser.add_argument("--filename",
                        default=AUTOJINJA_DEFAULT_FILENAME,
                        help=f"filename searched by '--search-filename'. Default filename is '{AUTOJINJA_DEFAULT_FILENAME}'")
    parser.add_argument("--tag",
                        default=AUTOJINJA_DEFAULT_TAG,
                        help=f"tag searched by '--search-tag'. Default tag is '{AUTOJINJA_DEFAULT_TAG}'\n"
                             f"Python scripts' first line must contain this tag (ex: '### {AUTOJINJA_DEFAULT_TAG} ###')")
    parser.add_argument("-e",
                        "--env",
                        action="append",
                        help="additional environment variable or .env file")
    parser.add_argument("-i",
                        "--includes",
                        action="append",
                        help="additional import directories for executed python scripts\n"
                             "Directory list separated by ':' (Unix only) or ';' (Windows and Unix)\n"
                             "Appended to environment variable 'PYTHONPATH'")
    parser.add_argument("--remove-markers",
                        help=f"removes markers from generated outputs\n"
                             f"Default value is '0' or environment variable '{AUTOJINJA_REMOVE_MARKERS}'\n"
                             f"Overrides environment variable '{AUTOJINJA_REMOVE_MARKERS}'")
    parser.add_argument("--silent",
                        action="store_true",
                        help=f"prevents executed python scripts from writing to stdout/stderr\n"
                             f"Enabled if environment variable '{AUTOJINJA_SILENT}' == 1\n"
                             f"Overrides environment variable '{AUTOJINJA_SILENT}'")
    parser.add_argument("--debug",
                        action="store_true",
                        help=f"enhances stacktraces for exceptions raised from Jinja context variables\n"
                             f"Enabled if environment variable '{AUTOJINJA_DEBUG}' == 1\n"
                             f"Overrides environment variable '{AUTOJINJA_DEBUG}'")
    parser.add_argument("--summary",
                        help=f"enables notifications for generated files to stdout\n"
                             f"Overrides environment variable '{AUTOJINJA_SUMMARY}'\n"
                             f"Default value is '1':\n"
                             f"    0: nothing\n"
                             f"    1: [autojinja]  -------  <abs_path>  (from <abs_path>)\n"
                             f"Also accepts 3 flags instead:\n"
                             f"    100\n"
                             f"    ^------ show (1) / hide (0) executing script path\n"
                             f"            0: [autojinja]  -------  <path>\n"
                             f"            1: [autojinja]  -------  <path>  (from <path>)\n"
                             f"    010\n"
                             f"     ^------ use absolute (1) / relative (0) paths\n"
                             f"            0: [autojinja]  -------  <rel_path>  (from <rel_path>)\n"
                             f"            1: [autojinja]  -------  <abs_path>  (from <abs_path>)\n"
                             f"    001\n"
                             f"      ^------ notification when changed only (1)\n"
                             f"            0: [autojinja]  -------  <path>  (from <path>)\n"
                             f"            1: [autojinja]  changed  <path>  (from <path>)")

    args = parser.parse_args(arguments)

    ### Prepare environment
    env = os.environ.copy()

    # Additional environment variables
    if args.env:
        utils.parse_envvars(env, args.env)

    # Additional import directories
    if args.includes:
        includes = [path[include].abspath for includes in args.includes for include in includes.split(utils.os_pathsep(includes))]
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{env['PYTHONPATH']}{os.pathsep}{os.pathsep.join(includes)}"
        else:
            env["PYTHONPATH"] = os.pathsep.join(includes)

    ### Verify options
    if args.all:
        args.search_filename = True
        args.search_tag = True
        args.recursive = True

    # remove_markers
    if args.remove_markers != None:
        if args.remove_markers == True:
            args.remove_markers = 1
        elif args.remove_markers == False:
            args.remove_markers = 0
        env[AUTOJINJA_REMOVE_MARKERS] = str(args.remove_markers)
    args.remove_markers = osenviron_remove_markers(env)
    env[AUTOJINJA_REMOVE_MARKERS] = str(args.remove_markers)

    # silent
    if args.silent == None or args.silent == False:
        args.silent = osenviron_silent(env)
    else:
        args.silent = 1
    env[AUTOJINJA_SILENT] = str(args.silent)

    # debug
    if args.debug == None or args.debug == False:
        args.debug = osenviron_debug(env)
    else:
        args.debug = 1
    env[AUTOJINJA_DEBUG] = str(args.debug)

    # summary
    if args.summary != None:
        env[AUTOJINJA_SUMMARY] = str(args.summary)
    args.summary = osenviron_summary(env)
    env[AUTOJINJA_SUMMARY] = str(args.summary)

    ### Parse arguments
    def is_file_tagged(script):
        try:
            return utils.is_file_tagged(script, args.tag)
        except:
            sys.stderr.write(f"[autojinja]  Couldn't read file at path  {script.abspath}\n")

    files = []
    for x in [path(x) for x in args.arguments]:
        if x.isfile:
            if x.ext != ".py":
                raise Exception(f"File at path \"{x.abspath}\" is not a python script (.py extension)")
            files.append(x)
        elif not x.isdir:
            raise Exception(f"File or directory at path \"{x.abspath}\" doesn't exist")
        else:
            if not args.search_filename and not args.search_tag:
                raise Exception("Directory arguments require '--search-filename' or '--search-tag'")
            if args.recursive:
                for wroot, _, wfiles in os.walk(x):
                    for script in [path(wroot).join(x) for x in wfiles]:
                        ## JINJA
                        if args.search_filename:
                            if script.filename == args.filename:
                                files.append(script)
                        ## PYTHON
                        if args.search_tag:
                            if script.ext == ".py":
                                if is_file_tagged(script):
                                    files.append(script)
            else:
                ## JINJA
                if args.search_filename:
                    script = x.join(args.filename)
                    if script.isfile:
                        files.append(script)
                ## PYTHON
                if args.search_tag:
                    for script in x.files("*.py"):
                        if is_file_tagged(script):
                            files.append(script)

    # Make absolute and remove duplicates
    files = [x.abspath for x in files]
    files = list(dict.fromkeys(files))

    ### Execute python scripts
    for script in files:
        process = subprocess.Popen([sys.executable, "-u", script],
                                    cwd=script.dirpath,
                                    env=env,
                                    stdout = subprocess.PIPE if args.silent else None,
                                    stderr = subprocess.STDOUT if args.silent else None,
                                    universal_newlines = True if args.silent else None)
        out, _ = process.communicate()
        errcode = process.returncode
        if errcode != 0:
            raise Exception(f"{out if args.silent else ''}Error {errcode} while executing script at path \"{script}\"")

class module_call:
    """ Overrides main() and main.attr
    """
    def __call__(self, *args, **kwargs):
        """ Calls the main function
        """
        return main(*args, **kwargs)
    def __getattribute__(self, attr):
        """ Forwards this module
        """
        return this_module.__getattribute__(attr)

sys.modules[__name__] = module_call()
