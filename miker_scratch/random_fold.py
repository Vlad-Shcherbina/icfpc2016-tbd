from origami_fold import *

import random, types


class RandomFolder(types.SimpleNamespace):
	
	spread = 2 # int
	count = 5
	
	def random_int(self):
		d = self.spread
		return int(random.random() * 2 * d - d)
	
	def random_point(self):
		r = self.random_int
		t = (r(), r())
		return make_point(t)
	
	def random_line(self):
		r = self.random_point
		t = (r(), r())
		return Edge(*t)
		
	def random_fold(self, polys=None):
		if polys is None:
			polys = [unitsq]
		count = self.count
		while len(polys) < count:
			e = None
			while not e or e.is_zero:
				e = self.random_line()
			polys = fold(polys, e)
		return polys
		
	def random_fold2(self, polys=None):
		if polys is None:
			polys = [unitsq]
		count = self.count
		
		def random_edge():
			poly = random.choice(polys)
			edge = random.choice(poly.edges)
			return edge
		
		def random_point_on_edge(e):
			rand = random.random()
			return e.r0 + Point(*map(lambda x:x*rand, e.a))
		
		while len(polys) < count:
			e1, e2 = random_edge(), random_edge()
			if e1 == e2: 
				continue
			
			p1 = random_point_on_edge(e1)
			p2 = random_point_on_edge(e2)
			
			e = Edge(p1, p2)
			
			polys = fold(polys, e)
		
		return polys
		
		
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Random fold generator.')
	parser.add_argument('-n', '--count', metavar='N', dest="count", type=int, help='target polygon count (not less than)')
	parser.add_argument('--to-png', metavar='PNG_PATH', dest="png_path", help='output png')
	parser.add_argument('--to-png-trans', metavar='PNG_PATH', dest="png_trans_path", help='output png transformed')
	parser.add_argument('--png-size', metavar='PNG_SIZE', dest="png_size", type=int, default=100, help='output png size')
	args = parser.parse_args().__dict__
	
	png_path = args.pop('png_path')
	png_trans_path = args.pop('png_trans_path')
	png_size = args.pop('png_size')
	
	rfl = RandomFolder(**{k: v for k, v in args.items() if v is not None})
	fold = rfl.random_fold()
	write_fold(fold)
	
	if png_path:
		from production.render import render_polys_and_edges
		fold_for_render = list(map(lambda x:list(polygon_points(x)), fold))
		im = render_polys_and_edges(fold_for_render, [], size=png_size)
		im.save(png_path)
	
	if png_trans_path:
		from production.render import render_polys_and_edges
		fold_for_render = list(map(lambda x:x.trans_points, fold))
		im = render_polys_and_edges(fold_for_render, [], size=png_size)
		im.save(png_trans_path)
