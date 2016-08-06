import requests
import pprint
import json
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
    r = req('http://2016sv.icfpcontest.org/api/blob/' + x)
    if r.status_code != 200: # uporno dolbimsja
        sleep(1)
        return getBlob(x)
    return r

r = getSnaps()
snaps = json.loads(r.text)

snap = snaps['snapshots'][-1]['snapshot_hash']

sleep(1)

r       = getBlob(snap)
scores  = json.loads(r.text)
ticks = 0

##########
# conf:

fetched_qty = 936
missed_ids = [ 1758 ]

#
##########
for problem in scores['problems']:
    ticks += 1
    if ticks < fetched_qty and (not problem['problem_id'] in missed_ids):
        continue
    if problem['owner'] == '118':
        continue
    sleep(1)
    h = problem['problem_spec_hash']
    i = problem['problem_id']
    s = problem['problem_size']
    t = getBlob(h).text
    x = len(str(i))
    n = 5 - x
    pprint.pprint(t)
    with open(('0' * n) + str(i) + '.txt', 'w+') as f:
        f.write(t)
with open('.last_tick', 'w+') as f:
    f.write(str(tick))
