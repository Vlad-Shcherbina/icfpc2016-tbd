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

solved_problems = [1,2,3,4,5,6,7,8,9,10,
                   11,12,13,14,15,16,17,18,
                   25,27,
                   36,37,38,39,
                   40,42,43,44,45,46,47,48,49,
                   50,53,55,56,57,58,59,
                   62,63,
                   83]

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
unsolved = list(filter((lambda x: x['ones'][0] == 0), scrunch))

fmt = '{id:>6}{solution_size:>6}{ones[0]:>8}{hours_ago:>10}'
print(fmt.format(
        id='id', solution_size='size', ones=('#exact', 0), hours_ago='ago(h)'))
#for q in sorted(scrunch, key=lambda q: q['hours_ago']):
for q in scrunch:
    q['hours_ago'] = int(q['hours_ago'])
    print(fmt.format(**q))

print("unsolved:")
pprint(list(map(lambda x: x['id'], unsolved)))
print("unsolved qty:")
print(len(unsolved))
