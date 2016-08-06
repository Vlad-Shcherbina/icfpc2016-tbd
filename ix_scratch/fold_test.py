import unittest

from production import cg
from production.cg import Point

from typing import NamedTuple, List, Tuple, Optional

from fractions import Fraction

import miker_scratch.origami_fold as of

class TestIntersections(unittest.TestCase):
    def test_1(self):        
        plg = unitsq()
        p = points()
        e1 = of.Edge(p[17], p[18])
        e2 = of.Edge(p[19], p[20])
        f1 = plg.dissect(e1)
        f2 = f1[1].dissect(e2) + (f1[0],)
        self.assertTrue(of.compare_folds(f2, of.fold(of.fold([plg], e1), e2)))

    def test_2(self):
        plg = unitsq()
        p = points()
        e1 = of.Edge(p[17], p[18])
        e2 = of.Edge(p[21], p[22])
        f1 = plg.dissect(e1)
        f2 = f1[1].dissect(e2) + (f1[0],)
        self.assertTrue(of.compare_folds(f2, of.fold(of.fold([plg], e1), e2)))

    def test_3(self):
        plg = unitsq()
        p = points()
        e1 = of.Edge(p[0], p[23])
        e2 = of.Edge(p[21], p[22])
        f2 = plg.dissect(e2)
        self.assertTrue(of.compare_folds(f2, of.fold(of.fold([plg], e1), e2)))
        

def points():
    return list(map(of.make_point, [
    (0, 0),    #p0
    (24, 3),   #p1
    (0, 4),    #p2
    (4, 5),    #p3
    (5, 1),    #p4
    (3, 10),   #p5
    (9, 5),    #p6
    (2, 10),   #p7
    (0, 10),   #p8
    (8, 10),   #p9
    (1, 12),   #p10
    (7, 12),   #p11
    (0, 12),   #p12
    (8, 12),   #p13
    (5, 0),    #p14
    (10, 6),   #p15
    (7, 2),    #p16

    (0.25,0),  #p17
    (0.25,1),  #p18
    (0.75,0),  #p19
    (0.75,1),  #p20
    (0,0.75),  #p21
    (1,0.75),  #p22

    (0,1)      #p23
]))

def unitsq():
    return of.make_poly(of.make_points([
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0)
]))

def bigger_square():
    return of.make_poly(of.make_points([
        (7, 2),
        (7, 7),
        (12, 7),
        (12, 2)
]))

def pentagon():
    return of.make_poly(of.make_points([
        (5, 11),
        (13, 9),
        (12, 5),
        (6, 5),
        (1, 5)
]))
    

if __name__ == '__main__':
    unittest.main()
