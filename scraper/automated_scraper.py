import sys
import os
import pickle
from datetime import datetime

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from scraper import scrape_with_cookies, NUWorksScraper
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join('.env'))

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ADMIN COOKIES - Used for all users
ADMIN_COOKIES_FILE = 'cookies_admin.pkl'


def validate_cookies(cookies):
    """Test if cookies are still valid by attempting to access the job page"""
    print("Validating cookies...")
    scraper = NUWorksScraper(headless=True)

    try:
        scraper.initialize_driver()
        scraper.navigate_to_page()
        scraper.login_with_cookies(cookies)

        # Check if we're actually logged in
        if "signin" in scraper.driver.current_url.lower() or "sign-in" in scraper.driver.title.lower():
            print("Cookies are INVALID or EXPIRED")
            return False

        print("Cookies are valid!")
        return True

    except Exception as e:
        print(f"Cookie validation failed: {e}")
        return False
    finally:
        scraper.close()


def save_fresh_cookies():
    """Prompt user to generate fresh cookies"""
    print("\n" + "!" * 60)
    print("COOKIES ARE EXPIRED - FRESH LOGIN REQUIRED")
    print("!" * 60)
    print("\nYou need to generate fresh cookies. Here's how:")
    print("\n1. Run: python save_user_cookies.py")
    print("2. Complete Duo authentication")
    print("3. Rename the output file to: cookies_admin.pkl")
    print("4. Run this script again")
    print("\nOR")
    print("\nProvide credentials for automatic re-login:")

    username = input("Enter username (or press Enter to skip): ").strip()
    if not username:
        return None

    password = input("Enter password: ").strip()
    if not password:
        return None

    print("\nAttempting to generate fresh cookies...")

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    duo_wait = WebDriverWait(driver, 60)

    try:
        driver.get("https://northeastern-csm.symplicity.com/students/?signin_tab=0")

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[value='Current Students and Alumni']")
        )).click()

        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.send_keys(username)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("Sending Duo push... (check your phone!)")
        duo_iframe = wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        driver.switch_to.frame(duo_iframe)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Send Me a Push')]")
        )).click()
        driver.switch_to.default_content()

        print("Waiting for Duo approval...")
        duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))

        print("Login successful! Navigating to job page...")
        driver.get("https://northeastern-csm.symplicity.com/students/index.php?mode=list&s=jobs")
        time.sleep(5)

        if "signin" in driver.current_url.lower():
            raise Exception("Still on login page after authentication!")

        cookies = driver.get_cookies()

        with open(ADMIN_COOKIES_FILE, 'wb') as f:
            pickle.dump(cookies, f)

        print(f"✓ Saved {len(cookies)} fresh cookies to {ADMIN_COOKIES_FILE}")
        return cookies

    except Exception as e:
        print(f"ERROR: Failed to generate fresh cookies: {e}")
        return None
    finally:
        driver.quit()


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

    # Load admin cookies
    print("Loading admin cookies...")
    with open(ADMIN_COOKIES_FILE, 'rb') as f:
        admin_cookies = pickle.load(f)
    print(f"Loaded {len(admin_cookies)} cookies\n")

    # Validate cookies before proceeding
    if not validate_cookies(admin_cookies):
        print("\nAttempting to generate fresh cookies...")
        admin_cookies = save_fresh_cookies()

        if not admin_cookies:
            print("\nCannot proceed without valid cookies. Exiting...")
            return

        # Validate the new cookies
        if not validate_cookies(admin_cookies):
            print("\nFresh cookies are still invalid. Please check manually.")
            return

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

        print(f"\n{'=' * 60}")
        print(f"Processing: {email}")
        print(f"Major: {major}")
        print(f"{'=' * 60}")

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

                    # Clean numeric fields - convert "Not listed" to None
                    if job.get('minimum_gpa') == 'Not listed':
                        job['minimum_gpa'] = None
                    if job.get('compensation') == 'Not listed':
                        job['compensation'] = None

                    # Check if job already exists for this user
                    existing = supabase.table('jobs') \
                        .select('id') \
                        .eq('user_id', user_id) \
                        .eq('title', job['title']) \
                        .eq('company', job['company']) \
                        .execute()

                    if existing.data:
                        print(f"  SKIPPED: Duplicate - {job['title']} at {job['company']}")
                        continue

                    # Insert only if it doesn't exist
                    supabase.table('jobs').insert(job).execute()
                    jobs_added += 1

                except Exception as e:
                    # Check if it's a duplicate error from database constraint
                    if 'unique_user_job' in str(e) or '23505' in str(e):
                        print(
                            f"  SKIPPED: Duplicate - {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                    else:
                        print(f"  WARNING: Could not insert job: {e}")
                    continue

            print(f"SUCCESS: Added {jobs_added} jobs for {email}")
            total_jobs_added += jobs_added
            successful_users += 1

        except Exception as e:
            print(f"ERROR: Failed to scrape for {email}: {e}")
            import traceback
            print(traceback.format_exc())
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