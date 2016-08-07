import sys
from ast import literal_eval

from production.tkrender import SolutionViewer
from production.ioformats import *
from production.bbfold import foldgrid

# sv = SolutionViewer()
# 
# s = foldgrid(Fraction(0), Fraction(0), Fraction(7, 16), Fraction(15, 16))
# # s = foldgrid(Fraction(0), Fraction(0), Fraction(1), Fraction(1, 3))
# # print(s)
# 
# while sv.show_and_wait(s):
#     break
#     s = foldgrid(Fraction(1/29), Fraction(1/29), Fraction(30, 29), Fraction(15, 16))
# #     print(s)
# #     print('Here we can refine the solution')

print(literal_eval('1, 2'))