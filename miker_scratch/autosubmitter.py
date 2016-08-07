from production import api_wrapper as api
from production.origami_fold import write_fold

from random_fold import RandomFolder, render_png

import shutil, datetime
rename_file = shutil.move

import re

_re_space = re.compile(r'\s*')

rfl = RandomFolder(count=9)

def gen():
	while True:
		yield rfl.random_fold()
	
ts_step = 3600
min_ts = 1470441600 + 25 * ts_step
max_ts = min_ts + 24 * ts_step + 1
#max_ts = min_ts + 1

tmp_fname = '/tmp/autosubmitter.tmpfile'
max_size = 2500

png_size = 480

def main(for_real=False):
	g = gen()
	
	for ts in range(min_ts, max_ts, ts_step):
		while True:
			polys = next(g)
			print('.')
			
			
			with open(tmp_fname, 'w') as f:
				write_fold(polys, f)
				
			with open(tmp_fname, 'r') as f:
				f.seek(0)	
				data = f.read()
			
			l = len(_re_space.sub('', data))
			if l > max_size:
				continue
			
			try:	
				if for_real:
					r = api.submit_problem(ts, tmp_fname)
					j = r.json()
				else:
					j = {'problem_id': 0}
			except Exception as e:
				print(e)
				break
			
			pid = j['problem_id']
			new_fname_base = 'solutions/subm_{}_{}'.format(ts, pid)
			rename_file(tmp_fname, new_fname_base + '.txt')
			render_png(polys, new_fname_base + '.png', png_size=png_size)
			render_png(polys, new_fname_base + '_tr.png', True, png_size=png_size)
			
			print('submitted {} for {} of length {}'.format(pid, repr(datetime.datetime.utcfromtimestamp(ts)), l))
			
			break
	
	
	



if __name__ == '__main__':
	main()
	
