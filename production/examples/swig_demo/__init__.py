# Magically compile extension in this package when we try to import it.

import os
import sys
import distutils.core


def build_extension():
    cur_dir = os.getcwd()
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        distutils.core.setup(
            name='sample',
            py_modules=['sample'],
            ext_modules=[
                distutils.core.Extension('_sample',
                    ['sample.i', 'sample.cpp'],
                    depends=['sample.h', '__init__.py'],
                    swig_opts=['-c++'],
                    extra_compile_args=['-std=c++11'],
                    undef_macros=['NDEBUG'],  # want assertions
                ),
            ],
            script_args=['--quiet', 'build_ext', '--inplace']
        )
    finally:
        os.chdir(cur_dir)


# contextlib.redirect_stdout is not enough because spawned processes
# (compilers and SWIG) can spam to stdout as well
try:
    stdout_backup = os.dup(sys.stdout.fileno())
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    build_extension()
finally:
    os.dup2(stdout_backup, sys.stdout.fileno())
