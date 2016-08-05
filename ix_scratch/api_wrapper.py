import re

import requests
import json

headers = {
    'Expect': '',
    'X-API-Key': '118-b9f09e59e76bd290bfec1b0513304002',
}


def get_snapshots_list():
    r = requests.get('http://2016sv.icfpcontest.org/api/snapshot/list', headers=headers)
    j = r.json()
    
    if j['ok']:
        return j['snapshots']
    else:
      raise Exception("Couldn't retrieve snapshots")

def get_latest_snapshot_hash():
    snapshots_dict = get_snapshots_list()

    latest = snapshots_dict[-1]
    return latest['snapshot_hash']

def blob_lookup(lhash):
    url = 'http://2016sv.icfpcontest.org/api/blob/' + lhash
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
      return r
    else:
      raise Exception("Couldn't retrieve the blob")

def get_problem(lhash):
    r = blob_lookup(lhash)
    return r.text

def get_solution(lhash):
    r = blob_lookup(lhash)
    return r.text

def get_snaphot(lhash):
    r = blob_lookup(lhash)
    return r.json()

def submit_problem(solution_spec_file, publish_time):
    s = {'solution_spec' : open(solution_spec_file, 'rb')}
    t = {'publish_time' : publish_time}

    requests.post('http://2016sv.icfpcontest.org/api/problem/submit', data=t, files=s, headers=headers)

def submit_solution(problem_id, solution_spec_file):
    p = {'problem_id' : problem_id}
    s = {'solution_spec' : open(solution_spec_file, 'rb')}

    requests.post('http://2016sv.icfpcontest.org/api/solution/submit', data=p, files=s, headers=headers)

def main():
    print(get_problem('f4b1a8567108154bae331340a57c68b85df487e0'))

if __name__ == "__main__":
    main()


