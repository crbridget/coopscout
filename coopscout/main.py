from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15) #if after 15 seconds the element doesn't exist crash the program

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

time.sleep(30)

driver.quit()

