"""
Find a convex hull for a set of points
"""

from math import sqrt

from production import cg, ioformats
import production.origami_fold as of

import argparse

#convex_hull :: [Point] -> [Point]
def convex_hull(points_list):
    '''
    The resulting convex hull is a list of points (counter-clockwise),
    in O(n log n)
    '''

    points_sorted = sorted(set(points_list))

    if len(points_sorted) <= 1:
        return points_sorted

    lower = []
    for p in points_sorted:
        while len(lower) >= 2 and (lower[-1] - lower[-2]).cross(p - lower[-2]) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points_sorted):
        while len(upper) >= 2 and (upper[-1] - upper[-2]).cross(p - upper[-2]) <= 0:
            upper.pop()

        upper.append(p)

    # Throw away the last point of each half-hull as it's repeated at the beginning of the other one. 
    return lower[:-1] + upper[:-1]

# fold_to_convex_hull :: [polygon] -> convex hull edges -> [polygon]
# fold_to_convex_hull :: [[Point]] -> [Edge] -> [Polygon]
def fold_to_convex_hull(polys, hull_edges, folded_polys=1):
    for e in hull_edges:
        polys = of.fold(polys, e, cg.Point(cg.Fraction(1,2), cg.Fraction(1,2)))
    if len(polys) > folded_polys:
        return fold_to_convex_hull(polys, hull_edges, len(polys))
    else:
        return polys

def visualise(polys, id):
    from production.render import render_polys_and_edges

    im = render_polys_and_edges(polys, [], size=1000)
    im.save('img/ch%s.png' % id)

