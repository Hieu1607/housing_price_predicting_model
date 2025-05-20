import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import csv
import os
from urllib.parse import urljoin
import traceback

# Base URL for pagination
BASE_URL = "https://batdongsan.com.vn/nha-dat-ban/p{}"

# File to save results
OUTPUT_FILE = "real_estate_links.csv"

def extract_property_links(driver, page_url, retry_count=0, max_retries=2):
    """Extract all property links from a given page URL using Selenium"""
    try:
        print(f"Navigating to {page_url}...")
        driver.get(page_url)
        
        # Wait for page to load (adjust selector based on the actual website)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-item, a.js__product-link-for-product-id, a[href*='/ban-']"))
            )
        except TimeoutException:
            print("Page load timeout - proceeding anyway...")
        
        # Add a randomized wait to simulate human browsing
        time.sleep(random.uniform(3, 6))
        
        # Extract links
        links = []
        
        # Try different selectors
        selectors = [
            "div.product-item a.product-title",
            "a.js__product-link-for-product-id",
            "a[href*='/ban-']",
            "div.product-item a"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and "/ban-" in href and href not in links:
                            links.append(href)
                    break  # If we found elements with this selector, no need to try others
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        print(f"Found {len(links)} links on the page")
        return links
        
    except Exception as e:
        print(f"Error processing {page_url}: {e}")
        traceback.print_exc()
        if retry_count < max_retries:
            print(f"Retrying ({retry_count + 1}/{max_retries})...")
            time.sleep(random.uniform(5, 10))
            return extract_property_links(driver, page_url, retry_count + 1, max_retries)
        return []

def setup_driver():
    """Set up an undetected Chrome driver"""
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    
    # Use a common screen resolution
    options.add_argument("--window-size=1920,1080")
    
    # Add language settings
    options.add_argument("--lang=vi-VN,vi")
    
    # Use incognito mode
    options.add_argument("--incognito")
    
    print("Starting Chrome browser...")
    driver = uc.Chrome(options=options)
    
    return driver

def main():
    # Check if required packages are installed
    try:
        import undetected_chromedriver
        from selenium.webdriver.common.by import By
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "undetected-chromedriver", "selenium"])
        print("Packages installed successfully.")
    
    # Create/open the output file
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    # Set up the driver
    driver = setup_driver()
    
    try:
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow(["URL"])
                
            # Number of pages to scrape
            start_page = 1621
            end_page = 9000
            
            # Track progress
            total_links = 0
            empty_page_count = 0
            
            for page_num in range(start_page, end_page + 1):
                # Form the pagination URL
                page_url = BASE_URL.format(page_num)
                print(f"\nProcessing page {page_num}/{end_page}...")
                
                # Extract links from this page
                links = extract_property_links(driver, page_url)
                
                # Check if we need to stop due to empty pages
                if not links:
                    empty_page_count += 1
                    print(f"Empty page detected ({empty_page_count}/3)")
                    if empty_page_count >= 3:
                        print("Three consecutive empty pages found. Assuming we've reached the end.")
                        break
                else:
                    empty_page_count = 0  # Reset counter if we found links
                
                # Update the total count
                total_links += len(links)
                
                # Write links to CSV
                for link in links:
                    writer.writerow([link])
                
                # Provide progress update
                print(f"Total links so far: {total_links}")
                
                # Flush the file to save progress regularly
                f.flush()
                
                # Add a random longer delay between pages to simulate human behavior
                sleep_time = random.uniform(5, 12)
                print(f"Waiting {sleep_time:.2f} seconds before next page...")
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Saving progress...")
    except Exception as e:
        print(f"\nError encountered: {e}")
        traceback.print_exc()
    finally:
        # Always close the driver
        print("Closing browser...")
        driver.quit()
        
        print(f"Scraping completed or stopped. Total links found: {total_links}")
        print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

    # from 1621 to 9000