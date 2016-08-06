from sys import argv

from evaluator import area_approximators as aas
from production import cg, ioformats

import miker_scratch.origami_fold as of


def evaluate_solution(sol_num):
    print('Evaluating solution #%d' % sol_num)
    polys = []
    matchers = []
    prob_matchers = []
    with open('problems/%03d.txt' % sol_num) as inf:
        prob_polys_cnt = int(inf.readline().strip())
        for poly_id in range(prob_polys_cnt):
            poly = []
            points_cnt = int(inf.readline().strip())
            for point_id in range(points_cnt):
                poly.append(ioformats.parse_point(inf.readline()))
            matcher = aas.Matcher.Area(len(polys))
            if cg.polygon_area(poly) < 0:
                matcher = aas.Matcher.Not(matcher)
            polys.append(poly)
            prob_matchers.append(matcher)
    # AND because of holes.
    prob_matcher = aas.Matcher.And(prob_matchers)
    sol_matchers = []
    with open('solutions/%03d.txt' % sol_num) as inf:
        points_cnt = int(inf.readline().strip())
        for point_id in range(points_cnt):
            inf.readline()
        sol_polys_cnt = int(inf.readline().strip())
        sol_facets = []
        for facet_id in range(sol_polys_cnt):
            sol_facets.append(list(map(int, inf.readline().strip().split(' '))))
        points = [ioformats.parse_point(inf.readline())
                  for i in range(points_cnt)]
        sol_polys = []
        for poly_id in range(sol_polys_cnt):
            poly = [points[i] for i in sol_facets[poly_id][1:]]
            append_poly_with_inclusion(sol_polys, poly)
        for poly in sol_polys:
            matcher = aas.Matcher.Area(len(polys))
            polys.append(poly)
            sol_matchers.append(matcher)
    sol_matcher = aas.Matcher.Or(sol_matchers)
    appr = aas.GridAreaApproximator(200, polys, [
        aas.Matcher.And([prob_matcher, sol_matcher]),
        aas.Matcher.Or([prob_matcher, sol_matcher]),
    ])
    values = appr.approximate()
    print(values[0] / values[1])


def append_poly_with_inclusion(polys, new_poly):
    """
    Modifies `polys` so that:
        * The union set of `polys` covers `new_poly`
        * `polys` don't contain such two polygons that one is subset of another.
    """
    new_polys = [new_poly]
    new_edges = list(zip(new_poly, new_poly[1:] + new_poly[:1]))
    for poly_id, poly in enumerate(polys):
        edges = list(zip(poly, poly[1:] + poly[:1]))
        new_poly_in_old = True
        for new_vert in new_poly:
            if (all(not cg.is_point_on_edge(new_vert, edge) for edge in edges)
                and cg.count_revolutions(new_vert, poly) == 0):
                new_poly_in_old = False
                break
        if new_poly_in_old:
            return
        for vert in poly:
            if (all(not cg.is_point_on_edge(vert, edge) for edge in new_edges)
                and cg.count_revolutions(vert, new_poly) == 0):
                new_polys.append(poly)
                break
    polys[:] = new_polys


def demo():
    unitsq = of.make_points([
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0)
    ])
    triangle1 = of.make_points([
        (0, 0),
        (0, 1),
        (1, 0)
    ])
    triangle2 = of.make_points([
        (0, 1),
        (1, 1),
        (1, 0)
    ])
    triangle3 = of.make_points([
        (0, 0),
        (1, 1),
        (1, 0)
    ])
    half_square = of.make_points([
        (0, 1),
        (1, 1),
        (1, 0.5),
        (0, 0.5),
    ])
    m_sq = aas.Matcher.Area(0)
    m_tr1 = aas.Matcher.Area(1)
    m_tr2 = aas.Matcher.Area(2)
    m_tr3 = aas.Matcher.Area(3)
    m_half = aas.Matcher.Area(4)
    m_tr1_union_tr3 = aas.Matcher.Or([m_tr1, m_tr3])
    appr = aas.GridAreaApproximator(
        200,
        [unitsq, triangle1, triangle2, triangle3, half_square],
        [
            m_sq, m_tr1, m_tr2,
            aas.Matcher.And([m_tr1, m_tr2]), aas.Matcher.Or([m_tr1, m_tr2]),
            aas.Matcher.And([m_tr1, m_tr3]), m_tr1_union_tr3,
            aas.Matcher.And([m_half, m_tr1_union_tr3]),
        ],
    )
    print(appr.approximate())


def main():
    sol_id = 1
    if len(argv) > 1:
        sol_id = int(argv[1])
    evaluate_solution(sol_id)


if __name__ == "__main__":
    main()
