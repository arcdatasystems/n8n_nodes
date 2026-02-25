import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---
TARGET_URL = "https://n8n.io/integrations/" # Update if the URL is different
BUTTON_TEXT = "Load more"

# --- Setup Chrome Options ---
options = Options()
# options.add_argument("--headless") # Uncomment this to run without a window opening
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

# Initialize Driver (Selenium Manager handles the version 141 mismatch automatically)
driver = webdriver.Chrome(options=options)

try:
    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    
    # Optional: Wait for any cookie banners and clear them if necessary
    # (n8n usually has a 'Accept' button you might need to click)
    
    click_count = 0
    while True:
        try:
            # 1. Look for the button by text
            # We use a more flexible XPath to find the button regardless of its container
            xpath = f"//button[contains(., '{BUTTON_TEXT}')] | //div[contains(text(), '{BUTTON_TEXT}')]"
            
            load_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            # 2. Scroll the button into the center of the screen
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
            time.sleep(1) # Let the scroll finish

            # 3. Use JavaScript to click to avoid "ElementClickInterceptedException"
            driver.execute_script("arguments[0].click();", load_more_button)
            
            click_count += 1
            print(f"Clicked '{BUTTON_TEXT}' ({click_count} times)...")
            
            # 4. Wait for the DOM to update
            time.sleep(2)

        except TimeoutException:
            print("No more 'Load More' button found or page fully loaded.")
            break
        except Exception as e:
            print(f"Stopping clicks due to: {e}")
            break

    # --- Data Extraction ---
    print("Extracting integration titles...")
    page_source = driver.page_source
    
    # Regex logic: 
    # Finds href="/integrations/some-name/" and captures "some-name"
    pattern = r'href="/integrations/([^/"]+)/"'
    integrations = re.findall(pattern, page_source)
    
    # Clean up: Remove duplicates and filter out generic strings if necessary
    unique_integrations = sorted(list(set(integrations)))

    # --- Results ---
    print("\n" + "="*30)
    print(f"TOTAL FOUND: {len(unique_integrations)}")
    print("="*30)
    for name in unique_integrations:
        print(name)

finally:
    print("\nClosing browser...")
    driver.quit()
