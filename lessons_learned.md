# Lessons Learned: Etsy Product Scraper

## Challenges
- **Anti-Scraping Measures**: Etsy’s CAPTCHAs and IP bans required proxy rotation.
- **Dynamic Content**: JavaScript-rendered listings needed ScrapingBee’s API.
- **Brand Extraction**: No explicit brand data required NLP with spaCy.

## Solutions
- Used ScrapingBee API for proxy rotation and JavaScript rendering.
- Targeted `<li class="wt-list-unstyled v2-listing-card">` for product data.
- Implemented spaCy for brand extraction with regex fallback.

## AI Usage
- spaCy for identifying brand names in product titles.
- Pandas for data cleaning and deduplication.

## Improvements
- Add image scraping using Etsy’s ListingImage API.
- Implement real-time price monitoring with scheduled scraping.
- Deploy API and React app to AWS for scalability.

## Performance
- Scraped ~100 products across 5 pages in ~1 minute.
- Normalized data in <1 second, served via Flask API.

## Scalability
- Modularized scraper for other search terms or categories.
- Integrated React dashboard for client-facing visualization.
