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

s2 = parse_solution('''9
0,1
1/2,1
0,0
1,0
8/19,17/19
2/5,1
1,1
3/5,0
8/33,1
4
5 0 1 2 3 4
3 2 5 3
3 5 6 3
5 6 7 8 4 3
10/13,15/13
1/2,1
15/13,3/13
1,0
8/19,17/19
518/1625,1401/1625
1,1
3/5,0
6/11,35/33''')

sv2 = SolutionViewer()
sv2.show_and_wait(solution)

while sv.show_and_wait(solution):
    solution = s2
