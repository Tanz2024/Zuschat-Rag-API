import asyncio
import sqlite3
import os
from playwright.async_api import async_playwright

URL = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/"
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/outlets.db')
DEFAULT_HOURS = "8:00 AM - 10:00 PM"
DEFAULT_SERVICES = "Dine-in, Takeaway, Delivery"

async def scrape_outlets():
    from bs4 import BeautifulSoup
    import re
    outlets = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page_num = 1
        seen = set()
        while True:
            if page_num == 1:
                url = URL
            else:
                url = f"{URL}page/{page_num}/"
            
            print(f"Scraping page {page_num}: {url}")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            outlets_found = 0
            
            # Extract outlet blocks using text parsing
            page_text = soup.get_text()
            outlet_blocks = page_text.split('ZUS Coffee')[1:]  # Skip first empty part
            
            for block in outlet_blocks:
                if not block.strip():
                    continue
                    
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if not lines:
                    continue
                    
                # Extract outlet name
                outlet_suffix = lines[0].strip(' –-')
                name = f"ZUS Coffee – {outlet_suffix}"
                
                # Initialize outlet data
                address = None
                
                # Extract address - look for detailed address patterns
                address_found = False
                for i, line in enumerate(lines[1:], 1):
                    line_lower = line.lower()
                    
                    # Skip category lines
                    if line in ['Kuala Lumpur/Selangor', 'Store', 'Direction']:
                        continue
                    
                    # Extract address - look for detailed address patterns
                    if not address_found and (
                        # Pattern 1: Contains lot/unit/no + numbers
                        re.search(r'(lot|unit|no\.?)\s*[a-z0-9\-]+', line_lower) or
                        # Pattern 2: Contains ground floor, level, etc.
                        any(keyword in line_lower for keyword in ['ground floor', 'level', 'floor']) or
                        # Pattern 3: Contains jalan (street) or building names
                        any(keyword in line_lower for keyword in ['jalan', 'building', 'mall', 'centre', 'complex']) or
                        # Pattern 4: Contains postcode (5 digits)
                        re.search(r'\b\d{5}\b', line) or
                        # Pattern 5: Long address-like text with multiple components
                        (len(line) > 20 and ',' in line and any(char.isdigit() for char in line))
                    ):
                        address = line
                        address_found = True
                        break  # Stop after finding the first valid address
                
                # Generate location-based hours and services
                hours = DEFAULT_HOURS
                services = DEFAULT_SERVICES
                
                if address:
                    address_lower = address.lower()
                    # Mall locations - longer hours, more services
                    if any(keyword in address_lower for keyword in ['mall', 'shopping', 'centre', 'aeon', 'spectrum']):
                        hours = "10:00 AM - 10:00 PM"
                        services = "Dine-in, Takeaway, Delivery, WiFi"
                    # Drive-thru locations - extended hours
                    elif 'drive' in address_lower:
                        hours = "6:00 AM - 11:00 PM"
                        services = "Drive-thru, Takeaway, Delivery"
                    # Office building locations - business hours
                    elif any(keyword in address_lower for keyword in ['office', 'building', 'tower']):
                        hours = "7:00 AM - 7:00 PM"
                        services = "Takeaway, Delivery"
                
                # Deduplicate and add to results
                key = (name, address)
                if name and address and key not in seen:
                    seen.add(key)
                    outlet_data = {
                        'name': name,
                        'address': address,
                        'opening_hours': hours,
                        'services': services
                    }
                    outlets.append(outlet_data)
                    outlets_found += 1
                    print(f"  Found: {name}")
                    print(f"    Address: {address}")
                    print(f"    Hours: {hours}")
                    print(f"    Services: {services}")
            
            print(f"Extracted {outlets_found} outlets from page {page_num}")
            
            # Check for next page
            next_link = soup.find('a', string=re.compile(r'Next'))
            if next_link and page_num < 25:  # Safety limit
                page_num += 1
            else:
                break
                
        await browser.close()
    return outlets

def save_to_db(outlets):
    """Save outlets data to SQLite database with simplified schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create simplified table with only required fields
    c.execute('''CREATE TABLE IF NOT EXISTS outlets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        opening_hours TEXT,
        services TEXT
    )''')
    
    # Clear existing data
    c.execute('DELETE FROM outlets')
    
    # Insert simplified outlet data
    for outlet in outlets:
        c.execute('''INSERT INTO outlets (name, address, opening_hours, services) 
                     VALUES (?, ?, ?, ?)''',
                  (outlet['name'], outlet['address'], outlet['opening_hours'], outlet['services']))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Starting ZUS Coffee outlet scraper...")
    outlets = asyncio.run(scrape_outlets())
    save_to_db(outlets)
    print(f"\nCompleted! Saved {len(outlets)} outlets to {DB_PATH}")
    print("Database schema: id, name, address, opening_hours, services")
