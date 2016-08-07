"""
Find a convex hull for a set of points
"""

from production import cg, ioformats

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

def visualize():
    from production.render import render_polys_and_edges
    i = '00034'
    poly = ioformats.load_problem(i).silhouette[0]
    hull = convex_hull(poly)

    im = render_polys_and_edges([poly, hull], [], size=1000)
    im.save('img/ch%s.png' % i)


if __name__ == '__main__':
    visualize()
