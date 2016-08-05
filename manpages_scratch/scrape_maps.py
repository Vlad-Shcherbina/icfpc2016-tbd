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

#r = getSnaps()
#snaps = json.loads(r.text)

snaps = {'ok': True,
		 'snapshots': [{'snapshot_hash': '89c4c40226f4efcdb8fc58c9f74339d768ef4737',
						'snapshot_time': 1470322800},
					   {'snapshot_hash': '055ed1e43c6c8632c2a980476fa48068ab6cb668',
						'snapshot_time': 1470326400},
					   {'snapshot_hash': '704c2e572cac17af59449d2faf6003d3f98d35d2',
						'snapshot_time': 1470330000},
					   {'snapshot_hash': '7eb37ebb9131198accaf9a5676b85a61aa547028',
						'snapshot_time': 1470333600},
					   {'snapshot_hash': '28815b002de153ffffd43e8026ded96ffe6c6170',
						'snapshot_time': 1470337200},
					   {'snapshot_hash': 'b8bea9c89823058ece06e7ebb882e95790408284',
						'snapshot_time': 1470340800},
					   {'snapshot_hash': '7de2715006b5c1d802858a8012aa06b46b0b315e',
						'snapshot_time': 1470344400},
					   {'snapshot_hash': '3c2462860b559c38f18149f98e61aa8315245a94',
						'snapshot_time': 1470348000},
					   {'snapshot_hash': '14d559294d8cf3d473eb639c7304add7ad678b37',
						'snapshot_time': 1470351600},
					   {'snapshot_hash': 'cb852d8e9ab6a1e9fbb2d471e30427fbad8097d6',
						'snapshot_time': 1470355200},
					   {'snapshot_hash': 'e613b3bbddf467b39c630d8c290c9d19ce11169c',
						'snapshot_time': 1470358800},
					   {'snapshot_hash': 'd3b221f5606083d47a1470ce875260aa0c147381',
						'snapshot_time': 1470362400},
					   {'snapshot_hash': '96cc9812b3184075bec9fd338fb1e19d1e19939e',
						'snapshot_time': 1470366000},
					   {'snapshot_hash': '1993d89195acf1850a16fcc80d636f30025dcb6e',
						'snapshot_time': 1470369600},
					   {'snapshot_hash': '4d3b2ee8773c21ff32648794d3e223708dcdd558',
						'snapshot_time': 1470373200},
					   {'snapshot_hash': 'a731dbc3f15008225521b9fa07f2b3de9e0990fd',
						'snapshot_time': 1470376800},
					   {'snapshot_hash': 'd79685e4bfad1cc701b452946cf9aefd366b45d1',
						'snapshot_time': 1470380400},
					   {'snapshot_hash': 'bbe7d278079a690055aab5a142688983fcf0d118',
						'snapshot_time': 1470384000},
					   {'snapshot_hash': '350b800138654c05b74f97000287b6cee0286271',
						'snapshot_time': 1470387600},
					   {'snapshot_hash': '660dc08eae605f704660f404d692b140301fadcc',
						'snapshot_time': 1470391200},
					   {'snapshot_hash': '3f4c0486850fe179d7aa2de0dccc42f6779707ca',
						'snapshot_time': 1470394800},
					   {'snapshot_hash': '907fe93cbbe4143cebccf6d3c646cdf4e00a72cc',
						'snapshot_time': 1470398400},
					   {'snapshot_hash': 'dee0d45c2146c5cc3e818ed4384caaf975d5c48a',
						'snapshot_time': 1470402000},
					   {'snapshot_hash': '3dd205103fbe55c4674e419168cc2c7fdaba3e53',
						'snapshot_time': 1470405600},
					   {'snapshot_hash': '5316e3b9d3224e6ef99a5220e8f3dcab5e58bb0d',
						'snapshot_time': 1470409200}]}

snap = snaps['snapshots'][-1]['snapshot_hash']

sleep(1)

#r      = requests.get(url1, headers=headers)
#scores = json.loads(r.text)

with open('/tmp/toscrape') as f:
	scores = json.load(f) 

for problem in scores['problems'][71:]:
	sleep(1)
	h = problem['problem_spec_hash']
	i = problem['problem_id']
	s = problem['problem_size']
	t = getBlob(h).text
	pprint.pprint(t)
	with open(str(s) + '-' + h + '-' + str(i) + '.problem', 'w+') as f:
		f.write(t)
