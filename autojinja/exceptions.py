import os
import traceback

### Base exception

class CommonException(Exception):
    @staticmethod
    def from_marker(exceptionType, marker, pos, size, message):
        line = line_at_index(marker.string, pos)
        (l, c) = index_to_coordinates(marker.string, pos)
        message = f"{message}\n{line}\n{' ' * (c-1)}{'^' * size} line {l}, column {c}"
        exception = exceptionType(message)
        exception.coordinates = (l, c)
        return exception
    @staticmethod
    def from_exception(exception, marker):
        exception = prepend_jinja2_traceback(exception)
        text = format_text(marker.header)
        (l, c) = index_to_coordinates(marker.string, marker.header_open)
        stack = f"\n  During {'reinsertion' if marker.is_edit else 'generation'} of \"{marker.open} {text} {marker.close}\" at line {l}, column {c}"
        message = str(exception).lstrip('\n')
        message = f"{stack}\n{message}"
        exception = wrap_exception(exception, message)
        exception.coordinates = (l, c)
        return exception

    def __init__(self, message):
        super().__init__(message)

### Parsing exception

class ParsingException(CommonException):
    def __init__(self, message):
        super().__init__(message)

class OpenMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(OpenMarkerNotFoundException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Couldn't find corresponding open marker \"{marker.open} {marker.close}\":")
    def __init__(self, message):
        super().__init__(message)

class CloseMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(CloseMarkerNotFoundException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Couldn't find corresponding close marker \"{marker.close}\":")
    def __init__(self, message):
        super().__init__(message)

class EndMarkerNotFoundException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(EndMarkerNotFoundException,
                                           marker,
                                           marker.header_close - len(marker.close),
                                           len(marker.close),
                                           f"Couldn't find corresponding end marker \"{marker.open} {marker.end} {marker.close}\":")
    def __init__(self, message):
        super().__init__(message)

class RequireHeaderInlineException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(RequireHeaderInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't have a multiline header:")
    def __init__(self, message):
        super().__init__(message)

class RequireHeaderMultilineException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(RequireHeaderMultilineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't have a one line header:")
    def __init__(self, message):
        super().__init__(message)

class WrongHeaderIndentationException(ParsingException):
    @staticmethod
    def from_marker(marker, pos):
        return CommonException.from_marker(WrongHeaderIndentationException,
                                           marker,
                                           pos,
                                           len(marker.open),
                                           f"Wrong marker header indentation:")
    def __init__(self, message):
        super().__init__(message)

class RequireNewlineException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(RequireNewlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker can't start on same line as previous end marker:")
    def __init__(self, message):
        super().__init__(message)

class RequireInlineException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(RequireInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker must start on same line as previous marker:")
    def __init__(self, message):
        super().__init__(message)

class WrongInclusionException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(WrongInclusionException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Marker has wrong inclusion regarding enclosing markers:")
    def __init__(self, message):
        super().__init__(message)

class DuplicateEditException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(DuplicateEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Duplicate edit marker \"{marker.open} {marker.header} {marker.close}\", consider reusing/removing duplicates:")
    def __init__(self, message):
        super().__init__(message)

class DirectlyEnclosedEditException(ParsingException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(DirectlyEnclosedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Directly enclosed edit marker \"{marker.open} {marker.header} {marker.close}\", consider reusing/removing it:")
    def __init__(self, message):
        super().__init__(message)

### Generation exception

class GenerationException(CommonException):
    def __init__(self, message):
        super().__init__(message)

class RequireBodyInlineException(GenerationException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(RequireBodyInlineException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Generated body must contain only one line to be inlined:")
    def __init__(self, message):
        super().__init__(message)

class NonGeneratedEditException(GenerationException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(NonGeneratedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Non-generated edit marker \"{marker.open} {marker.header} {marker.close}\", consider reusing/removing it:")
    def __init__(self, message):
        super().__init__(message)

class AlreadyGeneratedEditException(GenerationException):
    @staticmethod
    def from_marker(marker):
        return CommonException.from_marker(AlreadyGeneratedEditException,
                                           marker,
                                           marker.header_open,
                                           len(marker.open),
                                           f"Already generated edit marker \"{marker.open} {marker.header} {marker.close}\", consider fixing generation:")
    def __init__(self, message):
        super().__init__(message)

### Utils

def index_to_coordinates(string, index):
    """ Returns the corresponding tuple (line, column) of the character at the given index of the given string.
    """
    if index < 0:
        index =  index % len(string)
    sp = string[:index+1].splitlines(keepends=True)
    return len(sp), len(sp[-1])

def line_at_index(string, index):
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

def format_text(text, max_length = 50, suffix = "..."):
    """ Replaces tabulations and ends of line.
    """
    text = text if len(text) <= max_length else f"{text[:max_length]}{suffix}"
    return text.replace('\t', "\\t").replace('\n', "\\n")

def split_traceback(tb, remove_class_name = False):
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

def wrap_exception(exception, message):
    """ Wraps the given exception with a custom message.
        Creates an object that derives the exception class.
    """
    if hasattr(exception, "__exception") and hasattr(exception, "__message"):
        exception.__message = message
        return exception
    def __init__(self):
        pass
    def __repr__(self):
        return self.__message
    def __str__(self):
        return self.__message
    dicts = { "__init__" : __init__,
              "__repr__" : __repr__,
              "__str__" : __str__,
              "__module__" : exception.__class__.__module__ }
    wrapped_exception = type(exception.__class__.__qualname__, (exception.__class__,), dicts)()
    wrapped_exception.__dict__.update(exception.__dict__)
    wrapped_exception.__exception = exception
    wrapped_exception.__message = message
    return wrapped_exception

def prepend_jinja2_traceback(exception, tb = None):
    """ Prepends the Jinja2 traceback to the given exception.
        Creates an object that derives the exception class.
    """
    if tb == None:
        tb = traceback.format_exc().rstrip('\n')
    (stacktrace, message) = split_traceback(tb, True)
    if stacktrace != None:
        token = f"jinja2{os.sep}environment.py\", " # Jinja2 hack
        startidx = -1
        while True:
            idx = stacktrace.find(token, startidx+1)
            if idx < 0:
                break # Token not found
            startidx = stacktrace.find('\n', idx+len(token))
            if startidx < 0:
                startidx = len(stacktrace)
                break # No eol after token
            if not stacktrace.startswith('    ', startidx+1):
                continue # No inner traceback
            startidx = stacktrace.find('\n', startidx+1)
            if startidx < 0:
                startidx = len(stacktrace)
                break # No eol after inner traceback
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

def clean_traceback(exception):
    """ Removes the traceback of the given exception.
    """
    return prepend_jinja2_traceback(exception).with_traceback(None)
