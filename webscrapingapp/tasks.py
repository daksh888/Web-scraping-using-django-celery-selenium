


from celery import shared_task
from time import sleep
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import uuid  # For generating unique job ID


# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--ignore-certificate-errors")

# Set preferences for cookies
chrome_prefs = {
    "profile.default_content_setting_values.cookies": 1,  # Allow cookies
    "profile.default_content_settings.cookies": 1,
    "profile.cookie_controls_mode": 0  # Allow third-party cookies
}
chrome_options.experimental_options["prefs"] = chrome_prefs

# Path to the ChromeDriver executable
chrome_driver_path = r'C:\Users\DIESEL_ROCKET\.cache\selenium\chromedriver\win64\125.0.6422.141\chromedriver.exe'

# Function to scrape data for a specific coin
def scrape_coin_data(coin):
    # Create a ChromeService object
    service = ChromeService(executable_path=chrome_driver_path)
    # Initialize the WebDriver with the service object
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = f"https://coinmarketcap.com/currencies/{coin.lower()}/"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    data = {"coin": coin, "output": {"contracts": [], "official_links":[], "socials": []}}
    # Wait until the page is fully loaded
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Function to safely fetch element text
    def safe_fetch_element_text(locator):
        for _ in range(3):  # Retry 3 times
            try:
                element = wait.until(EC.presence_of_element_located(locator))
                return element.text.strip()
            except StaleElementReferenceException:
                continue
        return None
    def safe_fetch_element_attribute(locator, attribute):
        for _ in range(3):  # Retry 3 times
            try:
                element = wait.until(EC.presence_of_element_located(locator))
                return element.get_attribute(attribute)
            except StaleElementReferenceException:
                continue
        return None

    # Extract the data (continued from your code)

    # Add the rest of your scraping logic here

    driver.quit()
    return data

# Celery task for data scraping
@shared_task(bind=True)
def scrape_data_for_coins(self, coins):
    job_id = str(uuid.uuid4())  # Generate unique job ID
    task_data = []  # Store task data for each coin
    all_success = True  # Track if all scrapes are successful

    for coin in coins:
        success, data = scrape_coin_data(coin)
        if not success:
            all_success = False
        task_data.append(data)

    if all_success:
        final_data = {"job_id": job_id, "task_data": task_data}
    else:
        final_data = {"error": "One or more coin data scrapes failed", "task_data": task_data}

    return final_data

# Example usage:
# Call this task with a list of coins as an argument
# scrape_data_for_coins.delay(['DUKO', 'NOTCOIN', 'GORILLA-TOKEN'])
