from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import time
import csv
import random
import re
from CREDS import FOLDER_NAME, TAGS

# Configure ChromeOptions
opt = webdriver.ChromeOptions()
opt.add_argument("--disable-popup-blocking")
opt.add_argument("--headless")  # Run in headless mode to prevent UI interactions
opt.add_argument("--no-sandbox")
opt.add_argument("--disable-dev-shm-usage")
opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")  # Random User Agent

# Start Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opt)

# Ensure necessary directories exist
if not os.path.exists('./csvs'):
    os.mkdir('./csvs')
if not os.path.exists('./logs'):
    os.mkdir('./logs')

DIR = os.path.join('./csvs', FOLDER_NAME)
if not os.path.exists(DIR):
    os.mkdir(DIR)

# Define the target skill
TARGET_SKILL = "Mobile Developer"
COUNTRIES = ["United States", "Germany"]

output_file = os.path.join(DIR, 'scraped_mobile_companies.csv')

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Company Name", "Person Name", "Designation", "Location", "Profile Link", "Email", "Source"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for country in COUNTRIES:
        for tag in TAGS:
            query = f'"{tag}" "{TARGET_SKILL}" "{country}" site:linkedin.com/company'
            search_url = "https://www.google.com/search?q=" + query.replace(" ", "+")
            print(f"Searching: {query}")
            
            driver.get(search_url)
            time.sleep(random.randint(5, 10))  # Random sleep to avoid detection
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', class_='tF2Cxc')  # Adjust selector if needed

            for result in results:
                link_tag = result.find('a', href=True)
                if not link_tag:
                    continue
                profile_link = link_tag['href']

                title_tag = result.find('h3')
                company_name = title_tag.get_text(strip=True) if title_tag else ''

                try:
                    driver.get(profile_link)
                    time.sleep(random.randint(3, 7))
                    profile_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    person_name_tag = profile_soup.find('h1')
                    person_name = person_name_tag.get_text(strip=True) if person_name_tag else ""
                    
                    designation_tag = profile_soup.find('h2')
                    designation = designation_tag.get_text(strip=True) if designation_tag else ""
                    
                    location_tag = profile_soup.find('span', class_='t-16 t-black t-normal inline-block')
                    location = location_tag.get_text(strip=True) if location_tag else ""
                    
                    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", driver.page_source)
                    email = emails[0] if emails else ""
                    
                    writer.writerow({
                        "Company Name": company_name,
                        "Person Name": person_name,
                        "Designation": designation,
                        "Location": location,
                        "Profile Link": profile_link,
                        "Email": email,
                        "Source": search_url
                    })
                    print(f"Scraped: {profile_link}")
                except Exception as e:
                    print(f"Error processing {profile_link}: {e}")

# Close the driver
driver.quit()
