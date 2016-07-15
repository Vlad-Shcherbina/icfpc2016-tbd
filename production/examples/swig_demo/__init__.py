# Magically compile extension in this package when we try to import it.

import os
import sys
import distutils.core
import distutils.util


def build_extension():
    release = distutils.util.strtobool(os.getenv('TBD_RELEASE', '0'))
    if release:
        extra_compile_args = [
            '-ggdb', '-std=c++11',
            '-O2']
        undef_macros = ['NDEBUG']  # want assertions even in the release build?
    else:
        extra_compile_args = [
            '-ggdb', '-std=c++11',
            '-O0', '-D_GLIBCXX_DEBUG', '-D_GLIBCXX_DEBUG_PEDANTIC']
        undef_macros = ['NDEBUG']  # want assertions

    # TODO: force distutils to rebuild the extension when the environment
    # variable changes, even if the source was not touched.

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
                    extra_compile_args=extra_compile_args,
                    undef_macros=undef_macros,
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
