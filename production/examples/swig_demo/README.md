# Debugging C++ extensions

When Python program fails, you get a stacktrace.
It's a natural starting point for troubleshooting.

This writeup describes hoops that should be jumped through to get
similar diagnostics for crashes inside the C/C++ code invoked from
the Python code.

The debugging scenario below targets Linux and was tested on Ubuntu.
SWIG extensions themselves should work fine on all reasonable OSes.

### Preparation

```bash
# enable coredumps
ulimit -c unlimited

# work around the Ubuntu bug
# https://bugs.launchpad.net/ubuntu/+source/apport/+bug/160999
rm -f core
# (you'll have to delete it before each run)
```

### Running the program

```bash
python3 -m production.examples.swig_demo.debugging_demo fail_assert
```

You will get the Python part of the stacktrace right away,
assuming the fault handler is enabled:
```python
import faulthandler
faulthandler.enable()
```

`debugging_demo.py` supports a number of crash scenarios to play with,
see the source.

If the crash happens inside a test, you will see something like
```
...
test1 PASSED
test2 PASSED
test3 Segmentation fault (core dumped)
```

To get more information, you might want to disable stdout/stderr capture:
```bash
python3 -m production.test_all --capture=no
```

### The C/C++ part of the stacktrace

```bash
gdb "$(which python3)" core -batch -ex bt
```

Most of it will be inside the interpreter,
so usually only the first few stack frames are interesting.

### Bonus: the program is stuck in an infinite loop and you don't know where

For example,
```bash
# enable tail call elimination
TBD_RELEASE=yes \
python3 -m production.examples.swig_demo.debugging_demo infinite_recursion
```

Hit `Ctrl-\` to kill it with `SIGQUIT`. The rest is the same.
