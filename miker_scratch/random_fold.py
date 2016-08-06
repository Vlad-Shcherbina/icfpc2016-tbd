from origami_fold import *

import random, types


center_point = Point(Fraction(1, 2), Fraction(1, 2))

class RandomFolder(types.SimpleNamespace):
	
	spread = 5 # int
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
		p1, p2 = r(), r()
		p2 = Point(*map(lambda x:x*Fraction(5,3), p2))
		return Edge(p1, p2)
		
	def random_fold(self, polys=None):
		if polys is None:
			polys = [unitsq]
		count = self.count
		while len(polys) < count:
			e = None
			while not e or e.is_zero:
				e = self.random_line()
			
			polys = fold(polys, e)
			
			# take a point and offset all transforms to make it a center
			p = polys[0].trans_points[0]
			offs = p - center_point
			
			for poly in polys:
				t = poly.transform
				t.offset -= offs
				poly.transform = t
			
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
