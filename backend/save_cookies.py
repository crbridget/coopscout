from selenium import webdriver
import pickle
import base64

driver = webdriver.Chrome()
driver.get("https://nuworks.northeastern.edu")

input("Complete Duo login, then press Enter...")

# Save cookies
cookies = driver.get_cookies()
pickle.dump(cookies, open("cookies.pkl", "wb"))

# Convert to base64 for GitHub Secrets
with open("cookies.pkl", "rb") as f:
    cookies_b64 = base64.b64encode(f.read()).decode()
    print("\nCopy this to GitHub Secrets as 'NUWORKS_COOKIES':")
    print(cookies_b64)

driver.quit()