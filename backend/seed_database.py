""" For manual seeding of database """

from supabase import create_client
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")  # store in .env file
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

with open('../backend/coopsearch.json', 'r') as file:
    jobs = json.load(file)

# Insert all coops
for job in jobs:
    supabase.table('jobs').insert(job).execute()

print(f"Uploaded {len(jobs)} job")