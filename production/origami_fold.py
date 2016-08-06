
from production import ioformats
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
	
		d1 = p.x * (-a2.y) - p.y * (-a2.x)
		d2 = a1.x * p.y - a1.y * p.x
			
		if d == 0:
			if d1 == 0 and d2 == 0:
				return None  # overlay (infinite set of common points)
			else:
				return False # no common point
		
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
		
	def point_side(self, p):
		return self.a.cross(self.p1 - p)
		
		
Polygon = NamedTuple('Polygon', [('edges', List[Edge])])
class Polygon(Polygon):
		
	transform = cg.AffineTransform.identity()
	#~ inv = False
	t_number = 0
	
	@property
	def inv(self):
		return (self.t_number % 2 == 1)
		
		
	@property
	def transform(self):
		if hasattr(self, '_transform'):
			pass
		else:
			self._transform = cg.AffineTransform.identity()
		return self._transform
		
	@transform.setter
	def transform(self, t):
		self._transform = t 
		self.t_number += 1
		if hasattr(self, '_trans_points'):
			del self._trans_points
		
	@property
	def trans_points(self):
		if hasattr(self, '_trans_points'):
			pass
		else:
			t = self.transform
			self._trans_points = [t.transform(p) for p in polygon_points(self)]
		return self._trans_points 
		
	def dissect(self, e_dis):
		# apply transform to dissector line
		transform = self.transform
		e_dis = e_dis.transform(transform.inv())
	
		# find intersections with edges
		ps = []
		for e in self.edges:
			p = e.intersects_with_line(e_dis)
			if p is None:
				return False
			if p:
				ps.append((p, e))
				
		if len(ps) < 2: 
			return False
			
		p1, e1 = ps[0]
		p2, e2 = ps[1]
		
		es1, es2 = [], []
		es = es1
		for e in self.edges:
			if (e is e1) or (e is e2):
				e_new = Edge(e.p1, p1 if e is e1 else p2)
				# print('NEW top', e_new)
				if not e_new.is_zero:
					es.append(e_new)
				
				if es is es1:
					es.append(Edge(p1, p2))
					es = es2
				else:
					es.append(Edge(p2, p1))
					es = es1
					
				e_new = Edge(p1 if e is e1 else p2, e.p2)
				# print('NEW bottoms', e_new)
				if not e_new.is_zero:
					es.append(e_new)
			else:
				es.append(e)
		
		def spawn_polygon(es):
			poly = Polygon(es)
			poly.transform = transform
			poly.t_number = self.t_number
			return poly
		
		ret = (spawn_polygon(es1), spawn_polygon(es2))
		#~ 
		#~ if side(polygon_points(ret[0]), e_dis) > 0:
			#~ return (ret[1], ret[0])
		#~ else: 
			#~ return ret
		return ret
		
	
def fold(polys, e_dis, dir=0):
		
	this_transform = cg.AffineTransform.mirror(*e_dis)
	
	#~ def apply_this_transform(poly):
		#~ poly.transform = this_transform @ poly.transform
		
	ret_polys = []
	for poly in polys:
		ret = poly.dissect(e_dis)
		if not ret:
			if side(poly.trans_points, e_dis) < 0:
				poly.transform = this_transform @ poly.transform
			ret_polys.append(poly)
			continue
			
		poly1, poly2 = ret
		poly_to_transform = poly1 if side(poly1.trans_points, e_dis) < 0 else poly2 #ret[dir if not poly.inv else (1-dir)]
		poly_to_transform.transform = this_transform @ poly_to_transform.transform
		
		ret_polys.append(poly1)
		ret_polys.append(poly2)
	
	return ret_polys

	
def side(pp, e):  # we assume it's all on one side
	for p in pp:
		ret = e.point_side(p)
		if ret != 0:
			return ret
	return 0
	
	
def point_to_str(p):
	return ','.join([str(x) for x in p])

import sys, collections
def write_fold(polys, f=sys.stdout):
	polys = sorted(polys, key=lambda x:-x.t_number)  # highest transformation number goes first
	
	d = collections.OrderedDict()  # point -> polygon
	pp = [] # list of polygon point ids
	i = 0
	for poly in polys:
		ppi = []
		pp.append(ppi)
		for p in polygon_points(poly):
			if p not in d:
				d[p] = (poly, i)
				i += 1
			ppi.append(d[p][1])
					
	points = [(p, poly.transform.transform(p)) for p, (poly, i) in d.items()]  # (src, dest) points pairs
	points_src, points_dst = tuple(zip(*points))
	
	f.write('%d\n' % len(points))		# number of points
	for p in points_src:				# source point coords
		f.write(point_to_str(p)); f.write('\n')
		
	f.write('%d\n' % len(polys))		# number of polygons
	for ppi in pp:
		f.write('%d ' % len(ppi))
		f.write(' '.join(map(str, ppi)))
		f.write('\n')
					
	for p in points_dst:				# destination point coords
		f.write(point_to_str(p)); f.write('\n')
	return ioformats.Solution(orig_points=points_src, facets=pp, dst_points=points_dst)
	


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


def polygon_points(poly):
	return map(lambda e:e.p1, poly.edges)

def polygon_to_set(poly):
	return frozenset(polygon_points(poly))
	
def polygons_to_set(polys):
	return frozenset(map(polygon_to_set, polys))

def compare_folds(f1, f2):
	s1, s2 = tuple(map(polygons_to_set, (f1, f2)))
	if s1 == s2:
		return True
	
	return (s1 - s2), (s2 - s1)
