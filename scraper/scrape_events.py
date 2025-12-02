import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Category keywords for auto-categorization
CATEGORY_KEYWORDS = {
    'work': ['career', 'internship', 'job', 'recruitment', 'hiring', 'interview', 'resume', 
             'networking', 'professional', 'workshop', 'info session', 'infosession', 'tech talk',
             'employer', 'company', 'startup'],
    'social': ['social', 'mixer', 'meet and greet', 'happy hour', 'party', 'celebration', 
               'gathering', 'BBQ', 'dinner', 'lunch', 'breakfast', 'food', 'free food',
               'potluck', 'banquet', 'reception'],
    'sports': ['sport', 'game', 'tournament', 'fitness', 'yoga', 'run', 'marathon', 
               'basketball', 'soccer', 'volleyball', 'tennis', 'recreation', 'athletic',
               'intramural', 'competition'],
    'arts': ['art', 'music', 'concert', 'performance', 'theater', 'theatre', 'dance', 
             'exhibition', 'gallery', 'film', 'movie', 'poetry', 'cultural', 'show',
             'screening', 'anime', 'cosplay'],
    'leisure': ['club meeting', 'general meeting', 'study', 'discussion', 'seminar', 
                'lecture', 'talk', 'presentation', 'fundraiser', 'volunteer', 'community',
                'activism', 'awareness']
}

def categorize_event(title, description):
    """Categorize event based on keywords in title and description"""
    text = f"{title} {description}".lower()
    
    # Count matches for each category
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score, default to 'leisure'
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return 'leisure'

def scrape_callink():
    """Scrape events from CalLink Berkeley"""
    print("🔍 Scraping CalLink...")
    events = []
    
    try:
        url = "https://callink.berkeley.edu/events"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # CalLink specific selectors (may need adjustment based on actual HTML)
        event_cards = soup.find_all('div', class_=re.compile(r'event', re.I))[:50]
        
        if not event_cards:
            # Try alternative selectors
            event_cards = soup.find_all(['article', 'div'], attrs={'data-event': True})[:50]
        
        for card in event_cards:
            try:
                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|heading', re.I))
                if not title_elem:
                    title_elem = card.find('a', href=re.compile(r'/event/', re.I))
                title = title_elem.get_text(strip=True) if title_elem else "Untitled Event"
                
                if title == "Untitled Event":
                    continue
                
                # Extract description
                desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|summary|content', re.I))
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract location
                location_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'location|venue|place', re.I))
                location = location_elem.get_text(strip=True) if location_elem else "TBA"
                
                # Extract event link
                link_elem = card.find('a', href=True)
                source_url = link_elem['href'] if link_elem else url
                if not source_url.startswith('http'):
                    source_url = f"https://callink.berkeley.edu{source_url}"
                
                # Extract club/organization name
                club_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'club|organization|group', re.I))
                club_name = club_elem.get_text(strip=True) if club_elem else None
                
                # Categorize event
                category = categorize_event(title, description)
                
                event = {
                    'title': title,
                    'description': description[:500] if description else None,
                    'category': category,
                    'location': location,
                    'source_url': source_url,
                    'club_name': club_name,
                    'scraped_at': datetime.now().isoformat()
                }
                
                events.append(event)
                
            except Exception as e:
                print(f"  ⚠️  Error parsing CalLink event: {e}")
                continue
        
        print(f"  ✅ Found {len(events)} events from CalLink")
        
    except Exception as e:
        print(f"  ❌ Error scraping CalLink: {e}")
    
    return events

def scrape_berkeley_events():
    """Scrape events from Berkeley Events website"""
    print("🔍 Scraping Berkeley Events...")
    events = []
    
    try:
        url = "https://events.berkeley.edu/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Berkeley Events specific selectors
        event_cards = soup.find_all(['div', 'article'], class_=re.compile(r'event', re.I))[:50]
        
        if not event_cards:
            # Try alternative selectors
            event_cards = soup.find_all('div', attrs={'data-event-id': True})[:50]
        
        for card in event_cards:
            try:
                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|heading', re.I))
                if not title_elem:
                    title_elem = card.find('a', href=re.compile(r'/event/', re.I))
                title = title_elem.get_text(strip=True) if title_elem else "Untitled Event"
                
                if title == "Untitled Event":
                    continue
                
                # Extract description
                desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|summary|content', re.I))
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract location
                location_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'location|venue|place', re.I))
                location = location_elem.get_text(strip=True) if location_elem else "TBA"
                
                # Extract event link
                link_elem = card.find('a', href=True)
                source_url = link_elem['href'] if link_elem else url
                if not source_url.startswith('http'):
                    source_url = f"https://events.berkeley.edu{source_url}"
                
                # Categorize event
                category = categorize_event(title, description)
                
                event = {
                    'title': title,
                    'description': description[:500] if description else None,
                    'category': category,
                    'location': location,
                    'source_url': source_url,
                    'scraped_at': datetime.now().isoformat()
                }
                
                events.append(event)
                
            except Exception as e:
                print(f"  ⚠️  Error parsing Berkeley event: {e}")
                continue
        
        print(f"  ✅ Found {len(events)} events from Berkeley Events")
        
    except Exception as e:
        print(f"  ❌ Error scraping Berkeley Events: {e}")
    
    return events

def upload_to_supabase(events):
    """Upload events to Supabase database"""
    if not events:
        print("⚠️  No events to upload")
        return
    
    try:
        # Insert new events
        response = supabase.table('events').insert(events).execute()
        print(f"✅ Successfully uploaded {len(events)} events to Supabase")
        
    except Exception as e:
        print(f"❌ Error uploading to Supabase: {e}")
        print(f"   Details: {str(e)}")

def main():
    """Main scraper function"""
    print("\n" + "="*50)
    print("🎓 Berkeley Events Scraper")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Scrape from both sources
    callink_events = scrape_callink()
    berkeley_events = scrape_berkeley_events()
    
    # Combine all events
    all_events = callink_events + berkeley_events
    
    print(f"\n📊 Total events scraped: {len(all_events)}")
    print(f"   - CalLink: {len(callink_events)}")
    print(f"   - Berkeley Events: {len(berkeley_events)}")
    
    # Show category breakdown
    if all_events:
        categories = {}
        for event in all_events:
            cat = event.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📂 Category breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"   - {cat}: {count}")
    
    # Upload to Supabase
    if all_events:
        print("\n📤 Uploading to Supabase...")
        upload_to_supabase(all_events)
        print("\n✅ Scraping complete!\n")
    else:
        print("\n⚠️  No events found to upload\n")

if __name__ == "__main__":
    main()