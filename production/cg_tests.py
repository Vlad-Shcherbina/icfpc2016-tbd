#!/bin/env python3

from fractions import Fraction
from production.cg import Point, polygon_area


def test_area():
    sq = [
        Point(0, 0),
        Point(1, 0),
        Point(1, 1),
        Point(0, 1),
    ]
    assert polygon_area(sq) == 1

    tr = [
        Point(Fraction(1, 2), 0),
        Point(0, 1),
        Point(1, Fraction(1, 3)),
    ]
    assert polygon_area(tr) == -Fraction(1, 3)

if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
