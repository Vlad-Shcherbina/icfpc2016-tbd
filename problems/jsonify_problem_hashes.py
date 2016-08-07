from pprint import pprint

d = {}

with open('_problem_hashes') as f:
    for x in f:
        xs = x.split('  ')
        i  = (xs[1].split('.'))[0]
        if not (xs[0] in d):
            d[xs[0]] = [i]
        else:
            d[xs[0]].append(i)

pprint(d)
