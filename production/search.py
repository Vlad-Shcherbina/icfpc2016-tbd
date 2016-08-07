import pprint
import math

from production import ioformats
from production.meshes import Mesh



def edge_length(edge):
    d = edge[0] - edge[1]
    return math.sqrt(d.dot(d))

def find_all_borders(mesh):
    starts = {v for vs in mesh.transitions[1].values() for v in vs}

    borders = []
    for start in starts:
        path = [start]

        def rec(length):
            if length > 1 + 1e-6:
                return
            if math.isclose(length, 1) and mesh.transitions[1].get(path[-1]):
                borders.append(list(path))
                return

            if len(path) > 50:
                return

            for edge in mesh.transitions[2].get(path[-1], ()):
                path.append(edge)
                rec(length + edge_length(edge))
                path.pop()

        rec(edge_length(start))

    #pprint.pprint(starts)
    #pprint.pprint(borders)
    print(len(borders), 'borders')


def main():  # pragma: no cover
    p = ioformats.load_problem('00077')

    m = Mesh(p)
    m.debug_print()
    r = m.render()

    m.precompute_span_templates()
    for node in m.nodes:
        s = 0
        for angle in 1, 2, 4:
            if m.span_templates[node, angle]:
                s += angle
        if s != 7:
            r.draw_text(node, str(s), color=(0, 0, 255))

    r.get_img(200).save('mesh.png')

    print('*' * 20)
    find_all_borders(m)


if __name__ == '__main__':
    main()
