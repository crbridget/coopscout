from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import pandas as pd
from profiler import Profiler, profile
import time
from retry import retry_on_failure
from datetime import datetime

# load the env file 
load_dotenv()

# retrieve the username and password information
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# global variables
URL = "https://northeastern-csm.symplicity.com/students/?signin_tab=0"
SEARCH = "software engineering"
LOCATION = "Boston, MA, USA"

import json
from datetime import datetime


class WebScraper:

    def __init__(self):
        """ Constructor """
        self.chrome_options = Options()
        self.errors = []
        self.failed_jobs = []
        self.previous_jobs = {}  # Store previous job data
        print("🚀 CoopScout initialized!")

    def load_previous_scrape(self, filename='coopsearch.json'):
        """Load the previous scrape to compare against"""
        try:
            with open(filename, 'r') as f:
                previous_data = json.load(f)

            # Create a dict with job title + company as key for fast lookup
            for job in previous_data:
                # Use title + company as unique identifier
                job_key = f"{job.get('title', '')}|{job.get('company', '')}"
                self.previous_jobs[job_key] = job

            print(f" Loaded {len(self.previous_jobs)} jobs from previous scrape")
            return True
        except FileNotFoundError:
            print(" No previous scrape found - all jobs will be marked as NEW")
            return False
        except Exception as e:
            print(f"  Error loading previous scrape: {e}")
            return False

    def is_new_job(self, job_title, company_name):
        """Check if a job is new compared to previous scrape"""
        job_key = f"{job_title}|{company_name}"
        return job_key not in self.previous_jobs

    def compare_jobs(self, current_jobs):
        """Compare current jobs against previous scrape"""
        new_jobs = []
        existing_jobs = []

        # Track which previous jobs are still active
        still_active = set()

        for job in current_jobs:
            job_key = f"{job['title']}|{job['company']}"

            if job_key in self.previous_jobs:
                job['status'] = 'EXISTING'
                existing_jobs.append(job)
                still_active.add(job_key)
            else:
                job['status'] = 'NEW'
                new_jobs.append(job)

        # Find removed jobs (in previous but not in current)
        removed_jobs = []
        for job_key, job_data in self.previous_jobs.items():
            if job_key not in still_active:
                removed_jobs.append(job_data)

        return new_jobs, existing_jobs, removed_jobs

    @profile
    def initialize_driver(self):
        print("🔧 Starting Chrome driver...")
        self.chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        print("✓ Chrome driver ready")

    @profile
    def initalize_wait(self):
        self.wait = WebDriverWait(self.driver, 10)
        self.duo_wait = WebDriverWait(self.driver, 60)

    @profile
    def navigate_to_page(self, url):
        """ """
        print(f" Navigating to NUworks...")
        self.driver.get(url)
        print("✓ Page loaded")

    @profile
    def login(self, username, password):
        """ Login to NUworks with users user and password and then send a duo push to the user """
        print(" Logging in...")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Current Students and Alumni']"))).click()

        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.send_keys(username)

        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print(" Sending Duo push... (check your phone!)")
        duo_iframe = self.wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        self.driver.switch_to.frame(duo_iframe)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Me a Push')]"))).click()

        self.driver.switch_to.default_content()
        print(" Waiting for Duo approval...")
        self.duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))
        print("✓ Login successful!")

    @profile
    def search(self, search):
        """ Search for a job or key word in the NUworks main search """
        print(f" Searching for '{search}'...")

        time.sleep(2)

        # Click the search toggle button to open the search bar
        search_toggle = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.quicksearch-toggle")))
        search_toggle.click()
        time.sleep(1)

        # Now type in the search field
        search_bar = self.wait.until(EC.visibility_of_element_located((By.ID, "quicksearch-field")))
        search_bar.click()
        search_bar.send_keys(search)
        search_bar.send_keys(Keys.ENTER)

        time.sleep(2)  # Wait for search results to load
        print(" Search submitted")

    @profile
    def get_job_results(self):
        print(" Loading job results...")

        time.sleep(3)

        # Find the link
        job_results_link = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='See all job results']")))

        # Scroll it into view
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_results_link)
        time.sleep(1)

        # Click using JavaScript to bypass any overlays
        self.driver.execute_script("arguments[0].click();", job_results_link)

        time.sleep(3)  # Wait for new page to load

        # DEBUG: See what page we landed on
        print(" Debugging - Checking what page we're on after clicking...")
        print(f"Current URL: {self.driver.current_url}")

        # Look for job listings
        job_titles = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'title') or contains(@class, 'job')]")
        print(f"\nFound {len(job_titles)} elements with 'title' or 'job' in class:")
        for elem in job_titles[:10]:
            text = elem.text.strip()
            if text:
                print(f"  - '{text[:60]}' (tag: {elem.tag_name}, class: {elem.get_attribute('class')[:50]})")

        # Look for list items
        list_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item')]")
        print(f"\nFound {len(list_items)} list-item divs")

        print("Job results page loaded")

    @profile
    def filter_by_location(self, location):
        print(f"Filtering by location: {location}...")
        location_bar = self.wait.until(EC.element_to_be_clickable((By.ID, "jobs-location-input")))
        location_bar.send_keys(location + Keys.ENTER)
        time.sleep(2)
        print("Location filter applied")

    @profile
    def filter_by_coop(self):
        print("Filtering for Co-op positions...")

        time.sleep(2)

        # Find the checkbox (even if not clickable)
        coop_checkbox = self.driver.find_element(By.ID, "job_type-checkbox-0")

        # Scroll to it
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", coop_checkbox)
        time.sleep(1)

        # Click using JavaScript
        self.driver.execute_script("arguments[0].click();", coop_checkbox)
        time.sleep(2)

        print("Co-op filter applied")

    @profile
    def scrape_company(self):
        try:
            company_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3.space-right-sm.text-overflow")))
            return company_element.text.strip()
        except Exception as e:
            error_msg = f"Failed to scrape company: {str(e)}"
            self.errors.append(error_msg)
            print(f"        {error_msg}")
            return "Not listed"

    @profile
    def scrape_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_location_"]')
            return location_element.text.strip()
        except Exception as e:
            return "Not listed"

    @profile
    def scrape_deadline(self):
        try:
            deadline_element = self.driver.find_element(By.ID, "sy_formfield_job_deadline")
            return deadline_element.text.strip()
        except Exception as e:
            return "Not listed"

    @profile
    def scrape_compensation(self):
        try:
            compensation_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_compensation_"]')
            return compensation_element.text.strip()
        except Exception as e:
            return "Not listed"

    @profile
    def scrape_major(self):
        try:
            major_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_targeted_academic_majors_"]')
            return major_element.text.strip()
        except Exception as e:
            return "Not listed"

    @profile
    def scrape_min_gpa(self):
        try:
            min_gpa = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_screen_gpa_"]')
            return min_gpa.text.strip()
        except Exception as e:
            return "Not listed"

    @profile
    def scrape_description(self):
        try:
            description_div = self.driver.find_element(By.CSS_SELECTOR, "div.field-widget-tinymce")
            return description_div.text
        except Exception as e:
            return "Not listed"

    @profile
    def next_page(self):
        try:
            next_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Next"]]')
            # Scroll to the button (just like you do for job titles)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)
            next_button.click()
            time.sleep(2)  # Wait for page to load
            print("Moving to next page...")
            return True
        except:
            print("No more pages to scrape")
            return False

    @profile
    @retry_on_failure(max_retries=2, delay=1)
    def scrape_single_job(self, element, job_title):
        """Scrape a single job with retry logic"""
        # Scroll element into view
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

        # Use JavaScript click to avoid interception
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(1)

        company_name = self.scrape_company()
        location = self.scrape_location()
        deadline = self.scrape_deadline()
        compensation = self.scrape_compensation()
        major = self.scrape_major()
        min_GPA = self.scrape_min_gpa()
        description = self.scrape_description()

        return {
            'title': job_title,
            'company': company_name,
            'location': location,
            'deadline': deadline,
            'compensation': compensation,
            'targeted_major': major,
            'minimuma_gpa': min_GPA,
            'description': description
        }

    @profile
    def scrape_data(self, max_jobs=None):
        print("\n" + "=" * 50)
        print("🎯 Starting job scraping process...")
        if max_jobs:
            print(f"  Limited to {max_jobs} jobs for testing")
        print("=" * 50 + "\n")

        # Load previous scrape for comparison
        self.load_previous_scrape()

        all_jobs = []
        page_num = 1
        total_jobs_scraped = 0
        total_jobs_failed = 0
        new_jobs_count = 0

        while True:
            print(f"\nPAGE {page_num}")
            print("-" * 50)

            try:
                all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")

                job_data = []
                for span in all_spans:
                    text = span.text.strip()
                    if text and text != "NOT QUALIFIED":
                        job_data.append((span, text))

                num_jobs = len(job_data)
                print(f"Found {num_jobs} jobs on this page\n")

                for i in range(num_jobs):
                    # CHECK IF WE'VE HIT THE LIMIT
                    if max_jobs and total_jobs_scraped >= max_jobs:
                        print(f"\n️ Reached job limit of {max_jobs}. Stopping...")
                        break

                    try:
                        all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
                        job_elements = []
                        for span in all_spans:
                            text = span.text.strip()
                            if text and text != "NOT QUALIFIED":
                                job_elements.append(span)

                        # Check if element still exists
                        if i >= len(job_elements):
                            print(f"        Job #{i + 1} disappeared from list, skipping...")
                            total_jobs_failed += 1
                            continue

                        element = job_elements[i]
                        job_title = element.text

                        # Scroll element into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)

                        # Use JavaScript click to avoid interception
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(1)

                        company_name = self.scrape_company()
                        location = self.scrape_location()
                        deadline = self.scrape_deadline()
                        compensation = self.scrape_compensation()
                        major = self.scrape_major()
                        min_GPA = self.scrape_min_gpa()
                        description = self.scrape_description()

                        # Check if this is a new job
                        is_new = self.is_new_job(job_title, company_name)
                        status_emoji = "🆕" if is_new else "📋"

                        if is_new:
                            new_jobs_count += 1

                        print(f"  [{i + 1}/{num_jobs}] {status_emoji} Scraping: {job_title}")
                        print(f"      Company: {company_name}")
                        print(f"      Location: {location}")
                        print(f"      Compensation: {compensation}")
                        if is_new:
                            print(f"      NEW JOB!")

                        # Store data with metadata
                        job_entry = {
                            'title': job_title,
                            'company': company_name,
                            'location': location,
                            'deadline': deadline,
                            'compensation': compensation,
                            'targeted_major': major,
                            'minimum_gpa': min_GPA,
                            'description': description,
                            'status': 'NEW' if is_new else 'EXISTING',
                            'scraped_at': datetime.now().isoformat(),
                            'search_keywords': SEARCH,
                            'search_location': LOCATION
                        }

                        all_jobs.append(job_entry)
                        total_jobs_scraped += 1
                        print(f"       Job saved! (Total: {total_jobs_scraped})\n")

                    except Exception as e:
                        total_jobs_failed += 1
                        error_msg = f"Failed to scrape job #{i + 1}: {str(e)}"
                        self.errors.append(error_msg)
                        job_title_for_log = job_title if 'job_title' in locals() else f"Job #{i + 1}"
                        self.failed_jobs.append(job_title_for_log)
                        print(f"       Error scraping job: {str(e)[:100]}")
                        print(f"      Continuing to next job...\n")

                    finally:
                        try:
                            self.driver.back()
                            time.sleep(1)
                        except Exception as e:
                            print(f"        Warning: Failed to navigate back: {str(e)}")

                if max_jobs and total_jobs_scraped >= max_jobs:
                    break

            except Exception as e:
                print(f"\n Error on page {page_num}: {str(e)}")
                self.errors.append(f"Page {page_num} error: {str(e)}")
                print("Attempting to continue to next page...")

            if not self.next_page():
                break

            page_num += 1

        # Compare with previous scrape
        new_jobs, existing_jobs, removed_jobs = self.compare_jobs(all_jobs)

        # Final summary
        print("\n" + "=" * 50)
        print(f" SCRAPING COMPLETE!")
        print(f" Successfully scraped: {total_jobs_scraped} jobs")
        print(f" New jobs: {len(new_jobs)}")
        print(f" Existing jobs: {len(existing_jobs)}")
        if removed_jobs:
            print(f"  Removed jobs: {len(removed_jobs)} (no longer listed)")
        if total_jobs_failed > 0:
            print(f" Failed to scrape: {total_jobs_failed} jobs")
        print("=" * 50 + "\n")

        # Show new jobs summary
        if new_jobs:
            print(" NEW JOBS FOUND:")
            print("-" * 50)
            for i, job in enumerate(new_jobs[:10], 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   Compensation: {job['compensation']}")
                print()
            if len(new_jobs) > 10:
                print(f"... and {len(new_jobs) - 10} more new jobs\n")
        else:
            print("  No new jobs found - all jobs were in previous scrape\n")

        # Show removed jobs if any
        if removed_jobs:
            print("  REMOVED JOBS (no longer listed):")
            print("-" * 50)
            for i, job in enumerate(removed_jobs[:5], 1):
                print(f"{i}. {job.get('title', 'Unknown')}")
                print(f"   Company: {job.get('company', 'Unknown')}")
                print()
            if len(removed_jobs) > 5:
                print(f"... and {len(removed_jobs) - 5} more removed jobs\n")

        # Save data
        if all_jobs:
            print(" Saving data to coopsearch.json...")
            df = pd.DataFrame.from_dict(all_jobs)
            df.to_json('coopsearch.json', orient='records', indent=2)
            print(f"✓ Successfully saved {len(all_jobs)} jobs to coopsearch.json")

            # Save only new jobs to separate file
            if new_jobs:
                print(" Saving new jobs to coopsearch_new.json...")
                df_new = pd.DataFrame.from_dict(new_jobs)
                df_new.to_json('coopsearch_new.json', orient='records', indent=2)
                print(f"✓ Successfully saved {len(new_jobs)} new jobs to coopsearch_new.json")

            # Save scrape history
            self.save_scrape_history(all_jobs, new_jobs, existing_jobs, removed_jobs)
        else:
            print("️  No jobs were scraped - nothing to save")

        # Save error log if there were errors
        if self.errors:
            print("\n Saving error log to errors.txt...")
            with open('errors.txt', 'w') as f:
                f.write(f"CoopScout Error Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                for error in self.errors:
                    f.write(f"{error}\n")
            print(f" Saved {len(self.errors)} errors to errors.txt")

    def save_scrape_history(self, all_jobs, new_jobs, existing_jobs, removed_jobs):
        """Save history of scrapes for tracking changes over time"""
        try:
            # Load existing history
            try:
                with open('scrape_history.json', 'r') as f:
                    history = json.load(f)
            except FileNotFoundError:
                history = []

            # Add current scrape to history
            scrape_record = {
                'timestamp': datetime.now().isoformat(),
                'search_keywords': SEARCH,
                'search_location': LOCATION,
                'total_jobs': len(all_jobs),
                'new_jobs': len(new_jobs),
                'existing_jobs': len(existing_jobs),
                'removed_jobs': len(removed_jobs),
                'new_job_titles': [f"{job['title']} @ {job['company']}" for job in new_jobs[:20]]  # Save first 20
            }

            history.append(scrape_record)

            # Keep only last 30 scrapes
            history = history[-30:]

            with open('scrape_history.json', 'w') as f:
                json.dump(history, f, indent=2)

            print(f"✓ Updated scrape history (tracking last {len(history)} scrapes)")

        except Exception as e:
            print(f"  Warning: Could not save scrape history: {e}")

    def close_driver(self):
        print("\n Closing browser...")
        self.driver.quit()
        print(" Done! Happy job hunting! ")


def main():
    scraper = WebScraper()

    try:
        scraper.initialize_driver()
        scraper.initalize_wait()
        scraper.navigate_to_page(URL)
        scraper.login(username, password)
        scraper.search(SEARCH)
        scraper.get_job_results()
        scraper.filter_by_location(LOCATION)
        scraper.filter_by_coop()
        scraper.scrape_data()  # Test with 5 jobs

    except KeyboardInterrupt:
        print("\n\n️  Scraping interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n Critical error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.close_driver()
        except Exception as e:
            print(f"  Warning: Failed to close driver: {e}")

        print("\n" + "=" * 50)
        print(" PERFORMANCE REPORT")
        print("=" * 50)
        Profiler.report()


if __name__ == "__main__":
    main()