__version__ = "1.9.0"

from . import defaults
from . import exceptions
from . import main
from .parser import ParserSettings
from . import path
from . import templates
from .templates import AutoLoader
from .templates import CogTemplate
from .templates import JinjaTemplate
from .templates import RawTemplate
from . import utils

import os
import typing

class PathWrapper:
    """ Allows to perform autojinja.Path(...) and autojinja.Path[...].
    """
    def __call__(self, arg1: str, *args: str) -> path.Path:
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        return path.Path(path.join(arg1, *args))
    def __getitem__(self, args: typing.Union[str, typing.Tuple[str, ...]]) -> path.Path:
        """ /dir1/dir2   file.txt -> /dir1/dir2/file.txt/
            /dir1/dir2/  dir3/    -> /dir1/dir2/dir3/
        """
        return path.Path(path.join[args])

Path = PathWrapper()
