#!/bin/env python3

from fractions import Fraction
from production.cg import Point
from peluche_scratch.dummy_rectangle import *

def test_bounding_box():
    assert bounding_box([Point(0, 2), Point(-1, 1), Point(3, 0)]) == (-1, 3, 0, 2)

def test_compute_intersection():
    unit_square = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    assert compute_intersection(unit_square, [
        Point(Fraction('1/2'), Fraction('1/2')),
        Point(Fraction('1/3'), Fraction('1/2')),
        Point(Fraction('1/2'), Fraction('1/3')),
        Point(Fraction('2'), Fraction('2'))
    ]) == 3

