from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

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

    # Extract the data
    price = safe_fetch_element_text((By.CSS_SELECTOR, '.sc-d1ede7e3-0.fsQm.base-text'))
    price_change = safe_fetch_element_text((By.CSS_SELECTOR, '.sc-71024e3e-0.sc-58c82cf9-1.bgxfSG.iPawMI'))
    market_cap = safe_fetch_element_text((By.XPATH, '//dd[@class="sc-d1ede7e3-0 hPHvUM base-text"]'))
    market_cap_rank = safe_fetch_element_text((By.XPATH, '//span[@class="text slider-value rank-value"]'))
    volume = safe_fetch_element_text((By.XPATH, '//div[@class="sc-4c05d6ef-0 sc-58c82cf9-0 dlQYLv dTczEt"]'))
    volume_rank = safe_fetch_element_text((By.XPATH, '//span[@class="text slider-value rank-value"]'))
    volume_change = safe_fetch_element_text((By.XPATH, '//dd[@class="sc-d1ede7e3-0 hPHvUM base-text"]'))
    circulating_supply = safe_fetch_element_text((By.XPATH, '//dt[div[text()="Circulating supply"]]/following-sibling::dd[@class="sc-d1ede7e3-0 hPHvUM base-text"]'))
    total_supply = safe_fetch_element_text((By.XPATH, '//dt[div[text()="Total supply"]]/following-sibling::dd[@class="sc-d1ede7e3-0 hPHvUM base-text"]'))
    diluted_market_cap = safe_fetch_element_text((By.XPATH, '//dt[div[text()="Fully diluted market cap"]]/following-sibling::dd[@class="sc-d1ede7e3-0 hPHvUM base-text"]'))
    contracts_name = safe_fetch_element_text((By.XPATH, '//span[@class="sc-71024e3e-0 dEZnuB"]'))
    contracts_address = safe_fetch_element_text((By.XPATH, '//span[@class="sc-71024e3e-0 eESYbg address"]'))
    official_links_name = safe_fetch_element_text((By.XPATH, '//div[@class="sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf"]'))
    official_link = safe_fetch_element_attribute((By.XPATH, '//div[@class="sc-7f0f401-3 dSYsgF"]/ancestor::a'), 'href')
    socials_name1 = safe_fetch_element_text((By.XPATH, '//div[@class="sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf"][1]/a'))
    socials_url1 = safe_fetch_element_attribute((By.XPATH, '//div[@class="sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf"][1]/a'), 'href')
    socials_name2 = safe_fetch_element_text((By.XPATH, '//div[@class="sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf"][2]/a'))
    socials_url2 = safe_fetch_element_attribute((By.XPATH, '//div[@class="sc-d1ede7e3-0 sc-7f0f401-0 gRSwoF gQoblf"][2]/a'), 'href')

    # print("contracts_name",contracts_name)

    contracts_data = {
        "name": contracts_name,
        "address": contracts_address
    }
    official_links = {
        "name": official_links_name,
        "link": official_link
    }
    socials_data1 = {
        "name": socials_name1,
        "url": socials_url1
    }
    socials_data2 = {
        "name": socials_name2,
        "url": socials_url2
    }
    print("socials_data1",socials_data1)
    print("socials_data2",socials_data2)




    if price and price_change and market_cap and market_cap_rank and volume and volume_rank and volume_change and circulating_supply and total_supply and diluted_market_cap and contracts_name and contracts_address:
        data["output"]["price"] = float(price.replace('$', '').replace(',', ''))
        price_change_percentage = price_change.split('%')[0]
        data["output"]["price_change"] = price_change_percentage
        data["output"]["market_cap"] = int(market_cap.split('$')[1].replace(',', ''))
        data["output"]["market_cap_rank"] = int(market_cap_rank.replace('#', ''))
        data["output"]["volume"] = float(volume.split('%')[0])
        data["output"]["volume_rank"] = int(volume_rank.replace('#', ''))
        data["output"]["volume_change"] = float(volume_change.split('%')[0])
        data["output"]["circulating_supply"] = int(circulating_supply.replace(",", "").split()[0])
        data["output"]["total_supply"] = int(circulating_supply.replace(",", "").split()[0])
        data["output"]["diluted_market_cap"] = int(diluted_market_cap.split('$')[1].replace(',', ''))
        # data["output"]["contracts"]["name"] = contracts_name
        # data["output"]["contracts"]["address"] = contracts_address
        
        data["output"]["contracts"].append(contracts_data)
        data["output"]["official_links"].append(official_links)
        data["output"]["socials"].append(socials_data1)
        data["output"]["socials"].append(socials_data2)
        

    driver.quit()
    return data

# Main script
if __name__ == "__main__":
    coins = ['DUKO', 'NOTCOIN', 'GORILLA-TOKEN']
    coin_data = []
    task = []

    for coin in coins:
        data = scrape_coin_data(coin)
        coin_data.append(data)

    # Print the data
    for data in coin_data:
        task.append(data)
    print(task)
        # print(data)
