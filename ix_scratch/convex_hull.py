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
        x,y = p
        while len(lower) >= 2 and (lower[-1] - lower[-2]).cross(p - lower[-2]) <= 0:
            lower.pop()
        lower.append(cg.Point(cg.Fraction(x), cg.Fraction(y)))

    upper = []
    for p in reversed(points_sorted):
        x,y = p
        while len(upper) >= 2 and (upper[-1] - upper[-2]).cross(p - upper[-2]) <= 0:
            upper.pop()

        upper.append(cg.Point(cg.Fraction(x), cg.Fraction(y)))

    # Throw away the last point of each half-hull as it's repeated at the beginning of the other one. 
    return lower[:-1] + upper[:-1]

# fold_to_convex_hull :: [polygon] -> convex hull edges -> [polygon]
# fold_to_convex_hull :: [[Point]] -> [Edge] -> [Polygon]
def fold_to_convex_hull(polys, hull_edges, folded_polys=1):
    i = 0
    l = len(hull_edges)
    for e in hull_edges:
        next_e = hull_edges[i+1 if i < (l-1) else 0]
        ref_p = next_e.p1
        print(str(folded_polys) + '-' + str(i+1))
        if i == 0 and folded_polys == 8:
            print (polys)
            print(e)
            print(ref_p)
        polys = of.fold(polys, e, ref_p)
        trpts = [p.trans_points for p in polys]
        visualise(trpts, str(folded_polys) + '-' + str(i+1) + 'partial')
        i += 1

    if len(polys) > folded_polys:
        return fold_to_convex_hull(polys, hull_edges, len(polys))
    else:
        return polys

def visualise(polys, id):
    from production.render import render_polys_and_edges

    im = render_polys_and_edges(polys, [], size=1000)
    im.save('img/ch%s.png' % id)

