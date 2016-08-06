from fractions import Fraction

from peluche_scratch import dummy_rectangle
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
        * Matcher.Area(poly_num): tells the approximator to include the area of
          the polygon #`poly_num`.
        * Matcher.Not(matcher): tells the approximator to exclude the area
          of the figure specified by the nested matcher.
        * Matcher.And(nested_matchers): tells the approximator to compute
          the intersection area of the figures specified by the nested matchers.
        * Matcher.Or(nested_matchers): tells the approximator to compute
          the union area of the figures specified by the nested matchers.
    """

    AREA = 0
    AND = 1
    OR = 2
    NOT = 3

    def __init__(self, matcher_type, param):
        self.matcher_type = matcher_type
        if self.matcher_type == self.AREA:
            self.num = param
        elif self.matcher_type == self.NOT:
            self.nested_matcher = param
        else:
            self.nested_matchers = param

    def decision(self, polygon_decisions):
        if self.matcher_type == self.AREA:
            return polygon_decisions[self.num]
        elif self.matcher_type == self.AND:
            return all(matcher.decision(polygon_decisions) for
                       matcher in self.nested_matchers)
        elif self.matcher_type == self.OR:
            return any(matcher.decision(polygon_decisions) for
                       matcher in self.nested_matchers)
        elif self.matcher_type == self.NOT:
            return not nested_matcher.decision(polygon_decisions)

    @classmethod
    def Area(cls, poly_num):
        return cls(cls.AREA, poly_num)

    @classmethod
    def And(cls, nested_matchers):
        return cls(cls.AND, nested_matchers)

    @classmethod
    def Or(cls, nested_matchers):
        return cls(cls.OR, nested_matchers)

    @classmethod
    def Not(cls, nested_matcher):
        return cls(cls.NOT, nested_matcher)


class GridAreaApproximator:
    """
    Approximates the areas of polygons inside their bounding box.

    The results are set according to the `matchers` parameter.
    """

    def __init__(self, points, polys, matchers):
        self.points = points
        self.polys = polys
        all_points = [point for poly in polys for point in poly]
        (self.min_x, self.max_x,
         self.min_y, self.max_y) = dummy_rectangle.bounding_box(all_points)
        self.x_spacing = (self.max_x - self.min_x) / points
        self.y_spacing = (self.max_y - self.min_y) / points
        self.poly_edges = [list(zip(poly, poly[1:] + poly[:1]))
                           for poly in polys]
        self.matchers = matchers
        self.answers = [0] * len(self.matchers)

    def approximate(self):
        for x in range(self.points):
            for y in range(self.points):
                pt = cg.Point(self.min_x + x * self.x_spacing,
                              self.min_y + y * self.y_spacing)
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
