"""
Utility functions to ease path manipulations.
The API manipulates paths for either files or directories:

    D:/dir1/dir2       -> dir2      is a file      (no ending /)
    D:/dir1/file.txt/  -> file.txt/ is a directory (   ending /)

Converts antislashes to normal slashes.
"""

import glob
import os.path
import sys

this_module = sys.modules[__name__]

class _join_class:
    def __call__(self, arg1, *args): # type: (str, *str) -> str
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        return no_antislash(os.path.join(arg1, *args))
    def __getitem__(self, args): # type: (*str) -> str
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt/
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        if type(args) == tuple:
            return slash(join.__call__(*args))
        return slash(join.__call__(args))

join = _join_class()

def add(arg1, *args): # type: (str, *str) -> str
    """ /dir1/dir2   file.txt -> /dir1/dir2file.txt
        /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
    """
    return no_antislash("".join([arg1, *args]))

def files(path, pattern = "*"): # type: (str, str) -> list(str)
    """ /dir1/dir2/  *.txt -> [/dir1/dir2/file.txt]
    """
    return [no_antislash(x) for x in glob.glob(dirpath(path) + pattern, recursive=True) if os.path.isfile(x)]

def dirs(path, pattern = "*"): # type: (str, str) -> list(str)
    """ /dir1/*/ -> [/dir1/dir2/]
    """
    return [slash(x) for x in glob.glob(dirpath(path) + pattern, recursive=True) if os.path.isdir(x)]

def filepath(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> /dir1/dir2/file.txt
        /dir1/dir2/         -> /dir1/dir2/
    """
    return no_antislash(path)

def filename(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> file.txt
        /dir1/dir2/         ->
    """
    if not path:
        return ""
    if path[-1] in ['/', '\\']:
        return ""
    return no_antislash(os.path.basename(path))

def set_filename(path, filename): # type: (str, str) -> str
    """ /dir1/dir2/file.txt -> /dir1/dir2/newfile.xml
        /dir1/dir2/         -> /dir1/dir2/newfile.xml
    """
    return dirpath(path) + no_antislash(filename)

def dirpath(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> /dir1/dir2/
        /dir1/dir2/         -> /dir1/dir2/
    """
    if not path:
        return ""
    path = no_antislash(path)
    if path[-1] == '/':
        return path
    result = os.path.dirname(path)
    if not result:
        return ""
    if result[-1] == '/':
        return result
    return result + '/'

def dirname(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> dir2
        /dir1/dir2/         -> dir2
    """
    result = dirpath(path)
    if not result:
        return ""
    return result.rsplit('/', 2)[-2]

def parent_dirpath(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> /dir1/
        /dir1/dir2/         -> /dir1/
    """
    return dirpath(os.path.dirname(no_antislash(path)))

def parent_dirname(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> dir1
        /dir1/dir2/         -> dir1
    """
    return dirname(os.path.dirname(no_antislash(path)))

def ext(path): # type: (str) -> str
    """ /dir1/dir2/file.ext.txt -> .txt
        /dir1/dir2/             ->
    """
    return os.path.splitext(path)[1]

def set_ext(path, extension): # type: (str, str) -> str
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.ext.new
        /dir1/dir2/             -> /dir1/dir2/.new
    """
    return no_ext(path) + extension

def no_ext(path): # type: (str) -> str
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.ext
        /dir1/dir2/             -> /dir1/dir2/
    """
    return no_antislash(os.path.splitext(path)[0])

def fullext(path): # type: (str) -> str
    """ /dir1/dir2/file.ext.txt -> .ext.txt
        /dir1/dir2/             ->
    """
    if not path:
        return ""
    if path[-1] in ['/', '\\']:
        return ""
    splits = os.path.basename(path).split('.', 1)
    if len(splits) == 1:
        return ""
    return '.' + splits[1]

def set_fullext(path, extension): # type: (str, str) -> str
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.new
        /dir1/dir2/             -> /dir1/dir2/.new
    """
    return no_fullext(path) + extension

def no_fullext(path): # type: (str) -> str
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file
        /dir1/dir2/             -> /dir1/dir2/
    """
    extension = fullext(path)
    if not extension:
        return no_antislash(path)
    return no_antislash(path[:-len(extension)])

def slash(path): # type: (str) -> str
    """ /dir1/dir2/file.txt -> /dir1/dir2/file.txt/
        /dir1/dir2/         -> /dir1/dir2/
    """
    if not path:
        return "/"
    path = no_antislash(path)
    if path[-1] == '/':
        return path
    return path + '/'

def no_slash(path): # type: (str) -> str
    if not path:
        return ""
    if path[-1] in ['/', '\\']:
        return no_antislash(path[:-1])
    return no_antislash(path)

def no_antislash(path): # type: (str) -> str
    """ \dir1\dir2\file.txt -> /dir1/dir2/file.txt/
        \dir1\dir2\         -> /dir1/dir2/
    """
    return path.replace('\\', '/')

def realpath(path): # type: (str) -> str
    return os.path.realpath(path)

def relpath(path, start = "."): # type: (str, str) -> str
    return os.path.relpath(path, start)

def samefile(path1, path2): # type: (str, str) -> str
    return os.path.samefile(path1, path2)

class Path(str):
    """ Allows a functional API of the above functions:

            path("/dir").join("file.txt").exists
                instead of
            os.path.exists(os.path.join("/dir", "file.txt"))
    """
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, no_antislash(args[0]), *args[1:], **kwargs)
    def __getattribute__(self, attr):
        try:
            attribute = object.__getattribute__(self, attr)
            return PathWrapper(attribute) if callable(attribute) else attribute
        except:
            result = os.path.__getattribute__(attr)(self)
            return Path(result) if type(result) == str else result

    class _join_class:
        def __init__(self, path):
            self.path = path
        def __call__(self, *args):
            path = join.__call__(self.path, *args)
            return Path(path)
        def __getitem__(self, args):
            if type(args) == tuple:
                path = slash(join.__call__(self.path, *args))
            else:
                path = slash(join.__call__(self.path, args))
            return Path(path)

    @property
    def join(self):
        return Path._join_class(self)
    def add(self, *args):
        path = add(self, *args)
        return Path(path)
    def __add__(self, other):
        return self.add(other)
    def __radd__(self, other):
        return Path(other.__add__(self))
    def files(self, pattern = "*"):
        list = files(self, pattern)
        return [Path(path) for path in list]
    def dirs(self, pattern = "*"):
        list = dirs(self, pattern)
        return [Path(path) for path in list]
    @property
    def filepath(self):
        path = filepath(self)
        return Path(path)
    @property
    def filename(self):
        path = filename(self)
        return Path(path)
    def set_filename(self, filename):
        path = set_filename(self, filename)
        return Path(path)
    @property
    def dirpath(self):
        path = dirpath(self)
        return Path(path)
    @property
    def dirname(self):
        path = dirname(self)
        return Path(path)
    @property
    def parent_dirpath(self):
        path = parent_dirpath(self)
        return Path(path)
    @property
    def parent_dirname(self):
        path = parent_dirname(self)
        return Path(path)
    @property
    def ext(self):
        path = ext(self)
        return Path(path)
    def set_ext(self, extension):
        path = set_ext(self, extension)
        return Path(path)
    @property
    def no_ext(self):
        path = no_ext(self)
        return Path(path)
    @property
    def fullext(self):
        path = fullext(self)
        return Path(path)
    def set_fullext(self, extension):
        path = set_fullext(self, extension)
        return Path(path)
    @property
    def no_fullext(self):
        path = no_fullext(self)
        return Path(path)
    @property
    def slash(self):
        path = slash(self)
        return Path(path)
    @property
    def no_slash(self):
        path = no_slash(self)
        return Path(path)
    @property
    def realpath(self):
        path = realpath(self)
        return Path(path)
    def relpath(self, start = "."):
        path = relpath(self, start)
        return Path(path)
    def samefile(self, path2):
        path = samefile(self, path2)
        return Path(path)

class PathWrapper:
    """ Helps forwarding to callables of os.path
    """
    def __init__(self, attribute):
        self.attribute = attribute
    def __call__(self, *args, **kwargs):
        result = self.attribute.__call__(*args, **kwargs)
        return Path(result) if type(result) == str else result
    def __getitem__(self, args):
        result = self.attribute.__getitem__(args)
        return Path(result) if type(result) == str else result
    def __getattr__(self, attr):
        return getattr(self.attribute, attr)

class module_call:
    """ Overrides path(), path[] and path.attr
    """
    def __call__(self, path):
        """ path("/my/path") -> "/my/path"
        """
        return Path(path)
    def __getitem__(self, path):
        """ path["/my/path"] -> "/my/path/"
        """
        return Path(slash(path))
    def __getattribute__(self, attr):
        """ Forwards os.path if not defined in this module
        """
        try:
            return this_module.__getattribute__(attr)
        except:
            return os.path.__getattribute__(attr)

sys.modules[__name__] = module_call()
