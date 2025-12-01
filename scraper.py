#!/usr/bin/env python3
"""
Web scraper for The Greek Theatre Berkeley events.
Scrapes event information and stores it in Supabase.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


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
    
    Args:
        date_str: Date string (e.g., "January 15, 2024", "Jan 15, 2024", "2024-01-15")
        time_str: Optional time string (e.g., "7:00 PM", "19:00")
    
    Returns:
        Formatted timestamp string or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats
    date_formats = [
        "%B %d, %Y",      # January 15, 2024
        "%b %d, %Y",      # Jan 15, 2024
        "%m/%d/%Y",       # 01/15/2024
        "%Y-%m-%d",       # 2024-01-15
        "%d %B %Y",       # 15 January 2024
        "%d %b %Y",       # 15 Jan 2024
        "%B %d %Y",       # January 15 2024
        "%b %d %Y",       # Jan 15 2024
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
    
    # Parse time if provided
    hour = 0
    minute = 0
    
    if time_str:
        time_str = time_str.strip().upper()
        # Handle 12-hour format (e.g., "7:00 PM", "7 PM")
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
            # Handle 24-hour format
            if ":" in time_str:
                hour, minute = map(int, time_str.split(":"))
            else:
                hour = int(time_str)
                minute = 0
    
    # Default to 7:00 PM if no time specified
    if not time_str:
        hour = 19
        minute = 0
    
    parsed_date = parsed_date.replace(hour=hour, minute=minute, second=0)
    return parsed_date.strftime("%Y-%m-%d %H:%M:%S")


def extract_event_data(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """
    Extract event data from the parsed HTML.
    
    Args:
        soup: BeautifulSoup object of the page
        base_url: Base URL for resolving relative links
    
    Returns:
        List of event dictionaries
    """
    events = []
    
    # Try multiple selectors to find event containers
    # Common patterns: article, div with event classes, list items
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
    
    event_elements = []
    for selector in selectors:
        event_elements = soup.select(selector)
        if event_elements:
            break
    
    # If no specific event containers found, try to find all links that might be events
    if not event_elements:
        # Look for common event patterns
        event_elements = soup.find_all(['article', 'div'], class_=re.compile(r'event|listing|card', re.I))
    
    print(f"Found {len(event_elements)} potential event elements")
    
    for element in event_elements:
        try:
            # Extract title
            title = None
            title_elem = element.select_one('.show-title, h2.show-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            if not title:
                continue
            
            # Extract description
            description = ""
            desc_selectors = ['.description', '.event-description', 'p', '.excerpt']
            for sel in desc_selectors:
                desc_elem = element.select_one(sel)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    if description:
                        break
            
            # Extract date/time
            start_time = None
            date_elem = element.select_one('.date-show')
            if date_elem:
                date_content = date_elem.get('content')
                if date_content:
                    # Parse "May 3, 2026 7:00 pm" format
                    try:
                        dt = datetime.strptime(date_content, "%B %d, %Y %I:%M %p")
                        start_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
            
            # Extract source URL
            source_url = None
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem.get('href')
                if href:
                    source_url = urljoin(base_url, href)
            
            # Extract image URL
            image_url = None
            img_elem = element.find('img', src=True)
            if img_elem:
                src = img_elem.get('src')
                if src:
                    image_url = urljoin(base_url, src)
            
            # Only add event if we have at least title and start_time
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
        
        except Exception as e:
            print(f"  Error extracting event: {e}")
            continue
    
    return events


def scrape_events() -> List[Dict]:
    """
    Scrape events from The Greek Theatre Berkeley website.
    
    Returns:
        List of event dictionaries
    """
    print(f"Scraping events from {EVENT_URL}...")
    
    # More complete browser headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    # Use a session to maintain cookies
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # First, try to visit the main page to establish a session
        print("Establishing connection...")
        session.get('https://thegreekberkeley.com/', timeout=30)
        
        # Now request the event listing page
        response = session.get(EVENT_URL, timeout=30)
        response.raise_for_status()
        
        print(f"Page fetched successfully (Status: {response.status_code})")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        events = extract_event_data(soup, EVENT_URL)
        
        print(f"Successfully scraped {len(events)} events")
        return events
    
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        print("\n⚠️  The website may be blocking automated requests.")
        print("💡 Trying Playwright as fallback (handles JavaScript and anti-bot protection better)...")
        
        # Try Playwright as fallback
        try:
            from playwright.sync_api import sync_playwright
            
            events = []
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                try:
                    print("Loading page with Playwright...")
                    page.goto(EVENT_URL, wait_until='networkidle', timeout=30000)
                    
                    # Get page content and parse with BeautifulSoup
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    events = extract_event_data(soup, EVENT_URL)
                    
                    print(f"Successfully scraped {len(events)} events using Playwright")
                except Exception as playwright_error:
                    print(f"Playwright also failed: {playwright_error}")
                finally:
                    browser.close()
            
            return events
            
        except ImportError:
            print("\n❌ Playwright not installed. Install it with:")
            print("   pip install playwright")
            print("   playwright install chromium")
            return []
        except Exception as fallback_error:
            print(f"Fallback to Playwright failed: {fallback_error}")
            return []


def check_duplicate(supabase: Client, title: str, start_time: str) -> bool:
    """
    Check if an event with the same title and start_time already exists.
    
    Args:
        supabase: Supabase client
        title: Event title
        start_time: Event start time in TIMESTAMP format
    
    Returns:
        True if duplicate exists, False otherwise
    """
    try:
        result = supabase.table('events').select('id').eq('title', title).eq('start_time', start_time).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False


def insert_events(events: List[Dict]) -> None:
    """
    Insert events into Supabase, skipping duplicates.
    
    Args:
        events: List of event dictionaries
    """
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
            # Check for duplicate
            if check_duplicate(supabase, event['title'], event['start_time']):
                print(f"⏭️  SKIPPED (duplicate): {event['title']} - {event['start_time']}")
                skipped_count += 1
                continue
            
            # Insert event
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
    print("The Greek Theatre Berkeley Event Scraper")
    print("=" * 60)
    
    # Scrape events
    events = scrape_events()
    
    if events:
        # Insert into Supabase
        insert_events(events)
    else:
        print("No events found to insert")


if __name__ == "__main__":
    main()

