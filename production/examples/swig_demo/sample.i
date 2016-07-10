%module sample

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
