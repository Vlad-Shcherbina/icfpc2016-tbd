from origami_fold import *

import random, types


class RandomFolder(types.SimpleNamespace):
	
	spread = 10 # int
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
		
		
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Random fold generator.')
	parser.add_argument('-n', '--count', metavar='N', dest="count", type=int, help='target polygon count (not less than)')
	args = parser.parse_args()
	
	rfl = RandomFolder(**{k: v for k, v in args.__dict__.items() if v is not None})
	fold = rfl.random_fold()
	write_fold(fold)
	
