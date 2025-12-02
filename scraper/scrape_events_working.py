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
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Category keywords
CATEGORY_KEYWORDS = {
    'work': ['career', 'internship', 'job', 'recruitment', 'hiring', 'interview', 'resume', 
             'networking', 'professional', 'workshop', 'info session', 'infosession', 'tech talk',
             'employer', 'company', 'startup', 'fair'],
    'social': ['social', 'mixer', 'meet and greet', 'happy hour', 'party', 'celebration', 
               'gathering', 'BBQ', 'dinner', 'lunch', 'breakfast', 'food', 'free food',
               'potluck', 'banquet', 'reception'],
    'sports': ['sport', 'game', 'tournament', 'fitness', 'yoga', 'run', 'marathon', 
               'basketball', 'soccer', 'volleyball', 'tennis', 'recreation', 'athletic',
               'intramural', 'competition', 'cal bears'],
    'arts': ['art', 'music', 'concert', 'performance', 'theater', 'theatre', 'dance', 
             'exhibition', 'gallery', 'film', 'movie', 'poetry', 'cultural', 'show',
             'screening', 'anime', 'cosplay', 'bampfa'],
    'leisure': ['club meeting', 'general meeting', 'study', 'discussion', 'seminar', 
                'lecture', 'talk', 'presentation', 'fundraiser', 'volunteer', 'community',
                'activism', 'awareness', 'scavenger hunt']
}

def categorize_event(title, description):
    """Categorize event based on keywords"""
    text = f"{title} {description}".lower()
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return 'leisure'

def setup_driver():
    """Set up Chrome driver with Selenium"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_callink():
    """Scrape CalLink events page"""
    print("🔍 Scraping CalLink (https://callink.berkeley.edu/events)...")
    events = []
    driver = None
    
    try:
        driver = setup_driver()
        driver.get("https://callink.berkeley.edu/events")
        
        # Wait for page to load
        print("   ⏳ Waiting for events to load (15 seconds)...")
        time.sleep(15)  # Give lots of time for JavaScript
        
        # Save screenshot for debugging
        driver.save_screenshot("/tmp/callink_debug.png")
        print("   📸 Screenshot saved to /tmp/callink_debug.png")
        
        # Try to find events with multiple strategies
        print("   🔎 Looking for event elements...")
        
        # Strategy 1: Look for any clickable event elements
        event_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/event/']")
        print(f"   Found {len(event_links)} event links")
        
        for link in event_links[:50]:  # Limit to 50
            try:
                title = link.text.strip()
                url = link.get_attribute('href')
                
                if not title or len(title) < 3:
                    continue
                
                events.append({
                    'title': title[:200],
                    'description': None,
                    'category': categorize_event(title, ""),
                    'location': "Berkeley, CA",
                    'source_url': url,
                    'scraped_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                continue
        
        # Strategy 2: Get all text and parse it
        if len(events) == 0:
            print("   Trying alternative scraping method...")
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"   Page text length: {len(page_text)} characters")
            
            # Look for event-like patterns in text
            lines = page_text.split('\n')
            for line in lines:
                if len(line) > 10 and len(line) < 200:
                    # This might be an event title
                    events.append({
                        'title': line[:200],
                        'description': None,
                        'category': 'leisure',
                        'location': "Berkeley, CA",
                        'source_url': "https://callink.berkeley.edu/events",
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"   ✅ Found {len(events)} events from CalLink")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return events

def scrape_berkeley_events():
    """Scrape Berkeley Events page"""
    print("🔍 Scraping Berkeley Events (https://events.berkeley.edu/)...")
    events = []
    driver = None
    
    try:
        driver = setup_driver()
        driver.get("https://events.berkeley.edu/")
        
        print("   ⏳ Waiting for events to load (15 seconds)...")
        time.sleep(15)
        
        driver.save_screenshot("/tmp/berkeley_events_debug.png")
        print("   📸 Screenshot saved to /tmp/berkeley_events_debug.png")
        
        print("   🔎 Looking for event elements...")
        
        # Look for event links
        event_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/event/']")
        print(f"   Found {len(event_links)} event links")
        
        for link in event_links[:50]:
            try:
                title = link.text.strip()
                url = link.get_attribute('href')
                
                if not title or len(title) < 3:
                    continue
                
                events.append({
                    'title': title[:200],
                    'description': None,
                    'category': categorize_event(title, ""),
                    'location': "Berkeley, CA",
                    'source_url': url,
                    'scraped_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                continue
        
        print(f"   ✅ Found {len(events)} events from Berkeley Events")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return events

def upload_to_supabase(events):
    """Upload events to Supabase"""
    if not events:
        print("\n⚠️  No events to upload")
        return
    
    try:
        response = supabase.table('events').insert(events).execute()
        print(f"\n✅ Successfully uploaded {len(events)} events to Supabase!")
    except Exception as e:
        print(f"\n❌ Error uploading: {e}")

def main():
    print("\n" + "="*60)
    print("🎓 Berkeley Events Scraper")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    callink_events = scrape_callink()
    berkeley_events = scrape_berkeley_events()
    
    all_events = callink_events + berkeley_events
    
    print(f"\n📊 Total events scraped: {len(all_events)}")
    print(f"   - CalLink: {len(callink_events)}")
    print(f"   - Berkeley Events: {len(berkeley_events)}")
    
    if all_events:
        categories = {}
        for event in all_events:
            cat = event.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📂 Category breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"   - {cat}: {count}")
        
        upload_to_supabase(all_events)
        print("\n✅ Done! Check screenshots in /tmp/ if needed.\n")
    else:
        print("\n⚠️  No events found. Check /tmp/ screenshots for debugging.\n")

if __name__ == "__main__":
    main()