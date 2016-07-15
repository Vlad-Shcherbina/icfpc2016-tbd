import faulthandler
faulthandler.enable()

import sys
from production.examples.swig_demo.sample import Fail


def main():  # pragma: no cover
    assert len(sys.argv) == 2
    if sys.argv[1] == 'fail_assert':
        Fail.fail_assert()
    elif sys.argv[1] == 'index_out_of_bounds':
        Fail.index_out_of_bounds()
    elif sys.argv[1] == 'page_fault':
        Fail.page_fault()
    elif sys.argv[1] == 'infinite_recursion':
        Fail.infinite_recursion()
    else:
        assert False, sys.argv[1]


if __name__ == '__main__':
    main()
