import argparse

from evaluator import area_approximators as aas
from production import cg, ioformats

import production.origami_fold as of



def evaluate_file(prob_id, sol_id):
    print('Evaluating solution #%s' % sol_id)
    
    with open('solutions/%s.txt' % sol_id) as f:
        sol = ioformats.parse_solution(f.read())

    prob = ioformats.load_problem(prob_id)

    return evaluate(prob, sol)

def evaluate_strings(probs, sols, sol_num=None):
    if sol_num is not None:
        print('Evaluating solution #%s' % sol_num)
  
    sol = parse_solution(sols)

    prob = ioformats.parse_problem(probs)
    
    return evaluate(prob, sol)

def evaluate_solution(prob, sol, sol_num=None):
    if sol_num is not None:
        print('Evaluating solution #%s' % sol_num)
  
    return evaluate(prob, sol)


def evaluate(prob, sol):
    polys = []
    matchers = []
    prob_matchers = []
    for poly in prob.silhouette:
        matcher = aas.Matcher.Area(len(polys))
        if cg.polygon_area(poly) < 0:
            matcher = aas.Matcher.Not(matcher)
        polys.append(poly)
        prob_matchers.append(matcher)
    # AND because of holes.
    prob_matcher = aas.Matcher.And(prob_matchers)
    sol_matchers = []
    sol_polys_cnt = len(sol.facets)
    sol_polys = []
    for f in sol.facets:
        poly = [sol.dst_points[i] for i in f]
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
    parser = argparse.ArgumentParser(description='Validate solution in a file')
    parser.add_argument(dest='prob_id')
    parser.add_argument(dest='sol_id')
    args = parser.parse_args()
    evaluate_file(args.prob_id, args.sol_id)


if __name__ == "__main__":
    main()
