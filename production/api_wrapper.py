import time
import requests

from time import sleep

from pprint import pprint
import json
from production.ioformats import get_root

headers = {
    'Expect': '',
    'X-API-Key': '118-b9f09e59e76bd290bfec1b0513304002',
}

class RateLimiter():
    def __init__(self):
        self.delay = 1.0
        self.last_time = None
    
    def sleep(self):
        t = time.time()
        if self.last_time is not None:
            sleep_for = self.delay - (t - self.last_time)
            if sleep_for > 0:
                print('Sleeping for {}'.format(sleep_for))
                time.sleep(sleep_for)
        
    def __call__(self, request):
        while True:
            self.sleep()
            r = request()
            return r
        

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

# lhash :: str
def blob_lookup(lhash):
    url = 'http://2016sv.icfpcontest.org/api/blob/' + lhash
    print(url)
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r
    else:
        print(r.text)
        raise Exception("Couldn't retrieve the blob")

# lhash :: str
def get_problem(lhash):
    r = blob_lookup(lhash)
    return r.text

# lhash :: str
def get_solution(lhash):
    r = blob_lookup(lhash)
    return r.text

# lhash :: str
def get_snapshot(lhash):
    r = blob_lookup(lhash)
    return r.json()


'''
solution_spec_file should be a valid path to a solution file
'''
# solution_spec_file :: str
# publish_time :: utctime
def submit_problem(publish_time, solution_spec_file):
    s = {'solution_spec' : open(solution_spec_file, 'r').read()}
    t = {'publish_time' : publish_time}

    r = requests.post('http://2016sv.icfpcontest.org/api/problem/submit', data=t, files=s, headers=headers)

    if r.status_code == 200:
        # makes sense to overwrite the file since we're only publishing the last submission
        with open('responses/problems/%d' % publish_time, 'w') as f:
            dat = {'req': {{**s, **t}},
                   'res': r.json()}
            json.dump(dat, f)
            f.write('\n\n')
        return r
    elif r.status_code == 429:
        sleep(1)
        return submit_problem(publish_time, solution_spec_file)
    else:
        pprint((r.status_code, r.text))
        raise Exception("Couldn't submit the problem")


class ServerRejectedError(Exception):
    pass

# problem_id :: int
# solution_spec :: str
def submit_solution(problem_id, solution_spec, file=False):
    p = {'problem_id' : problem_id}
    
    if file:
        solution_spec = open(solution_spec, 'r')
        solution_spec = solution_spec.read()
    s = {'solution_spec' : solution_spec}

    r = requests.post('http://2016sv.icfpcontest.org/api/solution/submit', data=p, files=s, headers=headers)
    if r.status_code == 200:
        with (get_root() / 'responses' / 'solutions' / str(problem_id)).open('a') as f:
            dat = {
                   'req': solution_spec,
                   'res': r.json()
                  }
            json.dump(dat, f)
            f.write('\n\n')
        return r
    elif r.status_code == 429:
        sleep(1)
        return submit_solution(problem_id, solution_spec)
    elif r.status_code == 400:
        raise ServerRejectedError(r.json()['error']) 
    else:
        pprint((r.status_code, r.text))
        raise Exception("Couldn't submit the solution")


'''
This function sleeps for 1 second after every submission so as to support painless submission
(due to the constraint of 1 query per second)
'''
def s_submit_solution(problem_id, solution_spec, file=False):
    r = submit_solution(problem_id, solution_spec, file)
    sleep(1)
    return r


def main():
    # test problem lookup

    # test solution submission
    submit_solution(1, 'solutions/001.txt', True)

if __name__ == "__main__":
    main()


