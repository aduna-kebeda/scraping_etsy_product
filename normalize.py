import pandas as pd
import json
import re
import spacy

# Load spaCy model for brand extraction
nlp = spacy.load("en_core_web_sm")

def normalize_data(json_file):
    with open(json_file, 'r') as f:
        products = json.load(f)

    df = pd.DataFrame(products)

    # Clean price: Remove currency symbols and convert to float
    df['price'] = df['price'].apply(lambda x: float(re.sub(r'[^\d.]', '', x)) if x != "0.00" else 0.0)

    # Normalize brand: Use spaCy to identify potential brand names
    def extract_brand(name):
        doc = nlp(name)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        # Fallback: Remove product types and take first word
        return re.sub(r'\s+(Jewelry|Necklace|Ring|Bracelet|Earrings|Pendant|Handmade|Vintage|Custom)', '', name).split()[0]

    df['brand'] = df['brand'].apply(lambda x: extract_brand(x) if x == "Unknown" else x)

    # Clean rating: Extract numerical rating (e.g., "4.8 out of 5" -> 4.8)
    def clean_rating(rating):
        match = re.search(r'(\d+\.\d+)', rating)
        return float(match.group(0)) if match else 0.0

    df['rating'] = df['rating'].apply(clean_rating)

    # Remove duplicates based on name and price
    df = df.drop_duplicates(subset=['name', 'price'])

    # Handle missing values
    df = df.fillna({'brand': 'Unknown', 'price': 0.0, 'seller': 'Unknown', 'rating': 0.0})
    return df

def save_to_csv(df, filename="etsy_products.csv"):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    df = normalize_data('etsy_products_raw.json')
    save_to_csv(df)
