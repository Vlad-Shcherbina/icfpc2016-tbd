#!/bin/env python3

from fractions import Fraction

import pytest

from production.cg import (
    Point, polygon_area, is_point_on_edge, count_revolutions)


unit_square = [
    Point(0, 0),
    Point(1, 0),
    Point(1, 1),
    Point(0, 1),
]


def test_area():
    assert polygon_area(unit_square) == 1

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


def test_count_revolutions():
    with pytest.raises(AssertionError) as exc_info:
        count_revolutions(Point(1, Fraction(1, 3)), unit_square)
    assert 'on the border' in str(exc_info.value)

    assert count_revolutions(
        Point(Fraction(1, 2), Fraction(1, 2)), unit_square) == 1
    assert count_revolutions(
        Point(Fraction(1, 2), Fraction(1, 2)), unit_square[::-1]) == -1

    assert count_revolutions(
        Point(Fraction(3, 2), Fraction(1, 2)), unit_square) == 0
    assert count_revolutions(
        Point(Fraction(1, 2), Fraction(3, 2)), unit_square) == 0

    assert count_revolutions(Point(2, 0), unit_square) == 0
    assert count_revolutions(Point(-2, 0), unit_square) == 0
    assert count_revolutions(Point(2, 1), unit_square) == 0
    assert count_revolutions(Point(-2, 1), unit_square) == 0


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])