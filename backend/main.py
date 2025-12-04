from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from dotenv import load_dotenv
import os
import pandas as pd
from profiler import Profiler, profile
import time

# load the env file 
load_dotenv()

# retrieve the username and password information
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# global variables
URL = "https://northeastern-csm.symplicity.com/students/?signin_tab=0"
SEARCH = "software engineering"
LOCATION = "Boston, MA, USA"


class WebScraper:

    def __init__(self):
        """ Constructor """
        self.chrome_options = Options()
        print("🚀 CoopScout initialized!")

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
        print(f"🌐 Navigating to NUworks...")
        self.driver.get(url)
        print("✓ Page loaded")

    @profile
    def login(self, username, password):
        """ Login to NUworks with users user and password and then send a duo push to the user """
        print("🔐 Logging in...")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Current Students and Alumni']"))).click()

        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.send_keys(username)

        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("📱 Sending Duo push... (check your phone!)")
        duo_iframe = self.wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        self.driver.switch_to.frame(duo_iframe)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Me a Push')]"))).click()

        self.driver.switch_to.default_content()
        print("⏳ Waiting for Duo approval...")
        self.duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))
        print("✓ Login successful!")

    @profile
    def search(self, search):
        """ Search for a job or key word in the NUworks main search """
        print(f"🔍 Searching for '{search}'...")

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
        print("✓ Search submitted")

    @profile
    def get_job_results(self):
        print("📋 Loading job results...")

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
        print("🔍 Debugging - Checking what page we're on after clicking...")
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

        print("✓ Job results page loaded")

    @profile
    def filter_by_location(self, location):
        print(f"📍 Filtering by location: {location}...")
        location_bar = self.wait.until(EC.element_to_be_clickable((By.ID, "jobs-location-input")))
        location_bar.send_keys(location + Keys.ENTER)
        time.sleep(2)
        print("✓ Location filter applied")

    @profile
    def filter_by_coop(self):
        print("🎓 Filtering for Co-op positions...")

        time.sleep(2)

        # Find the checkbox (even if not clickable)
        coop_checkbox = self.driver.find_element(By.ID, "job_type-checkbox-0")

        # Scroll to it
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", coop_checkbox)
        time.sleep(1)

        # Click using JavaScript
        self.driver.execute_script("arguments[0].click();", coop_checkbox)
        time.sleep(2)

        print("✓ Co-op filter applied")

    @profile
    def scrape_company(self):
        company_element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.space-right-sm.text-overflow")))
        return company_element.text.strip()

    @profile
    def scrape_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_location_"]')
            return location_element.text.strip()
        except:
            return "Not listed"

    @profile
    def scrape_deadline(self):
        try:
            deadline_element = self.driver.find_element(By.ID, "sy_formfield_job_deadline")
            return deadline_element.text.strip()
        except:
            return "Not listed"

    @profile
    def scrape_compensation(self):
        try:
            compensation_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_compensation_"]')
            return compensation_element.text.strip()
        except:
            return "Not listed"

    @profile
    def scrape_major(self):
        try:
            major_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_targeted_academic_majors_"]')
            return major_element.text.strip()
        except:
            return "Not listed"

    @profile
    def scrape_min_gpa(self):
        try:
            min_gpa = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_screen_gpa_"]')
            return min_gpa.text.strip()
        except:
            return "Not listed"

    @profile
    def scrape_description(self):
        description_div = self.driver.find_element(By.CSS_SELECTOR, "div.field-widget-tinymce")
        return description_div.text

    @profile
    def next_page(self):
        try:
            next_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Next"]]')
            # Scroll to the button (just like you do for job titles)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)
            next_button.click()
            time.sleep(2)  # Wait for page to load
            print("→ Moving to next page...")
            return True
        except:
            print("✓ No more pages to scrape")
            return False

    @profile
    @profile
    def scrape_data(self, max_jobs=None):  # Add max_jobs parameter with default None
        print("\n" + "=" * 50)
        print("🎯 Starting job scraping process...")
        if max_jobs:
            print(f"⚠️  Limited to {max_jobs} jobs for testing")
        print("=" * 50 + "\n")

        all_jobs = []
        page_num = 1
        total_jobs_scraped = 0

        while True:
            print(f"\n📄 PAGE {page_num}")
            print("-" * 50)

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
                    print(f"\n⚠️  Reached job limit of {max_jobs}. Stopping...")

                    # Save what we have so far
                    if all_jobs:
                        print("💾 Saving data to coopsearch.json...")
                        df = pd.DataFrame.from_dict(all_jobs)
                        df.to_json('coopsearch.json', orient='records', indent=2)
                        print(f"✓ Successfully saved {len(all_jobs)} jobs to coopsearch.json")

                    return  # Exit the function early

                all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
                job_elements = []
                for span in all_spans:
                    text = span.text.strip()
                    if text and text != "NOT QUALIFIED":
                        job_elements.append(span)

                element = job_elements[i]
                job_title = element.text

                print(f"  [{i + 1}/{num_jobs}] Scraping: {job_title}")

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)

                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(1)  # Reduced from 2

                company_name = self.scrape_company()
                location = self.scrape_location()
                deadline = self.scrape_deadline()
                compensation = self.scrape_compensation()
                major = self.scrape_major()
                min_GPA = self.scrape_min_gpa()
                description = self.scrape_description()

                print(f"      Company: {company_name}")
                print(f"      Location: {location}")
                print(f"      Compensation: {compensation}")

                all_jobs.append({
                    'title': job_title,
                    'company': company_name,
                    'location': location,
                    'deadline': deadline,
                    'compensation': compensation,
                    'targeted major': major,
                    'minimum GPA': min_GPA,
                    'description': description
                })

                total_jobs_scraped += 1
                print(f"      ✓ Job saved! (Total: {total_jobs_scraped})\n")

                self.driver.back()
                time.sleep(1)  # Reduced from 2

            if not self.next_page():
                break

            page_num += 1

        print("\n" + "=" * 50)
        print(f"🎉 SCRAPING COMPLETE!")
        print(f"Total jobs scraped: {total_jobs_scraped}")
        print("=" * 50 + "\n")

        print("💾 Saving data to coopsearch.json...")
        df = pd.DataFrame.from_dict(all_jobs)
        df.to_json('coopsearch.json', orient='records', indent=2)
        print(f"✓ Successfully saved {len(all_jobs)} jobs to coopsearch.json")

    def close_driver(self):
        print("\n🔒 Closing browser...")
        self.driver.quit()
        print("✓ Done! Happy job hunting! 🚀")


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

        # SET THIS TO LIMIT JOBS - Easy to change for testing!
        scraper.scrape_data(max_jobs=5)  # Change to None for all jobs

    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
    finally:
        try:
            scraper.close_driver()
        except:
            pass

        print("\n" + "=" * 50)
        print("📊 PERFORMANCE REPORT")
        print("=" * 50)
        Profiler.report()


if __name__ == "__main__":
    main()