import requests

from time import sleep

from pprint import pprint
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
# publish_time :: int
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
        

# problem_id :: utctime
# solution_spec :: str
def submit_solution(problem_id, solution_spec, file=False):
    p = {'problem_id' : problem_id}
    
    if file:
        solution_spec = open(solution_spec, 'r')
        solution_spec = solution_spec.read()
    s = {'solution_spec' : solution_spec}

    r = requests.post('http://2016sv.icfpcontest.org/api/solution/submit', data=p, files=s, headers=headers)
    if r.status_code == 200:
        with open('responses/solutions/%s' % problem_id, 'a') as f:
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


