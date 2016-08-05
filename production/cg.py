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


def count_revolutions(pt: Point, poly: List[Point]) -> int:
    """The number of revolutions the polygon "makes" around the point.

    If the point is outside of the poly, 0.
    If the point is inside CCW poly, +1.
    If the point is inside CW poly, -1.
    """
    edges = list(zip(poly, poly[1:] + poly[:1]))
    assert all(not is_point_on_edge(pt, edge) for edge in edges), (
        ('undefined because the point is on the border', pt, poly))

    cnt = 0
    for pt1, pt2 in edges:
        if min(pt1.y, pt2.y) <= pt.y < max(pt1.y, pt2.y):
            t = (pt.y - pt1.y) / Fraction(pt2.y - pt1.y)
            print(pt, pt1, pt2, t)
            assert 0 <= t <= 1
            x = pt1.x + t * (pt2.x - pt1.x)
            assert x != pt.x
            if x > pt.x:
                if pt1.y < pt2.y:
                    cnt += 1
                else:
                    cnt -= 1

    return cnt


def rational_angle(pt: Point) -> Fraction:
    """Kinda like atan2, but rational.

    Return some monotonous transformation of angle (so it can still be used
    for sorting).
    Result is in [0, 4) range.
    """

    assert pt != Point(0, 0)

    rot = 0
    while not (pt.x > 0 and pt.y >= 0):
        rot += 1
        pt = Point(pt.y, -pt.x)

    return pt.y / Fraction(pt.x + pt.y) + rot
