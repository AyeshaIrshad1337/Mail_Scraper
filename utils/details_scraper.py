import csv
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# 🚀 Setup Selenium WebDriver
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    ]
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")

    driver = uc.Chrome(options=options)
    return driver

# 🚀 Read Company Names from CSV
def read_companies_from_csv(csv_filename):
    companies = []
    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            companies.append(row['company_name'])  # Assuming "company_name" column exists
    return companies

# 🚀 Scrape Bing for Company Details
def scrape_company_details(input_csv, state="Germany", output_dir="scraped/company"):
    driver = setup_driver()
    companies = read_companies_from_csv(input_csv)
    results = []

    try:
        for company in companies:
            search_url = f"https://www.bing.com/search?q={company}+company+website+description"
            driver.get(search_url)

            print(f"🔎 Searching: {company} on Bing")

            try:
                wait = WebDriverWait(driver, 10)
                result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.b_algo')))
                
                link_element = result.find_element(By.CSS_SELECTOR, 'h2 a')
                description_element = result.find_element(By.CSS_SELECTOR, 'p')

                link = link_element.get_attribute('href') if link_element else "N/A"
                description = description_element.text if description_element else "N/A"

                print(f"✅ Found: {company} | {link}")

                results.append({
                    'company_name': company,
                    'website': link,
                    'description': description
                })

            except (TimeoutException, NoSuchElementException):
                print(f"❌ No results for: {company}")
                results.append({'company_name': company, 'website': "N/A", 'description': "N/A"})

            time.sleep(random.uniform(2, 5))  # Sleep to avoid detection

        # 🚀 Save Results to CSV in Directory Structure
        country_dir = os.path.join(output_dir, state)
        os.makedirs(country_dir, exist_ok=True)

        output_file = os.path.join(country_dir, f"{state}-company-details.csv")

        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'website', 'description'])
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ Finished! Saved to {output_file}")

    finally:
        driver.quit()

# 🚀 Run the Scraper
if __name__ == "__main__":
    input_csv = 'hiring_companies_google.csv'  # Adjust input CSV path
    scrape_company_details(input_csv, state="US")
