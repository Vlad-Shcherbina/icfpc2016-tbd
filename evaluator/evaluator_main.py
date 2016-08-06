from evaluator import area_approximators as aas
from production import cg, ioformats

import miker_scratch.origami_fold as of


def evaluate_solution(sol_num):
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
    #TODO: detect coinciding/nested facets; it would improve
    # efficiency dramatically.
    # Should be easy: facets are convex.
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
        for poly_id in range(sol_polys_cnt):
            poly = [points[i] for i in sol_facets[poly_id][1:]]
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
    evaluate_solution(1)


if __name__ == "__main__":
    main()
