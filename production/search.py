import pprint
import math
import time

from production import ioformats
from production.meshes import Mesh, TooHardError



def edge_length(edge):
    d = edge[0] - edge[1]
    return math.sqrt(d.dot(d))

def find_all_borders(mesh):
    starts = {v for vs in mesh.transitions[1].values() for v in vs}

    finish_time = time.time() + 15

    borders = []
    for start in starts:
        path = [start]

        def rec(length):
            if time.time() > finish_time:
                raise TooHardError('border timeout')

            if length > 1 + 1e-6:
                return
            if math.isclose(length, 1) and mesh.transitions[1].get(path[-1]):
                borders.append(list(path))
                if len(borders) > 1000:
                    raise TooHardError('too many candidate borders')
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
    #print(len(borders), 'borders')
    return borders


def find_perimeters(mesh, borders):
    def can_turn(e1, e2):
        return e2 in mesh.transitions[1].get(e1, ())

    cnt = 0
    for b1 in borders:
        for b2 in borders:
            if not can_turn(b1[-1], b2[0]):
                continue
            if b1 > b2:
                continue
            for b3 in borders:
                if not can_turn(b2[-1], b3[0]):
                    continue
                for b4 in borders:
                    if not can_turn(b3[-1], b4[0]):
                        continue
                    if not can_turn(b4[-1], b1[0]):
                        continue

                    cnt += 1
                    if cnt > 1000:
                        raise TooHardError('too many candidate perimeters')

                    points = set(sum(b1 + b2 + b3 + b4, ()))
                    #print(points)
                    bad = False
                    for node in mesh.nodes:
                        if node not in points and not mesh.span_templates[node, 4]:
                            bad = True
                            break
                    if bad:
                        #print('bad')
                        continue

                    yield (b1, b2, b3, b4)


def all_substrings(xs):
    for i in range(len(xs)):
        for j in range(i + 1, len(xs) + 1):
            yield xs[i:j]


class Solver:
    def __init__(self, mesh, perimeter):
        self.mesh = mesh

        self.allowed_by_node = {node: set() for node in mesh.nodes}

        for node in mesh.nodes:
            for q in mesh.span_templates[node, 4]:
                for i in range(len(q)):
                    q = q[1:] + q[:1]
                    a = mesh.describe_span_template(node, q)
                    # TODO
                    #for j in range(len(a)):
                    #    for k in range(j + 1, len(a) + 1):
                    #        self.allowed_by_node[node].add(tuple(a[j:k]))
                    a = ['cycle'] + a + ['cycle']
                    self.allowed_by_node[node].add(tuple(a))


        def flip(a):
            return  [
                x.replace('forward', 'tmp')
                 .replace('back', 'forward')
                 .replace('tmp', 'back')
                for x in a[::-1]]

        for border_no, border in enumerate(perimeter):
            for i in range(len(border) - 1):
                node = border[i][1]
                for st in mesh.span_templates[node, 2]:
                    bone1, bone2 = mesh.span_end_bones(node, st)
                    if bone1[::-1] != border[i] or bone2 != border[i + 1]:
                        # print('uff')
                        continue

                    a = (['border_{}_{}'.format(border_no, i)] +
                         mesh.describe_span_template(node, st) +
                         ['border_{}_{}'.format(border_no, i + 1)])

                    for a in (a, flip(a)):
                        self.allowed_by_node[node].add(tuple(a))

        for border_no in range(4):
            node = perimeter[border_no][0][0]
            print(node)

            for st in mesh.span_templates[node, 1]:
                bone1, bone2 = mesh.span_end_bones(node, st)
                if (bone1[::-1] != perimeter[(border_no - 1) % 4][-1] or
                    bone2 != perimeter[border_no][0]):
                    # print('uff')
                    continue

                a = (['border_{}_{}'.format((border_no - 1) % 4, len(perimeter[(border_no - 1) % 4]) - 1)] +
                     mesh.describe_span_template(node, st) +
                     ['border_{}_{}'.format(border_no, 0)])

                for a in (a, flip(a)):
                    self.allowed_by_node[node].add(tuple(a))

        pprint.pprint(self.allowed_by_node)
        #for node in mesh.node


def main():  # pragma: no cover
    p = ioformats.load_problem('00012')

    m = Mesh(p)
    #m.debug_print()
    r = m.render()

    m.precompute_span_templates()
    for node in m.nodes:
        s = 0
        for angle in 1, 2, 4:
            if m.span_templates[node, angle]:
                s += angle
        if s != 7:
            r.draw_text(node, str(s), color=(0, 0, 255))

    #r.get_img(200).save('mesh.png')

    print('*' * 20)
    borders = find_all_borders(m)
    print(len(borders), 'borders')
    perimeters = list(find_perimeters(m, borders))
    print(len(perimeters), 'perimeters')

    perimeter = perimeters[0]

    r = m.render()
    for border in perimeter:
        for edge in border:
            r.draw_edge(*edge, color=(50, 50, 0))

    r.get_img(200).save('perimeter.png')

    solver = Solver(m, perimeter)


if __name__ == '__main__':
    main()
