from production import render
from production.cg import Point
from production import ioformats
from production.origami_fold import fold, write_fold, unitsq_f, Edge, polygon_points
from fractions import Fraction
import random
import itertools

def get_points(poly):
    return list(itertools.chain.from_iterable(poly.edges))

def make_flap(poly, i, flap_size, delta_fold_width):
    points = get_points(poly)
    botl = min(points, key=lambda p: (p.y, p.x))
    delta = 0 if i else flap_size
    delta += delta_fold_width * i
    return Edge(Point(botl.x + delta + flap_size, botl.y),
                Point(botl.x + delta, botl.y + 1))

def fold_at_45(polys, eps=Fraction(-1, 2)):
    points = get_points(polys[-1])
    botr = min(points, key=lambda p: (p.y, -p.x))
    return fold(polys, Edge(Point(botr.x - 1, botr.y + eps),
                            Point(botr.x, botr.y + 1 + eps)))

def fold_at_3_4(polys, eps=Fraction(-1, 2)):
    points = get_points(polys[-1])
    botr = min(points, key=lambda p: (p.y, -p.x))
    return fold(polys, Edge(Point(botr.x - 1, botr.y + eps),
                            Point(botr.x + 3, botr.y + 1 + eps + 4)))

# def fold_at_3_4_2(polys):
#     # eps = Fraction(1, 50) # tweek me for 3/4 rot
#     eps = Fraction(1, 6) 
#     return fold(polys, Edge(Point(Fraction(1), Fraction(1, 2) + eps),
#                             Point(Fraction(3, 2) + 3, Fraction(0) + eps + 4)))


def fold_at_45_2(polys):
    # eps = Fraction(1, 50) # 1st submission
    # eps = Fraction(1, 5) # TWEEK HERE
    # eps = Fraction(97, 800) # just touch
    eps = Fraction(96, 800) # TWEEK HERE
    return fold(polys, Edge(Point(Fraction(1), Fraction(1, 2) + eps),
                            Point(Fraction(3, 2), Fraction(0) + eps)))

def quadratic_skeleton(n):
    flap_size = Fraction(1, n + 4)
    delta_fold_width = flap_size / (2 * n ** 2)
    polys = [unitsq_f()]
    print(polys[-1])
    for i in range(n):
        e = make_flap(polys[-1], i, flap_size, delta_fold_width)
        polys = fold(polys, e)
    # polys = fold_at_45(polys)
    polys = fold_at_3_4(polys)
    # polys = fold_at_3_4_2(polys)
    polys = fold_at_45_2(polys)
    return polys

if __name__ == '__main__':
    from production.render import render_polys_and_edges

    sizes = []
    # for i in range(1, 15):
    for i in [10]:
        polys = quadratic_skeleton(n=i)
        print('*' * 50)
        res = write_fold(polys)
        print('*' * 50)
        # x = ioformats.solution_to_str(res)
        size = ioformats.solution_size(ioformats.solution_to_str(res))
        sizes.append((i, size))
        print('size {}'.format(size))
        
        im = render.render_solution(res, size=2000)
        im.save('img/x{:>02}.png'.format(i))

    for i, size in sizes:
        print('{:>02}: {:>5}'.format(i, size))
    
