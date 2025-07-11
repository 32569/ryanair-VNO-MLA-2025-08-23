import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

def fetch_price():
    url = "https://www.ryanair.com/gb/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2025-08-23&isConnectedFlight=false&discount=0&promoCode=&originIata=VNO&destinationIata=MLA&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2025-08-23&tpEndDate=2025-08-23&tpDiscount=0"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_selector("div.flight-header__min-price", timeout=15000)

        try:
            price_element = page.query_selector("div.flight-header__min-price")
            price_text = price_element.inner_text().replace("€", "").strip() if price_element else "N/A"
        except:
            price_text = "N/A"

        browser.close()
        return price_text

def save_to_csv(price):
    filename = "data/flights.csv"
    date_scraped = datetime.now().strftime("%Y-%m-%d")
    origin = "Vilnius"
    destination = "Malta"
    departure_date = "2025-08-23"

    try:
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["date_scraped", "origin", "destination", "departure_date", "price_eur"])
            writer.writerow([date_scraped, origin, destination, departure_date, price])
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    price = fetch_price()
    save_to_csv(price)
