from PyFwk import PyFwk

app = PyFwk()

@app.route('/index', methods = ['GET'])
def index():
    return 'This is a router test page'

@app.route('/test/js')
def test_js():
    return '<script src="/static/test.js"></script>'

app.run()

