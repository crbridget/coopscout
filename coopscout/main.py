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

    def initialize_driver(self):
        # self.chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome()

    def initalize_wait(self):
        self.wait = WebDriverWait(self.driver, 5) 
        self.duo_wait = WebDriverWait(self.driver, 60)

    def navigate_to_page(self, url):
        """ """
        self.driver.get(url)

    def login(self, username, password):
        """ Login to NUworks with users user and password and then send a duo push to the user """

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Current Students and Alumni']"))).click()

        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.send_keys(username)

        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        duo_iframe = self.wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        self.driver.switch_to.frame(duo_iframe)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Me a Push')]"))).click()

        self.driver.switch_to.default_content()
        self.duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))

    def search(self, search):
        """ Search for a job or key word in the NUworks main search """

        search_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search']")))
        search_bar.send_keys(search + Keys.ENTER)

    def get_job_results(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='See all job results']"))).click()

    def filter_by_location(self, location):
        location_bar = self.wait.until(EC.element_to_be_clickable((By.ID, "jobs-location-input")))
        location_bar.send_keys(location + Keys.ENTER)

    def filter_by_coop(self):
        self.driver.find_element(By.CLASS_NAME, "icn-chevron_down").click()
        self.driver.find_element(By.ID, "job_type-checkbox-0").click()
        self.driver.find_element(By.XPATH, '//button[text()="Apply"]').click()

    def filter_not_qualified(self):
        time.sleep(2)
        all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
        self.job_titles_elements = [span for span in all_spans if span.text.strip() and span.text.strip() != "NOT QUALIFIED"]
        
    def scrape_company(self):
        company_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.space-right-sm.text-overflow")))
        time.sleep(2)
        print(f"Successfully scraped company!: {company_element.text.strip()} ")
        return company_element.text.strip()
    
    def scrape_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_location_"]')
            print(f"Successfully scraped location!: {location_element.text.strip()} ")
            return location_element.text.strip()
        except:
            return "Not listed"
    
    def scrape_deadline(self):
        try:
            deadline_element = self.driver.find_element(By.ID, "sy_formfield_job_deadline")
            print(f"Successfully scraped description!: {deadline_element.text.strip()}")
            return deadline_element.text.strip()
        except:
            return "Not listed"
    
    def scrape_compensation(self):
        try:
            compensation_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_compensation_"]')
            print(f"Successfully scraped pay!: {compensation_element.text.strip()} ")
            return compensation_element.text.strip()
        except:
            return "Not listed"

    def scrape_major(self):
        try:
            major_element = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_targeted_academic_majors_"]')
            print(f"Successfully scraped major!: {major_element.text.strip()} ")
            return major_element.text.strip()
        except:
            return "Not listed"
    
    def scrape_min_gpa(self):
        try:
            min_gpa = self.driver.find_element(By.CSS_SELECTOR, '[id^="sy_formfield_screen_gpa_"]')
            print(f"Successfully scraped min GPA!: {min_gpa.text.strip()} ")
            return min_gpa.text.strip()
        except:
            return "Not listed"
    
    def scrape_description(self):
        description_div = self.driver.find_element(By.CSS_SELECTOR, "div.field-widget-tinymce")
        print(f"Successfully scraped description!: {description_div.text}")
        return description_div.text

    def scrape_data(self):
        coop_search = {}
        num_jobs = len(self.job_titles_elements)

        for i in range(num_jobs):
            all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
            job_titles = [span for span in all_spans if span.text.strip() and span.text.strip() != "NOT QUALIFIED"]

            job_title = job_titles[i].text

            # Scroll element into view before clicking
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_titles[i])
            time.sleep(0.5)

            job_titles[i].click()
            time.sleep(2)

            company_name = self.scrape_company()
            location = self.scrape_location()
            deadline = self.scrape_deadline()
            compensation = self.scrape_compensation()
            major = self.scrape_major()
            min_GPA = self.scrape_min_gpa()
            description = self.scrape_description()

            # Store data
            coop_search[f'coop{i+1}'] = {
                'title': job_title,
                'company': company_name,
                'location': location,
                'deadline': deadline,
                'compensation': compensation,
                'targeted major': major,
                'minimum GPA': min_GPA,
                'description': description
            }

            self.driver.back()
            time.sleep(2)

        df = pd.DataFrame.from_dict(coop_search, orient='index')
        df.to_json('coopsearch.json', orient='records', indent=2)

    def close_driver(self):
        self.driver.quit()


def main():
    scraper = WebScraper()  # Create an instance
    scraper.initialize_driver()
    scraper.initalize_wait()
    scraper.navigate_to_page(URL)
    scraper.login(username, password)
    scraper.search(SEARCH)
    scraper.get_job_results()
    scraper.filter_by_location(LOCATION)
    scraper.filter_by_coop()
    scraper.filter_not_qualified()
    scraper.scrape_data()
    scraper.close_driver()

if __name__ == "__main__":
    main()