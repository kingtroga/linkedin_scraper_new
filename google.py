import os
import requests
import pandas as pd

def create_directories():
    # Directories to create
    directories = ["csv", "xlsx"]
    
    for directory in directories:
        try:
            # Create the directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            print(f"Directory '{directory}' is ready.")
        except OSError as e:
            print(f"Error creating directory '{directory}': {e}")


def remove_redundancies_and_save(df_new, filepath):
    if os.path.exists(filepath):
        # Load the existing file
        df_existing = pd.read_excel(filepath)
        
        # Concatenate the new and existing data, then drop duplicates
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(keep='last')
        
        # Save the updated file
        try:
            df_combined.to_excel(filepath, index=False)
        except Exception as e:
            print(f"Error saving file: {e}. Try running 'pip install openpyxl'")
            df_combined.to_csv('csv/linkedin_profiles.csv')
       
    else:
        # Save the new data if the file doesn't exist
        try:
            df_new.to_excel(filepath, index=False)
        except Exception as e:
            print(f"Error saving file: {e}. Try running 'pip install openpyxl'")
            df_new.to_csv('csv/linkedin_profiles.csv')
        


create_directories()

API_KEY = "AIzaSyBbbhA_0Lr42AivcPlwf2S5MnH8lZZ2aRg"
SEARCH_ENGINE_KEY = "f6e4825e942a248e1"

linkedin_profiles_new = []
seen_profiles = set()
max_results = 200  # Set the maximum number of results you want to retrieve

# Perform the search
print("Searching for LinkedIn profiles...")

search_query = "site:linkedin.com/in director of ecommerce united states"
url = 'https://www.googleapis.com/customsearch/v1'

# Retrieve multiple pages of results
for start in range(1, max_results):
    params = {
        'q': search_query,
        'key': API_KEY,
        'cx': SEARCH_ENGINE_KEY,
        'start': start
    }
    
    response = requests.get(url, params=params)
    results = response.json()
    
    if 'items' in results:
        for item in results['items']:
            link = item['link']
            # Check if the link is already in the set
            if link not in seen_profiles:
                linkedin_profiles_new.append(link)
                seen_profiles.add(link)  # Add the link to the set
    else:
        print('No more results found.')
        break

# Convert the list to a DataFrame
df_new = pd.DataFrame(linkedin_profiles_new, columns=['LinkedIn Profile'])

# Filepath to save the profiles
filepath = "xlsx/linkedin_profiles.xlsx"

# Remove redundancies and save the new list
remove_redundancies_and_save(df_new, filepath)

# Also save the new profiles to CSV
df_new.to_csv("csv/linkedin_profiles_new.csv", index=False)

print("LinkedIn profile search completed.")
