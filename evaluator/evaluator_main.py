from evaluator import area_approximators as aas

import miker_scratch.origami_fold as of


def main():
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


if __name__ == "__main__":
    main()
