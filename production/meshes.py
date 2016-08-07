import pprint
from typing import List, Tuple
from fractions import Fraction
import itertools
import math

from production import cg
from production.cg import Point
from production import ioformats
from production import render


class TooHardError(Exception):
    pass


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

    def describe_node(self, node):
        return tuple(self.left_fragment_by_bone[bone]
                     for bone in self.bones_by_node[node])

    def get_forbidden_idx(self, node):
        return {i for i, bone in enumerate(self.bones_by_node[node])
                if self.left_fragment_by_bone[bone].endswith('_virt')}

    def describe_span_template(self, node, span):
        result = []
        for dir, f in span:
            result.append(
                {1: 'forward ', -1: 'back '}[dir] + 
                self.left_fragment_by_bone[self.bones_by_node[node][f]]
            )
        return result

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

    def get_node_star(self, node):
        return [bone[1] - bone[0] for bone in self.bones_by_node[node]]

    def span_end_bones(self, node, st):
        n = len(self.bones_by_node[node])
        if st[0][0] == 1:
            end1 = st[0][1]
        else:
            end1 = (st[0][1] + 1) % n
        if st[-1][0] == 1:
            end2 = (st[-1][1] + 1) % n
        else:
            end2 = st[-1][1]
        return self.bones_by_node[node][end1], self.bones_by_node[node][end2]

    def precompute_span_templates(self):
        self.corners = set()
        self.transitions = {1: {}, 2: {}}

        self.span_templates = {}
        for node in self.nodes:
            star = self.get_node_star(node)
            has_any = False
            for angle in 1, 2, 4:
                self.span_templates[node, angle] = list(
                    generate_span_templates(star, angle, self.get_forbidden_idx(node)))

                if angle == 4:
                    continue

                for st in self.span_templates[node, angle]:
                    has_any = True
                    if angle == 1:
                        self.corners.add(node)

                    if st[0][0] == 1:
                        end1 = st[0][1]
                    else:
                        end1 = (st[0][1] + 1) % len(star)
                    if st[-1][0] == 1:
                        end2 = (st[-1][1] + 1) % len(star)
                    else:
                        end2 = st[-1][1]

                    for e1, e2 in (end1, end2), (end2, end1):
                        bone1 = self.bones_by_node[node][e1][::-1]
                        bone2 = self.bones_by_node[node][e2]
                        self.transitions[angle].setdefault(bone1, set()).add(bone2)

            if not has_any:
                raise TooHardError('no spans for a node')


def match_angle(start, finish, angle):
    if angle == 1:
        return start.dot(finish) == 0 and start.cross(finish) > 0
    elif angle == 2:
        return start.dot(finish) < 0 and start.cross(finish) == 0
    elif angle == 4:
        return start.dot(finish) > 0 and start.cross(finish) == 0
    else:
        assert False, angle


def enumerate_idx(*, angle, star_size, start_loc, flip_locs, target_loc):
    result = []
    idx = start_loc
    dir = 1
    for i, flip_loc in enumerate(flip_locs):
        while True:
            if i == 0 and idx == flip_loc:
                break

            if dir > 0:
                result.append(idx)
            idx += dir
            idx %= star_size
            if dir < 0:
                result.append(idx)

            if idx == flip_loc:
                break
        dir = -dir

    while idx != target_loc or (angle == 4 and not flip_locs):
        if dir > 0:
            result.append(idx)
        idx += dir
        idx %= star_size
        if dir < 0:
            result.append(idx)

        if idx == target_loc:
            break

    return result


def approx_angleasdf(angle, float_angles, start_loc, flip_locs, target_loc):
    return sum(
        float_angles[idx]
        for idx in enumerate_idx(
                angle=angle,
                star_size=len(float_angles),
                start_loc=start_loc,
                flip_locs=flip_locs,
                target_loc=target_loc))


def generate_span_templates_internal(star, angle, forbidden_idx):
    #if angle >= 1: print('star size', len(star))

    assert len(star) >= 2

    float_angles = []
    for pt1, pt2 in zip(star, star[1:] + star[:1]):
        float_angles.append(math.atan2(pt1.cross(pt2), pt1.dot(pt2)) % (2 * math.pi))
    assert math.isclose(sum(float_angles), 2 * math.pi)
    #print(float_angles)

    cnt = 0
    for num_flips in range(4 + 1):
        if angle == 4 and num_flips % 2 == 1:
            continue
#        if angle == 1: print(num_flips, len(star) ** (num_flips + 2))
        for flip_locs in itertools.product(range(len(star)), repeat=num_flips):
            if any(a == b for a, b in zip(flip_locs, flip_locs[1:])):
                continue
            for start_loc, start in enumerate(star):
                for target_loc in range(len(star)):
                    cnt += 1
                    #if cnt % 1000 == 0: print('cnt', cnt)
                    if cnt > 20000:
                        return

                    idxes = enumerate_idx(
                        angle=angle,
                        star_size=len(float_angles),
                        start_loc=start_loc,
                        flip_locs=flip_locs,
                        target_loc=target_loc)

                    if any(idx in forbidden_idx for idx in idxes):
                        continue

                    #s = approx_angle(
                    #    angle, float_angles, start_loc, flip_locs, target_loc)
                    approx_angle = sum(float_angles[idx] for idx in idxes)
                    if not math.isclose(approx_angle, math.pi / 2 * angle, abs_tol=1e-6):
                        continue

                    span = []

                    trajectory = [start]
                    idx = start_loc
                    dir = 1

                    ss = list(star)
                    for i, flip_loc in enumerate(flip_locs):
                        #print('*')
                        while True:
                            if i == 0 and idx == flip_loc:
                                break

                            if dir > 0:
                                span.append((dir, idx))
                            idx += dir
                            idx %= len(star)
                            if dir < 0:
                                span.append((dir, idx))

                            trajectory.extend(
                                intermediate_points(
                                    trajectory[-1], ss[idx]))
                            trajectory.append(ss[idx])
                            #print(trajectory)

                            if idx == flip_loc:
                                break

                        t = cg.AffineTransform.mirror(Point(0, 0), ss[flip_loc])
                        ss = list(map(t.transform, ss))
                        dir = -dir

                    if angle != 4 and idx == target_loc:
                        continue

                    #print('*')
                    while idx != target_loc or (angle == 4 and not flip_locs):
                        if dir > 0:
                            span.append((dir, idx))
                        idx += dir
                        idx %= len(star)
                        if dir < 0:
                            span.append((dir, idx))

                        trajectory.extend(
                            intermediate_points(trajectory[-1], ss[idx]))
                        trajectory.append(ss[idx])

                        if idx == target_loc:
                            break

                    assert idxes == [s for _, s in span]
                    if match_angle(start, ss[target_loc], angle):
                        trajectory.extend(
                            intermediate_points(trajectory[-1], trajectory[0]))
                        #print(trajectory)

                        rev = cg.count_revolutions(Point(0, 0), trajectory)
                        #print(rev)
                        assert rev >= 0
                        if angle == 4:
                            if rev != 2:
                                continue
                        else:
                            if rev != 1:
                                continue

                        assert span
                        #assert span[0][0] == 1
                        #print(' ', start_loc, flip_locs, target_loc, trajectory, span)

                        if angle == 4 and max(span) != span[0]:
                            continue

                        assert math.isclose(approx_angle, math.pi / 2 * angle)
                        yield span


def intermediate_points(angle1, angle2):
    if angle1.cross(angle2) == 0:
        if angle1.dot(angle2) > 0:
            # this should not happen but happens for corner case reasons
            return [
                Point(-angle1.y, angle1.x),
                angle1 * -1,
                Point(angle1.y, -angle1.x)]

        return [Point(-angle1.y, angle1.x)]
    if angle1.cross(angle2) < 0:
        return [(angle1 + angle2) * -1]
    return []


def generate_span_templates(star, angle, forbidden_idx):

    spans = set()
    for span in generate_span_templates_internal(star, angle, forbidden_idx):
        rspan = [(-d, f) for d, f in reversed(span)]
        spans.add(tuple(span))
        spans.add(tuple(rspan))

    # deduplicate cyclyc stuff
    if angle == 4:
        def canonicalize(span):
            return max(span[i:] + span[:i] for i in range(len(span)))
        spans = set(map(canonicalize, spans))

    return sorted(spans, reverse=True)


def main():  # pragma: no cover
    p = ioformats.load_problem('00012')

    m = Mesh(p)
    m.debug_print()
    m.render().get_img(200).save('mesh.png')

    #m.precompute_span_templates()
    #print('corners', m.corners)
    #pprint.pprint(m.transitions)
    #return

    for node in m.nodes:
        print()
        print('node', node, m.describe_node(node))
        star = m.get_node_star(node)
        print('star', star)

        for angle in 1, 2, 4:
            for span in generate_span_templates(star, angle, m.get_forbidden_idx(node)):
                print(' ', angle, m.describe_span_template(node, span))


    return

    facets = reconstruct_facets(p)
    print(list(map(len, facets)))

    facets = keep_real_facets(facets, p)
    print(list(map(len, facets)))

    im = render.render_polys_and_edges(facets, [])
    im.save('hz2.png')


if __name__ == '__main__':
    main()
