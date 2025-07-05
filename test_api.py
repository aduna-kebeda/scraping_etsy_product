import requests
import urllib.parse

# Your ScrapingBee API key
SCRAPINGBEE_API_KEY = "B8TTL8MIZC46RVBCFV75H0LDLXXZY8L5A6GZ740GM1M1OWZALC3F3JR8YFWLRJAMXCVW27M035AARJIG"

def test_scrapingbee_api():
    """Test if the ScrapingBee API key is working"""
    
    # Test with a simple website first
    test_url = "https://httpbin.org/html"
    encoded_url = urllib.parse.quote(test_url, safe=':/?=&')
    
    api_url = f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}"
    
    print("Testing ScrapingBee API with a simple website...")
    print(f"API URL: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API key is working!")
            print(f"Response length: {len(response.text)} characters")
            print(f"First 200 chars: {response.text[:200]}...")
        else:
            print(f"❌ API key test failed: {response.status_code}")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_etsy_url():
    """Test with the actual Etsy URL using various ScrapingBee options"""
    
    etsy_url = "https://www.etsy.com/search?q=vintage+jewelry"
    encoded_url = urllib.parse.quote(etsy_url, safe=':/?=&')
    
    options = [
        ("Default (render_js)", f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}&render_js=true"),
        ("block_resources=False", f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}&render_js=true&block_resources=false"),
        ("premium_proxy=True", f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}&render_js=true&premium_proxy=true"),
        ("stealth_proxy=True", f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}&render_js=true&stealth_proxy=true"),
        ("stealth_proxy=True + block_resources=False", f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={encoded_url}&render_js=true&stealth_proxy=true&block_resources=false"),
    ]
    
    for label, api_url in options:
        print(f"\nTesting with option: {label}")
        print(f"API URL: {api_url}")
        try:
            response = requests.get(api_url, timeout=90)
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success!")
                print(f"Response length: {len(response.text)} characters")
                if "<html" in response.text.lower():
                    print("✅ HTML content received")
                else:
                    print("⚠️ No HTML content detected")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error response: {response.text[:500]}...")
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_scrapingbee_api()
    test_etsy_url() 