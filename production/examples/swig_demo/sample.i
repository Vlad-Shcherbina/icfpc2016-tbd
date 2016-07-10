%module sample

%feature("python:nondynamic", "1");
// Otherwise you can add arbitrary new attributes to swigged classes' __dict__,
// and even assign to read-only properties.

%include "typemaps.i"
%include "std_vector.i"
%include "std_string.i"

%template(IntVector) std::vector<int>;

%{
#include "sample.h"
%}

%include "sample.h"

%template(square_int) square<int>;
%template(square_float) square<double>;
