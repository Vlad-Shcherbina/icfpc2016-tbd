import requests
import json
from pprint import pprint
from time import sleep, time

def ak():
	return '118-b9f09e59e76bd290bfec1b0513304002'

def headers():
	return { 'X-API-Key': ak() }

def req(x):
	return requests.get(x, headers = headers())

def getSnaps():
    r = req('http://2016sv.icfpcontest.org/api/snapshot/list')
    if r.status_code != 200: # uporno dolbimsja
        sleep(1)
        return getSnaps()
    return r

def getBlob(x):
    r = req('http://2016sv.icfpcontest.org/api/blob/' + x)
    if r.status_code != 200: # uporno dolbimsja
        sleep(1)
        return getBlob(x)
    return r

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

for problem in d['problems']:

    if problem['owner'] != '118' and False:
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
                   'id': problem['problem_id'], 'solution_size': problem['solution_size'],
                   'hours_ago': (time() - problem['publish_time']) / 3600})

scrunch = sorted(crunch, key=lambda x: x['ones'][0])
pprint(list(map(lambda x: x['id'], scrunch)))
