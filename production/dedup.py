import os
import json
from pprint import pprint

def to_five_digits(x):
    n = len(str(x))
    z = '0' * (5 - n)
    return z + str(x)

def to_solution_file(x):
    return five_digits_to_solution_file(to_five_digits(x))

def five_digits_to_solution_file(five_digits):
    path = os.path.join(__file__, '..', '..', 'solutions', 'solved_' + five_digits + '.txt')
    return os.path.normpath(path)

def find_original_solution_file(problem_id):
    maybe_orig = find_original_solution(problem_id)
    if maybe_orig == None:
        return maybe_orig
    else:
        return to_solution_file(maybe_orig)

def find_original_solution(problem_id):
    pid  = to_five_digits(problem_id)
    path = os.path.join(__file__, '..', '..', 'problems', '__problem_hashes')
    path = os.path.normpath(path)
    mapping = {}
    with open(path) as f:
        mapping = json.load(f)
    candidates = []
    for k, v in mapping.items():
        if pid in v:
            candidates = v
            break
    for candidate in candidates:
        if os.path.exists(five_digits_to_solution_file(candidate)):
            return int(candidate)

def main():
    pprint(find_original_solution(63))
    pprint(find_original_solution_file(63))
    pprint(find_original_solution(666))
    pprint(find_original_solution_file(666))

if __name__ == "__main__":
    main()
