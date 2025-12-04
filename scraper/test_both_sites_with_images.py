"""
Complete Test - Tests both CalLink and Berkeley Events scraping
Now includes image URL extraction!
"""

import os
import re
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

CATEGORY_KEYWORDS = {
    'work': ['career', 'internship', 'job', 'recruitment', 'hiring', 'interview', 'resume', 
             'networking', 'professional', 'workshop', 'info session', 'infosession', 'tech talk'],
    'social': ['social', 'mixer', 'meet and greet', 'happy hour', 'party', 'celebration', 
               'gathering', 'BBQ', 'dinner', 'lunch', 'food', 'free food'],
    'sports': ['sport', 'game', 'tournament', 'fitness', 'yoga', 'run', 'basketball', 
               'soccer', 'volleyball', 'tennis', 'cal bears'],
    'arts': ['art', 'music', 'concert', 'performance', 'theater', 'dance', 
             'film', 'movie', 'screening'],
    'leisure': ['club meeting', 'general meeting', 'study', 'discussion', 'seminar', 
                'lecture', 'talk', 'presentation']
}

def categorize_event(title, description):
    text = f"{title} {description}".lower()
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    return max(category_scores, key=category_scores.get) if category_scores else 'leisure'

def extract_image_url(element):
    """Extract image URL from background-image style or img src"""
    try:
        # Method 1: Check for div with role="img" and background-image
        img_divs = element.find_elements(By.CSS_SELECTOR, 'div[role="img"]')
        for img_div in img_divs:
            style = img_div.get_attribute('style')
            if style:
                # Extract URL from background-image: url('...')
                url_match = re.search(r'url\(["\']?(https?://[^"\')]+)["\']?\)', style)
                if url_match:
                    return url_match.group(1)
        
        # Method 2: Check for regular img tags
        img_tags = element.find_elements(By.TAG_NAME, 'img')
        for img in img_tags:
            src = img.get_attribute('src')
            if src and src.startswith('http'):
                return src
        
        return None
    except Exception as e:
        return None

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
    print("\n" + "="*70)
    print("🔍 TESTING CALLINK (with images)")
    print("="*70 + "\n")
    
    driver = setup_driver()
    events = []
    
    try:
        driver.get("https://callink.berkeley.edu/events")
        print("⏳ Waiting for CalLink to load...")
        
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='Card']")))
        
        event_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='Card']")
        print(f"✅ Found {len(event_elements)} event cards\n")
        
        for i, element in enumerate(event_elements[:10], 1):
            try:
                # Get title
                title = None
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, "h2, h3, h4")
                    title = title_element.text.strip()
                except:
                    text_lines = element.text.strip().split('\n')
                    title = text_lines[0] if text_lines else ""
                
                # Get URL
                url = "https://callink.berkeley.edu/events"
                try:
                    link = element.find_element(By.TAG_NAME, 'a')
                    url = link.get_attribute('href')
                except:
                    pass
                
                # Get image URL
                image_url = extract_image_url(element)
                
                # Get description
                description = element.text.strip()
                
                if title and len(title) > 3:
                    category = categorize_event(title, description)
                    
                    print(f"{i}. [{category.upper()}] {title[:60]}")
                    print(f"   URL: {url}")
                    if image_url:
                        print(f"   🖼️  Image: {image_url[:80]}...")
                    else:
                        print(f"   🖼️  Image: None")
                    
                    events.append({
                        'title': title[:200],
                        'description': description[:500] if description else None,
                        'category': category,
                        'location': "Berkeley, CA",
                        'source_url': url,
                        'image_url': image_url,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"⚠️  Error on event {i}: {e}")
        
        print(f"\n✅ CalLink: {len(events)} events extracted")
        images_found = sum(1 for e in events if e.get('image_url'))
        print(f"   🖼️  Images found: {images_found}/{len(events)}")
        
    except Exception as e:
        print(f"❌ CalLink Error: {e}")
        driver.save_screenshot("/tmp/callink_test_error.png")
    
    finally:
        driver.quit()
    
    return events

def test_berkeley_events():
    print("\n" + "="*70)
    print("🔍 TESTING BERKELEY EVENTS (with images)")
    print("="*70 + "\n")
    
    driver = setup_driver()
    events = []
    
    try:
        driver.get("https://events.berkeley.edu/")
        print("⏳ Waiting for Berkeley Events to load...")
        
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='event']")))
        
        event_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='event']")
        print(f"✅ Found {len(event_elements)} event divs\n")
        
        for i, element in enumerate(event_elements[:15], 1):
            try:
                # Get title
                title = None
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, "h2, h3, h4, a")
                    title = title_element.text.strip()
                except:
                    text_lines = element.text.strip().split('\n')
                    # Find the longest line that's not a date
                    for line in text_lines:
                        if len(line) > 10 and not line.startswith('DEC') and not line.startswith('Time:'):
                            title = line
                            break
                
                # Get URL
                url = "https://events.berkeley.edu/"
                try:
                    link = element.find_element(By.TAG_NAME, 'a')
                    url = link.get_attribute('href')
                    if url and not url.startswith('http'):
                        url = f"https://events.berkeley.edu{url}"
                except:
                    pass
                
                # Get image URL
                image_url = extract_image_url(element)
                
                # Get description
                description = element.text.strip()
                
                if title and len(title) > 3:
                    category = categorize_event(title, description)
                    
                    print(f"{i}. [{category.upper()}] {title[:60]}")
                    print(f"   URL: {url}")
                    if image_url:
                        print(f"   🖼️  Image: {image_url[:80]}...")
                    else:
                        print(f"   🖼️  Image: None")
                    
                    events.append({
                        'title': title[:200],
                        'description': description[:500] if description else None,
                        'category': category,
                        'location': "Berkeley, CA",
                        'source_url': url,
                        'image_url': image_url,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"⚠️  Error on event {i}: {e}")
        
        print(f"\n✅ Berkeley Events: {len(events)} events extracted")
        images_found = sum(1 for e in events if e.get('image_url'))
        print(f"   🖼️  Images found: {images_found}/{len(events)}")
        
    except Exception as e:
        print(f"❌ Berkeley Events Error: {e}")
        driver.save_screenshot("/tmp/berkeley_test_error.png")
    
    finally:
        driver.quit()
    
    return events

def main():
    print("\n" + "="*70)
    print("🎓 Berkeley Events Scraper - Complete Test (with Images!)")
    print("="*70)
    
    callink_events = test_callink()
    berkeley_events = test_berkeley_events()
    
    all_events = callink_events + berkeley_events
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total events: {len(all_events)}")
    print(f"  - CalLink: {len(callink_events)}")
    print(f"  - Berkeley Events: {len(berkeley_events)}")
    
    # Image stats
    total_images = sum(1 for e in all_events if e.get('image_url'))
    print(f"\n🖼️  Total images: {total_images}/{len(all_events)}")
    
    # Category breakdown
    categories = {}
    for event in all_events:
        cat = event.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📂 Categories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Upload prompt
    if all_events:
        print("\n" + "="*70)
        upload = input("Upload to Supabase? (y/n): ").strip().lower()
        
        if upload == 'y':
            try:
                from supabase import create_client
                
                SUPABASE_URL = os.getenv("SUPABASE_URL")
                SUPABASE_KEY = os.getenv("SUPABASE_KEY")
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                
                response = supabase.table('events').insert(all_events).execute()
                print(f"\n✅ Successfully uploaded {len(all_events)} events to Supabase!")
            except Exception as e:
                print(f"\n❌ Upload failed: {e}")
        else:
            print("\n✅ Test complete. Skipped upload.")
    
    print()

if __name__ == "__main__":
    main()