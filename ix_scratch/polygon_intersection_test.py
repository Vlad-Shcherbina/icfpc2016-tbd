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
        e = of.Edge(p[2], p[10])
        self.assertFalse(plg.dissect(e))

    def test_2(self):        
        plg = bigger_square()
        p = points()
        e = of.Edge(p[16], p[3])
        self.assertFalse(plg.dissect(e))

    def test_3(self):
        plg = bigger_square()
        p = points()
        e = of.Edge(p[0], p[1])
        self.assertFalse(plg.dissect(e))

    def test_4(self):
        plg = bigger_square()
        p = points()
        e = of.Edge(p[1], p[2])
        self.assertTrue(plg.dissect(e))
        
    def test_5(self):
        plg = bigger_square()
        p = points()
        e = of.Edge(p[1], p[3])
        self.assertTrue(plg.dissect(e))
        
    def test_6(self):
        plg = bigger_square()
        p = points()
        e = of.Edge(p[15], p[6])
        self.assertTrue(plg.dissect(e))

    def test_7(self):
        plg = bigger_square()
        p = points()
        e = of.Edge(p[15], p[6])
        self.assertTrue(plg.dissect(e))

    def test_8(self):
        plg = pentagon()
        p = points()
        e = of.Edge(p[3], p[6])
        self.assertFalse(plg.dissect(e))

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
    (7, 2)     #p16
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
