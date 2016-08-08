from fractions import Fraction
from typing import NamedTuple, List, Tuple
from pathlib import Path

from production.cg import Point


Problem = NamedTuple('Problem', [
    ('silhouette', List[List[Point]]),
    ('skeleton', List[Tuple[Point, Point]]),
])


Solution = NamedTuple('Solution', [
    ('orig_points', List[Point]),
    ('facets', List[List[int]]),
    ('dst_points', List[Point]),
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
    Point(1, 2/3)
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


def get_root() -> Path:
    return Path(__file__).resolve().parent / '..'


def get_problem_file(name: str) -> Path:
    return get_root() / 'problems' / '{}.txt'.format(name)

def get_solution_file(name: str) -> Path:
    return get_root() / 'solutions' / 'solved_{}.txt'.format(name)


def load_problem(name: str) -> Problem:
    with get_problem_file(name).open('r') as f:
        data = f.read()
        return parse_problem(data)


def solution_to_str(sol: Solution) -> str:
    lines = []
    lines.append(str(len(sol.orig_points)))
    for pt in sol.orig_points:
        lines.append('{},{}'.format(pt.x, pt.y))
    lines.append(str(len(sol.facets)))
    for facet in sol.facets:
        lines.append(' '.join(map(str, [len(facet)] + facet)))
    assert len(sol.orig_points) == len(sol.dst_points)
    for pt in sol.dst_points:
        lines.append('{},{}'.format(pt.x, pt.y))

    return '\n'.join(lines)


def solution_size(s: str) -> int:
    r"""
    >>> solution_size('1, 2\n3')
    4
    """
    assert isinstance(s, str)
    return sum(1 for c in s if not c.isspace())


def parse_solution(s: str) -> Solution:
    lines = iter(line for line in s.splitlines() if line.strip())

    num_points = int(next(lines))
    orig_points = []
    for _ in range(num_points):
        orig_points.append(parse_point(next(lines)))

    num_facets = int(next(lines))
    facets = []
    for _ in range(num_facets):
        facet = list(map(int, next(lines).split()))
        assert facet[0] == len(facet) - 1
        facets.append(facet[1:])

    dst_points = []
    for _ in range(num_points):
        dst_points.append(parse_point(next(lines)))

    return Solution(orig_points, facets, dst_points)


def center_problem(problem: Problem) -> Problem:
    sx, sy, cnt = Fraction(0), Fraction(0), 0
    for f in problem.silhouette:
        for p in f:
            sx += p.x
            sy += p.y
            cnt += 1
    sx = sx / cnt - Fraction(1,2)
    sy = sy / cnt - Fraction(1,2)
    return Problem(
            [[Point(p.x - sx, p.y - sy) for p in f] for f in problem.silhouette],
            [(Point(p1.x - sx, p1.y - sy), Point(p2.x - sx, p2.y - sy)) for p1, p2 in problem.skeleton])
