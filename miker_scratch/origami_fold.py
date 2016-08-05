from production import cg
from production.cg import Point

from typing import NamedTuple, List, Tuple, Optional
# from memoized_property import memoized_property

from fractions import Fraction

memoized_property = property



def mult_vector(p, n):
	return Point(p.x * n, p.y * n)

Edge = NamedTuple('Edge', [('p1', Point), ('p2', Point)])
class Edge(Edge):
	
	@memoized_property
	def r0(self):
		return self.p1
		
	@memoized_property
	def a(self):
		return self.p2 - self.p1
	
	def _intersects(self, e):
		p1, p2 = self.r0, e.r0		# radius-vector to the first end point
		a1, a2 = self.a, e.a		# direction vector with module equal to edge length
		p = p2 - p1
		d = a1.x * (-a2.y) - a1.y * (-a2.x)	# Cramer's method
		
		if d == 0:
			return False
		
		d1 = p.x * (-a2.y) - p.y * (-a2.x)
		d2 = a1.x * p.y - a1.y * p.x
		
		t1 = d1 / d
		t2 = d2 / d
		
		return t1, t2
		
	def intersects_with_line(self, e):
		t = self._intersects(e)
		if t is False:
			return False
			
		t1, t2 = t
		
		if t1 < 0 or t1 > 1:
			return False		# outside edge boundary
			
		return self.r0 + mult_vector(self.a, t1)
		
Polygon = NamedTuple('Polygon', [('edges', List[Edge])])
class Polygon(Polygon):
		
	def dissect_polygon(e_dis):
		ps = []
		for e in self.edges:
			p = e.intersects_with_line(e_dis)
			if p:
				ps.append((p, e))
				
		if len(ps) < 2: 
			return False
			
		p1, e1 = ps[0]
		p2, e2 = ps[1]
		
		es1, es2 = [], []
		es = es1
		for e in self.edges:
			if (e is e1) or (e is es2):
				es.append(Edge(e.p1, p1))
				
				if es is es1:
					es.append(Edge(p1, p2))
					es = es2
				else:
					es.append(Edge(p2, p1))
					es = es1
					
				es.append(Edge(p1, e.p2))
			else:
				es.append(e)
		
		return Polygon(es1), Polygon(es2)
		
		
pnts = [
	(0, 0),
	(1, 0),
	(0.5, 0.5),
	(0.5, -0.5)
]

def make_point(t):
	c1, c2 = t
	return Point(Fraction(c1), Fraction(c2))
	
pnts = list(map(make_point, pnts))

e1 = Edge(pnts[0], pnts[1])
e2 = Edge(pnts[2], pnts[3])
