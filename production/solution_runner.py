#!/bin/env python3

import os, sys
import re
import pprint, ast
from typing import NamedTuple, Tuple, Dict, List
from collections import namedtuple
import threading, queue
from multiprocessing import Process, Pipe
from threading import Thread
from io import StringIO

from production import cg
from production.cg import Point
from production import ioformats, meshes, render, api_wrapper
from production.ioformats import get_root

THREADS = 6
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

def print_err(*args, **kwargs):
    print(*args, file=sys.stderr)
    sys.stderr.flush()
    

class SolutionDb(dict):
    def __init__(self):
        self.db_file = get_root() / 'solutions' / 'solution_db.txt' 
        self.load()
        self.update_from_directory()


    def load(self):
        self.clear()
        if not self.db_file.exists(): return
        
        with self.db_file.open('r') as f:
            for line in f:
                if not line.strip(): continue
                s = ProblemStatus(*ast.literal_eval(line))
                self.validate(s)
                assert s.id not in self
                self[s.id] = s

    def update_from_directory(self):
        solutions = self.db_file.parent.glob('solved_*.txt')
        for f in solutions:
            sid = f.stem[len('solved_'):]
            if sid in self: continue 
            assert int(sid, 10)
            s = ProblemStatus(sid, STATUS_SOLVED, 'Unknown', f.name, '')
            self[s.id] = s
        self.write()

    def write(self):
        with self.db_file.open('w') as f:
            for p in sorted(self.values()):
                f.write(', '.join(repr(it) for it in p))
                f.write('\n')


    def validate(self, status):
        assert status.status in legit_statuses
        if status.status in (STATUS_SOLVED, STATUS_REJECTED):
            assert (self.db_file.parent / status.file).exists() 
        

    def update(self, sid, status, solver, data, note=''):
        if status in (STATUS_SOLVED, STATUS_REJECTED):
            assert data is not None

        existing = self.get(sid)
        # TODO: add check for partial
        assert existing is None or existing.status != STATUS_SOLVED
            
        filename = None
        if data is not None:
            filename = status + '_' + sid + '.txt'
            with (self.db_file.parent / filename).open('w') as f:
                f.write(data)
        self[sid] = ProblemStatus(sid, status, solver, filename, note)
        self.write()  
                 


def run_solver(solver_cls, problem):
    parent_conn, child_conn = Pipe()
    try:
        p = Process(target=runner, args=(solver_cls, problem, child_conn))
        p.start()
        p.join(TIMEOUT)
        if p.exitcode is None:
            print_err('Timeout, terminating!!!')
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


def thread_worker(solver_cls, input_q, output_q):
    while True:
        problem = input_q.get()
        print_err('Thread: dequed', problem)
        if problem is None:
            return
        output_q.put((problem, run_solver(solver_cls, problem)))
        print_err('Thread: enqueued', problem)


def process_solved(solution_db, problem, solver_name, status, result):
    if problem in solution_db: return
    
    if status == STATUS_SOLVED:
        # try submitting
        try:
            print(api_wrapper.s_submit_solution(int(problem), result).json())
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


def solve_problems(solution_db, solver_cls, problems, max_processes=1):
    solver_name = solver_cls.__name__
    print('Solving with {}'.format(solver_name))
    
    input_q, output_q = queue.Queue(), queue.Queue()
    threads = [threading.Thread(target=thread_worker, args=(solver_cls, input_q, output_q), daemon=True) for _ in range(max_processes)]
    for t in threads: t.start()
    
    seed_problems = max_processes
    for p in problems:
        if p in solution_db: continue
        
        print_err('Runner: enqueue', p)
        input_q.put(p)

        if seed_problems:
            seed_problems -= 1
            continue
        
        p, (status, result) = output_q.get()
        print_err('Runner: dequeued', p, status)
        process_solved(solution_db, p, solver_name, status, result)
    
    # tell threads to terminate
    print_err('Runner: terminating threads')
    for _ in len(threads):
        input_q.put(None)
    for t in threads:
        t.join()

    while True:
        try:
            p, status, result = output_q.get_nowait()
        except queue.Empty:
            break
        print_err('Runner: dequeued', p, status)
        process_solved(p, solver_name, status, result)


def runner(solver_cls, problem_id, solution_pipe):
    try:
        problem = ioformats.load_problem(problem_id)
        solv = solver_cls(problem, problem_id, solution_pipe)
        solv.run()
    except Exception as e:
        solution_pipe.write(e)


def list_problems():
    return sorted(s.stem for s in (get_root() / 'problems').glob('[0-9]' * 5 + '.txt'))


def list_hard_problems():
    ps = set(list_problems())
    result = []
    with (get_root() / 'manpages_scratch' / 'all_problems.txt').open() as fin:
        for line in fin:
            m = re.match(r'\s+(\d+)\s+\d+\s+\d+\s+\d+', line)
            if m is not None:
                #print(m.group(1))
                p = '{:05}'.format(int(m.group(1)))
                if p in ps:
                    result.append(p)
    return result


def main():
    from production.solver import Solver
    problems = list_problems()
    solve_problems(SolutionDb(), Solver, problems, 8)


if __name__ == '__main__':
    main()
