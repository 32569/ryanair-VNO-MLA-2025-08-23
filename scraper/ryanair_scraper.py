# scraper/ryanair_scraper.py

from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import os

# Konfigūracija
URL = "https://www.ryanair.com/gb/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2025-08-23&isConnectedFlight=false&discount=0&promoCode=&originIata=VNO&destinationIata=MLA&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2025-08-23&tpEndDate=2025-08-23"
CSV_PATH = "data/flights.csv"

def fetch_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        try:
            page.wait_for_selector("flights-price-simple.flight-card-summary__full-price", timeout=30000)
            price_element = page.query_selector("flights-price-simple.flight-card-summary__full-price")
            if price_element:
                price_text = price_element.inner_text().strip()
                browser.close()
                return price_text.replace("€", "").strip()
            else:
                browser.close()
                return "N/A"
        except Exception as e:
            print("Kaina nerasta:", e)
            browser.close()
            return "N/A"

def save_to_csv(price):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date_scraped", "origin", "destination", "departure_date", "price_eur"])
        writer.writerow([
            datetime.today().strftime("%Y-%m-%d"),
            "Vilnius",
            "Malta",
            "2025-08-23",
            price
        ])

if __name__ == "__main__":
    price = fetch_price()
    print("Rasta kaina:", price)
    save_to_csv(price)
