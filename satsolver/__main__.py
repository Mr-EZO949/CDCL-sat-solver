import sys

from satsolver.cli import main

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    sys.exit(main(sys.argv))
