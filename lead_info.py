import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
import random
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Lead Links
DATA_FRAME = pd.read_excel('xlsx/linkedin_profiles.xlsx')
LEAD_PROFILE_LINKS = DATA_FRAME['LinkedIn Profile'].tolist()

socials_info_list = []
emails_info_list = []
website_info_list = []
address_info_list = []
phone_info_list = []

about_info_list = []

lead_name_list = []
lead_role_list = []
company_link_list = []

def random_delay(min_delay=3, max_delay=10):
    """Introduce a random delay between actions to mimic human behavior."""
    time.sleep(random.uniform(min_delay, max_delay))

def main():
    # Get session details from user
    session_url = os.getenv("SESSION_URL")
    session_id = os.getenv("SESSION_ID")

    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure the browser is in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    for lead_link in LEAD_PROFILE_LINKS:
        # Connect to the existing browser session
        try:
            driver = webdriver.Remote(command_executor=session_url, options=chrome_options)
            driver.session_id = session_id
            link_to_scrape = lead_link
            driver.get(link_to_scrape)
        except Exception as e:
            logging.error(f"Error connecting to browser session or loading page: {e}")
            print("Close the terminal you are running this code on and open a new one and run it again")
            continue

        random_delay()

        # Get lead name
        try:
            links = driver.find_elements(By.TAG_NAME, 'a')
            links = [link for link in links if (link_to_scrape.split('/')[-1] + "/overlay/about-this-profile/") in link.get_attribute('href')]
            logging.info(f"Lead name: {links[0].text}")
            lead_name_list.append(links[0].text)
        except Exception as e:
            logging.warning(f"Could not retrieve lead name: {e}")
            lead_name_list.append("NULL")

        # Get lead role
        try:
            role = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-generated-suggestion-target]')))
            logging.info(f"Lead role: {role.text}")
            lead_role_list.append(role.text)
        except Exception as e:
            logging.warning(f"Could not retrieve lead role: {e}")
            lead_role_list.append("NULL")

        # Get lead about
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h2//*[text()='About']")))
            logging.info("This user has About info")
        except Exception as e:
            logging.info("This user has no About info")
            element = False
        finally:
            random_delay()
            if element:
                try:
                    button = element.find_element(By.XPATH, "//button[text()='…see more']")
                    button.click()
                    random_delay()
                    section = driver.find_elements(By.CSS_SELECTOR, 'div[data-generated-suggestion-target]')[1]
                    about_info = str(section.text)
                except Exception as e:
                    logging.warning(f"Error expanding or retrieving About section: {e}")
                    about_info = "NULL"
            else:
                about_info = "NULL"
            about_info_list.append(about_info)

        # Get lead Phone, Email, Address, Social, Websites
        socials_string = ""
        emails_string = ""
        phones_string = ""
        website_string = ""
        address_string = ""

        try:
            contact_info_button = driver.find_element(By.CSS_SELECTOR, f"a[href='/in/{link_to_scrape.split('/')[-1]}/overlay/contact-info/']")
            random_delay()
            contact_info_button.click()
            random_delay()

            contact_info_modal = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.artdeco-modal__content")))
            contact_info = contact_info_modal.find_elements(By.TAG_NAME, 'a')
            filtered_contact_info = [link for link in contact_info if "www.linkedin.com" not in link.get_attribute('href')]

            for link in filtered_contact_info:
                actual_link = link.get_attribute('href')

                if "https://www.twitter.com/" in actual_link:
                    socials_string += f" {actual_link.strip()};"
                elif "https://www.x.com/" in actual_link:
                    socials_string += f" {actual_link.strip()};"
                elif "https://www.instagram.com/" in actual_link:
                    socials_string += f" {actual_link.strip()};"
                elif "https://www.facebook.com/" in actual_link:
                    socials_string += f" {actual_link.strip()};"
                elif "https://www.pinterest.com/" in actual_link:
                    socials_string += f" {actual_link.strip()};"
                elif "mailto:" in actual_link:
                    emails_string += f" {actual_link.strip().replace('mailto:', '')};"
                elif "tel:" in actual_link:
                    phones_string += f" {actual_link.strip().replace('tel:', ' ')};"
                elif "www" in actual_link:
                    website_string += f" {actual_link.strip()};"
                else:
                    address_string += f" {actual_link.strip()};"

            socials_info_list.append(socials_string if socials_string else "NULL")
            emails_info_list.append(emails_string if emails_string else "NULL")
            website_info_list.append(website_string if website_string else "NULL")
            address_info_list.append(address_string if address_string else "NULL")
            phone_info_list.append(phones_string if phones_string else "NULL")

        except Exception as e:
            logging.warning(f"Error retrieving contact information: {e}")
            socials_info_list.append("NULL")
            emails_info_list.append("NULL")
            website_info_list.append("NULL")
            address_info_list.append("NULL")
            phone_info_list.append("NULL")

        # Get company URL
        try:
            first_company_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-field^='experience_company_logo']"))
            )
            logging.info(f"Company URL: {first_company_link.get_attribute('href')}")
            company_link_list.append(str(first_company_link.get_attribute('href')))
        except Exception as e:
            logging.warning(f"Could not retrieve company URL: {e}")
            company_link_list.append("NULL")

    # Create a dictionary to store the lists and their names
    lists_dict = {
        'Lead Name': lead_name_list,
        'LinkedIn URL': LEAD_PROFILE_LINKS,
        'Lead Role': lead_role_list,
        'About Info': about_info_list,
        'Socials Info': socials_info_list,
        'Emails Info': emails_info_list,
        'Website Info': website_info_list,
        'Address Info': address_info_list,
        'Phone Info': phone_info_list,
        'Company Link': company_link_list
    }

    df_lead_info = pd.DataFrame(lists_dict)
    try:
        df_lead_info.to_excel('xlsx/leads_info.xlsx', index=False)
    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        print("Run 'pip install openpyxl' and then run transform.py")
    try:
        df_lead_info.to_csv('csv/leads_info.csv', index=False)
    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")

if __name__ == "__main__":
    try:
        main()
        print("Scrapping successful!")
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}")

        # DATA LOSS PREVENTION
        lists_dict = {
            'Lead Name': lead_name_list,
            'LinkedIn URL': LEAD_PROFILE_LINKS,
            'Lead Role': lead_role_list,
            'About Info': about_info_list,
            'Socials Info': socials_info_list,
            'Emails Info': emails_info_list,
            'Website Info': website_info_list,
            'Address Info': address_info_list,
            'Phone Info': phone_info_list,
            'Company Link': company_link_list
        }

        # Find the list with the least elements
        least_elements_list_name = min(lists_dict, key=lambda k: len(lists_dict[k]))
        no_of_elements = len(lists_dict[least_elements_list_name])

        # Trim all lists to have the same length as the shortest list
        dlp_dict = {k: v[:no_of_elements] for k, v in lists_dict.items()}

        # Create a DataFrame and save it
        dlp_lead_info = pd.DataFrame(dlp_dict)
        try:
            dlp_lead_info.to_excel('xlsx/dlp_leads_info.xlsx', index=False)
        except Exception as e:
            logging.error(f"Error saving DLP data to Excel: {e}")
            print("Run 'pip install openpyxl' and then run transform.py")
        try:
            dlp_lead_info.to_csv('csv/dlp_leads_info.csv', index=False)
        except Exception as e:
            logging.error(f"Error saving DLP data to CSV: {e}")
        print("Data Loss Prevention Successful!")
