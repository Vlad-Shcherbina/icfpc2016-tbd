import glob
import os
import re
import traceback

from production import ioformats
from production import render


def main():
    path = os.path.join(__file__, '..', '..', 'problems', '*.txt')
    path = os.path.normpath(path)
    print(path)

    for filename in sorted(glob.glob(path)):
        m = re.search(r'(\d+).txt', os.path.basename(filename))
        print('problem', m.group(1))

        with open(filename) as fin:
            try:
                problem = ioformats.parse_problem(fin.read())
            except:
                traceback.print_exc()
                continue

            im = render.render_polys_and_edges(
                problem.silhouette, problem.skeleton, size=200)
            im.save('{}.png'.format(m.group(1)))


if __name__ == '__main__':
    main()
