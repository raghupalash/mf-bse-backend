from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os

# Set up the Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Set the download directory
download_dir = "/Users/palash/code/mf_bse_backend/scheme_master"  # Change this to your desired directory
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,  # This skips the download prompt
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Open the webpage
    driver.get("https://bsestarmf.in/")  # Replace with the actual URL

    # Wait until the "Scheme Master" button is clickable and then click it
    scheme_master_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='javascript:openUpSchemeMaster();']"))
    )
    scheme_master_button.click()

    # Switch to the new window opened
    driver.switch_to.window(driver.window_handles[-1])

    # Wait until the dropdown is visible and select "Scheme Code Master Details"
    dropdown = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.TAG_NAME, "select"))
    )
    # Select the option with value 'SCHEMEMASTER'
    select = Select(dropdown)
    select.select_by_value("SCHEMEMASTERPHYSICAL")

    # Wait until the export button is clickable and click it
    export_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Export to Text']"))
    )
    export_button.click()

    # Wait for the download to complete
    time.sleep(10)  # Adjust this depending on your internet speed and file size

    print(f"File downloaded to: {download_dir}")

finally:
    # Close the driver
    driver.quit()
