import glob
import os
import re

from production import ioformats
from production import render


def main():
    path = os.path.join(__file__, '..', '..', 'problems', '*.txt')
    path = os.path.normpath(path)
    print(path)

    for filename in glob.glob(path):
        m = re.search(r'(\d+).txt', os.path.basename(filename))
        print(filename)
        with open(filename) as fin:
            problem = ioformats.parse_problem(fin.read())
            im = render.render_polys_and_edges(
                problem.silhouette, problem.skeleton)
            im.save('{}.png'.format(m.group(1)))


if __name__ == '__main__':
    main()
