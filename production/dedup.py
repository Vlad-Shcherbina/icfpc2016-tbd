import os
import json
from pprint import pprint
from production.ioformats import get_root

map_hash_to_ids, map_id_to_hash = None, None 
def load_mapping():
    global map_hash_to_ids, map_id_to_hash
    if map_hash_to_ids is not None: return
    path = os.path.join(__file__, '..', '..', 'problems', '__problem_hashes')
    path = os.path.normpath(path)
    with open(path) as f:
        map_hash_to_ids = json.load(f)
    map_id_to_hash = {id:k for k, v in map_hash_to_ids.items() for id in v}
        
    
def to_five_digits(x):
    n = len(str(x))
    z = '0' * (5 - n)
    return z + str(x)

def to_solution_file(x):
    return five_digits_to_solution_file(to_five_digits(x))

def five_digits_to_solution_file(five_digits):
    return str((get_root() / 'solutions' / 'solved_{}.txt'.format(five_digits)).resolve())

def find_original_solution_file(problem_id):
    maybe_orig = find_original_solution(problem_id)
    if maybe_orig == None:
        return maybe_orig
    else:
        return to_solution_file(maybe_orig)

def get_collisions(problem_id):
    load_mapping()
    hash = map_id_to_hash.get(to_five_digits(problem_id))
    if hash:
        return map_hash_to_ids[hash]
    return []

def get_thingies():
    load_mapping()
    tosort = []
    for k, v in map_hash_to_ids.items():
        tosort.append( (v[0], len(v) ))
    return sorted(tosort, key=lambda x: x[1])

def find_original_solution(problem_id):
    for candidate in get_collisions(problem_id):
        if os.path.exists(five_digits_to_solution_file(candidate)):
            return int(candidate)

def main():
    pprint(find_original_solution(63))
    pprint(find_original_solution_file(63))
    pprint(find_original_solution(666))
    pprint(find_original_solution_file(666))

if __name__ == "__main__":
    main()
