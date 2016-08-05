from production.tkrender import SolutionViewer
from production.ioformats import *
from production.bbfold import foldgrid

sv = SolutionViewer()

s = foldgrid(Fraction(0), Fraction(0), Fraction(7, 16), Fraction(15, 16))
# s = foldgrid(Fraction(1/2), Fraction(1))
print(s)

while sv.show_and_wait(s):
    s = foldgrid(Fraction(1/29), Fraction(1/29), Fraction(7, 16), Fraction(15, 16))
#     print('Here we can refine the solution')
