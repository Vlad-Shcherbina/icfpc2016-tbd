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

#r = getSnaps()
#snaps = json.loads(r.text)

#snap = snaps['snapshots'][-1]['snapshot_hash']

#sleep(1)

#r      = getBlob(snap)
#print(r.text)

d = loadJson('stats_24.txt')

for problem in d['problems']:
    pprint(problem['problem_id'])
    pprint(problem['problem_size'])

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

    pprint(ones)
    pprint(size_ones)
    pprint(partials)
    pprint(size_partials)

    pprint('===')
