import pprint
from typing import NamedTuple, Tuple, Dict, List

from production import cg
from production.cg import Point
from production import ioformats
from production import meshes


FrontierEntry = NamedTuple('FrontierEntry', [
    ('facet_idx', int),
    ('edge', Tuple[Point, Point]),
    ('orig_edge', Tuple[Point, Point]),
])


FrozenFacet = NamedTuple('FrozenFacet', [
    ('facet_idx', int),
    ('orig_facet', List[Point]),
    ('t', cg.AffineTransform),
])


State = NamedTuple('State', [
    ('frozen_facets', List[FrozenFacet]),
    ('frontier', List[FrontierEntry]),
    #('unused_idxes', set(int)),
])


class Solver:
    def __init__(self, p: ioformats.Problem):
        self.facets = meshes.reconstruct_facets(p)
        self.facets = meshes.keep_real_facets(self.facets, p)

        # self.facet_idx_by_edge = {}
        # for facet_idx, facet in enumerate(self.facets):
        #     for e in zip(facet, facet[1:] + facet[:1]):
        #         assert e not in self.facet_idx_by_edge
        #         facet_idx_by_edge[e] = facet_idx


    def gen_initial_states(self):
        for facet_idx, facet in enumerate(self.facets):
            for align_edge in zip(facet, facet[1:] + facet[:1]):
                for pt1, pt2 in align_edge, align_edge[::-1]:
                    try:
                        t = cg.AffineTransform.align(
                            pt1, pt2,
                            Point(0, 0), Point(1, 0))
                    except cg.IrrationalError:
                        continue

                    orig_facets = []
                    frontier = []

                    orig_facet = list(map(t.transform, facet))
                    if not cg.poly_inside_unit_square(orig_facet):
                        continue

                    for e in zip(facet, facet[1:] + facet[:1]):
                        orig_edge = t.transform(e[0]), t.transform(e[1])
                        if cg.edge_on_unit_square_border(*orig_edge):
                            continue

                        fronter.append(FrontierEntry(
                            facet_idx=facet_idx,
                            edge=e,
                            orig_edge=orig_edge))

                    yield State(
                        frozen_facets=[
                            FrozenFacet(
                                facet_idx=facet_idx,
                                orig_facet=orig_facet,
                                t=t)],
                        frontier=frontier)

    def is_final(self, state: State):
        if state.frontier:
            return False

        used_idxes = {f.facet_idx for f in state.frozen_facets}
        if len(used_idxes) < len(self.facets):
            return False

        orig_area = sum(
            abs(cg.polygon_area(self.facets[f.facet_idx]))
            for f in state.frozen_facets)
        assert 0 <= orig_area <= 1
        if orig_area < 1:
            return False

        return True

    def to_solution(self, state) -> ioformats.Solution:
        orig_points = {pt for f in state.frozen_facets for pt in f.orig_facet}
        orig_points = list(orig_points)
        dst_points = [None] * len(orig_points)

        facets = []
        for f in state.frozen_facets:
            facets.append([])
            for pt, orig_pt in zip(self.facets[f.facet_idx], f.orig_facet):
                idx = orig_points.index(orig_pt)
                if dst_points[idx] is None:
                    dst_points[idx] = pt
                else:
                    assert dst_points[idx] == pt
                facets[-1].append(idx)

        assert None not in dst_points

        return ioformats.Solution(
            orig_points=orig_points, facets=facets, dst_points=dst_points)


def main():
    p = ioformats.load_problem('1')
    solv = Solver(p)

    for state in solv.gen_initial_states():
        if solv.is_final(state):
            print(state)
            print('solved')

            sol = solv.to_solution(state)

            print(sol)
            print(ioformats.solution_to_str(sol))
            break


if __name__ == '__main__':
    main()
