import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    print("🔍 Scraping CalLink (https://callink.berkeley.edu/events)...")
    events = []
    driver = None
    
    try:
        driver = setup_driver()
        driver.get("https://callink.berkeley.edu/events")
        
        # Wait for React app to load - look for specific elements
        print("   ⏳ Waiting for CalLink to load...")
        wait = WebDriverWait(driver, 20)
        
        # Try multiple selectors for CalLink
        # a[href*='/event/'] and div[class*='Card']
        selectors_to_try = [
            (By.CSS_SELECTOR, "div[class*='Card']"),  # MuiCard-root - 9 events
            (By.CSS_SELECTOR, "a[href*='/event/']"),   # Direct links - 9 events
        ]
        
        event_elements = []
        for by_method, selector in selectors_to_try:
            try:
                wait.until(EC.presence_of_element_located((by_method, selector)))
                event_elements = driver.find_elements(by_method, selector)
                if event_elements:
                    print(f"   ✅ Found {len(event_elements)} events using selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        # no events debugging
        if not event_elements:
            print("   ⚠️  No events found with known selectors. Saving debug info...")
            driver.save_screenshot("/tmp/callink_debug.png")
            with open('/tmp/callink_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   📸 Screenshot: /tmp/callink_debug.png")
            print("   📄 HTML: /tmp/callink_debug.html")
            return events
        
        # Extract event data
        for element in event_elements[:50]:  # Limit to 50
            try:
                # Try to get title from various places
                title = None
                try:
                    title = element.find_element(By.CSS_SELECTOR, "h2, h3, h4, .title, [class*='title']").text.strip()
                except:
                    title = element.text.strip()
                
                # Get URL
                url = None
                try:
                    if element.tag_name == 'a':
                        url = element.get_attribute('href')
                    else:
                        link = element.find_element(By.TAG_NAME, 'a')
                        url = link.get_attribute('href')
                except:
                    url = "https://callink.berkeley.edu/events"
                
                # Get description if available
                description = ""
                try:
                    description = element.find_element(By.CSS_SELECTOR, ".description, [class*='description'], p").text.strip()
                except:
                    pass
                
                if title and len(title) > 3:
                    events.append({
                        'title': title[:200],
                        'description': description[:500] if description else None,
                        'category': categorize_event(title, description),
                        'location': "Berkeley, CA",
                        'source_url': url,
                        'scraped_at': datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"   ⚠️  Error parsing event: {e}")
                continue
        
        print(f"   ✅ Successfully scraped {len(events)} events from CalLink")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if driver:
            driver.save_screenshot("/tmp/callink_error.png")
            print("   📸 Error screenshot: /tmp/callink_error.png")
    
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
        
        print("   ⏳ Waiting for Berkeley Events to load...")
        wait = WebDriverWait(driver, 20)
        
        # Try multiple selectors
        # Based on discovery: div[class*='event'] works best with 31 events
        selectors_to_try = [
            (By.CSS_SELECTOR, "div[class*='event']"),      # 31 events - includes featured-event
            (By.CSS_SELECTOR, "div[class*='card']"),       # 60 events - might include non-events
            (By.CSS_SELECTOR, "a[href*='/events/']"),      # 37 event links
        ]
        
        event_elements = []
        for by_method, selector in selectors_to_try:
            try:
                wait.until(EC.presence_of_element_located((by_method, selector)))
                event_elements = driver.find_elements(by_method, selector)
                if event_elements:
                    print(f"   ✅ Found {len(event_elements)} events using selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        if not event_elements:
            print("   ⚠️  No events found. Saving debug info...")
            driver.save_screenshot("/tmp/berkeley_events_debug.png")
            with open('/tmp/berkeley_events_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   📸 Screenshot: /tmp/berkeley_events_debug.png")
            print("   📄 HTML: /tmp/berkeley_events_debug.html")
            return events
        
        # Extract event data
        for element in event_elements[:50]:
            try:
                title = None
                try:
                    title = element.find_element(By.CSS_SELECTOR, "h2, h3, h4, .title, [class*='title']").text.strip()
                except:
                    title = element.text.strip()
                
                url = None
                try:
                    if element.tag_name == 'a':
                        url = element.get_attribute('href')
                    else:
                        link = element.find_element(By.TAG_NAME, 'a')
                        url = link.get_attribute('href')
                except:
                    url = "https://events.berkeley.edu/"
                
                description = ""
                try:
                    description = element.find_element(By.CSS_SELECTOR, ".description, [class*='description'], p").text.strip()
                except:
                    pass
                
                if title and len(title) > 3:
                    events.append({
                        'title': title[:200],
                        'description': description[:500] if description else None,
                        'category': categorize_event(title, description),
                        'location': "Berkeley, CA",
                        'source_url': url,
                        'scraped_at': datetime.now().isoformat()
                    })
                
            except Exception as e:
                continue
        
        print(f"   ✅ Successfully scraped {len(events)} events from Berkeley Events")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if driver:
            driver.save_screenshot("/tmp/berkeley_events_error.png")
    
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
        print(f"\n❌ Error uploading to Supabase: {e}")

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
        
        # Show sample events
        print("\n📋 Sample events:")
        for event in all_events[:3]:
            print(f"   • {event['title'][:60]}... [{event['category']}]")
        
        upload_to_supabase(all_events)
        print("\n✅ Done! Check /tmp/ for debug files if needed.\n")
    else:
        print("\n⚠️  No events found. Check /tmp/ screenshots and HTML files for debugging.\n")

if __name__ == "__main__":
    main()