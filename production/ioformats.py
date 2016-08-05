from fractions import Fraction
from typing import NamedTuple, List, Tuple

from production.cg import Point


Problem = NamedTuple('Problem', [
    ('silhouette', List[List[Point]]),
    ('skeleton', List[Tuple[Point, Point]]),
])


def parse_fraction(s: str) -> Fraction:
    """
    >>> parse_fraction('42')
    42
    >>> parse_fraction('2/6')
    Fraction(1, 3)
    """
    if '/' in s:
        nom, denom = s.split('/')
        return Fraction(int(nom), int(denom))
    else:
        return int(s)


def parse_point(s: str) -> Point:
    r"""
    >>> parse_point('  1, 2/ 3 \n')
    Point(x=1, y=Fraction(2, 3))
    """
    x, y = s.split(',')
    return Point(parse_fraction(x), parse_fraction(y))


def parse_problem(s: str) -> Problem:
    lines = iter(line for line in s.splitlines() if line.strip())

    num_polys = int(next(lines))
    silhouette = []
    for _ in range(num_polys):
        silhouette.append([])
        num_vertices = int(next(lines))
        for _ in range(num_vertices):
            silhouette[-1].append(parse_point(next(lines)))

    num_edges = int(next(lines))
    skeleton = []
    for _ in range(num_edges):
        # TODO: won't work if there are whitespaces inside, but do we care?
        pt1, pt2 = next(lines).split()
        skeleton.append((parse_point(pt1), parse_point(pt2)))

    return Problem(silhouette=silhouette, skeleton=skeleton)
