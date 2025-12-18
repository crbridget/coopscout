import flask
from flask import request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

def handle_supabase_query(query_function):
    """Wrapper to handle Supabase errors"""
    try:
        response = query_function()
        if response.data is None:
            return jsonify({"error": "No data found"}), 404
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

# Initialize Supabase
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")  # store in .env file
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Coop Scout</h1>
    <p>An API for coop job postings on NUworks.</p>'''

@app.route('/api/v1/jobs/all', methods=['GET'])
def api_all():
    response = supabase.table('jobs').select("*").execute()
    return jsonify(response.data)

@app.route('/api/v1/jobs', methods=['GET'])
def api_filter():
    query = supabase.table('jobs').select("*")
    
    if 'title' in request.args:
        query = query.ilike('title', f'%{request.args["title"]}%')
    
    if 'location' in request.args:
        query = query.ilike('location', f'%{request.args["location"]}%')
    
    if 'company' in request.args:
        query = query.ilike('company', f'%{request.args["company"]}%')
    
    response = query.execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run()