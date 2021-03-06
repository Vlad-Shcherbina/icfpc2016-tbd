from sys import argv
from math import sqrt
import argparse

from production import cg, ioformats

import production.origami_fold as of


'''
Use validate_file, validate_string, validate_solution from end programms
according to the type you want to validate.
'''

def validate_file(sol_num):
    print('Validating solution #%s' % sol_num)
    
    with open('solutions/%s.txt' % sol_num) as f:
        sol_str = f.read()
    if ioformats.solution_size(sol_str) > 5000:
        return (False, "Solution too long")

    sol = ioformats.parse_solution(sol_str)

    return validate(sol)

def validate_string(sol, sol_num=None):
    if sol_num is not None:
      print('Validating solution #%d' % sol_num)
    
    if ioformats.solution_size(sol_str) > 5000:
        return (False, "Solution too long")

    sol = ioformats.parse_solution(sol_str)

    return validate(sol)

def validate_solution(sol, sol_num=None):
    if sol_num is not None:
      print('Validating solution #%d' % sol_num)
    
    sol_str = ioformats.solution_to_str(sol)

    if ioformats.solution_size(sol_str) > 5000:
        return (False, "Solution too long")

    return validate(sol)


def validate(sol):

    # every point appears exactly once
    if len(sol.orig_points) > len(set(sol.orig_points)):
        return (False, "Coordinates appear repeatedly in the source positions")
    
    for p in sol.orig_points:
        if not cg.point_inside_unit_square(p):
            return (False, "Source vertix(ces) outside unit square")
    
    for f1 in sol.facets:

        # Check that any edge of any facet has length greater than zero
        if len(f1) > len(set(f1)):
            return (False, "Facet edge length is zero")

        # check that transformation was congruent
        if not transformed_congruently(sol.orig_points, f1, sol.dst_points):
            return (False, "Facet was not transformed congruently")

        '''
        This right now solves three validation problems:
        - all facet polygons should be simple
        - the intersection set of any two different facets should have zero area
        - if two different edges share a point, the point should always be
        one of the endpoints for both the edges
        With shitty quadratic approaches. Will optimizing it require several passes?
        '''
        for f2 in sol.facets:
            if do_facets_intersect(sol.orig_points, f1, f2):
                return (False, "The edges or facets are intersecting")
    s = 0
    for f in sol.facets:
        vs = list(map((lambda x: sol.orig_points[x]), f))
        s += union_polygon_area(vs)
    if s != 1:
        return (False, "Union set does not equal the unit square")


    return True

def union_polygon_area(vertices):
    return abs(cg.polygon_area(vertices))

def transformed_congruently(op, facet, dp):
    edges = cg.get_edges(op, facet)

    for p1,p2 in edges:
        oa = of.Edge(op[p1], op[p2]).a
        da = (of.Edge(dp[p1], dp[p2])).a

        orig_edge_len = sqrt(oa.dot(oa))
        dest_edge_len = sqrt(da.dot(da))

        if abs(orig_edge_len) != abs(dest_edge_len):
            return False

    return True


def do_facets_intersect(op, f1, f2):
    '''
    Note that this is a shitty naive O(n^2) version.
    Is this good enough for our use case?
    See: Bentley-Ottmann algorithm
    '''

    for edge1 in cg.get_edges(f1):
        edge1 = op[edge1[0]], op[edge1[1]]
        for edge2 in cg.get_edges(f2):
            edge2 = op[edge2[0]], op[edge2[1]]
            if cg.edge_intersection_not_at_endpoints(edge1, edge2) is not None:
                return True

    return False


def main():
    parser = argparse.ArgumentParser(description='Validate solution in a file')
    parser.add_argument(dest='sol_id')
    args = parser.parse_args()
    sol_id = args.sol_id
    v = validate_file(sol_id)
    if v is True:
        print("Solution validated")
    else:
        print("Solution incorrect: ", v[1])

 
if __name__ == "__main__":
    main()
