#!/bin/env python3

import os, sys
import pprint
from typing import NamedTuple, Tuple, Dict, List
import random

from production import cg
from production.cg import Point
from production import ioformats
from production import meshes
from production import render
from production import api_wrapper


FrontierEntry = NamedTuple('FrontierEntry', [
    ('facet_idx', int),
    ('edge', Tuple[Point, Point]),
    ('orig_edge', Tuple[Point, Point]),
    ('t', cg.AffineTransform),
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


class SolvedException(Exception):
    def __init__(self, state):
        self.state = state


class Solver:
    def __init__(self, p: ioformats.Problem, problem_id, solution_pipe=None):
        self.problem_id = problem_id
        self.solution_pipe = solution_pipe
        self.snapshot_cnt = 0

        self.facets = meshes.reconstruct_facets(p)
        self.facets = meshes.keep_real_facets(self.facets, p)
        random.shuffle(self.facets)

        self.facet_idx_by_edge = {}
        for facet_idx, facet in enumerate(self.facets):
            for e in zip(facet, facet[1:] + facet[:1]):
                assert e not in self.facet_idx_by_edge
                self.facet_idx_by_edge[e] = facet_idx


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

                        frontier.append(FrontierEntry(
                            facet_idx=facet_idx,
                            edge=e,
                            orig_edge=orig_edge,
                            t=t))

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

    def is_deadend(self, state: State):
        orig_area = sum(
            abs(cg.polygon_area(self.facets[f.facet_idx]))
            for f in state.frozen_facets)
        if orig_area > 1:
            return True
        return False

    def expand_frontier_entry(self, state: State, i: int):
        #print('expanding', len(state.frontier))
        entry = state.frontier[i]

        for f in state.frontier:
            if (entry.orig_edge == f.orig_edge and
                entry.t.mat.det() * f.t.mat.det() == -1):

                #self.render_state(state).save('before_assert.png')
                #print(entry.orig_edge)
                if entry.edge != f.edge:
                    # really does not make sense, but it helps with some
                    # problems so whatever
                    return

                assert entry.edge == f.edge, (entry.edge, f.edge)

                new_frontier = list(state.frontier)
                new_frontier.remove(entry)
                new_frontier.remove(f)
                yield State(
                    frozen_facets=state.frozen_facets,
                    frontier=new_frontier)
                return

        rev_orig_edge = entry.orig_edge[::-1]
        rev_edge = entry.edge[::-1]
        #print('yi', len(state.frontier))
        #pprint.pprint(state.frontier)
        for f in state.frontier:
            if (f.orig_edge == rev_orig_edge and
                entry.t.mat.det() * f.t.mat.det() == 1):

                if entry.edge != f.edge[::-1]:
                    # really does not make sense, but it helps with some
                    # problems so whatever
                    return

                assert entry.edge == f.edge[::-1]

                #print('bitch')
                new_frontier = list(state.frontier)
                new_frontier.remove(entry)
                new_frontier.remove(f)
                yield State(
                    frozen_facets=state.frozen_facets,
                    frontier=new_frontier)
                return

        #print(rev_edge)
        #print(list(self.facet_idx_by_edge.keys()))
        if rev_edge in self.facet_idx_by_edge:
            #print('hz')
            idx = self.facet_idx_by_edge[rev_edge]
            new_frontier = list(state.frontier)
            new_frontier.remove(entry)

            t = entry.t

            facet = self.facets[idx]
            orig_facet = list(map(t.transform, facet))

            if cg.poly_inside_unit_square(orig_facet):
                #print('hi')
                # TODO: check for overlap with other orig facets

                new_frozen_facets = list(state.frozen_facets)
                new_frozen_facets.append(FrozenFacet(
                    facet_idx=idx,
                    orig_facet=orig_facet,
                    t=t))

                for e in zip(facet, facet[1:] + facet[:1]):
                    if e == rev_edge:
                        continue

                    orig_edge = t.transform(e[0]), t.transform(e[1])
                    if cg.edge_on_unit_square_border(*orig_edge):
                        continue

                    new_frontier.append(FrontierEntry(
                        facet_idx=idx,
                        edge=e,
                        orig_edge=orig_edge,
                        t=t))

                yield State(
                    frozen_facets=new_frozen_facets,
                    frontier=new_frontier)


        idx = entry.facet_idx
        new_frontier = list(state.frontier)
        new_frontier.remove(entry)

        t = cg.AffineTransform.mirror(*entry.orig_edge) @ entry.t

        facet = self.facets[idx]
        orig_facet = list(map(t.transform, facet))

        if cg.poly_inside_unit_square(orig_facet):
            #print('hi')
            # TODO: check for overlap with other orig facets

            new_frozen_facets = list(state.frozen_facets)
            new_frozen_facets.append(FrozenFacet(
                facet_idx=idx,
                orig_facet=orig_facet,
                t=t))

            for e in zip(facet, facet[1:] + facet[:1]):
                if e == entry.edge:
                    continue

                orig_edge = t.transform(e[0]), t.transform(e[1])
                if cg.edge_on_unit_square_border(*orig_edge):
                    continue

                new_frontier.append(FrontierEntry(
                    facet_idx=idx,
                    edge=e,
                    orig_edge=orig_edge,
                    t=t))

            yield State(
                frozen_facets=new_frozen_facets,
                frontier=new_frontier)

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

    def to_normalized_thingie(self, state):
        assert self.is_final(state)
        visited_facets = set()

        def share_orig_edge(f1, f2):
            return any(
                e1 == e2[::-1]
                for e1 in zip(f1.orig_facet,
                              f1.orig_facet[1:] + f1.orig_facet[:1])
                for e2 in zip(f2.orig_facet,
                              f2.orig_facet[1:] + f2.orig_facet[:1]))

        def adjacent(f):
            for f2 in state.frozen_facets:
                if f2.t == f.t and share_orig_edge(f, f2):
                    yield f2

        result = []
        for f in state.frozen_facets:
            if repr(f) in visited_facets:
                continue
            cluster = []
            worklist = [f]
            while worklist:
                f = worklist.pop()
                if repr(f) in visited_facets:
                    continue
                visited_facets.add(repr(f))
                cluster.append(f)
                for f2 in adjacent(f):
                    worklist.append(f2)

            #print()
            #print('cluster', cluster)

            cluster_pile = set()
            cluster_orig_edges = []
            cluster_dst_edges = []

            for f in cluster:
                facet = self.facets[f.facet_idx]
                orig_facet = f.orig_facet

                dst_edges = zip(facet, facet[1:] + facet[:1])
                orig_edges = zip(orig_facet, orig_facet[1:] + orig_facet[:1])

                for orig_edge, dst_edge in zip(orig_edges, dst_edges):
                    assert not orig_edge in cluster_pile
                    if orig_edge[::-1] in cluster_pile:
                        cluster_pile.remove(orig_edge[::-1])
                        cluster_orig_edges.remove(orig_edge[::-1])
                        cluster_dst_edges.remove(dst_edge[::-1])
                    else:
                        cluster_pile.add(orig_edge)
                        cluster_orig_edges.append(orig_edge)
                        cluster_dst_edges.append(dst_edge)

            #print(cluster_orig_edges)
            #print(cluster_dst_edges)

            cluster_orig_pts = []
            cluster_dst_pts = []
            i = 0
            while True:
                cluster_orig_pts.append(cluster_orig_edges[i][0])
                cluster_dst_pts.append(cluster_dst_edges[i][0])

                q = cluster_orig_edges[i][1]
                for j, e in enumerate(cluster_orig_edges):
                    if q == e[0]:
                        break
                else:
                    assert False

                i = j
                if i == 0:
                    break

            assert len(cluster_orig_pts) == len(cluster_orig_edges)
            #print(cluster_orig_pts)
            #print(cluster_dst_pts)

            result.append((cluster_orig_pts, cluster_dst_pts))

        return result


    def render_state(self, state):
        orig_polys = [f.orig_facet for f in state.frozen_facets]
        orig_edges = [f.orig_edge for f in state.frontier]
        orig_im = render.render_polys_and_edges(orig_polys, orig_edges)

        dst_polys = [self.facets[f.facet_idx] for f in state.frozen_facets]
        dst_edges = [f.edge for f in state.frontier]
        dst_im = render.render_polys_and_edges(dst_polys, dst_edges)

        return render.hstack_images(orig_im, dst_im)

    def state_successors(self, state):
        best_candidates = None
        for i in range(len(state.frontier)):
            candidates = [
                s2
                for s2 in self.expand_frontier_entry(state, i)
                if not self.is_deadend(s2)]
            if (best_candidates is None or
                len(candidates) < len(best_candidates)):
                best_candidates = candidates

        if best_candidates is None:
            return []
        return best_candidates

    def rec(self, state):
        if self.is_final(state):
            process_final_state(self, state, self.solution_pipe)

        successors = self.state_successors(state)
        if not successors:
            print('*' * 40)
            print('snapshot', self.snapshot_cnt)
            print('frontier size', len(state.frontier))

            #self.render_state(state).save(
            #    'tmp/{:06}.png'.format(self.snapshot_cnt))
            self.snapshot_cnt += 1

        for s2 in successors:
            self.rec(s2)
            
    def run(self):
        for state in self.gen_initial_states():
            self.rec(state)
            continue
        


def render_thingie(thingie):
    polys1, polys2 = zip(*thingie)
    im1 = render.render_polys_and_edges(polys1, [])
    im2 = render.render_polys_and_edges(polys2, [])
    return render.hstack_images(im1, im2)


def thingie_to_solution(thingie):
    orig_points = {pt for t in thingie for pt in t[0]}
    orig_points = list(orig_points)
    dst_points = [None] * len(orig_points)

    for t in thingie:
        print(len(t[0]), len(t[1]))

    facets = []
    for t in thingie:
        facets.append([])
        assert len(t[0]) == len(t[1]) >= 3
        for pt, orig_pt in zip(t[1], t[0]):
            idx = orig_points.index(orig_pt)
            if dst_points[idx] is None:
                dst_points[idx] = pt
            else:
                assert dst_points[idx] == pt
            facets[-1].append(idx)

    assert None not in dst_points
    #print(facets)

    return ioformats.Solution(
        orig_points=orig_points, facets=facets, dst_points=dst_points)


def process_final_state(solv, state, solution_pipe=None):
    im = solv.render_state(state)
    thingie = solv.to_normalized_thingie(state)
    print('thingie', thingie)

    im = render.hstack_images(im, render_thingie(thingie))

    im.save('SOLUTION.png')

    sol = thingie_to_solution(thingie)
    sol = ioformats.solution_to_str(sol)
    print('-' * 20)
    print(sol)
    print('-' * 20)
    
    if solution_pipe is not None:
        solution_pipe.send(sol)
    else:
        r = api_wrapper.s_submit_solution(int(solv.problem_id), sol)
        print(r.text)

    print('SOLVED')
    exit()


def main():
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    problem_id = sys.argv[1]
    p = ioformats.load_problem(problem_id)
    solv = Solver(p, problem_id)

    for state in solv.gen_initial_states():
        solv.rec(state)
        continue

        solv.render_state(state).save('sol.png')
        if len(list(solv.expand_frontier_entry(state, 0))) < 2:
            continue

        state = list(solv.expand_frontier_entry(state, 0))[1]
        solv.render_state(state).save('sol2.png')
        print('zzzzzzzz')
        break

        if solv.is_final(state):
            print(state)
            print('solved')

            sol = solv.to_solution(state)

            print(sol)
            print(ioformats.solution_to_str(sol))
            break


if __name__ == '__main__':
    main()
