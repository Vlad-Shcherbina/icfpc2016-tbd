"""
Basic computational geometry stuff.
"""

from fractions import Fraction
from typing import NamedTuple, List, Tuple


Point = NamedTuple('Point', [('x', Fraction), ('y', Fraction)])


def polygon_area(vertices: List[Point]) -> Fraction:
    """Counterclockwise results in positive area."""
    assert vertices
    s = 0
    for pt1, pt2 in zip(vertices, vertices[1:] + vertices[:1]):
        s += (pt1.x - pt2.x) * (pt1.y + pt2.y)

    return s / Fraction(2)


def is_point_on_edge(pt: Point, edge: Tuple[Point, Point]) -> bool:
    pt1, pt2 = edge
    assert pt1 != pt2

    if pt.x < pt1.x and pt.x < pt2.x:
        return False
    if pt.y < pt1.y and pt.y < pt2.y:
        return False
    if pt.x > pt1.x and pt.x > pt2.x:
        return False
    if pt.y > pt1.y and pt.y > pt2.y:
        return False

    dx = pt1.x - pt2.x
    dy = pt1.y - pt2.y

    dxp = pt.x - pt1.x
    dyp = pt.y - pt1.y

    return dx * dyp == dy * dxp
