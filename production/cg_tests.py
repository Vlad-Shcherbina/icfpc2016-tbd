#!/bin/env python3

from fractions import Fraction

import pytest

from production.cg import Point, polygon_area, is_point_on_edge


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


@pytest.mark.parametrize("edge", [
    (Point(0, 0), Point(2, 1)),
    (Point(2, 1), Point(0, 0)),
])
def test_point_on_edge(edge):
    assert is_point_on_edge(Point(0, 0), edge)
    assert is_point_on_edge(Point(2, 1), edge)
    assert is_point_on_edge(Point(Fraction(2, 3), Fraction(1, 3)), edge)

    assert not is_point_on_edge(Point(1, 2), edge)
    assert not is_point_on_edge(
        Point(Fraction(31, 30), Fraction(19, 30)), edge)
    assert not is_point_on_edge(Point(4, 2), edge)
    assert not is_point_on_edge(Point(-2, -1), edge)


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
