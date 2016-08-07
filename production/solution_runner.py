#!/bin/env python3

import os, sys
import pprint, ast
from typing import NamedTuple, Tuple, Dict, List
from collections import namedtuple
from multiprocessing import Process, Pipe
from threading import Thread
from io import StringIO

from production import cg
from production.cg import Point
from production import ioformats, meshes, render, api_wrapper
from production.ioformats import get_root


TIMEOUT = 15

STATUS_SOLVED = 'solved'
STATUS_PARTIAL = 'partial'
STATUS_TIMEOUT = 'timeout'
STATUS_CRASHED = 'crashed'
STATUS_REJECTED = 'rejected'

legit_statuses = frozenset((
        STATUS_SOLVED,
        STATUS_PARTIAL,
        STATUS_TIMEOUT,
        STATUS_CRASHED,
        STATUS_REJECTED,
        ))

ProblemStatus = namedtuple('ProblemStatus', 'id status solver file note')


class SolutionDb(dict):
    def __init__(self):
        self.directory = get_root() / 'solutions'
        self.load()


    def load(self):
        self.clear()
        with (self.directory / 'solution_db.txt').open('r') as f:
            for line in f:
                if not line.strip(): continue
                s = ProblemStatus(*ast.literal_eval(line))
                self.validate(s)
                assert s.id not in self
                self[s.id] = s


    def write(self):
        with (self.directory / 'solution_db.txt').open('w') as f:
            for p in sorted(self.values()):
                f.write(', '.join(repr(it) for it in p))
                f.write('\n')


    def validate(self, status):
        assert status.status in legit_statuses
        if status.status in (STATUS_SOLVED, STATUS_REJECTED):
            assert (self.directory / status.file).exists() 
        

    def update(self, sid, status, solver, data, note=''):
        if status in (STATUS_SOLVED, STATUS_REJECTED):
            assert data is not None

        existing = self.get(sid)
        # TODO: add check for partial
        assert existing is None or existing.status != STATUS_SOLVED
            
        filename = None
        if data is not None:
            filename = status + '_' + sid + '.txt'
            with (self.directory / filename).open('w') as f:
                f.write(data)
        self[sid] = ProblemStatus(sid, status, solver, filename, note)
        self.write()  
                 

solution_db = SolutionDb()

def _generate_solution_db_from_legacy():
    assert not solution_db
    solutions = (get_root() / 'solutions').glob('solved_*.txt')
    for f in solutions:
        sid = f.stem[len('solved_'):]
        assert int(sid, 10)
        s = ProblemStatus(sid, STATUS_SOLVED, 'Solver', f.name, '')
        solution_db[s.id] = s
    solution_db.write()
# _generate_solution_db_from_legacy()


def run_solver(solver_cls, problem):
    parent_conn, child_conn = Pipe()
    try:
        p = Process(target=runner, args=(solver_cls, problem, child_conn))
        p.start()
        p.join(TIMEOUT)
        if p.exitcode is None:
            print('Terminating!!!', file=sys.stderr)
            p.terminate()
            p.join()
            return STATUS_TIMEOUT, TIMEOUT
        else:
            child_conn.close()
            try:
                result = parent_conn.recv()
                if isinstance(result, Exception):
                    return STATUS_CRASHED, result 
                return STATUS_SOLVED, result 
            except EOFError:
                return STATUS_CRASHED, 'no backtrace available'
    finally:
        parent_conn.close()
        child_conn.close()


def solve_problem(solver_cls, problem):
    solver_name = solver_cls.__name__
    print('Solving {} with {}'.format(problem, solver_name))
    status, result = run_solver(solver_cls, problem)
    if status == STATUS_SOLVED:
        # try submitting
        try:
            api_wrapper.s_submit_solution(int(problem), result)
        except api_wrapper.ServerRejectedError as exc:
            print(exc)
            status = STATUS_REJECTED
            result = str(exc) + '\n========= Submission =========\n' + result
        
    if status in (STATUS_CRASHED, STATUS_SOLVED, STATUS_REJECTED):
        solution_db.update(problem, status, solver_name, result)
    elif status == STATUS_TIMEOUT:
        # store timeout in note
        solution_db.update(problem, status, solver_name, None, result)
    else:
        assert False, 'Unknown status {!r} {!r}'.format(status, result)
    return status


def runner(solver_cls, problem_id, solution_pipe):
    try:
        problem = ioformats.load_problem(problem_id)
        solv = solver_cls(problem, problem_id, solution_pipe)
        solv.run()
    except Exception as e:
        solution_pipe.write(e)


def list_problems():
    return sorted(s.stem for s in (get_root() / 'problems').glob('[0-9]' * 5 + '.txt'))

def main():
    from production.solver import Solver
    problems = list_problems()
    limit = 3
    for p in problems:
        existing = solution_db.get(p)
        if existing is not None: continue
        if STATUS_SOLVED == solve_problem(Solver, p):
            limit -= 1
            if limit < 0:
                break


if __name__ == '__main__':
    main()
