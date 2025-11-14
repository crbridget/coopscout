from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
import pandas as pd
from collections import defaultdict

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5) #if after 5 seconds the element doesn't exist crash the program

driver.get("https://northeastern-csm.symplicity.com/students/?signin_tab=0")

# click student button
button_element = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Current Students and Alumni']"))
    )
button_element.click()

# enter login and password
username_input = wait.until(
    EC.presence_of_element_located((By.ID, "username"))
    )
username_input.send_keys(username)

password_input = driver.find_element(By.ID, "password")
password_input.send_keys(password)

submit_element = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
submit_element.click()

# Duo Push
duo_iframe = wait.until(
    EC.presence_of_element_located((By.ID, "duo_iframe"))
    )
driver.switch_to.frame(duo_iframe)

# click push button
push_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Me a Push')]"))
    )
push_button.click()

# Switch back to main page
driver.switch_to.default_content()

# wait until duo push goes through (longer wait - 60 seconds)
duo_wait = WebDriverWait(driver, 60)
duo_wait.until(EC.invisibility_of_element_located((By.ID, "duo_iframe")))


# search for data analyst jobs
search_bar = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search']"))
    )
search_bar.send_keys("data analyst" + Keys.ENTER)

# click on all job results
all_job_results = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[text()='See all job results']"))
    )
all_job_results.click()

# filter by location
location_bar = wait.until(
    EC.element_to_be_clickable((By.ID, "jobs-location-input"))
    )
location_bar.send_keys("Boston, MA, USA" + Keys.ENTER)

time.sleep(2)

# Select job titles but filter out "NOT QUALIFIED"
all_spans = driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
job_titles_elements = [span for span in all_spans if span.text.strip() and span.text.strip() != "NOT QUALIFIED"]

coop_search = {}

num_jobs = len(job_titles_elements)

for i in range(num_jobs):
    try:
        all_spans = driver.find_elements(By.CSS_SELECTOR, "div.list-item-title span")
        job_titles = [span for span in all_spans if span.text.strip() and span.text.strip() != "NOT QUALIFIED"]

        job_title = job_titles[i].text
        print(f"Job {i+1}: {job_title}")

        # Scroll element into view before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_titles[i])
        time.sleep(0.5)

        job_titles[i].click()
        time.sleep(2)

        # Get company info
        try:
            company_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.space-right-sm.text-overflow"))
            )
    
            # Wait longer for Angular to populate
            time.sleep(2)
    
            company_name = company_element.text.strip()
    
        except Exception as e:
            print(f"  Error getting company: {e}")
            company_name = "N/A"

        # Store data INSIDE try block
        coop_search[f'coop{i+1}'] = {
            'title': job_title,
            'company': company_name,
        }

        driver.back()
        time.sleep(2)

    except Exception as e:
        print(f"Error on job {i+1}: {e}")
        continue

df = pd.DataFrame.from_dict(coop_search, orient='index')
df.to_csv('coopsearch.csv', index=False)

driver.quit()

