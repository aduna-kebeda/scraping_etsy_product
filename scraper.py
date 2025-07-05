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

def init_driver():
    ua = UserAgent()
    user_agent = ua.random
    
    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
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

def scrape_etsy_products(search_url, max_pages=5):
    driver = init_driver()
    products = []
    seen_products = set()  # Deduplicate by name and price
    page = 1

    try:
        while page <= max_pages:
            print(f"Scraping page {page}...")
            
            # Construct the page URL
            if "?" in search_url:
                page_url = f"{search_url}&page={page}"
            else:
                page_url = f"{search_url}?page={page}"
            
            print(f"Navigating to: {page_url}")
            
            try:
                driver.get(page_url)
                
                # Wait a bit for the page to start loading
                time.sleep(5)
                
                # Check if we got a CAPTCHA or blocked page
                page_title = driver.title.lower()
                if "captcha" in page_title or "blocked" in page_title or "access denied" in page_title:
                    print(f"Page appears to be blocked or has CAPTCHA. Title: {driver.title}")
                    break
                
                # Try to find product elements with different approaches
                product_elements = []
                
                # Method 1: Wait for specific elements
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card"))
                    )
                    print("Found product elements using wait method")
                except:
                    print("Timeout waiting for product elements")
                
                # Method 2: Direct selection
                product_elements = driver.find_elements(By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card")
                
                # Method 3: Alternative selectors if the above don't work
                if not product_elements:
                    product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-listing-id]")
                    print("Trying alternative selector for products")
                
                print(f"Found {len(product_elements)} product elements on page {page}")

                if not product_elements:
                    print(f"No product elements found on page {page}. Ending crawl.")
                    # Save the page source for debugging
                    with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Saved page source to debug_page_{page}.html for debugging")
                    break

                # Get the page source and parse with BeautifulSoup
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Find product elements using the current Etsy structure
                product_elements_soup = soup.select('li.wt-list-unstyled.v2-listing-card')
                
                if not product_elements_soup:
                    # Try alternative selectors
                    product_elements_soup = soup.select('[data-listing-id]')
                
                print(f"BeautifulSoup found {len(product_elements_soup)} product elements")

                for product in product_elements_soup:
                    try:
                        # Extract product information using the current Etsy selectors
                        name_elem = product.select_one('h3.wt-text-body-small.v2-listing-card__title')
                        price_elem = product.select_one('span.currency-value')
                        seller_elem = product.select_one('p.wt-text-caption.wt-text-truncate')
                        rating_elem = product.select_one('span.wt-text-title-small')
                        
                        # Alternative selectors if the above don't work
                        if not name_elem:
                            name_elem = product.select_one('h3[title]')
                        if not price_elem:
                            price_elem = product.select_one('.lc-price .currency-value')
                        if not seller_elem:
                            seller_elem = product.select_one('.streamline-seller-shop-name__line-height')

                        name = name_elem.get('title', '').strip() if name_elem else name_elem.text.strip() if name_elem else "Unknown"
                        price = price_elem.text.strip() if price_elem else "0.00"
                        seller = seller_elem.text.strip() if seller_elem else "Unknown"
                        
                        # Extract rating and review count
                        rating = "No rating"
                        if rating_elem:
                            rating_text = rating_elem.text.strip()
                            if rating_text:
                                rating = rating_text
                        
                        # Get product URL
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
                                'brand': "Unknown"  # Etsy doesn't explicitly list brands
                            })
                            print(f"Added product: {name[:50]}... - {price}")
                            
                    except Exception as e:
                        print(f"Error parsing product on page {page}: {e}")
                        continue

            except Exception as e:
                print(f"Error loading page {page}: {e}")
                # Save the page source for debugging
                try:
                    with open(f'debug_error_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Saved error page source to debug_error_page_{page}.html")
                except:
                    pass
                break

            page += 1
            time.sleep(random.uniform(5, 10))  # Longer delays to avoid rate limits

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
