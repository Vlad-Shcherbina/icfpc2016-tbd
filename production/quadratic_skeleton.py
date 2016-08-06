from production import render
from production.cg import Point
from production import ioformats
from production.origami_fold import fold, write_fold, unitsq, Edge, polygon_points
from fractions import Fraction
import random
import itertools

def get_points(poly):
    return list(itertools.chain.from_iterable(poly.edges))

def make_flap(poly, i, flap_size):
    points = get_points(poly)
    delta = i * flap_size / 10
    
    botl = min(points, key=lambda p: (p.y, p.x))
    return Edge(Point(botl.x + i * flap_size + 2 * delta, botl.y),
                Point(botl.x + i * flap_size + delta, botl.y + 1))

def fold_at_45(polys):
    points = get_points(polys[-1])
    botl = min(points, key=lambda p: (p.y, p.x))
    rtop = max(points, key=lambda p: (p.x, p.y))
    return fold(polys, Edge(Point(botl.x, (botl.y + rtop.y) / 2), rtop))

def quadratic_skeleton(n=10, flap_size=Fraction(1, 100)):
    polys = [unitsq]
    print(polys[-1])
    for i in range(n):
        e = make_flap(polys[-1], i, flap_size)
        polys = fold(polys, e)
    # 45 degre fold
    polys = fold_at_45(polys)
    return polys

if __name__ == '__main__':
    from production.render import render_polys_and_edges
    fold = quadratic_skeleton()
    res = write_fold(fold)
    # x = ioformats.solution_to_str(res)
    
    im = render.render_solution(res, size=2000)
    im.save('img/x.png')
