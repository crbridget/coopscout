import flask
from flask import request, jsonify
import json

app = flask.Flask(__name__) # creates the flask application object, contains data about the application
                            # and also methods that tell the application to do certain actions (e.g. app.run())
app.config["DEBUG"] = True  # starts the debugger

# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

with open('../backend/coopsearch.json', 'r') as file:
    coops = json.load(file)

@app.route('/', methods=['GET']) # maps URL to function
def home():
    return '''<h1>Coop Scout</h1>
    <p>A API for coop job postings on NUworks.</p>'''

# a route to return all of the available entries in our catalog.
@app.route('/api/v1/coops/all', methods=['GET'])
def api_all():
    return jsonify(coops)

app.run()  # method that runs the application server