# Magically compile the extension in this package when we try to import it.
from production.swig_utils import magic_extension
magic_extension(
    __file__,
    name='sample',
    sources=['sample.i', 'sample.cpp'],
    headers=['sample.h'])
