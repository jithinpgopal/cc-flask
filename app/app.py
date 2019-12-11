import flask

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/first', methods=['GET'])
def first():
    return '''<h1>Container Crush Testing</h1>
<p>I have no idea what to type here</p>'''

app.run()
