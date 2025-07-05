import requests
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib.parse
import undetected_chromedriver as uc
import pandas as pd

class EtsyScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def init_driver(self, headless=False):
        """Initialize undetected Chrome driver with anti-detection measures"""
        user_agent = self.ua.random
        
        options = uc.ChromeOptions()
        options.add_argument(f"user-agent={user_agent}")
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Add additional preferences to avoid detection
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = uc.Chrome(options=options)
        
        # Execute scripts to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        return driver

    def try_direct_requests(self, search_url, max_pages=3):
        """Try using direct requests first (fastest but most likely to be blocked)"""
        print("Strategy 1: Direct HTTP requests...")
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                if "?" in search_url:
                    page_url = f"{search_url}&page={page}"
                else:
                    page_url = f"{search_url}?page={page}"
                
                print(f"Requesting page {page}: {page_url}")
                
                response = self.session.get(page_url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check for CAPTCHA or blocking
                    if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                        print(f"Page {page} blocked or has CAPTCHA")
                        break
                    
                    # Extract products
                    product_elements = soup.select('li.wt-list-unstyled.v2-listing-card')
                    print(f"Found {len(product_elements)} products on page {page}")
                    
                    page_products = self.extract_products_from_elements(product_elements)
                    products.extend(page_products)
                    
                else:
                    print(f"HTTP {response.status_code} for page {page}")
                    break
                    
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
                
            time.sleep(random.uniform(2, 4))
        
        return products

    def try_selenium_stealth(self, search_url, max_pages=3):
        """Try using Selenium with stealth measures"""
        print("Strategy 2: Selenium with stealth measures...")
        products = []
        driver = None
        
        try:
            driver = self.init_driver(headless=True)
            
            for page in range(1, max_pages + 1):
                try:
                    if "?" in search_url:
                        page_url = f"{search_url}&page={page}"
                    else:
                        page_url = f"{search_url}?page={page}"
                    
                    print(f"Navigating to page {page}: {page_url}")
                    
                    driver.get(page_url)
                    time.sleep(random.uniform(3, 6))
                    
                    # Check for CAPTCHA or blocking
                    page_source = driver.page_source
                    if "captcha-delivery.com" in page_source or "captcha" in driver.title.lower():
                        print(f"CAPTCHA detected on page {page}")
                        break
                    
                    # Try to find product elements
                    product_elements = driver.find_elements(By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card")
                    
                    if not product_elements:
                        product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-listing-id]")
                    
                    print(f"Found {len(product_elements)} product elements on page {page}")
                    
                    if product_elements:
                        # Convert to BeautifulSoup for parsing
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        product_elements_soup = soup.select('li.wt-list-unstyled.v2-listing-card')
                        
                        if not product_elements_soup:
                            product_elements_soup = soup.select('[data-listing-id]')
                        
                        page_products = self.extract_products_from_elements(product_elements_soup)
                        products.extend(page_products)
                    else:
                        print(f"No products found on page {page}")
                        break
                        
                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    break
                    
                time.sleep(random.uniform(4, 8))
                
        except Exception as e:
            print(f"Selenium error: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products

    def try_selenium_manual(self, search_url, max_pages=3):
        """Try using Selenium with manual CAPTCHA solving"""
        print("Strategy 3: Selenium with manual CAPTCHA solving...")
        products = []
        driver = None
        
        try:
            driver = self.init_driver(headless=False)  # Visible browser for manual solving
            
            for page in range(1, max_pages + 1):
                try:
                    if "?" in search_url:
                        page_url = f"{search_url}&page={page}"
                    else:
                        page_url = f"{search_url}?page={page}"
                    
                    print(f"Navigating to page {page}: {page_url}")
                    
                    driver.get(page_url)
                    time.sleep(3)
                    
                    # Check for CAPTCHA
                    page_source = driver.page_source
                    if "captcha-delivery.com" in page_source or "captcha" in driver.title.lower():
                        print("CAPTCHA detected! Please solve it manually in the browser window.")
                        print("After solving, press Enter to continue...")
                        input()
                        
                        # Refresh page after CAPTCHA solving
                        driver.refresh()
                        time.sleep(3)
                    
                    # Try to find product elements
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card"))
                        )
                    except:
                        print("Timeout waiting for product elements")
                    
                    product_elements = driver.find_elements(By.CSS_SELECTOR, "li.wt-list-unstyled.v2-listing-card")
                    
                    if not product_elements:
                        product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-listing-id]")
                    
                    print(f"Found {len(product_elements)} product elements on page {page}")
                    
                    if product_elements:
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        product_elements_soup = soup.select('li.wt-list-unstyled.v2-listing-card')
                        
                        if not product_elements_soup:
                            product_elements_soup = soup.select('[data-listing-id]')
                        
                        page_products = self.extract_products_from_elements(product_elements_soup)
                        products.extend(page_products)
                    else:
                        print(f"No products found on page {page}")
                        break
                        
                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    break
                    
                time.sleep(random.uniform(5, 10))
                
        except Exception as e:
            print(f"Selenium error: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products

    def extract_products_from_elements(self, product_elements):
        """Extract product information from BeautifulSoup elements"""
        products = []
        seen_products = set()
        
        for product in product_elements:
            try:
                # Extract product information using current Etsy selectors
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
                        'brand': "Unknown"
                    })
                    print(f"Added product: {name[:50]}... - {price}")
                    
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue
        
        return products

    def scrape_etsy_products(self, search_url, max_pages=3):
        """Main scraping method that tries multiple strategies"""
        print(f"Starting Etsy scraping for: {search_url}")
        print(f"Max pages: {max_pages}")
        print("=" * 50)
        
        all_products = []
        seen_products = set()
        
        # Strategy 1: Direct HTTP requests
        products = self.try_direct_requests(search_url, max_pages)
        if products:
            print(f"Strategy 1 successful: {len(products)} products")
            all_products.extend(products)
        else:
            print("Strategy 1 failed")
        
        print("-" * 30)
        
        # Strategy 2: Selenium stealth
        if not all_products:
            products = self.try_selenium_stealth(search_url, max_pages)
            if products:
                print(f"Strategy 2 successful: {len(products)} products")
                all_products.extend(products)
            else:
                print("Strategy 2 failed")
        
        print("-" * 30)
        
        # Strategy 3: Selenium with manual CAPTCHA solving
        if not all_products:
            print("All automated strategies failed. Trying manual CAPTCHA solving...")
            products = self.try_selenium_manual(search_url, max_pages)
            if products:
                print(f"Strategy 3 successful: {len(products)} products")
                all_products.extend(products)
            else:
                print("Strategy 3 failed")
        
        # Remove duplicates
        unique_products = []
        for product in all_products:
            product_key = (product['name'], product['price'])
            if product_key not in seen_products:
                seen_products.add(product_key)
                unique_products.append(product)
        
        # Save results
        with open('etsy_products_raw.json', 'w') as f:
            json.dump(unique_products, f, indent=2)
        print("Results saved to etsy_products_raw.json")
        # Save results as CSV
        if unique_products:
            df = pd.DataFrame(unique_products)
            df.to_csv('etsy_products_raw.csv', index=False)
            print("Results also saved to etsy_products_raw.csv")
        else:
            print("No products to save as CSV.")
        print("=" * 50)
        print(f"Scraping completed! Total unique products: {len(unique_products)}")
        return unique_products

if __name__ == "__main__":
    scraper = EtsyScraper()
    search_url = "https://www.etsy.com/search?q=vintage+jewelry"
    products = scraper.scrape_etsy_products(search_url, max_pages=2)
    print(f"Final result: {len(products)} products scraped.") 