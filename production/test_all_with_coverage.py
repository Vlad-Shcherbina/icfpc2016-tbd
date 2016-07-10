import sys
import webbrowser
import os
import pytest

if __name__ == '__main__':
    # Coverage relies on the current directory to locate .coveragerc
    # and to place .coverage and htmlcov/.
    cur_dir = os.getcwd()
    try:
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

        return_code = pytest.main(['--cov', '--cov-report=html'] + sys.argv[1:])
        if return_code:
            sys.exit(return_code)

        webbrowser.open(os.path.abspath('htmlcov/index.html'))

    finally:
        os.chdir(cur_dir)
