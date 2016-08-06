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
    appr = aas.GridAreaApproximator(
        200,
        [unitsq, triangle1, triangle2, triangle3],
        [
            aas.Matcher.Area(0), aas.Matcher.Area(1), aas.Matcher.Area(2),
            aas.Matcher.And(1, 2), aas.Matcher.Or(1, 2),
            aas.Matcher.And(1, 3), aas.Matcher.Or(1, 3),
        ],
    )
    print(appr.approximate())


if __name__ == "__main__":
    main()
