"""
Quick Test Script - Run this to verify your setup before scraping
"""

import sys

print("🧪 Testing Berkeley Events Scraper Setup...\n")

# Test 1: Python version
print("1️⃣ Checking Python version...")
if sys.version_info >= (3, 7):
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"   ❌ Python version too old. Need 3.7+, have {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Test 2: Required packages
print("\n2️⃣ Checking required packages...")
packages = {
    'selenium': 'selenium',
    'webdriver_manager': 'webdriver-manager',
    'supabase': 'supabase',
    'dotenv': 'python-dotenv'
}

missing = []
for module_name, package_name in packages.items():
    try:
        __import__(module_name)
        print(f"   ✅ {package_name}")
    except ImportError:
        print(f"   ❌ {package_name} - run: pip install {package_name}")
        missing.append(package_name)

if missing:
    print(f"\n⚠️  Install missing packages:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)

# Test 3: Environment variables
print("\n3️⃣ Checking environment variables...")
try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        print("   ✅ SUPABASE_URL found")
        print("   ✅ SUPABASE_KEY found")
    else:
        print("   ❌ Missing environment variables in .env file")
        print("   Create a .env file with:")
        print("   SUPABASE_URL=your_url_here")
        print("   SUPABASE_KEY=your_key_here")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")
    sys.exit(1)

# Test 4: Supabase connection
print("\n4️⃣ Testing Supabase connection...")
try:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
    
    # Try to query the events table
    result = supabase.table('events').select("count", count="exact").execute()
    print(f"   ✅ Connected! Your events table has {result.count} rows")
except Exception as e:
    print(f"   ❌ Supabase connection failed: {e}")
    print("   Make sure:")
    print("   - Your Supabase URL and key are correct")
    print("   - Your 'events' table exists")
    print("   - Your API key has access to the table")
    sys.exit(1)

# Test 5: Chrome/Chromium
print("\n5️⃣ Checking Chrome/Chromium...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.quit()
    
    print("   ✅ Chrome and ChromeDriver working")
except Exception as e:
    print(f"   ❌ Chrome/ChromeDriver issue: {e}")
    print("   Install Chrome or Chromium:")
    print("   - Mac: brew install --cask google-chrome")
    print("   - Linux: sudo apt-get install chromium-browser")
    sys.exit(1)

# All tests passed!
print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nNext steps:")
print("1. Run: python discover_selectors.py")
print("   This will help you find the correct CSS selectors")
print()
print("2. Update scraper_improved.py with the correct selectors")
print()
print("3. Run: python scraper_improved.py")
print("   This will start scraping events")
print()
print("📖 Check SETUP_GUIDE.md for detailed instructions")
print()