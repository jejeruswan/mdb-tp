# The Greek Theatre Berkeley Event Scraper

A Python web scraper that extracts concert and show information from The Greek Theatre Berkeley website and stores it in Supabase.

## Features

- Scrapes event listings from https://thegreekberkeley.com/event-listing/
- Extracts event details (title, description, date/time, images, URLs)
- Stores data in Supabase with proper formatting
- Checks for duplicate events before inserting
- Handles errors gracefully
- Supports both static HTML (BeautifulSoup) and JavaScript-rendered content (Playwright)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. If using the Playwright version, install browser drivers:
```bash
playwright install chromium
```

## Usage

### Option 1: BeautifulSoup (Recommended - Faster, simpler)

For websites with static HTML content:
```bash
python scraper.py
```

### Option 2: Playwright (For JavaScript-rendered content)

If the website requires JavaScript to load content:
```bash
python scraper_playwright.py
```

## Output

The scraper will:
- Print progress as it scrapes events
- Show which events were added, skipped (duplicates), or had errors
- Display a summary at the end

Example output:
```
✅ ADDED: Artist Name - 2024-01-15 19:00:00
⏭️  SKIPPED (duplicate): Another Artist - 2024-01-20 20:00:00

Summary:
  ✅ Added: 5
  ⏭️  Skipped (duplicates): 2
  ❌ Errors: 0
  📊 Total processed: 7
```

## Data Structure

Events are inserted into the `events` table with the following fields:
- `title`: Artist/show name
- `description`: Event details
- `category`: Always "arts"
- `location`: "The Greek Theatre, Berkeley"
- `latitude`: 37.8733
- `longitude`: -122.2545
- `start_time`: TIMESTAMP format (YYYY-MM-DD HH:MM:SS)
- `end_time`: NULL
- `source_url`: Link to the event page
- `image_url`: Event poster URL (if available)
- `club_name`: NULL

## Notes

- The scraper automatically parses various date/time formats
- Duplicate checking is based on `title` + `start_time` combination
- If no time is found, events default to 7:00 PM
- The scraper handles missing fields gracefully

