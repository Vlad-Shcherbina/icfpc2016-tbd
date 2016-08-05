import json
import pprint
import os.path

def db():
    return 'solved.txt'

def touch_or_read(x):
    if not os.path.isfile(x):
        with open(x, 'w+') as f:
            return ''
    else:
        with open(x) as f:
            return f.read()

def write_set(t, xs):
    with open(t, 'w') as f:
        json.dump(list(xs), f)

def mark_solved(x):
    xs = set(json.loads(touch_or_read(db())))
    xs.add(x)
    write_set(db(), xs)

def unmark_solved(x):
    xs = set(json.loads(touch_or_read(db())))
    try:
        xs.remove(x)
        write_set(db(), xs)
    except:
        return
