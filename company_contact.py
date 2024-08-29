import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re

DATA_FRAME = pd.read_excel('xlsx/company_info.xlsx')

COMPANY_WEBSITES = DATA_FRAME['Company Website'].to_list()
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
COMPANY_OVERVIEW_LIST = list(DATA_FRAME['Company Overview'])
COMPANY_WEBSITE_LIST = list(DATA_FRAME['Company Website'])
COMPANY_HEADQUARTERS_LIST = list(DATA_FRAME['Company Headquarters'])

from urllib.parse import urlparse


company_emails_list = []
company_socials_list = []
company_phone_list = []


def extract_info(soup):
    # Define regex patterns
    emails_string = ""
    phones_string = ""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d[\d -]{8,}\d'
    

    # Extract emails
    emails = set(re.findall(email_pattern, soup.get_text(), re.IGNORECASE))
    
    # Extract phone numbers
    phone_numbers = set(re.findall(phone_pattern, soup.get_text()))


    # Print extracted information
    
    for email in emails:
        emails_string = emails_string + " " + str(email) + ";"
    
    
    for phone in phone_numbers:
        phones_string = phones_string + " " + str(phone) + ";" 


    return emails_string, phones_string

    



def google_custom_search(url):
    # API endpoint and query parameters
    api_key = "AIzaSyBbbhA_0Lr42AivcPlwf2S5MnH8lZZ2aRg"
    search_engine_key = "f6e4825e942a248e1"
    search_url = 'https://www.googleapis.com/customsearch/v1'
    
    raw_domain = str(url).split('.')
    domain = raw_domain[-2] + '.' + raw_domain[-1]

    # SEARCH GOOGLE  
    search_query = f"site:{domain} contact"
    params = {
        'key': api_key,
        'cx': search_engine_key,
        'q': search_query
    }

    try:
        # Make the GET request to the Google Custom Search API
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        # Parse the JSON response
        search_results = response.json()
        if 'items' in search_results and len(search_results['items']) > 0:
            # Return the first result
            first_result = search_results['items'][0]
            return first_result.get('link')
        else:
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None

def main():
    driver = webdriver.Chrome()
    

    for company_website in COMPANY_WEBSITES:
        socials_string = ""
        contact_link = google_custom_search(company_website)
        if contact_link:

            try:
                driver.get(contact_link)
            except Exception as e:
                print(e)
                company_emails_list.append("NULL")
                company_socials_list.append("NULL")
                company_phone_list.append("NULL")
                continue

            time.sleep(15)
            try:
                links = driver.find_elements(By.TAG_NAME, 'a')


                for link in links:
                    link = link.get_attribute('href')
                    # Social(s)
                    if "twitter.com/" in link:
                        socials_string = socials_string + " " + link.strip() + ";"
                    elif "x.com/" in link:
                        socials_string = socials_string + " " + link.strip() + ";"
                    elif "instagram.com/" in link:
                        socials_string = socials_string + " " + link.strip() + ";"
                    elif "facebook.com/" in link:
                        socials_string = socials_string + " " + link.strip() + ";"
                    elif "pinterest.com/" in link:
                        socials_string = socials_string + " " + link.strip() + ";"
            except Exception as e:
                print(f"Couldn't find socials on this page: {e}")
                

                    


            soup = BeautifulSoup(driver.page_source, 'html.parser')
            emails_string, phones_string =  extract_info(soup)
            if emails_string:
                company_emails_list.append(emails_string)
            else:
                company_emails_list.append("NULL")
            
            if phones_string:
                company_phone_list.append(phones_string)
            else:
                company_phone_list.append("NULL")


            if socials_string:
                company_socials_list.append(socials_string)
            else:
                company_socials_list.append("NULL")
    
        else:
            company_emails_list.append("NULL")
            company_socials_list.append("NULL")
            company_phone_list.append("NULL")
            continue

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
            'Company Overview': COMPANY_OVERVIEW_LIST,
            'Company Website': COMPANY_WEBSITE_LIST,
            'Company Headquarters': COMPANY_HEADQUARTERS_LIST,
            'Company Email(s)': company_emails_list,
            'Company Phone(s)': company_phone_list,
            'Company Social(s)': company_socials_list,
    }


    df_company_info = pd.DataFrame(lists_dict)
    try:
        df_company_info.to_excel('xlsx/scrape_final.xlsx', index=False)
    except Exception as e:
        print(f"Error saving data to Excel: {e}")
        print("Run 'pip install openpyxl' and then run transform.py")
    try:
        df_company_info.to_csv('csv/scrape_final.csv', index=False)
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
    


    


if __name__ == "__main__":
    try:
        main()
        print("Scrapping successful!")
    except Exception as e:
        print(f"Critical error occurred: {e}")

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
            'Company Overview': COMPANY_OVERVIEW_LIST,
            'Company Website': COMPANY_WEBSITE_LIST,
            'Company Headquarters': COMPANY_HEADQUARTERS_LIST,
            'Company Email(s)': company_emails_list,
            'Company Phone(s)': company_phone_list,
            'Company Social(s)': company_socials_list,
    }

        # Find the list with the least elements
        least_elements_list_name = min(lists_dict, key=lambda k: len(lists_dict[k]))
        no_of_elements = len(lists_dict[least_elements_list_name])

        # Trim all lists to have the same length as the shortest list
        dlp_dict = {k: v[:no_of_elements] for k, v in lists_dict.items()}

        # Create a DataFrame and save it
        dlp_lead_info = pd.DataFrame(dlp_dict)
        try:
            dlp_lead_info.to_excel('xlsx/dlp_scrape_final.xlsx', index=False)
        except Exception as e:
            print(f"Error saving DLP data to Excel: {e}")
            print("Run 'pip install openpyxl' and then run transform.py")
        try:
            dlp_lead_info.to_csv('csv/dlp_scrape_final.csv', index=False)
        except Exception as e:
            print(f"Error saving DLP data to CSV: {e}")
        print("Data Loss Prevention Successful!")
