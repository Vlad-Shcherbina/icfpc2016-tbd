#!/bin/env python3

import os, sys
import pprint
from typing import NamedTuple, Tuple, Dict, List
from multiprocessing import Process, Pipe

from production import cg
from production.cg import Point
from production import ioformats, meshes, render, api_wrapper


TIMEOUT = 15


def run_solution(solver_cls, problem):
    parent_conn, child_conn = Pipe()
    p = Process(target=runner, args=(solver_cls, problem, child_conn))
    p.start()
    p.join(TIMEOUT)
    if p.exitcode is None:
        print('Terminating!!!', file=sys.stderr)
        p.terminate()
        p.join()
    else:
        # FIXME: figure out why this is necessary. Maybe actually spawn a separate thread in case there's a lot of shit in the pipe.
        # And why we get here and get stuck if there was an assertion error.
        if parent_conn.poll():
            return parent_conn.recv()
    

def runner(solver_cls, problem_id, solution_pipe):
    problem = ioformats.load_problem(problem_id)
    solv = solver_cls(problem, problem_id, solution_pipe)
    
    # FIXME: this is retarded
    for state in solv.gen_initial_states():
        solv.rec(state)
        continue


def main():
    print('yo')
    from production.solver import Solver
    for problem in range(101):
        problem = '{:03}'.format(problem + 1)
        print(problem)
        
        result_file = ioformats.get_root() / 'solutions' / (problem + '.txt')
        
        # FIXME: have something like error file that describes what went wrong on the previous try and maybe do something about it.
        if result_file.exists(): continue
        
        result = run_solution(Solver, problem)
        if result is not None:
            with result_file.open('w') as f:
                f.write(result)
    

if __name__ == '__main__':
    main()
    