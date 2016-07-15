#!python3
import faulthandler
faulthandler.enable()
import sys
import pytest

if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv[1:]))
