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

	def __repr__(self):
		return 'Edge(%r, %r)' % self
	
	@memoized_property
	def r0(self):
		return self.p1
		
	@memoized_property
	def a(self):
		return self.p2 - self.p1
		
	def transform(self, at):
		return Edge(at.transform(self.p1), at.transform(self.p2))
	
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
		
	@property
	def is_zero(self):
		a = self.a
		ax = a.x; ay = a.y
		return ax == 0 and ay == 0
		
		
Polygon = NamedTuple('Polygon', [('edges', List[Edge])])
class Polygon(Polygon):
		
	transform = cg.AffineTransform.identity()
		
	# def __init__(self, *args, **kwargs):
		# if 'transform' in kwargs:
			# self.transform = kwargs.pop('transform')
		# super().__init__(*args, **kwargs)
		
	def dissect(self, e_dis):
		# apply transform to dissector line
		transform = self.transform
		e_dis = e_dis.transform(transform)
	
		# find intersections with edges
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
				e_new = Edge(e.p1, p1)
				if not e.is_zero:
					es.append(e_new)
				
				if es is es1:
					es.append(Edge(p1, p2))
					es = es2
				else:
					es.append(Edge(p2, p1))
					es = es1
					
				e_new = Edge(p1, e.p2)
				if not e_new.is_zero:
					es.append(e_new)
			else:
				es.append(e)
		
		def spawn_polygon(es):
			poly = Polygon(es)
			poly.transform = transform
			return poly
		
		return spawn_polygon(es1), spawn_polygon(es2)
		
		
		
def fold(polys, e_dis):
	ret_polys = []
	for poly in polys:
		ret = poly.dissect(e_dis)
		if not ret:
			ret_polys.append(poly)
			continue
			
		poly1, poly2 = ret
		poly2.transform = poly2.transform @ cg.AffineTransform.mirror(*e_dis)
		
		ret_polys.append(poly1)
		ret_polys.append(poly2)
	
	return ret_polys


def make_point(t):
	c1, c2 = t
	return Point(Fraction(c1), Fraction(c2))

def make_points(pnts):
	return list(map(make_point, pnts))
	
def make_poly(pnts):
	return Polygon(list(map(lambda t:Edge(*t), zip(pnts, pnts[1:] + [pnts[0]]))))

	
pnts = make_points([
	(0, 0),
	(1, 0),
	(0.5, 0.5),
	(0.5, -0.5)
])

e1 = Edge(pnts[0], pnts[1])
e2 = Edge(pnts[2], pnts[3])

pnts_unitsq = make_points([
	(0, 0),
	(0, 1),
	(1, 1),
	(1, 0)
])

unitsq = make_poly(pnts_unitsq)

