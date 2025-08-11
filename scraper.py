# scraper.py

import time
from typing import Dict, List, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # For deployment
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('chromedriver.exe')  # Update path if needed
    return webdriver.Chrome(service=service, options=chrome_options)


def scrape_flipkart_product(url: str) -> Tuple[Dict, List[Dict]]:
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)

    # Extract Product Info
    product_info = {
        "title": "N/A",
        "price": "N/A",
        "rating": "N/A",
        "total_ratings": "N/A",
        "total_reviews": "N/A"
    }

    try:
        product_info['title'] = driver.find_element(By.CLASS_NAME, 'VU-ZEz').text.strip()
    except:
        pass

    try:
        price_div = driver.find_element(By.CLASS_NAME, 'UOCQB1').text.strip()
        product_info['price'] = '₹' + price_div.split('₹')[1].strip()
    except:
        pass

    try:
        product_info['rating'] = driver.find_element(By.CLASS_NAME, 'XQDdHH').text.strip()
    except:
        pass

    try:
        rr_blocks = driver.find_elements(By.CLASS_NAME, 'j-aW8Z')
        if len(rr_blocks) >= 1:
            product_info['total_ratings'] = rr_blocks[0].text.strip()
        if len(rr_blocks) >= 2:
            product_info['total_reviews'] = rr_blocks[1].text.strip()
    except:
        pass

    # Click "All Reviews" Button
    try:
        all_reviews_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//div[contains(@class, '_23J90q')] and .//span[contains(text(), 'All') and contains(text(), 'reviews')]]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", all_reviews_link)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", all_reviews_link)
        time.sleep(3)
    except TimeoutException:
        print("❌ Could not find 'All reviews' button.")
        driver.quit()
        return product_info, []

    # Scrape Reviews
    page_num = 1
    all_reviews = []
    seen_reviews = set()

    while True:
        print(f"Scraping Page {page_num}...")
        paginated_url = driver.current_url.split('&page=')[0] + f"&page={page_num}"
        driver.get(paginated_url)
        time.sleep(2)

        reviews = driver.find_elements(By.CLASS_NAME, 'cPHDOP')
        if not reviews:
            break

        new_found = False

        for r in reviews:
            try:
                review_rating = r.find_element(By.CLASS_NAME, 'XQDdHH').text.strip()
                if review_rating == product_info['rating']:
                    continue  # ❌ Skip if same as product overall rating
            except:
                continue

            try:
                title = r.find_element(By.CLASS_NAME, 'z9E0IG').text.strip()
            except:
                title = "No Title"

            try:
                content = r.find_element(By.CLASS_NAME, 'ZmyHeo').text.strip().replace("READ MORE", "")
            except:
                content = "N/A"

            review_id = review_rating + title + content
            if review_id not in seen_reviews:
                seen_reviews.add(review_id)
                all_reviews.append({
                    "rating": review_rating,
                    "title": title,
                    "content": content
                })
                new_found = True

        if not new_found:
            break

        page_num += 1
        time.sleep(1.5)

    driver.quit()
    return product_info, all_reviews
