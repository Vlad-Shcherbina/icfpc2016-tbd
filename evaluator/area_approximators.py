from fractions import Fraction

from production import cg

class Matcher:
    """
    Helper class used for evaluation optimization.

    An approximator recieves a polygon list and a matcher list before
    evaluation. The polygon numbers are 0-based indices in the initial polygon
    list.

    A matcher represents our interest in an approximation to be made by an
    approximator.

    Can be one of:
        * Matcher.Area(poly_num): tells the approximator to compute the area of
          the polygon #`poly_num`.
        * Matcher.And(poly_num1, poly_num2): tells the approximator to compute
          the intersection area of the polygons #`poly_num1` and `poly_num2`.
        * Matcher.Or(poly_num1, poly_num2): tells the approximator to compute
          the union area of the polygons #`poly_num1` and `poly_num2`.
    """

    AREA = 0
    AND = 1
    OR = 2

    def __init__(self, matcher_type, num1, num2=None):
        self.matcher_type = matcher_type
        self.num1 = num1
        self.num2 = num2

    def decision(self, polygon_decisions):
        if self.matcher_type == self.AREA:
            return polygon_decisions[self.num1]
        elif self.matcher_type == self.AND:
            return polygon_decisions[self.num1] and polygon_decisions[self.num2]
        elif self.matcher_type == self.OR:
            return polygon_decisions[self.num1] or polygon_decisions[self.num2]

    @classmethod
    def Area(cls, poly_num):
        return cls(cls.AREA, poly_num)

    @classmethod
    def And(cls, poly_num1, poly_num2):
        return cls(cls.AND, poly_num1, poly_num2)

    @classmethod
    def Or(cls, poly_num1, poly_num2):
        return cls(cls.OR, poly_num1, poly_num2)

class GridAreaApproximator:
    """
    Approximates the areas of polygons inside the unit square.

    The results are set according to the `matchers` parameter.
    """

    def __init__(self, points, polys, matchers):
        self.points = points
        self.polys = polys
        self.poly_edges = [list(zip(poly, poly[1:] + poly[:1]))
                           for poly in polys]
        self.matchers = matchers
        self.answers = [0] * len(self.matchers)

    def approximate(self):
        for x in range(self.points):
            for y in range(self.points):
                pt = cg.Point(Fraction(x, self.points),
                              Fraction(y, self.points))
                decisions = []
                for edges, poly in zip(self.poly_edges, self.polys):
                    if any(cg.is_point_on_edge(pt, edge) for edge in edges):
                        decisions.append(True)
                        continue
                    decisions.append(bool(cg.count_revolutions(pt, poly)))
                for answer_id, matcher in enumerate(self.matchers):
                    if matcher.decision(decisions):
                        self.answers[answer_id] += 1
        return [self.points_to_area(answer) for answer in self.answers]

    def points_to_area(self, matching_points):
        return matching_points * 1.0 / (self.points * self.points)
