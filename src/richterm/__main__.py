"""Entry-point module, in case you use `python -m pp3`."""

import sys

from richterm import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
