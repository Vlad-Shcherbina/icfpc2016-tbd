import pprint
from typing import List, Tuple
from fractions import Fraction

from production import cg
from production.cg import Point
from production import ioformats
from production import render


def subdivide_edges(
        edges: List[Tuple[Point, Point]]) -> List[Tuple[Point, Point]]:
    """
    After subdivision for any pair of edges they either do not have
    any points in common, or they have an endpoint in common.
    """
    result = []
    for edge in edges:
        points = set(edge)
        for e2 in edges:
            pt = cg.edge_intersection(edge, e2)
            if pt is not None:
                points.add(pt)
        points = sorted(points)
        assert len(points) >= 2
        result.extend(zip(points[:-1], points[1:]))
    return result


def reconstruct_facets(problem: ioformats.Problem) -> List[List[Point]]:
    """Return list of faces corresponding to smallest pieces possible.

    This set of facets covers the whole plane and is topologically equivalent
    to a sphere. Most of the facets will be CCW and one facet that corresponds
    to the infinite area outside will be CW.
    """

    adjacent = {}

    for edge in subdivide_edges(problem.skeleton):
        for pt1, pt2 in edge, edge[::-1]:
            adjacent.setdefault(pt1, []).append(pt2)

    for center_pt, v in adjacent.items():
        v.sort(key=lambda pt: cg.rational_angle(pt - center_pt))

    def next_in_facet(e):
        pt1, pt2 = e
        pts = adjacent[pt2]
        i = pts.index(pt1)  # TODO: quadratic complexity
        return (pt2, pts[(i - 1) % len(pts)])

    facets = []

    visited = set()
    for start_pt1, v in adjacent.items():
        for start_pt2 in v:
            e = start_pt1, start_pt2
            if e in visited:
                continue

            facets.append([])
            e2 = e
            while True:
                facets[-1].append(e2[0])

                assert e2 not in visited
                visited.add(e2)

                e2 = next_in_facet(e2)
                if e2 == e:
                    break

    return facets


def gen_point_in_facet(facet):
    assert len(facet) >= 3
    assert cg.polygon_area(facet) > 0

    d = facet[1] - facet[0]
    orth = Point(-d.y, d.x)
    m = facet[0] + d * Fraction(1, 2)

    # TODO: can fail if point happens to bo in the border
    for i in range(10, 10000):
        pt = m + orth * Fraction(1, 2**i)
        if (not cg.is_point_on_poly_border(pt, facet) and
            cg.count_revolutions(pt, facet) == 1):
            return pt
    assert False, facet


def is_facet_real(facet, problem):
    a = cg.polygon_area(facet)
    assert a != 0
    if a < 0:
        return False

    pt = gen_point_in_facet(facet)
    cnt = 0
    for silh_poly in problem.silhouette:
        a = cg.polygon_area(silh_poly)
        assert a != 0
        cnt += cg.count_revolutions(pt, silh_poly)
    assert cnt in (0, 1), cnt
    return cnt == 1


def keep_real_facets(facets, problem):
    result = []
    for facet in facets:
        if is_facet_real(facet, problem):
            result.append(facet)

    return result


alphabet = 'ABCDEFGHKM'
human_ids = []
human_ids.extend(alphabet)
human_ids.extend(
    c1 + c2 for c1 in alphabet for c2 in alphabet)
human_ids.extend(
    c1 + c2 + c3 for c1 in alphabet for c2 in alphabet for c3 in alphabet)

# inside this class, the vocabulary from
# vlad_scratch/undead.md is used,
# except that `reconstruct_facets` and `is_facet_real`
# actually refer to *fragments* for historical reasons.
class Mesh:
    def __init__(self, p: ioformats.Problem):
        fragments = reconstruct_facets(p)
        fragment_ids = []
        fragment_by_id = {}

        for i, fragment in enumerate(fragments):
            fragment_ids.append('{}_{}{}'.format(
                human_ids[i],
                len(fragment),
                '' if is_facet_real(fragment, p) else '_virt'))
            fragment_by_id[fragment_ids[-1]] = fragment

        assert len(set(fragment_ids)) == len(fragment_ids)
        #print(fragment_ids)

        nodes = set.union(*map(set, fragments))
        nodes = list(nodes)
        nodes.sort()
        #print(nodes)

        bones_by_node = {}
        left_fragment_by_bone = {}
        right_fragment_by_bone = {}

        for fragment_id, fragment in fragment_by_id.items():
            for bone in zip(fragment, fragment[1:] + fragment[:1]):
                t = bones_by_node.setdefault(bone[0], [])
                assert bone not in t, t
                t.append(bone)

                assert bone not in left_fragment_by_bone
                left_fragment_by_bone[bone] = fragment_id
                assert bone[::-1] not in right_fragment_by_bone
                right_fragment_by_bone[bone[::-1]] = fragment_id

        for bones in bones_by_node.values():
            bones.sort(key=lambda bone: cg.rational_angle(bone[1] - bone[0]))


        self.nodes = nodes
        self.bones_by_node = bones_by_node
        self.left_fragment_by_bone = left_fragment_by_bone
        self.right_fragment_by_bone = right_fragment_by_bone
        self.fragment_by_id = fragment_by_id

    def debug_print(self):
        print('**** MESH *******')
        print('bones_by_node')
        pprint.pprint(self.bones_by_node)
        print()
        print('left_fragment_by_bone')
        pprint.pprint(self.left_fragment_by_bone)
        print()
        print('right_fragment_by_bone')
        pprint.pprint(self.right_fragment_by_bone)

    def render(self):
        r = render.Renderer()
        r.points_for_viewport.clear()
        for fragment_id, fragment in self.fragment_by_id.items():
            if not fragment_id.endswith('_virt'):
                r.draw_poly(fragment)

            if cg.polygon_area(fragment) > 0:
                center = sum(fragment, Point(0, 0)) / Fraction(len(fragment))
                r.draw_text(center, fragment_id)

        return r


def generate_span_templates(star, angle):
    pass


def main():  # pragma: no cover
    p = ioformats.load_problem('00025')

    m = Mesh(p)
    m.debug_print()
    m.render().get_img(200).save('mesh.png')

    for node in m.nodes:
        print(node, m.describe_node(node))

    return

    facets = reconstruct_facets(p)
    print(list(map(len, facets)))

    facets = keep_real_facets(facets, p)
    print(list(map(len, facets)))

    im = render.render_polys_and_edges(facets, [])
    im.save('hz2.png')


if __name__ == '__main__':
    main()
