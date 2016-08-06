"""
Basic computational geometry stuff.
"""

from fractions import Fraction
from typing import NamedTuple, List, Tuple, Optional


Point = NamedTuple('Point', [('x', Fraction), ('y', Fraction)])
class Point(Point):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def __mul__(self, a):
        return Point(self.x * a, self.y * a)
    def __truediv__(self, a):
        return self * (1 / Fraction(a))
    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)


class Mat2:
    @staticmethod
    def identity():
        return Mat2()

    def __init__(self, a=None):
        if a is None:
            self.a = [[1, 0], [0, 1]]
        else:
            assert len(a) == 2
            assert len(a[0]) == 2
            assert len(a[1]) == 2
            self.a = [list(row) for row in a]

    def __repr__(self):
        return 'Mat2([{}, {}], [{}, {}])'.format(
            self.a[0][0], self.a[0][1], self.a[1][0], self.a[1][1])

    def __eq__(self, other):
        return self.a == other.a

    def transform(self, pt: Point) -> Point:
        a = self.a
        return Point(
            x=pt.x * a[0][0] + pt.y * a[0][1],
            y=pt.x * a[1][0] + pt.y * a[1][1],
        )

    def __mul__(self, k: Fraction) -> 'Mat2':
        assert isinstance(k, (int, Fraction)), k
        result = Mat2()
        for i in range(2):
            for j in range(2):
                result.a[i][j] = self.a[i][j] * k
        return result

    def __matmul__(self, other):
        result = Mat2()
        for i in range(2):
            for j in range(2):
                result.a[i][j] = sum(
                    self.a[i][k] * other.a[k][j] for k in range(2))
        return result

    def det(self):
        return self.a[0][0] * self.a[1][1] - self.a[0][1] * self.a[1][0]

    def inv(self):
        d = self.det()
        d_inv = 1 / Fraction(d)
        result = Mat2()
        result.a[0][0] = self.a[1][1] * d_inv
        result.a[1][1] = self.a[0][0] * d_inv
        result.a[0][1] = self.a[0][1] * d_inv * -1
        result.a[1][0] = self.a[1][0] * d_inv * -1
        return result


class AffineTransform:
    @staticmethod
    def identity():
        return AffineTransform()

    def __init__(self, mat=None, offset=None):
        self.mat = mat or Mat2()
        self.offset = offset or Point(0, 0)

    def __repr__(self):
        return 'AffineTransform({}, {})'.format(self.mat, self.offset)

    def __eq__(self, other):
        return self.mat == other.mat and self.offset == other.offset

    def transform(self, pt: Point) -> Point:
        return self.mat.transform(pt) + self.offset

    def __matmul__(self, other):
        mat = self.mat @ other.mat
        offset = self.mat.transform(other.offset) + self.offset
        return AffineTransform(mat, offset)

    def inv(self):
        m_inv = self.mat.inv()
        offset_inv = m_inv.transform(self.offset) * -1
        return AffineTransform(m_inv, offset_inv)

    @staticmethod
    def align(pre1: Point, pre2: Point,
              post1: Point, post2: Point) -> 'AffineTransform':
        """Congruence transform that aligns two vectors.

        pre1 maps to post1
        and transformed pre2 points in the same direction as post2

        Orientation is preserved.

        Raise IrrationalError when appropriate
        (for example, when rotating 45 deg).
        """
        assert pre1 != pre2
        assert post1 != post2

        pre_d = pre2 - pre1
        post_d = post2 - post1

        rot_x = post_d.x * pre_d.x + post_d.y * pre_d.y
        rot_y = post_d.y * pre_d.x - post_d.x * pre_d.y
        d2 = rot_x * rot_x + rot_y * rot_y
        d = rational_sqrt(d2)

        rot_x /= d
        rot_y /= d

        mat = Mat2([[rot_x, -rot_y], [rot_y, rot_x]])
        offset = post1 - mat.transform(pre1)

        return AffineTransform(mat, offset)

    @staticmethod
    def mirror(pt1: Point, pt2: Point):
        assert pt1 != pt2
        flip = AffineTransform(Mat2([[1, 0], [0, -1]]))
        fixup = AffineTransform.align(
            flip.transform(pt1), flip.transform(pt2),
            pt1, pt2)
        return fixup @ flip


class IrrationalError(Exception):
    pass


def rational_sqrt(x: Fraction) -> Fraction:
    """Raise IrrationalError if sqrt is irrational.

    >>> rational_sqrt(Fraction(2, 8))
    Fraction(1, 2)

    >>> rational_sqrt(2)
    Traceback (most recent call last):
       ...
    production.cg.IrrationalError: sqrt(2)
    """
    return Fraction(int_sqrt(x.numerator), int_sqrt(x.denominator))


def int_sqrt(x: int) -> int:
    """Raise IrrationalError if sqrt is irrational.

    >>> int_sqrt(9)
    3

    >>> int_sqrt(2)
    Traceback (most recent call last):
       ...
    production.cg.IrrationalError: sqrt(2)

    >>> int_sqrt(123456789**2)
    123456789
    """
    assert x >= 0

    b = 1
    while b * b <= x:
        b += b

    s = 0
    while b > 0:
        if (s + b) ** 2 <= x:
            s += b
        b //= 2

    if s**2 == x:
        return s

    raise IrrationalError('sqrt({})'.format(x))


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


def is_point_on_poly_border(pt: Point, poly: List[Point]) -> bool:
    edges = list(zip(poly, poly[1:] + poly[:1]))
    return any(is_point_on_edge(pt, edge) for edge in edges)


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


def edge_intersection(edge1, edge2) -> Optional[Point]:
    """
    Note: return None for parallel edges, even if they have exactly one point
    in common.
    """
    pt1, pt2 = edge1
    pt3, pt4 = edge2
    assert pt1 != pt2
    assert pt3 != pt4

    bb_x1 = max(min(pt1.x, pt2.x), min(pt3.x, pt4.x))
    bb_y1 = max(min(pt1.y, pt2.y), min(pt3.y, pt4.y))
    bb_x2 = min(max(pt1.x, pt2.x), max(pt3.x, pt4.x))
    bb_y2 = min(max(pt1.y, pt2.y), max(pt3.y, pt4.y))

    if bb_x1 > bb_x2 or bb_y1 > bb_y2:
        return None  # bounding boxes do not overlap

    d1 = pt2 - pt1
    d2 = pt4 - pt3

    if d1.cross(d2) == 0:
        return None  # edges are parallel

    alpha = d1.cross(pt3 - pt1)
    beta = d1.cross(pt4 - pt1)
    assert alpha != beta

    pt = (pt3 * beta - pt4 * alpha) / Fraction(beta - alpha)

    if bb_x1 <= pt.x <= bb_x2 and bb_y1 <= pt.y <= bb_y2:
        return pt
    else:
        return None


def point_inside_unit_square(pt: Point) -> bool:
    return 0 <= pt.x <= 1 and 0 <= pt.y <= 1


def poly_inside_unit_square(poly: List[Point]) -> bool:
    return all(point_inside_unit_square(pt) for pt in poly)


def edge_on_unit_square_border(pt1: Point, pt2: Point):
    assert point_inside_unit_square(pt1)
    assert point_inside_unit_square(pt2)
    if pt1.x == pt2.x == 0:
        return True
    if pt1.y == pt2.y == 0:
        return True
    if pt1.x == pt2.x == 1:
        return True
    if pt1.y == pt2.y == 1:
        return True
    return False
