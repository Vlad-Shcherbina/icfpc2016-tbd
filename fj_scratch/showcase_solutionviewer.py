from production.tkrender import SolutionViewer
from production.ioformats import *

sv = SolutionViewer()

orig_points = [
    Point(x=0, y=0),
    Point(x=1, y=0),
    Point(x=1, y=1),
    Point(x=0, y=1),
    Point(x=0, y=Fraction(1, 2)),
    Point(x=Fraction(1, 2), y=Fraction(1, 2)),
    Point(x=Fraction(1, 2), y=1),
]
facets = [
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [4, 5, 3],
    [5, 6, 3],
]
dst_points = [
    Point(x=0, y=0),
    Point(x=1, y=0),
    Point(x=0, y=0),
    Point(x=0, y=0),
    Point(x=0, y=Fraction(1, 2)),
    Point(x=Fraction(1, 2), y=Fraction(1, 2)),
    Point(x=0, y=Fraction(1, 2)),
]
solution = Solution(
    orig_points=orig_points,
    facets=facets,
    dst_points=dst_points)

while sv.show_and_wait(solution):
    print('Here we can refine the solution')