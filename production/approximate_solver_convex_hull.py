from production import cg, ioformats
from production import origami_fold as of

from production import api_wrapper as aw

from ix_scratch.convex_hull import fold_to_convex_hull, convex_hull, visualise

import argparse

from time import sleep

def compute_approximate_solution(i):
    print(i)

    try:
        prob = ioformats.load_problem(i)
    except:
        return
    p1 = prob.silhouette[0][0]

    prob = ioformats.center_problem(prob)
    p2 = prob.silhouette[0][0]

    offset = p1 - p2

    pts = [p for f in prob.silhouette for p in f]
    
    hull = convex_hull(pts)
    hull_edges = [of.Edge(a,b) for a,b in cg.get_edges(hull)]
    hull_edges = list(reversed(sorted(hull_edges, key=lambda x: x.length)))

    polys = fold_to_convex_hull([of.unitsq_f()], hull_edges)

    edges =  [e for p in polys for e in p]
    points = list(map(lambda x: [p for e in x for p in e], edges))

    #trpts = [p.trans_points for p in polys]
    #trpts.append(pts)
    #visualise(trpts)

    with open('solutions/%s-ch.txt' % i, 'w') as f:
        sol = of.write_fold(polys, f, offset)
        sol = ioformats.solution_to_str(sol)

    if ioformats.solution_size(sol) < 5000:
        problem_id = int(i)
        try:
            r = aw.submit_solution(problem_id, sol)
            print(r.text)
        except:
            pass


        sleep(1)
        

if __name__ == '__main__':
    # 4461
    # problems = [989, 1456, 2606, 3560, 3852, 3854, 3929, 4008, 4010, 4229, 4236, 4239, 4861, 5195, 5199, 5293, 5311, 5724, 5726, 5907, 5933, 5949]
    #problems = [5195, 5199, 5293, 5311, 5724, 5726, 5907, 5949]
    problems = range(3303, 3766)

    parser = argparse.ArgumentParser(description='Compute approximate solution')
    parser.add_argument(dest='prob_id')
    args = parser.parse_args()
    compute_approximate_solution(args.prob_id)
    #~ for p in problems:
        #~ prob = '{0:05d}'.format(p)
        #~ compute_approximate_solution(prob)
