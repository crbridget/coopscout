from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import pickle
from datetime import datetime
import pandas as pd
from selenium.common.exceptions import TimeoutException

class NUWorksScraper:
    """Reusable NUworks scraper - can use login or saved cookies"""
    
    def __init__(self, headless=True):
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless=new")
        self.errors = []
        self.failed_jobs = []
        self.previous_jobs = {}
        self.driver = None
        print("CoopScout NUworks Scraper initialized")

    def initialize_driver(self):
        print("Starting Chrome driver...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.duo_wait = WebDriverWait(self.driver, 60)
        print("Chrome driver ready")

    def navigate_to_page(self, url="https://northeastern-csm.symplicity.com/students/?signin_tab=0"):
        print(f"Navigating to NUworks...")
        self.driver.get(url)
        print("Page loaded")

    def login_with_credentials(self, username, password):
        """Traditional login with Duo push"""
        print("Logging in...")
        
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Current Students and Alumni']"))).click()

        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.send_keys(username)

        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("Sending Duo push... (check your phone!)")
        duo_iframe = self.wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        self.driver.switch_to.frame(duo_iframe)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Me a Push')]"))).click()

        self.driver.switch_to.default_content()
        print("Waiting for Duo approval...")
        self.duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))
        print("Login successful")

    def login_with_cookies(self, cookies):
        """Login using saved cookies - no Duo needed"""
        print("Loading saved cookies...")

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        print("Logged in with cookies")

        # Navigate to the job search page
        print("Navigating to job search page...")
        self.driver.get("https://northeastern-csm.symplicity.com/students/index.php?mode=list&s=jobs")
        time.sleep(3)  # Give the page time to load

        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")

    def load_cookies_from_file(self, filename):
        """Load cookies from pickle file"""
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def search(self, search_term):
        try:
            print(f"Looking for search toggle button...")
            search_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.quicksearch-toggle"))
            )
            print("Search toggle found, clicking...")
            search_toggle.click()
            time.sleep(1)

            # Enter the Search term
            print(f"Entering search term: '{search_term}'...")
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.ENTER)

            print(f"Search submitted for '{search_term}'")
            time.sleep(3)  # Wait for results to load

        except TimeoutException:
            print("WARNING: Search toggle not found. Trying alternative selector...")
            try:
                # Maybe the search is already expanded?
                search_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='search']")
                print("Search input already visible")
                search_input.clear()
                search_input.send_keys(search_term)
                search_input.send_keys(Keys.ENTER)
                print(f"Search submitted for '{search_term}'")
                time.sleep(3)
            except:
                print("ERROR: Could not find search elements")
                raise

    def get_job_results(self):
        print("Looking for job results...")
        time.sleep(3)

        try:
            # Try the original method first
            job_results_link = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='See all job results']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_results_link)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", job_results_link)
            time.sleep(3)
            print("Job results page loaded")
        except TimeoutException:
            print("'See all job results' link not found - results may already be displayed")
            # Check if we're already on a results page
            print(f"Current URL: {self.driver.current_url}")

            # Try to find job listings directly
            try:
                job_listings = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
                if job_listings:
                    print(f"Found {len(job_listings)} job listings already displayed")
                    return  # We're good, results are already shown
                else:
                    raise Exception("Could not find job results or listings")
            except:
                raise Exception("Could not find job results - page may have changed")

    def filter_by_location(self, location):
        print(f"Filtering by location: {location}...")
        location_bar = self.wait.until(EC.element_to_be_clickable((By.ID, "jobs-location-input")))
        location_bar.send_keys(location + Keys.ENTER)
        time.sleep(2)
        print("Location filter applied")

    def filter_by_coop(self):
        print("Filtering for Co-op positions...")
        time.sleep(2)

        coop_checkbox = self.driver.find_element(By.ID, "job_type-checkbox-0")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", coop_checkbox)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", coop_checkbox)
        time.sleep(2)
        print("Co-op filter applied")

    def scrape_company(self):
        try:
            company_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3.space-right-sm.text-overflow")))
            return company_element.text.strip()
        except Exception as e:
            return "Not listed"

    def scrape_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_location_"]')
            return location_element.text.strip()
        except Exception as e:
            return "Not listed"

    def scrape_deadline(self):
        try:
            deadline_element = self.driver.find_element(By.ID, "sy_formfield_job_deadline")
            return deadline_element.text.strip()
        except Exception as e:
            return "Not listed"

    def scrape_compensation(self):
        try:
            compensation_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_compensation_"]')
            comp_text = compensation_element.text.strip()

            # Return None if not listed or empty
            if comp_text == "Not listed" or not comp_text:
                return None

            return comp_text  # Keep as text since compensation can be "$20-25/hr" etc.

        except Exception as e:
            return None

    def scrape_major(self):
        try:
            major_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_targeted_academic_majors_"]')
            return major_element.text.strip()
        except Exception as e:
            return "Not listed"

    def scrape_min_gpa(self):
        try:
            min_gpa = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_screen_gpa_"]')
            gpa_text = min_gpa.text.strip()

            # Return None if not a valid number
            if gpa_text == "Not listed" or not gpa_text:
                return None

            # Try to convert to float, return None if it fails
            try:
                return float(gpa_text)
            except ValueError:
                return None

        except Exception as e:
            return None

    def scrape_description(self):
        try:
            description_div = self.driver.find_element(By.CSS_SELECTOR, "div.field-widget-tinymce")
            return description_div.text
        except Exception as e:
            return "Not listed"

    def next_page(self):
        try:
            next_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Next"]]')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)
            next_button.click()
            time.sleep(2)
            print("Moving to next page...")
            return True
        except:
            print("No more pages to scrape")
            return False

    def scrape_all_jobs(self, search_term, location, max_jobs=None):
        """Main scraping method - returns list of job dicts"""
        print("\n" + "=" * 50)
        print("Starting job scraping process...")
        if max_jobs:
            print(f"Limited to {max_jobs} jobs for testing")
        print("=" * 50 + "\n")

        all_jobs = []
        page_num = 1
        total_jobs_scraped = 0

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
                    if max_jobs and total_jobs_scraped >= max_jobs:
                        print(f"\nReached job limit of {max_jobs}. Stopping...")
                        break

                    try:
                        all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
                        job_elements = []
                        for span in all_spans:
                            text = span.text.strip()
                            if text and text != "NOT QUALIFIED":
                                job_elements.append(span)

                        if i >= len(job_elements):
                            continue

                        element = job_elements[i]
                        job_title = element.text

                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(1)

                        company_name = self.scrape_company()
                        location_data = self.scrape_location()
                        deadline = self.scrape_deadline()
                        compensation = self.scrape_compensation()
                        major = self.scrape_major()
                        min_GPA = self.scrape_min_gpa()
                        description = self.scrape_description()

                        print(f"  [{i + 1}/{num_jobs}] Scraped: {job_title}")
                        print(f"      Company: {company_name}")

                        job_entry = {
                            'title': job_title,
                            'company': company_name,
                            'location': location_data,
                            'deadline': deadline,
                            'compensation': compensation,
                            'targeted_major': major,
                            'minimum_gpa': min_GPA,
                            'description': description,
                            'scraped_at': datetime.now().isoformat(),
                            'search_keywords': search_term,
                            'search_location': location
                        }

                        all_jobs.append(job_entry)
                        total_jobs_scraped += 1

                    except Exception as e:
                        print(f"      Error scraping job: {str(e)[:100]}")

                    finally:
                        try:
                            self.driver.back()
                            time.sleep(1)
                        except:
                            pass

                if max_jobs and total_jobs_scraped >= max_jobs:
                    break

            except Exception as e:
                print(f"\nError on page {page_num}: {str(e)}")

            if not self.next_page():
                break

            page_num += 1

        print("\n" + "=" * 50)
        print(f"SCRAPING COMPLETE")
        print(f"Successfully scraped: {total_jobs_scraped} jobs")
        print("=" * 50 + "\n")

        return all_jobs

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed")


# Helper functions for easy use
def scrape_with_login(username, password, search_term="software engineering", 
                     location="Boston, MA, USA", max_jobs=None):
    """Scrape using username/password login"""
    scraper = NUWorksScraper(headless=True)
    
    try:
        scraper.initialize_driver()
        scraper.navigate_to_page()
        scraper.login_with_credentials(username, password)
        scraper.search(search_term)
        scraper.get_job_results()
        scraper.filter_by_location(location)
        scraper.filter_by_coop()
        jobs = scraper.scrape_all_jobs(search_term, location, max_jobs)
        return jobs
    finally:
        scraper.close()


def scrape_with_cookies(cookies, search_term="software engineering",
                       location="Boston, MA, USA", max_jobs=None):
    """Scrape using saved cookies - no Duo needed"""
    scraper = NUWorksScraper(headless=True)
    
    try:
        scraper.initialize_driver()
        scraper.navigate_to_page()
        scraper.login_with_cookies(cookies)
        scraper.search(search_term)
        scraper.get_job_results()
        scraper.filter_by_location(location)
        scraper.filter_by_coop()
        jobs = scraper.scrape_all_jobs(search_term, location, max_jobs)
        return jobs
    finally:
        scraper.close()