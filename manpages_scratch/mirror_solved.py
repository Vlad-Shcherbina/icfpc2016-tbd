import glob
import json
import os
from pprint import pprint
from production.dedup import to_solution_file
from production.ioformats import solution_size

def force_dump(what, where):
    pprint(('Dumping', what, 'to', where))
    with open(where, 'w+') as f:
        f.write(what)

def main():
    path = os.path.join(__file__, '..', '..', 'responses', 'solutions', '*')
    path = os.path.normpath(path)
    for filename in sorted(glob.glob(path)):
        with open(filename) as f:
            d = f.read()
            d = d.split('\n\n')
            for submission in d:
                if submission == '':
                    continue
                x = json.loads(submission)
                if x['res']['resemblance'] == 1.0:
                    solnfilename = to_solution_file(x['res']['problem_id'])
                    if os.path.exists(solnfilename):
                        with open(solnfilename) as g:
                            existing_solution = g.read()
                        if solution_size(existing_solution) > solution_size(x['req']):
                            force_dump(x['req'], solnfilename)
                    else:
                        force_dump(x['req'], solnfilename)

if __name__ == '__main__':
    main()
