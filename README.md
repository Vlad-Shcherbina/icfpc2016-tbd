## Setup

SWIG 3.0, it should be available in PATH under the name `swig`
(symlink if necessary):
```
$ swig -version
SWIG Version 3.0.8
...
```

On Windows, Visual Studio 2015 Community or Express edition (for C++ compiler).

CPython 3.5.2 (the latest stable release).

Virtualenv is optional.

`pip3 install -r requirements.txt`

Copy `git_hooks/pre-push` to `.git/hooks/`.


## Running stuff

Root of this repository should be in `PYTHONPATH`, because we use absolute imports (`from production import utils`). There are several ways to achieve that:
  - add project path to the environment variable
  - create the file `<python installation or venv>/lib/python3.5/site-packages/tbd.pth` whose content is a single line `/path/to/icfpc2016-tbd`
  - configure your favorite IDE appropriately
  - use `python3 -m production.some_script` instead of `python3 production/some_script.py`
