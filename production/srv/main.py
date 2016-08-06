from bottle import route, run, error
from pprint import pprint
from production import api_wrapper

@route('/hello')
def hello():
    return { 'ok': True, 'greeting': 'Hello, world!' }

@route('/blob/<hash>')
def blob(hash):
    pprint(hash)
    if hash == None:
        return error404()
    else:
        return 'Weee'


@error(404)
def error404(x):
    return str(x)

run(host='0.0.0.0', port = 8340, debug = True)
