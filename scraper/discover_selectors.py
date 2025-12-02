"""
Selector Discovery Tool
Run this locally to figure out the exact selectors for CalLink and Berkeley Events
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def discover_selectors(url, site_name):
    """
    Opens a site and tries many different selectors to find events
    """
    print(f"\n{'='*70}")
    print(f"🔍 DISCOVERING SELECTORS FOR: {site_name}")
    print(f"{'='*70}\n")
    
    driver = setup_driver(headless=False)  # Non-headless so you can see it
    driver.get(url)
    
    print(f"📍 URL: {url}")
    print("⏳ Waiting 15 seconds for page to load...\n")
    time.sleep(15)
    
    # Save HTML for inspection
    html_file = f"/tmp/{site_name.replace(' ', '_').lower()}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"💾 Saved HTML to: {html_file}\n")
    
    # Try many different selectors
    selectors = [
        # Common event selectors
        "article",
        "article.event",
        "div.event",
        "div[class*='event']",
        "div[class*='Event']",
        "[class*='event-card']",
        "[class*='EventCard']",
        "[class*='event-item']",
        "[class*='EventItem']",
        
        # Link-based
        "a[href*='/event/']",
        "a[href*='/events/']",
        
        # Card/container patterns
        "div[class*='card']",
        "div[class*='Card']",
        "[role='article']",
        
        # List patterns
        "li[class*='event']",
        "ul > li",
        
        # Grid patterns
        "div[class*='grid'] > div",
        
        # Data attributes
        "[data-testid*='event']",
        "[data-type='event']",
    ]
    
    print("🎯 TESTING SELECTORS:")
    print("-" * 70)
    
    results = []
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            count = len(elements)
            
            if count > 0:
                status = "✅"
                # Get sample text from first element
                sample = elements[0].text.strip()[:80] if elements[0].text else "(no text)"
                results.append((selector, count, sample))
                print(f"{status} {selector:40} → {count:3} elements")
                print(f"   Sample: {sample}")
            else:
                print(f"❌ {selector:40} → 0 elements")
                
        except Exception as e:
            print(f"⚠️  {selector:40} → ERROR: {e}")
    
    print("\n" + "="*70)
    print("📊 SUMMARY - WORKING SELECTORS:")
    print("="*70)
    
    if results:
        for selector, count, sample in results:
            print(f"\nSelector: {selector}")
            print(f"  Count: {count}")
            print(f"  Sample: {sample}")
    else:
        print("❌ No working selectors found!")
        print("\n💡 TIP: Open the HTML file and search for event-related elements:")
        print(f"   {html_file}")
    
    print("\n" + "="*70)
    print("🔍 INSPECTING PAGE STRUCTURE:")
    print("="*70)
    
    # Get all class names that might be relevant
    try:
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        class_names = set()
        for elem in all_elements[:1000]:  # Limit to first 1000
            classes = elem.get_attribute('class')
            if classes:
                class_names.update(classes.split())
        
        event_related = [c for c in class_names if 'event' in c.lower()]
        if event_related:
            print(f"\n📝 Event-related class names found:")
            for cls in sorted(event_related)[:20]:
                print(f"   • {cls}")
        else:
            print("\n⚠️  No 'event' in class names. Showing all classes:")
            for cls in sorted(list(class_names)[:30]):
                print(f"   • {cls}")
                
    except Exception as e:
        print(f"⚠️  Could not analyze classes: {e}")
    
    print(f"\n✅ Browser window is open - inspect the page manually!")
    print("   Press Enter when done to close...")
    input()
    
    driver.quit()
    print("\n✅ Done!\n")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    SELECTOR DISCOVERY TOOL                            ║
║                                                                       ║
║  This script will help you find the right CSS selectors for          ║
║  scraping CalLink and Berkeley Events.                               ║
║                                                                       ║
║  It will:                                                            ║
║    1. Open each site in a visible browser                           ║
║    2. Test many common selectors                                    ║
║    3. Show you which ones work                                      ║
║    4. Save HTML for manual inspection                               ║
║    5. Keep browser open so you can inspect elements                 ║
║                                                                       ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n🎯 Which site do you want to test?")
    print("   1. CalLink (callink.berkeley.edu/events)")
    print("   2. Berkeley Events (events.berkeley.edu)")
    print("   3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        discover_selectors("https://callink.berkeley.edu/events", "CalLink")
    
    if choice in ['2', '3']:
        discover_selectors("https://events.berkeley.edu/", "Berkeley Events")
    
    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Look at the working selectors above")
    print("  2. Update your scraper with the correct selectors")
    print("  3. Check the saved HTML files in /tmp/ if needed")
    print()