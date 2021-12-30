__version__ = "1.0.0"

from . import main

import sys

def entry_point():
    try:
        main(*sys.argv[1:])
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)

if __name__ == "__main__":
    entry_point()
