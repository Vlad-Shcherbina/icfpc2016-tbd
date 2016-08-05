"""
Basic computational geometry stuff.
"""

from fractions import Fraction
from typing import NamedTuple, List


Point = NamedTuple('Point', [('x', Fraction), ('y', Fraction)])


def polygon_area(vertices: List[Point]) -> Fraction:
    """Counterclockwise results in positive area."""
    assert vertices
    s = 0
    for pt1, pt2 in zip(vertices, vertices[1:] + vertices[:1]):
        s += (pt1.x - pt2.x) * (pt1.y + pt2.y)

    return s / Fraction(2)
