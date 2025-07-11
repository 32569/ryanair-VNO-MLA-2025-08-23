"""
Ryanair one-way skriptas
Vilnius (VNO) ➜ Malta (MLA) | Data: 2025-08-23

Kasdien paleidžiamas GitHub Actions:
• Aplanko paruoštą URL
• Ištraukia pigiausios kainos tekstą
• Įrašo į data/flights.csv

Jei kaina nesurandama – įrašo 'N/A'.
"""

import csv
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# --- Konfigūracija -----------------------------------------------------------
ORIGIN          = "Vilnius"
DESTINATION     = "Malta"
DEPARTURE_DATE  = "2025-08-23"
CSV_FILE        = Path("data/flights.csv")
URL             = (
    "https://www.ryanair.com/gb/en/trip/flights/select?"
    "adults=1&teens=0&children=0&infants=0"
    f"&dateOut={DEPARTURE_DATE}"
    "&isConnectedFlight=false&discount=0&promoCode="
    "&originIata=VNO&destinationIata=MLA"
)
TIMEOUT_MS      = 60_000
# -----------------------------------------------------------------------------

def fetch_price() -> str:
    """
    Atidaro Ryanair puslapį ir bando ištraukti kainą.
    Grąžina kainą be valiutos ženklo (pvz. '88.69') arba 'N/A'.
    """
    with sync_playwright() as p:
        browser  = p.chromium.launch(headless=True)
        context  = browser.new_context()
        page     = context.new_page()

        page.goto(URL, timeout=TIMEOUT_MS)

        try:
            # Patikimesnis selektorius (kainos span) – laukiame iki 20 s
            page.wait_for_selector("span.flight-card-price__price", timeout=20_000)
            price_elem = page.query_selector("span.flight-card-price__price")
            price_text = (
                price_elem.inner_text().replace("€", "").strip()
                if price_elem else "N/A"
            )
        except Exception as e:
            print("⚠️  Kaina nerasta:", e)
            price_text = "N/A"

        browser.close()
        return price_text

def save_to_csv(price: str) -> None:
    """Prideda eilutę prie CSV (sukuria failą su antrašte, jei dar nėra)."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    CSV_FILE.parent.mkdir(exist_ok=True)

    # jei CSV neegzistuoja – sukuriam su antrašte
    if not CSV_FILE.exists():
        with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["date_scraped", "origin", "destination", "departure_date", "price_eur"]
            )

    # tikriname ar jau rašėme šiandien
    with CSV_FILE.open("r", newline="", encoding="utf-8") as f:
        if any(row[0] == today for row in csv.reader(f)):
            print("ℹ️  Šios dienos įrašas jau yra – nieko nepridedama.")
            return

    # pridedame naują eilutę
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, ORIGIN, DESTINATION, DEPARTURE_DATE, price])
        print(f"✅ Išsaugota: {today} | {price} €")

def main():
    price = fetch_price()
    save_to_csv(price)

if __name__ == "__main__":
    main()
