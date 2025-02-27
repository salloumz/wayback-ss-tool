import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_wayback_snapshots(url):
    """
    Fetch all available snapshots for a given URL
    from the Wayback Machine CDX API.

    Returns a list of snapshot timestamps (strings).
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

def take_screenshots(url, output_dir="screenshots", limit=None):
    
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
            time.sleep(3)
            
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            
            driver.set_window_size(1920, scroll_height)
            
            time.sleep(1)

            screenshot_path = os.path.join(output_dir, f"{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Saved screenshot: {screenshot_path}")

        except Exception as e:
            print(f"Error capturing {archive_url}: {e}")

    driver.quit()
    print("Done.")

if __name__ == "__main__":
    target_url = "ninevehplaindefensefund.org/supporters"
    take_screenshots(target_url, output_dir="wayback_screenshots", limit=5)
