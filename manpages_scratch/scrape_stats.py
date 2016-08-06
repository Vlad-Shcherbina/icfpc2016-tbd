import requests
import json
from pprint import pprint
from time import sleep

def ak():
	return '118-b9f09e59e76bd290bfec1b0513304002'

def headers():
	return { 'X-API-Key': ak() }

def req(x):
	return requests.get(x, headers = headers())

def getSnaps():
	return req('http://2016sv.icfpcontest.org/api/snapshot/list')

def getBlob(x):
	return req('http://2016sv.icfpcontest.org/api/blob/' + x)

def loadJson(x):
    with open(x) as f:
        return json.load(f)

r = getSnaps()
snaps = json.loads(r.text)

snap = snaps['snapshots'][-1]['snapshot_hash']

sleep(1)

r = getBlob(snap)
#print(r.text)
d = json.loads(r.text)

#d = loadJson('stats_24.txt')

crunch = []

solved_problems = [1,2,3,4,5,6,7,8,9,10,
                   11,12,13,14,15,16,17,18,
                   25,27,
                   36,37,38,39,
                   40,42,43,44,45,46,47,48,49,
                   50,53,55,56,57,58,59,
                   62,63,
                   83]

for problem in d['problems']:

    if not problem['problem_id'] in solved_problems:
        continue

    ones = 0
    size_ones = 0
    partials = 0
    size_partials = 0

    for res in problem['ranking']:
        if res['resemblance'] == 1.0:
            ones += 1
            size_ones += res['solution_size']
        else:
            partials += 1
            size_partials += res['solution_size']

    crunch.append({'ones': (ones, size_ones), 'partials': (partials, size_partials),
                   'id': problem['problem_id'], 'size': problem['problem_size']})

scrunch = sorted(crunch, key=lambda x: x['ones'][0])

pprint(scrunch)
