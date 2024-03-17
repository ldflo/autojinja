"""
Utility functions to ease path manipulations.
The API manipulates paths for either files or directories:

    D:/dir1/dir2       -> dir2      is a file      (no ending /)
    D:/dir1/file.txt/  -> file.txt/ is a directory (   ending /)

Converts antislashes to normal slashes.
"""

import glob
import os
from typing import List, Tuple, Union

class _join_wrapper:
    def __call__(self, arg1: str, *args: str) -> str:
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        return no_antislash(os.path.join(arg1, *args))
    def __getitem__(self: str, args: Union[str, Tuple[str, ...]]) -> str:
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt/
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        if isinstance(args, tuple):
            return slash(join.__call__(*args))
        return slash(join.__call__(args))

join = _join_wrapper()

def add(arg1: str, *args: str) -> str:
    """ /dir1/dir2   file.txt -> /dir1/dir2file.txt
        /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
    """
    return no_antislash("".join([arg1, *args]))

def files(path: str = "", pattern: str = "*") -> List[str]:
    """ /dir1/dir2/  *.txt -> [/dir1/dir2/file.txt]
    """
    return [no_antislash(x) for x in glob.glob(dirpath(path) + pattern, recursive=True) if isfile(x)]

def dirs(path: str = "", pattern: str = "*") -> List[str]:
    """ /dir1/*/ -> [/dir1/dir2/]
    """
    return [slash(x) for x in glob.glob(dirpath(path) + pattern, recursive=True) if isdir(x)]

def filepath(path: str) -> str:
    """ /dir1/dir2/file.txt -> /dir1/dir2/file.txt
        /dir1/dir2/         -> /dir1/dir2/
    """
    return no_antislash(path)

def filename(path: str) -> str:
    """ /dir1/dir2/file.txt -> file.txt
        /dir1/dir2/         ->
    """
    if not path:
        return ""
    if path[-1] in ['/', '\\']:
        return ""
    return no_antislash(os.path.basename(path))

def set_filename(path: str, filename: str) -> str:
    """ /dir1/dir2/file.txt -> /dir1/dir2/newfile.xml
        /dir1/dir2/         -> /dir1/dir2/newfile.xml
    """
    return dirpath(path) + no_antislash(filename)

def dirpath(path: str) -> str:
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

def dirname(path: str) -> str:
    """ /dir1/dir2/file.txt -> dir2
        /dir1/dir2/         -> dir2
    """
    result = dirpath(path)
    if not result:
        return ""
    return result.rsplit('/', 2)[-2]

def parent_dirpath(path: str) -> str:
    """ /dir1/dir2/file.txt -> /dir1/
        /dir1/dir2/         -> /dir1/
    """
    return dirpath(os.path.dirname(no_antislash(path)))

def parent_dirname(path: str) -> str:
    """ /dir1/dir2/file.txt -> dir1
        /dir1/dir2/         -> dir1
    """
    return dirname(os.path.dirname(no_antislash(path)))

def ext(path: str) -> str:
    """ /dir1/dir2/file.ext.txt -> .txt
        /dir1/dir2/             ->
    """
    return splitext(path)[1]

def set_ext(path: str, extension: str) -> str:
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.ext.new
        /dir1/dir2/             -> /dir1/dir2/.new
    """
    return no_ext(path) + extension

def no_ext(path: str) -> str:
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.ext
        /dir1/dir2/             -> /dir1/dir2/
    """
    return no_antislash(splitext(path)[0])

def fullext(path: str) -> str:
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

def set_fullext(path: str, extension: str) -> str:
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file.new
        /dir1/dir2/             -> /dir1/dir2/.new
    """
    return no_fullext(path) + extension

def no_fullext(path: str) -> str:
    """ /dir1/dir2/file.ext.txt -> /dir1/dir2/file
        /dir1/dir2/             -> /dir1/dir2/
    """
    extension = fullext(path)
    if not extension:
        return no_antislash(path)
    return no_antislash(path[:-len(extension)])

def slash(path: str) -> str:
    """ /dir1/dir2/file.txt -> /dir1/dir2/file.txt/
        /dir1/dir2/         -> /dir1/dir2/
    """
    if not path:
        return ""
    path = no_antislash(path)
    if path[-1] == '/':
        return path
    return path + '/'

def no_slash(path: str) -> str:
    if not path:
        return ""
    if path[-1] in ['/', '\\']:
        return no_antislash(path[:-1])
    return no_antislash(path)

def no_antislash(path: str) -> str:
    """ \dir1\dir2\file.txt -> /dir1/dir2/file.txt/
        \dir1\dir2\         -> /dir1/dir2/
    """
    return path.replace('\\', '/')

###
### os.path wrapper functions
###

def abspath(path: str) -> str:
    if not path:
        path = "."
    result = os.path.abspath(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def commonpath(paths: List[str]) -> str:
    result = os.path.commonpath(paths)
    return slash(result)

def commonprefix(paths: List[str]) -> str:
    result = os.path.commonprefix(paths)
    return no_antislash(result)

def exists(path: str) -> bool:
    return os.path.exists(path)

def lexists(path: str) -> bool:
    return os.path.lexists(path)

def expanduser(path: str) -> str:
    if not path:
        return ""
    result = os.path.expanduser(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def expandvars(path: str) -> str:
    if not path:
        return ""
    result = os.path.expandvars(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def getatime(path: str) -> float:
    return os.path.getatime(path)

def getmtime(path: str) -> float:
    return os.path.getmtime(path)

def getctime(path: str) -> float:
    return os.path.getctime(path)

def isabs(path: str) -> bool:
    return os.path.isabs(path)

def isfile(path: str) -> bool:
    return os.path.isfile(path)

def isdir(path: str) -> bool:
    return os.path.isdir(path)

def islink(path: str) -> bool:
    return os.path.islink(path)

def ismount(path: str) -> bool:
    return os.path.ismount(path)

def normcase(path: str) -> str:
    if not path:
        return ""
    result = os.path.normcase(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def normpath(path: str) -> str:
    if not path:
        return ""
    result = os.path.normpath(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def realpath(path: str) -> str:
    if not path:
        path = "."
    result = os.path.realpath(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def relpath(path: str, start: str = ".") -> str:
    if not path:
        return start
    try:
        result = os.path.relpath(path, start)
    except Exception:
        return no_antislash(path)
    if path[-1] in ['/', '\\']:
        return slash(result)
    return no_antislash(result)

def samefile(path1: str, path2: str) -> bool:
    return os.path.samefile(path1, path2)

def sameopenfile(fp1: int, fp2: int) -> bool:
    return os.path.sameopenfile(fp1, fp2)

def samestat(stat1: os.stat_result, stat2: os.stat_result) -> bool:
    return os.path.samestat(stat1, stat2)

def splitpath(path: str) -> Tuple[str, str]:
    result = os.path.split(path)
    return (no_antislash(result[0]), no_antislash(result[1]))

def splitdrive(path: str) -> Tuple[str, str]:
    result = os.path.splitdrive(path)
    return (no_antislash(result[0]), no_antislash(result[1]))

def splitext(path: str) -> Tuple[str, str]:
    result = os.path.splitext(path)
    return (no_antislash(result[0]), no_antislash(result[1]))

class Path(str):
    """ Allows a functional API of the above functions:

            Path("/dir").join("file.txt").exists
                instead of
            os.path.exists(os.path.join("/dir", "file.txt"))
    """
    def __new__(cls, *args: str, **kwargs):
        if len(args) == 0:
            return str.__new__(cls, **kwargs)
        return str.__new__(cls, no_antislash(args[0]), *args[1:], **kwargs)

    class _join_wrapper:
        def __init__(self, path: str):
            self.path: str = path
        def __call__(self, *args: str) -> "Path":
            """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt
                /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
            """
            path = join.__call__(self.path, *args)
            return Path(path)
        def __getitem__(self, args: Union[str, Tuple[str, ...]]) -> "DirPath":
            """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt/
                /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
            """
            if isinstance(args, tuple):
                path = slash(join.__call__(self.path, *args))
            else:
                path = slash(join.__call__(self.path, args))
            return DirPath(path)

    @property
    def join(self) -> _join_wrapper:
        return Path._join_wrapper(self)

    def add(self, *args: str) -> "Path":
        result = add(self, *args)
        return Path(result)
    def __add__(self, other: str) -> "Path":
        return self.add(other)
    def __radd__(self, other: str) -> "Path":
        return Path(other.__add__(self))
    def __truediv__(self, other: str) -> "Path":
        return self.join.__call__(other)

    def files(self, pattern: str = "*") -> List["Path"]:
        result = files(self, pattern)
        return [Path(path) for path in result]

    def dirs(self, pattern: str = "*") -> List["DirPath"]:
        result = dirs(self, pattern)
        return [DirPath(path) for path in result]

    @property
    def filepath(self) -> "Path":
        result = filepath(self)
        return Path(result)

    @property
    def filename(self) -> "Path":
        result = filename(self)
        return Path(result)

    def set_filename(self, filename: str) -> "Path":
        result = set_filename(self, filename)
        return Path(result)

    @property
    def dirpath(self) -> "DirPath":
        result = dirpath(self)
        return DirPath(result)

    @property
    def dirname(self) -> "Path":
        result = dirname(self)
        return Path(result)

    @property
    def parent_dirpath(self) -> "DirPath":
        result = parent_dirpath(self)
        return DirPath(result)

    @property
    def parent_dirname(self) -> "Path":
        result = parent_dirname(self)
        return Path(result)

    @property
    def ext(self) -> "Path":
        result = ext(self)
        return Path(result)

    def set_ext(self, extension: str) -> "Path":
        result = set_ext(self, extension)
        return Path(result)

    @property
    def no_ext(self) -> "Path":
        result = no_ext(self)
        return Path(result)

    @property
    def fullext(self) -> "Path":
        result = fullext(self)
        return Path(result)

    def set_fullext(self, extension: str) -> "Path":
        result = set_fullext(self, extension)
        return Path(result)

    @property
    def no_fullext(self) -> "Path":
        result = no_fullext(self)
        return Path(result)

    @property
    def slash(self) -> "DirPath":
        result = slash(self)
        return DirPath(result)

    @property
    def no_slash(self) -> "Path":
        result = no_slash(self)
        return Path(result)

    ###
    ### os.path wrapper functions
    ###

    @property
    def abspath(self) -> "Path":
        result = abspath(self)
        return Path(result)

    def commonpath(self, paths: List[str]) -> "DirPath":
        result = commonpath([self] + paths)
        return DirPath(result)

    def commonprefix(self, paths: List[str]) -> "Path":
        result = commonprefix([self] + paths)
        return Path(result)

    @property
    def exists(self) -> bool:
        return exists(self)

    @property
    def lexists(self) -> bool:
        return lexists(self)

    @property
    def expanduser(self) -> "Path":
        result = expanduser(self)
        return Path(result)

    @property
    def expandvars(self) -> "Path":
        result = expandvars(self)
        return Path(result)

    @property
    def getatime(self) -> float:
        return getatime(self)

    @property
    def getmtime(self) -> float:
        return getmtime(self)

    @property
    def getctime(self) -> float:
        return getctime(self)

    @property
    def isabs(self) -> bool:
        return isabs(self)

    @property
    def isfile(self) -> bool:
        return isfile(self)

    @property
    def isdir(self) -> bool:
        return isdir(self)

    @property
    def islink(self) -> bool:
        return islink(self)

    @property
    def ismount(self) -> bool:
        return ismount(self)

    @property
    def normcase(self) -> "Path":
        result = normcase(self)
        return Path(result)

    @property
    def normpath(self) -> "Path":
        result = normpath(self)
        return Path(result)

    @property
    def realpath(self) -> "Path":
        result = realpath(self)
        return Path(result)

    def relpath(self, start: str = ".") -> "Path":
        result = relpath(self, start)
        return Path(result)

    def samefile(self, path: str) -> bool:
        return samefile(self, path)

    def samestat(self, stat: os.stat_result) -> bool:
        return samestat(os.stat(self), stat)

    @property
    def splitpath(self) -> Tuple["DirPath", "Path"]:
        result = splitpath(self)
        return (DirPath(result[0]), Path(result[1]))

    @property
    def splitdrive(self) -> Tuple["DirPath", "Path"]:
        result = splitdrive(self)
        return (DirPath(result[0]), Path(result[1]))

    @property
    def splitext(self) -> Tuple["Path", "Path"]:
        result = splitext(self)
        return (Path(result[0]), Path(result[1]))

class DirPath(Path):
    """ DirPath is a Path that ends with a trailing slash.

            print(Path("/dir1"))    # Prints "/dir1"
            print(DirPath("/dir1")) # Prints "/dir1/"
    """
    def __new__(cls, *args: str, **kwargs):
        return Path.__new__(cls, slash(args[0]), *args[1:], **kwargs)

    @property
    def abspath(self) -> "DirPath":
        result = abspath(self)
        return DirPath(result)

    def commonpath(self, paths: List[str]) -> "DirPath":
        result = commonpath([self] + paths)
        return DirPath(result)

    @property
    def expanduser(self) -> "DirPath":
        result = expanduser(self)
        return DirPath(result)

    @property
    def expandvars(self) -> "DirPath":
        result = expandvars(self)
        return DirPath(result)

    @property
    def normcase(self) -> "DirPath":
        result = normcase(self)
        return DirPath(result)

    @property
    def normpath(self) -> "DirPath":
        result = normpath(self)
        return DirPath(result)

    @property
    def realpath(self) -> "DirPath":
        result = realpath(self)
        return DirPath(result)

    def relpath(self, start: str = ".") -> "DirPath":
        result = relpath(self, start)
        return DirPath(result)

    @property
    def splitpath(self) -> Tuple["DirPath", "DirPath"]:
        result = splitpath(self)
        return (DirPath(result[0]), DirPath(result[1]))

    @property
    def splitdrive(self) -> Tuple["DirPath", "DirPath"]:
        result = splitdrive(self)
        return (DirPath(result[0]), DirPath(result[1]))

    @property
    def splitext(self) -> Tuple["DirPath", "Path"]:
        result = splitext(self)
        return (DirPath(result[0]), Path(result[1]))
