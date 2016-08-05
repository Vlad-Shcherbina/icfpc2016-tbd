import unittest

from production import cg
from production.cg import Point

from typing import NamedTuple, List, Tuple, Optional

from fractions import Fraction

import miker_scratch.origami_fold as of

class TestIntersections(unittest.TestCase):
    def test_1(self):        
        p = points()
        e1 = of.Edge(p[8], p[9])
        e2 = of.Edge(p[11], p[10])
        self.assertFalse(e1.intersects_with_line(e2))

    def test_2(self):        
        p = points()
        e1 = of.Edge(p[10], p[11])
        e2 = of.Edge(p[12], p[13])
        self.assertFalse(e1.intersects_with_line(e2))

    def test_3(self):
        p = points()
        e1 = of.Edge(p[0], p[1])
        e2 = of.Edge(p[2], p[3])
        self.assertFalse(e1.intersects_with_line(e2))

    def test_4(self):
        p = points()
        e1 = of.Edge(p[4], p[5])
        e2 = of.Edge(p[6], p[7])
        self.assertTrue(e1.intersects_with_line(e2))
        
    def test_5(self):
        p = points()
        e1 = of.Edge(p[9], p[6])
        e2 = of.Edge(p[10], p[1])
        self.assertTrue(e1.intersects_with_line(e2))
        
    def test_6(self):
        p = points()
        e1 = of.Edge(p[2], p[6])
        e2 = of.Edge(p[14], p[4])
        self.assertTrue(e1.intersects_with_line(e2))

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
    (5, 0)     #p14
]))

if __name__ == '__main__':
    unittest.main()
