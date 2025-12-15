from selenium import webdriver
import pickle

def save_cookies_interactive():
    """Save cookies after manual login"""
    driver = webdriver.Chrome()
    driver.get("https://northeastern-csm.symplicity.com/students/?signin_tab=0")
    
    print("\nPlease log in to NUworks and complete Duo authentication")
    input("Press Enter after you've successfully logged in...")
    
    cookies = driver.get_cookies()
    pickle.dump(cookies, open("nuworks_cookies.pkl", "wb"))
    
    print("Cookies saved to nuworks_cookies.pkl")
    print("You can now use these cookies for automated scraping")
    
    driver.quit()
    return cookies


if __name__ == "__main__":
    save_cookies_interactive()