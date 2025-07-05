from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import random
from fake_useragent import UserAgent
import requests

# You'll need to install: pip install 2captcha-python
# from twocaptcha import TwoCaptcha

def init_driver():
    ua = UserAgent()
    user_agent = ua.random
    
    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    # options.add_argument("--headless")  # Comment out headless for CAPTCHA solving
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Add additional preferences to avoid detection
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "geolocation": 2,
            "media_stream": 2,
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    
    # Execute scripts to avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    return driver

def solve_captcha(driver):
    """
    Handle CAPTCHA solving - you'll need to implement this with a service like 2captcha
    """
    print("CAPTCHA detected! You'll need to solve it manually or implement a CAPTCHA solving service.")
    print("For manual solving, the browser window should be visible.")
    
    # Wait for manual CAPTCHA solving
    input("Please solve the CAPTCHA manually and press Enter when done...")
    
    # Alternative: Use 2captcha service
    # solver = TwoCaptcha('YOUR_2CAPTCHA_API_KEY')
    # result = solver.recaptcha(sitekey='SITE_KEY', url=driver.current_url)
    # driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{result['code']}';")
    
    return True

def scrape_etsy_products(search_url, max_pages=5):
    driver = init_driver()
    products = []
    seen_products = set()
    page = 1

    try:
        while page <= max_pages:
            print(f"Scraping page {page}...")
            
            if "?" in search_url:
                page_url = f"{search_url}&page={page}"
            else:
                page_url = f"{search_url}?page={page}"
            
            print(f"Navigating to: {page_url}")
            
            try:
                driver.get(page_url)
                time.sleep(5)
                
                # Check for CAPTCHA
                page_source = driver.page_source
                if "captcha-delivery.com" in page_source or "captcha" in driver.title.lower():
                    print("CAPTCHA detected!")
                    if not solve_captcha(driver):
                        print("Failed to solve CAPTCHA")
                        break
                    # Refresh page after CAPTCHA solving
                    driver.refresh()
                    time.sleep(3)
                
                # Check if we got blocked
                if "blocked" in driver.title.lower() or "access denied" in driver.title.lower():
                    print(f"Page appears to be blocked. Title: {driver.title}")
                    break
                
                # Try to find product elements
                product_elements = []
                
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card"))
                    )
                    print("Found product elements using wait method")
                except:
                    print("Timeout waiting for product elements")
                
                product_elements = driver.find_elements(By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card")
                
                if not product_elements:
                    product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-listing-id]")
                    print("Trying alternative selector for products")
                
                print(f"Found {len(product_elements)} product elements on page {page}")

                if not product_elements:
                    print(f"No product elements found on page {page}. Ending crawl.")
                    with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Saved page source to debug_page_{page}.html for debugging")
                    break

                # Parse with BeautifulSoup
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                product_elements_soup = soup.select('li.wt-list-unstyled.v2-listing-card')
                
                if not product_elements_soup:
                    product_elements_soup = soup.select('[data-listing-id]')
                
                print(f"BeautifulSoup found {len(product_elements_soup)} product elements")

                for product in product_elements_soup:
                    try:
                        name_elem = product.select_one('h3.wt-text-body-small.v2-listing-card__title')
                        price_elem = product.select_one('span.currency-value')
                        seller_elem = product.select_one('p.wt-text-caption.wt-text-truncate')
                        rating_elem = product.select_one('span.wt-text-title-small')
                        
                        if not name_elem:
                            name_elem = product.select_one('h3[title]')
                        if not price_elem:
                            price_elem = product.select_one('.lc-price .currency-value')
                        if not seller_elem:
                            seller_elem = product.select_one('.streamline-seller-shop-name__line-height')

                        name = name_elem.get('title', '').strip() if name_elem else name_elem.text.strip() if name_elem else "Unknown"
                        price = price_elem.text.strip() if price_elem else "0.00"
                        seller = seller_elem.text.strip() if seller_elem else "Unknown"
                        
                        rating = "No rating"
                        if rating_elem:
                            rating_text = rating_elem.text.strip()
                            if rating_text:
                                rating = rating_text
                        
                        link_elem = product.select_one('a.listing-link')
                        product_url = link_elem.get('href') if link_elem else ""

                        product_key = (name, price)
                        if product_key not in seen_products:
                            seen_products.add(product_key)
                            products.append({
                                'name': name,
                                'price': price,
                                'seller': seller,
                                'rating': rating,
                                'url': product_url,
                                'brand': "Unknown"
                            })
                            print(f"Added product: {name[:50]}... - {price}")
                            
                    except Exception as e:
                        print(f"Error parsing product on page {page}: {e}")
                        continue

            except Exception as e:
                print(f"Error loading page {page}: {e}")
                try:
                    with open(f'debug_error_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Saved error page source to debug_error_page_{page}.html")
                except:
                    pass
                break

            page += 1
            time.sleep(random.uniform(5, 10))

    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()

    with open('etsy_products_raw.json', 'w') as f:
        json.dump(products, f, indent=2)
    print("Raw data saved to etsy_products_raw.json")

    return products

if __name__ == "__main__":
    search_url = "https://www.etsy.com/search?q=vintage+jewelry"
    products = scrape_etsy_products(search_url)
    print(f"Scraped {len(products)} products.") 