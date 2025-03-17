import csv
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 🚀 Setup Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    ]
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 🚀 Read Company Names from CSV
def read_companies_from_csv(csv_filename):
    companies = []
    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            companies.append(row['company_name'])  # Assuming "company_name" column exists
    return companies



# 🚀 Scrape LinkedIn for Contacts
def scrape_linkedin_for_contacts(input_csv, output_csv, state="US", max_pages=3):
    driver = setup_driver()
    companies = read_companies_from_csv(input_csv)
    results = []

    try:
        for company in companies:
            print(f"\n🚀 Searching for contacts at: {company}")  
            for page in range(max_pages):
                print(f"🔎 Scraping Page {page + 1} for {company}...")

                search_query = (
                    f"https://www.google.com/search?q=HR+OR+Recruiter+OR+Hiring+Manager+OR+Talent+Acquisition+"
                    f"OR+Founder+OR+Co-Founder+OR+CEO+site:linkedin.com/in/ {company} {state}&start={page * 10}"
                )
                driver.get(search_query)
                time.sleep(random.uniform(3, 6))  # Random delay to mimic human behavior

                try:
                    wait = WebDriverWait(driver, 10)
                    search_results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tF2Cxc')))
                    
                    if not search_results:
                        print(f"❌ No results found for {company} on Page {page + 1}. Stopping further search.")
                        break

                    for result in search_results:
                        retry_count = 3  # Retry mechanism for stale elements
                        while retry_count > 0:
                            try:
                                link_element = result.find_element(By.CSS_SELECTOR, 'h3')
                                description_element = result.find_element(By.CSS_SELECTOR, 'div.VwiC3b')
                                
                                linkedin_url = link_element.find_element(By.XPATH, './ancestor::a').get_attribute('href') if link_element else "N/A"
                                description = description_element.text if description_element else "N/A"
                                title = link_element.text if link_element else ""
                                
                                # Extract email and company name from description
                                extracted_company = title.split('-')[-1].strip() if '-' in title else company

                                if "linkedin.com/in" in linkedin_url:
                                    results.append({
                                        'company_name': extracted_company,
                                        'linkedin_profile': linkedin_url,
                                        'description': description,
                                    })
                                    print(f"✅ Found LinkedIn Profile: {linkedin_url} | Company: {extracted_company} | Description: {description}")
                                break  # Exit retry loop if successful
                            except StaleElementReferenceException:
                                print("🔴 Retrying due to stale element...")
                                retry_count -= 1
                                if retry_count == 0:
                                    print("❌ Failed to process element after multiple retries.")
                            except Exception as e:
                                print(f"⚠️ Error extracting profile: {e}")
                                break

                except TimeoutException:
                    print(f"❌ No search results found for {company} on Page {page + 1}. Stopping further search.")
                    break

        # 🚀 Save Results to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'linkedin_profile', 'description', 'email'])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Scraping complete! LinkedIn contacts saved to {output_csv}")

    finally:
        driver.quit()

# 🚀 Run the Scraper
if __name__ == "__main__":
    input_csv = 'hiring_companies_google.csv'  
    output_csv = 'linkedin_contacts.csv'  
    scrape_linkedin_for_contacts(input_csv, output_csv, state="US")
