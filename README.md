# Etsy Scraper Portfolio Project

## Overview
Scrapes Etsy product listings for a search term (e.g., "vintage jewelry"), normalizes the data, and provides a Flask API and React dashboard for visualization. Demonstrates full-stack scraping, data processing, and visualization skills.

## Technologies & Anti-Bot Strategies Used
- **Python** for backend, scraping, and data processing
- **Selenium** and **undetected-chromedriver** to bypass Etsy's advanced bot detection and DataDome CAPTCHA
- **Manual CAPTCHA solving**: When prompted, user solves CAPTCHA in browser to continue scraping
- **BeautifulSoup** for HTML parsing
- **Flask** for serving a REST API
- **Flask-CORS** to allow the React frontend to fetch data from the backend
- **React** for the frontend dashboard (with Chart.js for visualization)
- **Axios** for API requests in the frontend
- **pandas** for CSV/JSON data handling
- **fake-useragent** for rotating user agents

### Anti-Bot Bypass Details
- Uses `undetected-chromedriver` to avoid Selenium detection by Etsy
- Randomizes user agents and browser options
- Prompts for manual CAPTCHA solving if DataDome is triggered
- Enables CORS in Flask to allow local frontend-backend communication

## Features
- Scrapes product name, price, seller, and rating from Etsy search results
- Handles JavaScript rendering and anti-scraping with undetected-chromedriver
- Cleans and deduplicates data, extracts brands with spaCy
- Flask API serves data for frontend
- React dashboard visualizes price distribution and allows filtering

## Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   pip install undetected-chromedriver flask-cors
   ```
2. **Install ChromeDriver** matching your Chrome version.

## Usage
1. Run the robust scraper:
   ```bash
   python robust_scraper.py
   ```
2. Start the API:
   ```bash
   python api.py
   ```
3. Set up and run the React frontend (see `frontend/` for details).

## Ethical Use
- Respect Etsy's terms and robots.txt
- Use for portfolio/analysis, not for commercial resale

## Example Output
- `etsy_products_raw.json`, `etsy_products_raw.csv`
- React dashboard with price distribution chart

## Screenshots
![Dashboard Screenshot](frontend/dashboard.png)
