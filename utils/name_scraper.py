from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random
import os
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
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

def scrape_google_for_hiring_companies(tag="Mobile Developer", state="Germany", email_domain="gmail.com", max_pages=5):
    driver = setup_driver()
    companies = []

    try:
        for page in range(max_pages):
            # Google Search Query for Finding Companies Hiring Directly
            google_search_url = (
                f'https://www.google.com/search?q=%22{tag}%22+%22{state}%22+-intitle%3A%22profiles%22+-inurl%3A%22dir%2F+%22+'
                f'email%3A+%22%40{email_domain}%22+site%3Awww.linkedin.com%2Fin%2F+OR+site%3Awww.linkedin.com%2Fpub%2F'
                f'&start={page * 10}'  # Pagination
            )
            driver.get(google_search_url)

            wait = WebDriverWait(driver, 100)
            results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tF2Cxc')))

            for result in results:
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, 'h3')
                    link_element = result.find_element(By.CSS_SELECTOR, 'a')
                    description_element = result.find_element(By.CSS_SELECTOR, 'span')

                    title = title_element.text if title_element else ""
                    link = link_element.get_attribute('href') if link_element else ""
                    description = description_element.text if description_element else ""

                    # Extract Company Name from Title
                    job_title_extracted = title.split('-')[0].strip() if '-' in title else title
                    company_name = title.split('-')[-1].strip() if '-' in title else "Unknown"

                    if link and company_name and job_title_extracted:
                        company_data = {
                            'company_name': company_name,
                            'job_title': job_title_extracted,
                            'link': link,
                            'description': description
                        }
                        companies.append(company_data)

                    time.sleep(random.uniform(1, 3))

                except NoSuchElementException:
                    print("Element not found, skipping...")
                    continue
                except Exception as e:
                    print(f"Error extracting job details: {e}")
                    continue

        # Create main output directory if it doesn't exist
        output_dir = "scraped_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create subdirectory for the country/state if it doesn't exist
        country_dir = os.path.join(output_dir, state)
        if not os.path.exists(country_dir):
            os.makedirs(country_dir)

        # Create filename with country and job title
        filename = f"{state}-{tag}.csv"
        filepath = os.path.join(country_dir, filename)

        # Save the data
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'job_title', 'link', 'description'])
            writer.writeheader()
            writer.writerows(companies)

        print(f"Scraped {len(companies)} hiring companies successfully!")

    except TimeoutException:
        print("Timeout waiting for page to load")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_google_for_hiring_companies()
