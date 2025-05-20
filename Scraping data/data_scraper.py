import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import csv
import os
import re
import pandas as pd
from urllib.parse import urlparse, parse_qs
import traceback

# File to save results
OUTPUT_FILE = "real_estate_details.csv"

# Define the fields we want to extract based on the form in the screenshot
FIELDS = [
    "title",           # Title of the listing
    "price",           # Price
    "price_per_sqm",   # Price per square meter
    "area",            # Area in square meters
    "bedrooms",        # Number of bedrooms
    "bathrooms",       # Number of bathrooms
    "floors",          # Number of floors
    "house_direction", # House direction
    "balcony_direction", # Balcony direction
    "road_width",      # Road width
    "facade",          # Façade/frontage
    "legal_status",    # Legal status
    "property_type",   # Type of property
    "project",         # Project name if applicable
    "address",         # Address
    "description",     # Description
    "contact_name",    # Contact name
    "contact_phone",   # Contact phone
    "posted_date",     # Date posted
    "url"              # Original URL
]

def setup_driver():
    """Set up an undetected Chrome driver"""
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=vi-VN,vi")
    options.add_argument("--incognito")
    
    print("Starting Chrome browser...")
    driver = uc.Chrome(options=options)
    
    return driver

def extract_property_details(driver, url, retry_count=0, max_retries=2):
    """Extract detailed information about a property"""
    property_data = {field: "" for field in FIELDS}
    property_data["url"] = url
    
    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for the page to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.re__pr-title, h1.re__pr-title"))
            )
        except TimeoutException:
            print("Page load timeout - proceeding anyway...")
        
        # Add a wait to ensure JavaScript has loaded
        time.sleep(random.uniform(3, 5))
        
        # Extract title
        try:
            title_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-title h1, h1.re__pr-title")
            property_data["title"] = title_element.text.strip()
        except NoSuchElementException:
            print("Title not found")
        
        # Extract price
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, "span.re__pr-title-price-value, div.re__pr-title-price-value")
            property_data["price"] = price_element.text.strip()
        except NoSuchElementException:
            print("Price not found")
        
        # Extract price per square meter
        try:
            price_sqm_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-short-info div:contains('Giá/m²')")
            property_data["price_per_sqm"] = price_sqm_element.text.replace("Giá/m²", "").strip()
        except (NoSuchElementException, Exception):
            print("Price per sqm not found")
        
        # Extract area
        try:
            area_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-short-info div:contains('Diện tích')")
            property_data["area"] = area_element.text.replace("Diện tích", "").strip()
        except (NoSuchElementException, Exception):
            try:
                area_element = driver.find_element(By.CSS_SELECTOR, "span.re__pr-title-area-value, div.re__pr-title-area-value")
                property_data["area"] = area_element.text.strip()
            except NoSuchElementException:
                print("Area not found")
        
        # Extract detailed information from the property details section
        try:
            detail_elements = driver.find_elements(By.CSS_SELECTOR, "div.re__pr-specs-content-item")
            for element in detail_elements:
                try:
                    label = element.find_element(By.CSS_SELECTOR, "div.re__pr-specs-content-item-label").text.strip()
                    value = element.find_element(By.CSS_SELECTOR, "div.re__pr-specs-content-item-value").text.strip()
                    
                    if "phòng ngủ" in label.lower():
                        property_data["bedrooms"] = value
                    elif "phòng tắm" in label.lower() or "vệ sinh" in label.lower():
                        property_data["bathrooms"] = value
                    elif "số tầng" in label.lower():
                        property_data["floors"] = value
                    elif "hướng nhà" in label.lower():
                        property_data["house_direction"] = value
                    elif "hướng ban công" in label.lower():
                        property_data["balcony_direction"] = value
                    elif "đường vào" in label.lower() or "đường rộng" in label.lower():
                        property_data["road_width"] = value
                    elif "mặt tiền" in label.lower():
                        property_data["facade"] = value
                    elif "pháp lý" in label.lower():
                        property_data["legal_status"] = value
                    elif "loại tin" in label.lower() or "loại bds" in label.lower():
                        property_data["property_type"] = value
                    elif "dự án" in label.lower():
                        property_data["project"] = value
                except Exception as e:
                    print(f"Error extracting a detail field: {e}")
        except Exception as e:
            print(f"Error extracting property details: {e}")
        
        # Extract address
        try:
            address_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-short-info span.re__pr-short-info-address, span.re__pr-short-info-address")
            property_data["address"] = address_element.text.strip()
        except NoSuchElementException:
            print("Address not found")
        
        # Extract description
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-description, div.re__section-description")
            property_data["description"] = description_element.text.strip()
        except NoSuchElementException:
            print("Description not found")
        
        # Extract contact information
        try:
            contact_name_element = driver.find_element(By.CSS_SELECTOR, "div.re__contact-name, div.re__contact-info-name")
            property_data["contact_name"] = contact_name_element.text.strip()
        except NoSuchElementException:
            print("Contact name not found")
        
        try:
            contact_phone_element = driver.find_element(By.CSS_SELECTOR, "div.re__btn-phone-mobile, div.re__btn-phone")
            property_data["contact_phone"] = contact_phone_element.text.strip()
        except NoSuchElementException:
            print("Contact phone not found")
        
        # Extract posted date
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, "div.re__pr-short-info span:contains('Ngày đăng')")
            property_data["posted_date"] = date_element.text.replace("Ngày đăng:", "").strip()
        except (NoSuchElementException, Exception):
            print("Posted date not found")
        
        # Try alternative selectors for any missing key fields
        if not property_data["bedrooms"]:
            try:
                bedroom_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'phòng ngủ')]")
                for element in bedroom_elements:
                    text = element.text
                    match = re.search(r'(\d+)\s*phòng ngủ', text)
                    if match:
                        property_data["bedrooms"] = match.group(1)
                        break
            except Exception:
                pass
        
        if not property_data["bathrooms"]:
            try:
                bathroom_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'phòng tắm') or contains(text(), 'vệ sinh')]")
                for element in bathroom_elements:
                    text = element.text
                    match = re.search(r'(\d+)\s*(phòng tắm|vệ sinh)', text)
                    if match:
                        property_data["bathrooms"] = match.group(1)
                        break
            except Exception:
                pass
        
        # Extract project name from URL if not found on page
        if not property_data["project"] and "prj-" in url:
            try:
                project_match = re.search(r'prj-([^/]+)', url)
                if project_match:
                    project_name = project_match.group(1).replace('-', ' ').title()
                    property_data["project"] = project_name
            except Exception:
                pass
        
        return property_data
        
    except Exception as e:
        print(f"Error processing {url}: {e}")
        if retry_count < max_retries:
            print(f"Retrying ({retry_count + 1}/{max_retries})...")
            time.sleep(random.uniform(5, 10))
            return extract_property_details(driver, url, retry_count + 1, max_retries)
        return property_data

def main():
    # Check if required packages are installed
    try:
        import undetected_chromedriver
        from selenium.webdriver.common.by import By
        import pandas as pd # Ensure pandas is imported if not already
        import csv # Import csv module
        import os # Import os module
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "undetected-chromedriver", "selenium", "pandas"])
        print("Packages installed successfully.")

    # Set up the driver
    driver = setup_driver()

    # Read URLs from CSV file
    csv_file = "real_estate_links.csv"
    try:
        print(f"Reading URLs from {csv_file}...")
        urls_df = pd.read_csv(csv_file)
        urls = urls_df['URL'].tolist()
        print(f"Found {len(urls)} URLs to process.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        print("Using default URLs as fallback.")
        # Fallback to some example URLs if CSV reading fails
        urls = [
            "https://batdongsan.com.vn/ban-nha-biet-thu-lien-ke-xa-tan-hoi-7-prj-vinhomes-wonder-city/mua-vin-dan-phuong-dip-30-04-khi-1-ngay-bang-20-nam-co-den-mot-lan-gia-tu-18-70-ty-pr42821633",
            "https://batdongsan.com.vn/ban-can-ho-chung-cu-phuong-phuc-dong-prj-sunshine-green-iconic/-dan-ban-ch-1-ngu-4-ty-2-ngu-6-ty-3-ngu-8-ty-duplex-13-ty-pr42262144",
            "https://batdongsan.com.vn/ban-dat-xa-giao-phong/chinh-chu-can-tien-ban-nhanh-2-can-duong-lon-di-thang-ra-bien-quat-lam-gia-re-nhat-pr42839922"
        ]

    processed_count = 0
    file_exists = os.path.isfile(OUTPUT_FILE)

    try:
        # Open the CSV file in append mode
        with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            # Use DictWriter for easier handling of dictionary data
            writer = csv.DictWriter(f, fieldnames=FIELDS)

            # Write header only if the file is new
            if not file_exists:
                writer.writeheader()
                print(f"Created new output file: {OUTPUT_FILE}")

            # Process each URL
            for i, url in enumerate(urls):
                print(f"\nProcessing property {i+1}/{len(urls)}: {url}")

                # Extract details for this property
                property_data = extract_property_details(driver, url)

                # Write the extracted data to the CSV immediately
                if property_data: # Check if data was successfully extracted
                    writer.writerow(property_data)
                    f.flush() # Ensure data is written to disk
                    processed_count += 1
                    print(f"Saved data for property {i+1}")
                else:
                    print(f"Skipping save for property {i+1} due to extraction error.")

                # Add a random delay between requests
                # if i < len(urls) - 1:  # No need to wait after the last URL
                #     sleep_time = random.uniform(3, 7)
                #     print(f"Waiting {sleep_time:.2f} seconds before next property...")
                #     time.sleep(sleep_time)

        print(f"\nAll done! Processed and saved data for {processed_count} properties.")
        print(f"Results saved incrementally to {OUTPUT_FILE}")

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        print(f"Processed and saved data for {processed_count} properties before interruption.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc() # Print detailed traceback for debugging
    finally:
        # Always close the driver
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()