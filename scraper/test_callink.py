"""
Quick CalLink Test - Verifies scraping works before full run
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def test_callink():
    print("\n" + "="*60)
    print("🧪 Testing CalLink Scraper")
    print("="*60 + "\n")
    
    driver = setup_driver()
    events = []
    
    try:
        driver.get("https://callink.berkeley.edu/events")
        print("⏳ Waiting for page to load...")
        
        wait = WebDriverWait(driver, 20)
        
        # Use the working selector we discovered
        print("🔍 Looking for events with: div[class*='Card']")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='Card']")))
        
        event_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='Card']")
        print(f"✅ Found {len(event_elements)} event cards\n")
        
        for i, element in enumerate(event_elements[:10], 1):
            try:
                # Get title
                title = None
                try:
                    # Try to find title in various places
                    title_element = element.find_element(By.CSS_SELECTOR, "h2, h3, h4")
                    title = title_element.text.strip()
                except:
                    title = element.text.strip().split('\n')[0]  # First line
                
                # Get URL
                url = None
                try:
                    link = element.find_element(By.TAG_NAME, 'a')
                    url = link.get_attribute('href')
                except:
                    url = "https://callink.berkeley.edu/events"
                
                # Get description
                description = element.text.strip()
                
                if title and len(title) > 3:
                    print(f"{i}. {title[:70]}...")
                    print(f"   URL: {url}")
                    print(f"   Preview: {description[:100]}...\n")
                    
                    events.append({
                        'title': title[:200],
                        'description': description[:500] if description else None,
                        'location': "Berkeley, CA",
                        'source_url': url,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"⚠️  Skipped event {i}: {e}")
        
        print(f"\n✅ Successfully extracted {len(events)} events!")
        
        # Ask if user wants to upload
        if events:
            print("\n" + "="*60)
            upload = input("Upload to Supabase? (y/n): ").strip().lower()
            
            if upload == 'y':
                from supabase import create_client
                
                SUPABASE_URL = os.getenv("SUPABASE_URL")
                SUPABASE_KEY = os.getenv("SUPABASE_KEY")
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                
                try:
                    response = supabase.table('events').insert(events).execute()
                    print(f"✅ Uploaded {len(events)} events to Supabase!")
                except Exception as e:
                    print(f"❌ Upload failed: {e}")
            else:
                print("Skipped upload.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        driver.save_screenshot("/tmp/callink_error.png")
        print("📸 Screenshot saved to /tmp/callink_error.png")
    
    finally:
        driver.quit()
    
    return events

if __name__ == "__main__":
    test_callink()