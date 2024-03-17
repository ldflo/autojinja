from . import parser

import os
from typing import Generic, Tuple, Type, TypeVar
import traceback

_TException = TypeVar("_TException", bound=Exception)

### Base exception

class CommonException(Exception, Generic[_TException]):
    @staticmethod
    def from_marker(exceptionType: Type[_TException], marker: parser.Marker, pos: int, size: int, message: str) -> _TException:
        line = line_at_index(marker.string, pos)
        (l, c) = index_to_coordinates(marker.string, pos)
        message = f"{message}\n{line}\n{' ' * (c-1)}{'^' * size} line {marker.parent_lineno + l-1}, column {marker.parent_column + c}"
        exception = exceptionType(message)
        return exception
    
    @staticmethod
    def from_exception(exception: _TException, marker: parser.Marker) -> _TException:
        exception = prepend_jinja2_traceback(exception)
        text = format_text(marker.header)
        stack = f"\n  During {'reinsertion' if marker.is_edit else 'generation'} of \"{marker.open} {text} {marker.close}\" at line {marker.parent_lineno + marker.header_open_lineno-1}, column {marker.parent_column + marker.header_open_column+1}"
        message = str(exception).lstrip('\n')
        message = f"{stack}\n{message}"
        exception = wrap_exception(exception, message)
        return exception

    def __init__(self, message: str):
        super().__init__(message)

### Parsing exception

class ParsingException(CommonException):
    def __init__(self, message: str):
        super().__init__(message)

class OpenMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "OpenMarkerNotFoundException":
        return CommonException.from_marker(OpenMarkerNotFoundException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Couldn't find corresponding open marker \"{marker.open} {marker.close}\":")
    def __init__(self, message: str):
        super().__init__(message)

class CloseMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "CloseMarkerNotFoundException":
        return CommonException.from_marker(CloseMarkerNotFoundException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Couldn't find corresponding close marker \"{marker.close}\":")
    def __init__(self, message: str):
        super().__init__(message)

class EndMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "EndMarkerNotFoundException":
        return CommonException.from_marker(EndMarkerNotFoundException,
                                           marker,
                                           marker.header_close - len(marker.close),
                                           len(marker.close),
                                           f"Couldn't find corresponding end marker \"{marker.open} {marker.end} {marker.close}\":")
    def __init__(self, message: str):
        super().__init__(message)

class RequireHeaderInlineException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "RequireHeaderInlineException":
        return CommonException.from_marker(RequireHeaderInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't have a multiline header:")
    def __init__(self, message: str):
        super().__init__(message)

class RequireHeaderMultilineException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "RequireHeaderMultilineException":
        return CommonException.from_marker(RequireHeaderMultilineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't have a one line header:")
    def __init__(self, message: str):
        super().__init__(message)

class WrongHeaderIndentationException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker, pos) -> "WrongHeaderIndentationException":
        return CommonException.from_marker(WrongHeaderIndentationException,
                                           marker,
                                           pos,
                                           len(marker.open),
                                           f"Wrong marker header indentation:")
    def __init__(self, message: str):
        super().__init__(message)

class RequireNewlineException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "RequireNewlineException":
        return CommonException.from_marker(RequireNewlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't start on same line as previous end marker:")
    def __init__(self, message: str):
        super().__init__(message)

class RequireInlineException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "RequireInlineException":
        return CommonException.from_marker(RequireInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker must start on same line as previous marker:")
    def __init__(self, message: str):
        super().__init__(message)

class WrongInclusionException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "WrongInclusionException":
        return CommonException.from_marker(WrongInclusionException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker has wrong inclusion regarding enclosing markers:")
    def __init__(self, message: str):
        super().__init__(message)

class DuplicateEditException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "DuplicateEditException":
        return CommonException.from_marker(DuplicateEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Duplicate edit marker \"{marker.open} {marker.header} {marker.close}\", consider reusing/removing duplicates:")
    def __init__(self, message: str):
        super().__init__(message)

class DirectlyEnclosedEditException(ParsingException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "DirectlyEnclosedEditException":
        return CommonException.from_marker(DirectlyEnclosedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Directly enclosed edit marker \"{marker.open} {marker.header} {marker.close}\", probably missing \"{marker.open} {marker.end} {marker.close}\":")
    def __init__(self, message: str):
        super().__init__(message)

### Generation exception

class GenerationException(CommonException):
    def __init__(self, message: str):
        super().__init__(message)

class RequireBodyInlineException(GenerationException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "RequireBodyInlineException":
        return CommonException.from_marker(RequireBodyInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Generated body must contain only one line to be inlined:")
    def __init__(self, message: str):
        super().__init__(message)

class NonGeneratedEditException(GenerationException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "NonGeneratedEditException":
        return CommonException.from_marker(NonGeneratedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Non-generated edit marker \"{marker.open} {marker.header} {marker.close}\", consider reusing/removing it:")
    def __init__(self, message: str):
        super().__init__(message)

class AlreadyGeneratedEditException(GenerationException):
    @staticmethod
    def from_marker(marker: parser.Marker) -> "AlreadyGeneratedEditException":
        return CommonException.from_marker(AlreadyGeneratedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Already generated edit marker \"{marker.open} {marker.header} {marker.close}\", consider fixing generation:")
    def __init__(self, message: str):
        super().__init__(message)

### Utils

def index_to_coordinates(string: str, index: int) -> Tuple[int, int]:
    """ Returns the corresponding tuple (line, column) of the character at the given index of the given string.
    """
    if index < 0:
        index =  index % len(string)
    sp = string[:index+1].splitlines(keepends=True)
    return len(sp), len(sp[-1])

def line_at_index(string: str, index: int) -> str:
    """ Returns the line at the given index of the given string.
    """
    if index < 0:
        index =  index % len(string)
    start = string.rfind('\n', 0, index)+1
    end = string.find('\n', index)
    suffix = '\\n' if end >= 0 else '\\0'
    if end < 0:
        end = len(string)
    return f"{string[start:end]}{suffix}"

def format_text(text: str, max_length = 50, suffix = "...") -> str:
    """ Replaces tabulations and ends of line.
    """
    text = text if len(text) <= max_length else f"{text[:max_length]}{suffix}"
    return text.replace('\t', "\\t").replace('\n', "\\n")

def split_traceback(tb: str, remove_class_name = False) -> Tuple[str, str]:
    """ Splits the given traceback into (stacktrace, message).
    """
    startidx = -1
    while True:
        startidx = tb.find('\n', startidx+1)
        if startidx < 0:
            break # No stacktrace
        if not tb.startswith('  ', startidx+1):
            break # End of stacktrace
    if startidx < 0:
        stacktrace = None # No stacktrace
    else:
        stacktrace = tb[:startidx]
    if not remove_class_name:
        message = tb[startidx+1:]
    else:
        idx = tb.find(' ', startidx+1)
        if idx < 0:
            message = None # No message
        else:
            idx += 2 if tb[idx+1] == '\n' else 1 # lstrip one
            message = tb[idx:]
    return stacktrace, message

_disallowed_attrs = [
    "__delattr__",
    "__getattr__",
    "__getattribute__",
    "__init__",
    "__new__",
    "__setattr__",
    "__str__",
]

def wrap_exception(exception: _TException, message) -> _TException:
    """ Wraps the given exception with a custom message.
        Creates an object that mocks the exception class.
    """
    if hasattr(exception, "_wrapped_exception"):
        exception._wrapped_message = message
        return exception
    try:
        def __init__(self):
            pass
        def __str__(self):
            return self._wrapped_message
        dicts = { name: getattr(exception, name) for name in dir(exception)
                  if name.startswith("__") and name not in _disallowed_attrs }
        dicts["__init__"] = __init__
        dicts["__module__"] = exception.__class__.__module__
        dicts["__str__"] = __str__
        mock = type(exception.__class__.__qualname__, (exception.__class__,), dicts)()
        for key, value in mock.__dict__.items():
            setattr(mock, key, value)
        mock._wrapped_exception = exception
        mock._wrapped_message = message
        return mock
    except Exception:
        return exception

def prepend_jinja2_traceback(exception: _TException, tb: str = None) -> _TException:
    """ Prepends the Jinja2 traceback to the given exception.
        Creates an object that derives the exception class.
    """
    if tb == None:
        tb = traceback.format_exc().rstrip('\n')
    (stacktrace, message) = split_traceback(tb, True)
    if hasattr(exception, "_wrapped_exception"):
        stacktrace = None
    elif stacktrace != None:
        token1 = f"jinja2{os.sep}environment.py\", " # Jinja2 hack
        token2 = f"jinja2{os.sep}runtime.py\", " # Jinja2 hack
        startidx = -1
        while True:
            idx = stacktrace.find(token1, startidx+1)
            if idx < 0:
                idx = stacktrace.find(token2, startidx+1)
                if idx < 0:
                    break # Token not found
                startidx = stacktrace.find('\n', idx+len(token2))
            else:
                startidx = stacktrace.find('\n', idx+len(token1))
            while True:
                if startidx < 0:
                    startidx = len(stacktrace)
                    exit = True
                    break # No eol after token
                if not stacktrace.startswith("    ", startidx+1):
                    exit = False
                    break # No inner traceback
                startidx = stacktrace.find('\n', startidx+1)
            if exit:
                break # Done
        if startidx < 0:
            return exception
        stacktrace = stacktrace[startidx+1:]
        if len(stacktrace) == 0:
            stacktrace = None
        else:
            # Clean autojinja stacktrace
            token = f"autojinja{os.sep}templates.py\", "
            idx = stacktrace.find(token)
            if idx >= 0:
                startidx = stacktrace.rfind('\n', 0, idx)
                if startidx < 0: # No eol before token
                    stacktrace = None
                else:
                    stacktrace = stacktrace[:startidx]
    if message == None:
        message = ""
    message = f"\n{stacktrace}\n{message}" if stacktrace else f"\n{message}"
    return wrap_exception(exception, message)

def clean_traceback(exception: _TException) -> _TException:
    """ Removes the traceback of the given exception.
    """
    return prepend_jinja2_traceback(exception).with_traceback(None)
