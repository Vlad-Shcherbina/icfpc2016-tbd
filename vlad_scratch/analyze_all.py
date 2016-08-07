import glob
import os
import re
import traceback
import time

from production import ioformats
from production import render
from production import meshes


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
    for i, p in enumerate_all_problems():
        cnt += 1
        #print(i, len(repr(p)))
        facets = meshes.reconstruct_facets(p)
        #print(list(map(len, facets)))
        facets = meshes.keep_real_facets(facets, p)

        m = meshes.Mesh(p)

        t = time.time()

        m.precompute_span_templates()
        qq = sum(map(len, m.span_templates.values()))

        #for node in m.nodes:
        #    star = m.get_node_star(node)
        #    for angle in 1, 2, 4:
        #        list(meshes.generate_span_templates(
        #            star, angle, m.get_forbidden_idx(node)))


                #for span in generate_span_templates(star, angle):
                #print(' ', angle, m.describe_span_template(node, span))
        t = time.time() - t


        #print(list(map(len, facets)))
        print('{:>6} {:6} {:10} {:12.2}'.format(i, len(facets), qq, t))
        #print()

    print(cnt, 'problems total')
    #im = render.render_polys_and_edges(
    #    problem.silhouette, problem.skeleton)
    #im.save('{}.png'.format(m.group(1)))



if __name__ == '__main__':
    main()
