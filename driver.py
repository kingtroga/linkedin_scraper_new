import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, set_key

# Load environment variables from .env file
load_dotenv()

def update_env_file(key, value):
    """Updates the .env file with a new key-value pair."""
    dotenv_path = '.env'
    set_key(dotenv_path, key, value)

def launch_driver():
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Navigate to LinkedIn login page
    driver.get('https://www.linkedin.com/login')
    
    # Wait for the username input field to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'session_key')))
    
    # Get the input elements
    username_input = driver.find_element(By.NAME, 'session_key')
    password_input = driver.find_element(By.NAME, 'session_password')

    # Type into the inputs
    username_input.send_keys(os.getenv('LINKEDIN_USERNAME'))
    password_input.send_keys(os.getenv('LINKEDIN_PASSWORD'))

    # Submit the form by clicking the "Sign in" button
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # Function to check if still on the login page
    def check_login_page():
        try:
            current_url = driver.current_url
            if '/login-submit' in current_url or '/checkpoint/' in current_url:
                print("Go to your email and get the verification code or solve the CAPTCHA challenge and wait for the page to load.")
                return True
            return False
        except Exception as e:
            print(f"Error checking login page: {e}")
            return False

    # Wait for 20 seconds and check if still on the login page
    time.sleep(20)
    for _ in range(60):
        if check_login_page():
            time.sleep(120)  # Wait for the user to complete any additional verification
        else:
            print('Login Successful!')
            break
    
    # Get session details
    session_url = driver.command_executor._url
    session_id = driver.session_id

    # Print session details
    print(f"Session URL: {session_url}")
    print(f"Session ID: {session_id}")

    # Store session details in .env file
    update_env_file('SESSION_URL', session_url)
    update_env_file('SESSION_ID', session_id)
    print("Session details stored in .env file.")

    # Keep the browser open
    input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    launch_driver()
