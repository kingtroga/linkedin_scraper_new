import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import logging
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Lead Profiles
DATA_FRAME = pd.read_excel('xlsx/leads_info.xlsx')

COMPANY_LEAD_PROFILE_LINKS = DATA_FRAME['Company Link'].to_list()

LEAD_NAME_LIST = list(DATA_FRAME['Lead Name'])
LINKEDIN_URL_LIST = list(DATA_FRAME['LinkedIn URL'])
LEAD_ROLE_LIST = list(DATA_FRAME['Lead Role'])
ABOUT_INFO_LIST = list(DATA_FRAME['About Info'])
SOCIALS_INFO_LIST =  list(DATA_FRAME['Socials Info'])
EMAILS_INFO_LIST =  list(DATA_FRAME['Emails Info'])
WEBSITE_INFO_LIST = list(DATA_FRAME['Website Info'])
ADDRESS_INFO_LIST = list(DATA_FRAME['Address Info'])
PHONE_INFO_LIST = list(DATA_FRAME['Phone Info'])
COMPANY_LINK_LIST = list(DATA_FRAME['Company Link'])


def filter_company_links(company_links):
    """
    This function checks a list of LinkedIn company links, removes invalid links, 
    and returns a list of valid links. A valid LinkedIn company link usually follows the pattern:
    'https://www.linkedin.com/company/<company_id>/' or 'https://www.linkedin.com/company/<company_name>/'

    Parameters:
    company_links (list): List of LinkedIn company URLs.

    Returns:
    tuple: A tuple containing:
        - A list of valid LinkedIn company URLs.
        - A list of bad (invalid) LinkedIn company URLs that were removed.
    """
    valid_pattern = re.compile(r'https://www\.linkedin\.com/company/\d+/?$')
    valid_links = []
    

    for i, link in enumerate(company_links):
        if valid_pattern.match(link):
            valid_links.append(link)
        else:
            logging.warning(f"Invalid company link detected and removed: {link}\n", )
            LEAD_NAME_LIST.pop(i)
            LINKEDIN_URL_LIST.pop(i)
            LEAD_ROLE_LIST.pop(i)
            ABOUT_INFO_LIST.pop(i)
            SOCIALS_INFO_LIST.pop(i)
            EMAILS_INFO_LIST.pop(i)
            WEBSITE_INFO_LIST.pop(i)
            ADDRESS_INFO_LIST.pop(i)
            PHONE_INFO_LIST.pop(i)
            COMPANY_LINK_LIST.pop(i)
            

    return valid_links

def random_delay(min_delay=5, max_delay=8):
    """Introduce a random delay between actions to mimic human behavior."""
    time.sleep(random.uniform(min_delay, max_delay))




company_headquarters_list = []
company_overiew_list = []
company_website_list = []


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
    valid_company_links = filter_company_links(COMPANY_LEAD_PROFILE_LINKS)

    for link in valid_company_links:
        if link[-1] == '/':
            #print(link + 'about')
            link = link + 'about'
        else:
            #print(link + '/about')
            link = link + '/about'
        print("Link: ", link)

        try:
            driver = webdriver.Remote(command_executor=session_url, options=chrome_options)
            driver.session_id = session_id
            link_to_scrape = link
            driver.get(link_to_scrape)
        except Exception as e:
            logging.error(f"Error connecting to browser session or loading page: {e}")
            print("Close the terminal you are running this code on and open a new one and run it again")
            continue

        random_delay()

        # Company overview
        try:
            company_overview_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.org-page-details-module__card-spacing')))
            company_overview = company_overview_section.find_element(By.TAG_NAME, 'p')
            company_overiew_list.append(company_overview.text)

        except Exception as e:
            logging.warning(f"Could not retrieve company overview: {e}")
            company_overiew_list.append("NULL")

        
        # Company website
        try:
            company_overview_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.org-page-details-module__card-spacing')))
            company_website = company_overview_section.find_element(By.TAG_NAME, 'a')
            company_website_list.append(company_website.get_attribute('href')) 
            print(company_website.get_attribute('href'))
        except:
            logging.warning(f"Could not retrieve company website: {e}")
            company_website_list.append("NULL")

        
        # Company Headquarters
        try:
            # Locate the section containing the Headquarters information
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//section[contains(@class, 'org-page-details-module__card-spacing')]"))
            )
            
            # Find the 'Headquarters' dt element
            headquarters_dt = section.find_element(By.XPATH, ".//h3[text()='Headquarters']")
            
            # Locate the corresponding dd element
            headquarters_dd = headquarters_dt.find_element(By.XPATH, "../following-sibling::dd")
            
            # Extract and return the headquarters text
            company_headquarters = headquarters_dd.text
            print(f"Headquarters: {company_headquarters}")

            company_headquarters_list.append(company_headquarters)

        except Exception as e:
            logging.warning(f"Could not retrieve company headquarters: {e}")
            company_headquarters_list.append("NULL")


    # Create a dictionary to store the lists and their names
    lists_dict = {
            'Lead Name': LEAD_NAME_LIST,
            'LinkedIn URL': LINKEDIN_URL_LIST,
            'Lead Role': LEAD_ROLE_LIST,
            'About Info': ABOUT_INFO_LIST,
            'Socials Info': SOCIALS_INFO_LIST,
            'Emails Info': EMAILS_INFO_LIST,
            'Website Info': WEBSITE_INFO_LIST,
            'Address Info': ADDRESS_INFO_LIST,
            'Phone Info': PHONE_INFO_LIST,
            'Company Link': COMPANY_LINK_LIST,
            'Company Overview': company_overiew_list,
            'Company Website': company_website_list,
            'Company Headquarters': company_headquarters_list,
    }


    df_company_info = pd.DataFrame(lists_dict)
    try:
        df_company_info.to_excel('xlsx/company_info.xlsx', index=False)
    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        print("Run 'pip install openpyxl' and then run transform.py")
    try:
        df_company_info.to_csv('csv/company_info.csv', index=False)
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
            'Lead Name': LEAD_NAME_LIST,
            'LinkedIn URL': LINKEDIN_URL_LIST,
            'Lead Role': LEAD_ROLE_LIST,
            'About Info': ABOUT_INFO_LIST,
            'Socials Info': SOCIALS_INFO_LIST,
            'Emails Info': EMAILS_INFO_LIST,
            'Website Info': WEBSITE_INFO_LIST,
            'Address Info': ADDRESS_INFO_LIST,
            'Phone Info': PHONE_INFO_LIST,
            'Company Link': COMPANY_LINK_LIST,
            'Company Overview': company_overiew_list,
            'Company Website': company_website_list,
            'Company Headquarters': company_headquarters_list,
    }

        # Find the list with the least elements
        least_elements_list_name = min(lists_dict, key=lambda k: len(lists_dict[k]))
        no_of_elements = len(lists_dict[least_elements_list_name])

        # Trim all lists to have the same length as the shortest list
        dlp_dict = {k: v[:no_of_elements] for k, v in lists_dict.items()}

        # Create a DataFrame and save it
        dlp_lead_info = pd.DataFrame(dlp_dict)
        try:
            dlp_lead_info.to_excel('xlsx/dlp_company_info.xlsx', index=False)
        except Exception as e:
            logging.error(f"Error saving DLP data to Excel: {e}")
            print("Run 'pip install openpyxl' and then run transform.py")
        try:
            dlp_lead_info.to_csv('csv/dlp_company_info.csv', index=False)
        except Exception as e:
            logging.error(f"Error saving DLP data to CSV: {e}")
        print("Data Loss Prevention Successful!")
