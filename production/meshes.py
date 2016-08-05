import pprint
from typing import List, Tuple

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


def main():  # pragma: no cover
    p = ioformats.load_problem('problem95')

    print(len(p.skeleton))
    pprint.pprint(p.skeleton)

    basic_edges = subdivide_edges(p.skeleton)
    print(len(basic_edges))
    pprint.pprint(basic_edges)

    im = render.render_polys_and_edges([], basic_edges)
    im.save('hz2.png')


if __name__ == '__main__':
    main()
