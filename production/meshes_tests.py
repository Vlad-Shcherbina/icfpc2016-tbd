#!/bin/env python3

from production.cg import Point
from production.meshes import subdivide_edges


def test_subdivide_edges():
    edges = [
        (Point(0, 0), Point(0, 10)),
        (Point(0, 3), Point(4, 5)),
    ]

    expected_edges = [
        (Point(0, 0), Point(0, 3)),
        (Point(0, 3), Point(0, 10)),
        (Point(0, 3), Point(4, 5)),
    ]

    assert sorted(subdivide_edges(edges)) == sorted(expected_edges)


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
