"""
Chose a rectangle shape maximizing the jaccard index.
"""

import random

from fractions import Fraction
from typing import NamedTuple, List, Tuple, Optional
from production import cg
from production.cg import Point

def bounding_box(poly: List[Point]) -> List[int]:
    """Return the bounding box for a polygon"""
    min_x = min(poly, key=lambda p: p.x).x
    max_x = max(poly, key=lambda p: p.x).x
    min_y = min(poly, key=lambda p: p.y).y
    max_y = max(poly, key=lambda p: p.y).y
    return (min_x, max_x, min_y, max_y)

def random_points(min_x, max_x, min_y, max_y):
    """Generate random points in the given area"""
    while True:
        yield(Point(random.uniform(min_x, max_x),
                    random.uniform(min_y, max_y)))

def get_sample_points(poly: List[Point], point_count: int) -> List[Point]:
    """Return a list of points inside the polygon"""
    points = []
    for point in random_points(*bounding_box(poly)):
        if not point_count: break
        if cg.count_revolutions(point, poly) == 1:
            points.append(point)
        point_count -= 1
    return points

def compute_intersection(rect: Tuple[int], points: List[Point]) -> int:
    """Return the number of points inside a shape
    (at first shape will always be a rectangle)"""
    count = 0
    for point in points:
        if rect[0] < point.x < rect[2] and rect[1] < point.y < rect[3]:
            count += 1
    return count

def score_rect(rect: Tuple[int], points: List[Point], poly_area: float, area_by_point: float) -> float:
    """Return an approximate jaccard score for a rect
    rect: (x1, y1, x2, y2)
    """
    rect_area = abs((rect[0] - rect[2]) * (rect[1] - rect[3]))
    inter_area = compute_intersection(rect, points) * area_by_point
    jaccard = inter_area / (rect_area + poly_area - inter_area)
    return jaccard

def rand_rect(min_x, max_x, min_y, max_y):
    xs = sorted([random.uniform(min_x, max_x), random.uniform(min_x, max_x)])
    ys = sorted([random.uniform(min_y, max_y), random.uniform(min_y, max_y)])
    return (xs[0], ys[0], xs[1], ys[1])

def chose_rect(poly: List[Point], sample_size: int = 1000, round_count: int = 1000, incremental_step_coef: int = 100) -> Tuple[Point]:
    """Return a "best fit" grid alligned rectangle for the polygon"""
    box = bounding_box(poly)
    min_x, max_x, min_y, max_y = box
    bounding_box_area = abs((max_x - min_x) * (max_y - min_y))
    points = get_sample_points(poly, sample_size)
    area_by_point = bounding_box_area / sample_size
    poly_area = cg.polygon_area(poly)
    rect = (min_x, min_y, max_x, max_y)
    for _ in range(round_count):
        delta_x = (rect[2] - rect[0]) / incremental_step_coef
        delta_y = (rect[3] - rect[1]) / incremental_step_coef
        rects = (
            # current best
            rect,
            # random exploration
            # rand_rect(*box),
            # incrementally narrow the rect
            (rect[0] + delta_x, rect[1], rect[2], rect[3]),
            (rect[0], rect[1], rect[2] - delta_x, rect[3]),
            (rect[0], rect[1] + delta_y, rect[2], rect[3]),
            (rect[0], rect[1], rect[2], rect[3] - delta_y),
            # incrementally enlarge the rect
            (rect[0] - delta_x, rect[1], rect[2], rect[3]),
            (rect[0], rect[1], rect[2] + delta_x, rect[3]),
            (rect[0], rect[1] - delta_y, rect[2], rect[3]),
            (rect[0], rect[1], rect[2], rect[3] + delta_y)
        )
        rect = max(rects, key=lambda r: score_rect(r, points, poly_area, area_by_point))
        # print(score_rect(rect, points, poly_area, area_by_point))
    print(score_rect(rect, points, poly_area, area_by_point))
    rect = (max(0, rect[0]), max(0, rect[1]), min(1, rect[2]), min(1, rect[3]))
    return [
        Point(Fraction(rect[0]), Fraction(rect[1])),
        Point(Fraction(rect[0]), Fraction(rect[3])),
        Point(Fraction(rect[2]), Fraction(rect[3])),
        Point(Fraction(rect[2]), Fraction(rect[1]))
    ]
    
def visualize(argv):
    from production.render import render_polys_and_edges
    from production.ioformats import load_problem
    poly = load_problem("013").silhouette[0]
    # poly = [Point(0, 0), Point(0, -20), Point (0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    rect = chose_rect(poly, sample_size=1000, round_count=100)
    print(rect)
    im = render_polys_and_edges([poly, rect], [], size=1000)
    im.save('x.png')
    

if __name__ == '__main__':
    import sys
    visualize(sys.argv)
