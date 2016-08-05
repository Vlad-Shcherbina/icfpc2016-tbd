from production.tkrender import SolutionViewer
from production.ioformats import *
from production.bbfold import foldgrid

sv = SolutionViewer()

s = foldgrid(Fraction(7, 16), Fraction(3, 16))
# s = foldgrid(Fraction(1/2), Fraction(1))
print(s)

while sv.show_and_wait(s):
    print('Here we can refine the solution')