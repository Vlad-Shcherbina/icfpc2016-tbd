from production.tkrender import SolutionViewer
from production.ioformats import parse_solution

sv = SolutionViewer()

for x in ["../solutions/hz07.txt", "../solutions/hz12.txt"]:
    sv.show_and_wait(parse_solution(open(x).read()))
