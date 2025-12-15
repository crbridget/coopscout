import flask
from flask import request, jsonify
import json

app = flask.Flask(__name__) # creates the flask application object, contains data about the application
                            # and also methods that tell the application to do certain actions (e.g. app.run())
app.config["DEBUG"] = True  # starts the debugger


with open('../backend/coopsearch.json', 'r') as file:
    coops = json.load(file)

@app.route('/', methods=['GET']) # maps URL to function
def home():
    return '''<h1>Coop Scout</h1>
    <p>An API for coop job postings on NUworks.</p>'''

# a route to return all of the available entries in our catalog.
@app.route('/api/v1/coops/all', methods=['GET'])
def api_all():
    return jsonify(coops)

app.run()  # method that runs the application server