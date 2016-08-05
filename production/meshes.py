import pprint
from typing import List, Tuple
from fractions import Fraction

from production import cg
from production.cg import Point
from production import ioformats
from production import render


def subdivide_edges(
        edges: List[Tuple[Point, Point]]) -> List[Tuple[Point, Point]]:
    """
    After subdivision for any pair of edges they either do not have
    any points in common, or they have an endpoint in common.
    """
    result = []
    for edge in edges:
        points = set(edge)
        for e2 in edges:
            pt = cg.edge_intersection(edge, e2)
            if pt is not None:
                points.add(pt)
        points = sorted(points)
        assert len(points) >= 2
        result.extend(zip(points[:-1], points[1:]))
    return result


def reconstruct_facets(problem: ioformats.Problem) -> List[List[Point]]:
    """Return list of faces corresponding to smallest pieces possible.

    This set of facets covers the whole plane and is topologically equivalent
    to a sphere. Most of the facets will be CCW and one facet that corresponds
    to the infinite area outside will be CW.
    """

    adjacent = {}

    for edge in subdivide_edges(problem.skeleton):
        for pt1, pt2 in edge, edge[::-1]:
            adjacent.setdefault(pt1, []).append(pt2)

    for center_pt, v in adjacent.items():
        v.sort(key=lambda pt: cg.rational_angle(pt - center_pt))

    def next_in_facet(e):
        pt1, pt2 = e
        pts = adjacent[pt2]
        i = pts.index(pt1)  # TODO: quadratic complexity
        return (pt2, pts[(i - 1) % len(pts)])

    facets = []

    visited = set()
    for start_pt1, v in adjacent.items():
        for start_pt2 in v:
            e = start_pt1, start_pt2
            if e in visited:
                continue

            facets.append([])
            e2 = e
            while True:
                facets[-1].append(e2[0])

                assert e2 not in visited
                visited.add(e2)

                e2 = next_in_facet(e2)
                if e2 == e:
                    break

    return facets


def gen_point_in_facet(facet):
    assert len(facet) >= 3
    assert cg.polygon_area(facet) > 0

    d = facet[1] - facet[0]
    orth = Point(-d.y, d.x)
    m = facet[0] + d * Fraction(1, 2)

    # TODO: can fail if point happens to bo in the border
    for i in range(10, 10000):
        pt = m + orth * Fraction(1, 2**i)
        if cg.count_revolutions(pt, facet) == 1:
            return pt
    assert False, facet


def keep_real_facets(facets, problem):
    result = []
    for facet in facets:
        a = cg.polygon_area(facet)
        assert a != 0
        if a < 0:
            continue

        pt = gen_point_in_facet(facet)
        cnt = 0
        for silh_poly in problem.silhouette:
            a = cg.polygon_area(silh_poly)
            assert a != 0
            if a > 0:
                sign = 1
            else:
                sign = -1
            cnt += sign * cg.count_revolutions(pt, silh_poly)
        assert cnt in (0, 1)
        if cnt:
            result.append(facet)

    return result


def main():  # pragma: no cover
    p = ioformats.load_problem('problem95')
    facets = reconstruct_facets(p)
    print(list(map(len, facets)))

    facets = keep_real_facets(facets, p)
    print(list(map(len, facets)))

    im = render.render_polys_and_edges(facets, [])
    im.save('hz2.png')


if __name__ == '__main__':
    main()
