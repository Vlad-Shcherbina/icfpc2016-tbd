#!/bin/env python3

import textwrap

from fractions import Fraction
from production.cg import Point
from production.ioformats import parse_problem, Problem, load_problem


def test_problem_parser():
    s = textwrap.dedent('''\
    1
    4
    0,0
    1,0
    1/2,1/2
    0,1/2
    5
    0,0 1,0
    1,0 1/2,1/2
    1/2,1/2 0,1/2
    0,1/2 0,0
    0,0 1/2,1/2
    ''')
    print(s)

    problem = parse_problem(s)

    expected_problem = Problem(
        silhouette=[
            [Point(x=0, y=0), Point(x=1, y=0),
             Point(x=Fraction(1, 2), y=Fraction(1, 2)),
             Point(x=0, y=Fraction(1, 2))]],
        skeleton=[
            (Point(x=0, y=0), Point(x=1, y=0)),
            (Point(x=1, y=0), Point(x=Fraction(1, 2), y=Fraction(1, 2))),
            (Point(x=Fraction(1, 2), y=Fraction(1, 2)),
             Point(x=0, y=Fraction(1, 2))),
            (Point(x=0, y=Fraction(1, 2)), Point(x=0, y=0)),
            (Point(x=0, y=0), Point(x=Fraction(1, 2), y=Fraction(1, 2)))])

    assert problem == expected_problem


def test_load_problem():
    expected_problem = Problem(
        silhouette=[[Point(x=0, y=0), Point(x=1, y=0), Point(x=1, y=1), Point(x=0, y=1)]],
        skeleton=[
            (Point(x=0, y=0), Point(x=1, y=0)),
            (Point(x=0, y=0), Point(x=0, y=1)),
            (Point(x=1, y=0), Point(x=1, y=1)),
            (Point(x=0, y=1), Point(x=1, y=1)),
            ])
    assert load_problem('1') == expected_problem 


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
