import os
import json
import requests
from pathlib import Path
from robocorp.tasks import task
from robocorp import browser

# To simulate a shared drive, we will use a local folder.
# Use an env var override for Docker / Cloud deployment.
SHARED_DRIVE_PATH = Path(os.getenv("SHARED_DRIVE_PATH", "output/shared_drive"))
WORK_ITEMS_FILE = Path("output/work-items-in/workitems.json")

@task
def producer_add_images_to_queue():
    """
    PRODUCER (Dispatcher): Adds workload items (Queues) to be processed.
    In local mode, work items are saved to a JSON file.
    """
    print("Producer: Creating work items...")
    
    # We define a few targets to download images from
    queue_data = [
        {"url": "https://www.python.org", "selector": "img.python-logo", "name": "python_logo.png"},
        {"url": "https://news.ycombinator.com", "selector": "img.y18", "name": "hn_logo.gif"}
    ]
    
    # Ensure output directory exists
    WORK_ITEMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save work items to JSON file
    with open(WORK_ITEMS_FILE, "w") as f:
        json.dump(queue_data, f, indent=2)
    
    for data in queue_data:
        print(f"Added to queue: {data['url']}")

@task
def consumer_process_image_queue():
    """
    CONSUMER (Performer): Iterates through the Queue (Work Items) and processes them.
    In local mode, work items are read from a JSON file.
    """
    SHARED_DRIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    browser.configure(
        browser_engine="chromium",
        headless=True,
        install=False,  
        isolated=False, 
    )

    # Load work items from JSON file
    if not WORK_ITEMS_FILE.exists():
        print("No work items file found. Run producer_add_images_to_queue first.")
        return
    
    with open(WORK_ITEMS_FILE, "r") as f:
        work_items = json.load(f)
    
    # Process each work item
    for payload in work_items:
        url = payload.get("url")
        selector = payload.get("selector")
        suggested_name = payload.get("name", "download.png")
        
        if not url or not selector:
            print(f"Invalid payload - missing url or selector: {payload}")
            continue
            
        print(f"Processing queue item for URL: {url}")
        
        try:
            page = browser.goto(url)
            
            logo_locator = page.locator(selector).first
            img_url = logo_locator.get_attribute("src")
            
            if not img_url:
                raise ValueError(f"Could not find the image for selector '{selector}'")

            # Resolve relative URLs
            if img_url.startswith("/"):
                base_url = "/".join(url.split("/")[:3])
                img_url = f"{base_url}{img_url}"

            print(f"Found image URL: {img_url}. Downloading...")

            response = requests.get(img_url)
            response.raise_for_status()

            target_file = SHARED_DRIVE_PATH / suggested_name
            
            with open(target_file, "wb") as f:
                f.write(response.content)
                
            print(f"Successfully downloaded to: {target_file}")
            
        except Exception as e:
            print(f"Failed to process {url}. Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "producer":
        producer_add_images_to_queue()
    elif len(sys.argv) > 1 and sys.argv[1] == "consumer":
        consumer_process_image_queue()
    else:
        print("Usage: python tasks.py [producer|consumer]")
        print("  producer - Create work items")
        print("  consumer - Process work items")

