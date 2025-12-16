import sys
import os
import pickle
from datetime import datetime

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from scraper import scrape_with_cookies
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join('.env'))

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ADMIN COOKIES - Used for all users
ADMIN_COOKIES_FILE = 'cookies_admin.pkl'

def scrape_for_all_users():
    """
    Automated scraper: Uses admin cookies to scrape personalized jobs for each user
    """
    print("\n" + "=" * 60)
    print(f"AUTOMATED SCRAPER - {datetime.now()}")
    print("=" * 60 + "\n")

    # Check if admin cookies exist
    if not os.path.exists(ADMIN_COOKIES_FILE):
        print(f"ERROR: Admin cookies not found!")
        print(f"   Please run: python save_user_cookies.py")
        print(f"   Then rename the cookies file to: {ADMIN_COOKIES_FILE}")
        return

    # Load admin cookies ONCE
    print("Loading admin cookies...")
    with open(ADMIN_COOKIES_FILE, 'rb') as f:
        admin_cookies = pickle.load(f)
    print("Admin cookies loaded\n")

    # Get all users from database
    response = supabase.table('users').select('*').execute()
    users = response.data

    if not users:
        print("ERROR: No users found in database")
        return

    print(f"Found {len(users)} users in database\n")

    # Scrape for each user
    total_jobs_added = 0
    successful_users = 0
    failed_users = 0

    for user in users:
        user_id = user['id']
        email = user['email']
        major = user.get('major', 'Computer Science')

        print(f"\n{'='*60}")
        print(f"Processing: {email}")
        print(f"Major: {major}")
        print(f"{'='*60}")

        try:
            print("Starting scrape...")

            # Use ADMIN cookies to scrape based on THIS user's major
            jobs = scrape_with_cookies(
                cookies=admin_cookies,
                search_term=major,
                location='Boston, MA, USA',
                max_jobs=20
            )

            print(f"Scraper returned {len(jobs)} jobs")

            # Save jobs to database with THIS user's ID
            jobs_added = 0
            for job in jobs:
                try:
                    job['user_id'] = user_id
                    job['status'] = 'active'
                    supabase.table('jobs').insert(job).execute()
                    jobs_added += 1
                except Exception as e:
                    print(f"  WARNING: Could not insert job: {e}")
                    continue

            print(f"SUCCESS: Added {jobs_added} jobs for {email}")
            total_jobs_added += jobs_added
            successful_users += 1

        except Exception as e:
            print(f"ERROR: Failed to scrape for {email}: {e}")
            failed_users += 1
            continue

    # Print summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successful: {successful_users} users")
    print(f"Failed: {failed_users} users")
    print(f"Total jobs added: {total_jobs_added}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    scrape_for_all_users()