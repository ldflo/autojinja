class ignore:
    """ Allows to ignore/pass an error with context manager syntax.
        Usage:
            with ignore(KeyError):
                raise KeyError()
                print("Not reached")
            print("Reached")
    """
    def __init__(self, type = Exception):
            self.Type = type
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        if type != None and issubclass(type, self.Type):
            return True # Ignore
