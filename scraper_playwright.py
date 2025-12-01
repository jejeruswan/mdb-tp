#!/usr/bin/env python3
"""
Web scraper for The Greek Theatre Berkeley events using Playwright.
Use this version if the website requires JavaScript rendering.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


# Supabase configuration
SUPABASE_URL = "https://wyjvkvsejfwzhlivwccp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndqdnlrdnNlamZ3d3pobGl3Y2NwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM2NjIwODIsImV4cCI6MjA3OTIzODA4Mn0.tbncOCx4T44v0cn7NG30tYE64s9EyivthRF0_s-FUq0"

# Constants
EVENT_URL = "https://thegreekberkeley.com/event-listing/"
LOCATION = "The Greek Theatre, Berkeley"
LATITUDE = 37.8733
LONGITUDE = -122.2545
CATEGORY = "arts"


def parse_date_time(date_str: str, time_str: Optional[str] = None) -> Optional[str]:
    """
    Parse date and time strings into TIMESTAMP format 'YYYY-MM-DD HH:MM:SS'
    """
    if not date_str:
        return None
    
    date_formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d %Y",
        "%b %d %Y",
    ]
    
    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            break
        except ValueError:
            continue
    
    if not parsed_date:
        return None
    
    hour = 0
    minute = 0
    
    if time_str:
        time_str = time_str.strip().upper()
        if "PM" in time_str or "AM" in time_str:
            time_clean = re.sub(r'[^\d:]', '', time_str)
            if ":" in time_clean:
                hour, minute = map(int, time_clean.split(":"))
            else:
                hour = int(time_clean)
                minute = 0
            
            if "PM" in time_str and hour != 12:
                hour += 12
            elif "AM" in time_str and hour == 12:
                hour = 0
        else:
            if ":" in time_str:
                hour, minute = map(int, time_str.split(":"))
            else:
                hour = int(time_str)
                minute = 0
    
    if not time_str:
        hour = 19
        minute = 0
    
    parsed_date = parsed_date.replace(hour=hour, minute=minute, second=0)
    return parsed_date.strftime("%Y-%m-%d %H:%M:%S")


def extract_event_data(page) -> List[Dict]:
    """Extract event data from the page using Playwright."""
    events = []
    
    # Wait for content to load
    page.wait_for_load_state('networkidle')
    
    # Try multiple selectors
    selectors = [
        'div.mix.detail-information',
        'article.event',
        'div.event',
        '.event-item',
        '.event-card',
        'article',
        'li.event',
        '.listing-item',
    ]
    
    event_elements = None
    for selector in selectors:
        try:
            event_elements = page.query_selector_all(selector)
            if event_elements:
                print(f"Found {len(event_elements)} events using selector: {selector}")
                break
        except:
            continue
    
    if not event_elements:
        # Fallback: look for any article or div elements
        event_elements = page.query_selector_all('article, div[class*="event"], div[class*="listing"]')
        print(f"Found {len(event_elements)} potential event elements (fallback)")

    if event_elements and len(event_elements) > 0:
        print(f"\n=== DEBUG: Showing HTML for all {len(event_elements)} events ===")
        for i, elem in enumerate(event_elements):
            print(f"\n--- Event {i+1} HTML (first 500 chars) ---")
            print(elem.inner_html()[:500])
        print("=== END DEBUG ===\n")
    
    for element in event_elements:
        try:
            # Extract title
            title = None
            try:
                title_elem = element.query_selector('.show-title, h2.show-title')
                if title_elem:
                    title = title_elem.inner_text().strip()
            except:
                pass
            
            if not title:
                print(f"  ⚠️ Skipping event - no title found")  # ADD THIS LINE
                continue
            
            # Extract description
            description = ""
            for sel in ['.description', '.event-description', 'p', '.excerpt']:
                try:
                    desc_elem = element.query_selector(sel)
                    if desc_elem:
                        description = desc_elem.inner_text().strip()
                        if description:
                            break
                except:
                    continue
            
            # Extract date/time
            start_time = None
            try:
                date_elem = element.query_selector('.date-show')
                if date_elem:
                    date_content = date_elem.get_attribute('content')
                    if date_content:
                        # Parse "May 3, 2026 7:00 pm" format
                        try:
                            dt = datetime.strptime(date_content, "%B %d, %Y %I:%M %p")
                            start_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            pass
            except:
                pass
            
            # Extract source URL
            source_url = None
            try:
                link = element.query_selector('a[href]')
                if link:
                    href = link.get_attribute('href')
                    if href:
                        source_url = urljoin(EVENT_URL, href)
            except:
                pass
            
            # Extract image URL
            image_url = None
            try:
                img = element.query_selector('img[src]')
                if img:
                    src = img.get_attribute('src')
                    if src:
                        image_url = urljoin(EVENT_URL, src)
            except:
                pass
            
            if title and start_time:
                event = {
                    'title': title,
                    'description': description or "",
                    'category': CATEGORY,
                    'location': LOCATION,
                    'latitude': LATITUDE,
                    'longitude': LONGITUDE,
                    'start_time': start_time,
                    'end_time': None,
                    'source_url': source_url or "",
                    'image_url': image_url or None,
                    'club_name': None
                }
                events.append(event)
                print(f"  Extracted: {title} - {start_time}")
            elif title:  # ADD THIS
                print(f"  ⚠️ Skipping {title} - no valid date found")  # ADD THIS
            else:  # ADD THIS
                print(f"  ⚠️ Skipping - missing both title and date")  # ADD THIS
        
        except Exception as e:
            print(f"  Error extracting event: {e}")
            continue
    
    return events


def scrape_events() -> List[Dict]:
    """Scrape events using Playwright."""
    print(f"Scraping events from {EVENT_URL} using Playwright...")
    
    events = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(EVENT_URL, wait_until='networkidle', timeout=30000)
            events = extract_event_data(page)
            print(f"Successfully scraped {len(events)} events")
        except Exception as e:
            print(f"Error scraping page: {e}")
        finally:
            browser.close()
    
    return events


def check_duplicate(supabase: Client, title: str, start_time: str) -> bool:
    """Check if an event with the same title and start_time already exists."""
    try:
        result = supabase.table('events').select('id').eq('title', title).eq('start_time', start_time).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False


def insert_events(events: List[Dict]) -> None:
    """Insert events into Supabase, skipping duplicates."""
    if not events:
        print("No events to insert")
        return
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"\nConnecting to Supabase...")
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\nInserting {len(events)} events into Supabase...")
    print("-" * 60)
    
    for event in events:
        try:
            if check_duplicate(supabase, event['title'], event['start_time']):
                print(f"⏭️  SKIPPED (duplicate): {event['title']} - {event['start_time']}")
                skipped_count += 1
                continue
            
            result = supabase.table('events').insert(event).execute()
            
            if result.data:
                print(f"✅ ADDED: {event['title']} - {event['start_time']}")
                inserted_count += 1
            else:
                print(f"❌ ERROR: {event['title']} - No data returned")
                error_count += 1
        
        except Exception as e:
            print(f"❌ ERROR inserting {event['title']}: {e}")
            error_count += 1
    
    print("-" * 60)
    print(f"\nSummary:")
    print(f"  ✅ Added: {inserted_count}")
    print(f"  ⏭️  Skipped (duplicates): {skipped_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📊 Total processed: {len(events)}")


def main():
    """Main function to run the scraper."""
    print("=" * 60)
    print("The Greek Theatre Berkeley Event Scraper (Playwright)")
    print("=" * 60)
    
    events = scrape_events()
    
    if events:
        insert_events(events)
    else:
        print("No events found to insert")


if __name__ == "__main__":
    main()

