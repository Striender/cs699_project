from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import scrape
import backend.database.db_dump as db_dump

# URL to scrape
URL = "https://nreganarep.nic.in/netnrega/dynamic_work_details.aspx?lflag=eng&fin_year=2025-2026&source=national&labels=labels&Digest=0a5fZ+hdCIswROP5LqpxKg"

# Setup Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # Keeps browser open after script ends

# Initialize browser
browser = webdriver.Chrome(options=chrome_options)
browser.maximize_window()
browser.get(URL)

districts = ["PUNE", "THANE", "NAGPUR", "RATNAGIRI", "KOLHAPUR"]

# Fill in the form
state = browser.find_element(By.ID, "ddl_state")
state.send_keys("MAHARASHTRA")
time.sleep(2)

for district in districts:
    district = browser.find_element(By.ID, "ddl_dist")
    district.send_keys(district)
    time.sleep(2)
    submit_btn = browser.find_element(
        By.XPATH, "//input[@type='submit' and @id='ContentPlaceHolder1_Button1']"
    )
    submit_btn.click()

    time.sleep(20)

    # Wait until the table loads
    table_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive table"))
    )

    # Get table HTML
    table_html = table_element.get_attribute("outerHTML")

    # Call scraping function
    df = scrape.scrapeFunc(table_html)

    # Optional: close the browser
    # browser.quit()

    print("Scraping completed successfully!")


    print("Adding to supabase")
    db_dump.upload_to_supabase(df, f"{district}DB")
