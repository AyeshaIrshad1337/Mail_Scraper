from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_hiring_companies():
    driver = setup_driver()
    job_title = "Mobile Developer"
    location = "USA"
    max_pages = 3  # Increase pages for more results
    
    try:
        companies = []
        for page in range(max_pages):
            search_url = (
                f'https://www.google.com/search?q=%22{job_title}%22+%22hiring%22+%22{location}%22+'
                f'site:linkedin.com/jobs OR site:indeed.com/viewjob OR site:glassdoor.com/job-listing'
                f'&start={page * 10}'  # Pagination
            )
            driver.get(search_url)
            
            wait = WebDriverWait(driver, 10)
            results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tF2Cxc')))
            
            for result in results:
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, 'h3')
                    link_element = result.find_element(By.CSS_SELECTOR, 'a')
                    description_element = result.find_element(By.CSS_SELECTOR, 'div.VwiC3b')
                    
                    title = title_element.text if title_element else ""
                    link = link_element.get_attribute('href') if link_element else ""
                    description = description_element.text if description_element else ""
                    
                    job_title_extracted = ""
                    company_name = ""
                    if '-' in title:
                        parts = title.split('-')
                        job_title_extracted = parts[0].strip()
                        company_name = parts[-1].strip()
                    
                    if link and company_name and job_title_extracted:
                        company_data = {
                            'company_name': company_name,
                            'job_title': job_title_extracted,
                            'link': link,
                            'description': description
                        }
                        companies.append(company_data)
                    
                    time.sleep(random.uniform(1, 3))
                
                except Exception as e:
                    print(f"Error extracting company details: {e}")
                    continue
        
        with open('hiring_companies.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'job_title', 'link', 'description'])
            writer.writeheader()
            writer.writerows(companies)
        
        print(f"Scraped {len(companies)} companies successfully!")
        
    except TimeoutException:
        print("Timeout waiting for page to load")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_hiring_companies()