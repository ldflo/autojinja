class DiffException(Exception):
    def __init__(self, result, expected):
        result = str(result).replace('\t', "\\t").replace('\n', "\\n\n")
        expected = str(expected).replace('\t', "\\t").replace('\n', "\\n\n")
        message = f"--- Expected ---\n{expected}\\0\n--- Got ---\n{result}\\0"
        super().__init__(message)

def assert_exception(callable, exception_type, message, *args, **kwargs):
    try:
        callable(*args, **kwargs)
    except BaseException as e:
        exception = e
    else:
        exception = None
    if message != None and str(exception) != str(message):
        raise DiffException(exception, message)
    if exception == None or not isinstance(exception, exception_type):
        raise DiffException(type(exception), exception_type)

def clean_exception(exception):
    result = str(exception)
    lines = result.splitlines(keepends=True)
    for i in range(len(lines)):
        if lines[i].startswith("  File \""):
            idx1 = lines[i].index(", line")
            if idx1 >= 0:
                idx2 = lines[i].index(",", idx1 + len(", line"))
                lines[i] = "  File \"\", line ?" + lines[i][idx2:]
    return ''.join(lines)

def assert_clean_exception(callable, exception_type, message, *args, **kwargs):
    try:
        callable(*args, **kwargs)
    except BaseException as e:
        exception = e
    else:
        exception = None
    cleaned_exception = clean_exception(exception)
    if message != None and cleaned_exception != str(message):
        raise DiffException(cleaned_exception, message)
    if exception == None or not isinstance(exception, exception_type):
        raise DiffException(type(exception), exception_type)

class Class1:
    def a(self):
        return "b"
    @property
    def b(self):
        return "a"
    def f(self):
        return self.missing_f
    @property
    def x(self):
        return self.missing_x
    def ef(self):
        raise Exception("ef")
    @property
    def ex(self):
        raise Exception("ex")
class Class2:
    def a(self):
        return Class1().a()
    @property
    def b(self):
        return Class1().b
    def f(self):
        return Class1().f()
    @property
    def x(self):
        return Class1().x
    def ef(self):
        return Class1().ef()
    @property
    def ex(self):
        return Class1().ex
class Class3:
    def a(self):
        return Class2().a()
    @property
    def b(self):
        return Class2().b
    def f(self):
        return Class2().f()
    @property
    def x(self):
        return Class2().x
    def ef(self):
        return Class2().ef()
    @property
    def ex(self):
        return Class2().ex
