import json
from pprint import pprint

d = None

with open('__problem_hashes') as f:
    d = json.load(f)

for k, v in d.items():
    with open( v[0] + '.txt' ) as f:
        with open( 'hashed/' + k + '.txt', 'w+' ) as g:
            g.write(f.read())
