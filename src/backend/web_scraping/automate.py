from pathlib import Path
import sys
# ensure the 'src' folder is on sys.path so `import backend...` works
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from backend.database import db_dump
from backend.web_scraping import scrape  # use package import
import pandas as pd
# URLs
URL1 = "https://nreganarep.nic.in/netnrega/dynamic_work_details.aspx?lflag=eng&fin_year=2025-2026&source=national&labels=labels&Digest=0a5fZ+hdCIswROP5LqpxKg"
URL2 = "https://nreganarep.nic.in/netnrega/dynamic_work_details.aspx?lflag=eng&fin_year=2024-2025&source=national&labels=labels&Digest=O57D2k1AxQj89t4Y5xNiBg"

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_experimental_option("detach", True)

browser = webdriver.Chrome(options=chrome_options)
browser.maximize_window()

districts = ["PUNE", "THANE", "NAGPUR", "RATNAGIRI", "KOLHAPUR", "BHANDARA", "GADCHIROLI", "PALGHAR", "RAIGAD", "SANGLI", "SATARA", "SINDHUDURG", "WARDHA"]

def scrape_for_url(url, district):
    """Open URL, select district, scrape table, return df."""
    browser.get(url)

    # select state
    WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "ddl_state"))
    ).send_keys("MAHARASHTRA")
    time.sleep(1)

    # select district
    WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "ddl_dist"))
    ).send_keys(district)
    time.sleep(1)

    # click submit
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_Button1"))
    ).click()

    # wait until table loads
    table_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive table"))
    )

    time.sleep(2)
    # extract df
    table_html = table_element.get_attribute("outerHTML")
    return scrape.scrapeFunc(table_html)


# # Main loop
for district in districts:
# district = "KOLHAPUR"
    print(f"\nProcessing {district} ...")

# Scrape URL1
    df1 = scrape_for_url(URL1, district)
    print(f"URL1 done for {district}")

    # Scrape URL2
    df2 = scrape_for_url(URL2, district)
    print(f"URL2 done for {district}")

    # Combine both
    final_df = pd.concat([df1, df2])

    # Save to CSV
    final_df.to_csv(f"{district}.csv", index=False)
    print(f"Saved combined CSV: {district}.csv")

    print("\nAll districts completed.")
    print("Adding to supabase")
    db_dump.upload_to_supabase(final_df, f"{district}DB")
