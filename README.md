# Etsy Scraper Portfolio Project

## Overview
Scrapes Etsy product listings for a search term (e.g., "vintage jewelry"), normalizes the data, and provides a Flask API and React dashboard for visualization. Demonstrates full-stack scraping, data processing, and visualization skills.

## Features
- Scrapes product name, price, seller, and rating from Etsy search results
- Handles JavaScript rendering and anti-scraping with ScrapingBee
- Cleans and deduplicates data, extracts brands with spaCy
- Flask API serves data for frontend
- React dashboard visualizes price distribution and allows filtering

## Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
2. **Get a ScrapingBee API key**: https://www.scrapingbee.com/
3. **Install ChromeDriver** matching your Chrome version.

## Usage
1. Run the scraper:
   ```bash
   python scraper.py
   ```
2. Normalize data:
   ```bash
   python normalize.py
   ```
3. Start the API:
   ```bash
   python api.py
   ```
4. Set up and run the React frontend (see `frontend/` for details).

## Ethical Use
- Respect Etsy's terms and robots.txt
- Use for portfolio/analysis, not for commercial resale

## Example Output
- `etsy_products_raw.json`, `etsy_products.csv`
- React dashboard with price distribution chart

## Screenshots
![Dashboard Screenshot](frontend/dashboard.png)
