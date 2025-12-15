import flask
from flask import request, jsonify
import json
from flask_cors import CORS

app = flask.Flask(__name__) # creates the flask application object, contains data about the application
                            # and also methods that tell the application to do certain actions (e.g. app.run())

CORS(app) # Enable CORS for frontend requests
app.config["DEBUG"] = True  # starts the debugger


try:
    with open('../backend/coopsearch.json', 'r') as file:
        coops = json.load(file)
except FileNotFoundError:
    coops = []
    print("Warning: coopsearch.json not found")

@app.route('/', methods=['GET']) # maps URL to function
def home():
    return '''<h1>Coop Scout</h1>
    <p>An API for coop job postings on NUworks.</p>'''

# a route to return all of the available entries in our catalog.
@app.route('/api/v1/coops/all', methods=['GET'])
def api_all():
    return jsonify(coops)


@app.route('/api/v1/coops', methods=['GET'])
def api_filter():
    results = coops
    
    # Filter by title
    if 'title' in request.args:
        query = request.args['title'].lower()
        results = [c for c in results if query in c.get('title', '').lower()]
    
    # Filter by location
    if 'location' in request.args:
        location = request.args['location'].lower()
        results = [c for c in results if location in c.get('location', '').lower()]
    
    # Filter by company
    if 'company' in request.args:
        company = request.args['company'].lower()
        results = [c for c in results if company in c.get('company', '').lower()]
    
    return jsonify(results)

if __name__ == '__main__':
    app.run()