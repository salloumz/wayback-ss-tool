import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_wayback_snapshots(url):
    """
    Fetch all available snapshots for a given URL
    from the Wayback Machine CDX API.
    Returns a list of timestamps (strings).
    """
    cdx_url = "http://web.archive.org/cdx/search/cdx"
    params = {
        'url': url,
        'output': 'json',
        'fl': 'timestamp',
        'collapse': 'digest',        
        'filter': 'statuscode:200'  
    }
    
    try:
        response = requests.get(cdx_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if len(data) <= 1:
            return []
        timestamps = [row[0] for row in data[1:]]
        return timestamps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CDX data: {e}")
        return []

def set_window_size_for_full_page(driver):
  
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, scroll_height)
    time.sleep(1)

def click_and_screenshot(driver, button_text, output_path):
    """
    Click a button (by visible text) on the page to display the relevant tab,
    wait a bit, resize to full page, and take a screenshot.
    
    :param driver: Selenium WebDriver
    :param button_text: The visible text on the button (e.g. 'Individuals')
    :param output_path: File path for saving the screenshot
    """
    
    try:
        button = driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
        button.click()
 
        time.sleep(2)
        set_window_size_for_full_page(driver)
        driver.save_screenshot(output_path)
        print(f"Saved screenshot for: {button_text} -> {output_path}")
    except Exception as e:
        print(f"Could not click or screenshot '{button_text}': {e}")

def take_screenshots_of_tabs(url, output_dir="screenshots", limit=None):
    
    os.makedirs(output_dir, exist_ok=True)
    
    snapshots = get_wayback_snapshots(url)
    print(f"Found {len(snapshots)} snapshots for {url}")

    if limit is not None:
        snapshots = snapshots[:limit]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    for i, timestamp in enumerate(snapshots, start=1):
        archive_url = f"https://web.archive.org/web/{timestamp}/{url}"
        print(f"[{i}/{len(snapshots)}] Capturing {archive_url}")
        
        try:
            driver.get(archive_url)
            time.sleep(4)

            timestamp_folder = os.path.join(output_dir, timestamp)
            os.makedirs(timestamp_folder, exist_ok=True)

            click_and_screenshot(driver, "Individuals", os.path.join(timestamp_folder, "Individuals.png"))
            click_and_screenshot(driver, "Teams", os.path.join(timestamp_folder, "Teams.png"))
            click_and_screenshot(driver, "Anonymous", os.path.join(timestamp_folder, "Anonymous.png"))

        except Exception as e:
            print(f"Error processing {archive_url}: {e}")

    driver.quit()
    print("Done.")

if __name__ == "__main__":
    target_url = "ninevehplaindefensefund.org/supporters"
    take_screenshots_of_tabs(target_url, output_dir="wayback_screenshots", limit=None)
