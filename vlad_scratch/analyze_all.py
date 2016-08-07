import glob
import os
import re
import traceback
import time
import random

from production import ioformats
from production import render
from production import meshes
from production import search


def enumerate_all_problems():
    path = os.path.join(__file__, '..', '..', 'problems', '*.txt')
    path = os.path.normpath(path)
    print(path)

    for filename in sorted(glob.glob(path)):
        m = re.search(r'(\d{5}).txt', os.path.basename(filename))
        if m is None:
            continue

        n = int(m.group(1))

        #if n != 1714:
        #    continue

        with open(filename) as fin:
            try:
                problem = ioformats.parse_problem(fin.read())
            except:
                print('problem', m.group(1))
                traceback.print_exc()
                continue

            yield n, problem


def main():
    cnt = 0
    problems = list(enumerate_all_problems())
    random.shuffle(problems)

    for i, p in problems:
        cnt += 1
        #print(i, len(repr(p)))
        facets = meshes.reconstruct_facets(p)
        #print(list(map(len, facets)))
        facets = meshes.keep_real_facets(facets, p)


        t = time.time()

        try:
            m = meshes.Mesh(p)
            m.precompute_span_templates()
            qq = sum(map(len, m.span_templates.values()))

            #extra = str(qq)

            borders = search.find_all_borders(m)
            perimeters = list(search.find_perimeters(m, borders))
            extra = '{:>4}, {:>4}'.format(len(borders), len(perimeters))
        except meshes.TooHardError as e:
            extra = str(e)

        t = time.time() - t


        #print(list(map(len, facets)))
        print('{:>6} {:6} {:10.2}  |    {}'.format(i, len(facets), t, extra))
        #print()

    print(cnt, 'problems total')
    #im = render.render_polys_and_edges(
    #    problem.silhouette, problem.skeleton)
    #im.save('{}.png'.format(m.group(1)))



if __name__ == '__main__':
    main()
