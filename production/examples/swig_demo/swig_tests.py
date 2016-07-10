import pytest
from production.examples.swig_demo import sample


def test_stuff():
    assert sample.N == 42
    assert sample.square_float(2) == 4
    assert sample.reverse([1, 2, 3]) == (3, 2, 1)

    hz = sample.Hz()
    with pytest.raises(AttributeError):
        hz.zzz = 0
