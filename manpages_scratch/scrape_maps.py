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
	return req('http://2016sv.icfpcontest.org/api/blob/' + x)

r = getSnaps()
snaps = json.loads(r.text)

snap = snaps['snapshots'][-1]['snapshot_hash']

sleep(1)

r       = getBlob(snap)
scores  = json.loads(r.text)

for problem in scores['problems']:
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
