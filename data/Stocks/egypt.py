from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

def fetch_stock_data():
    # Launch Chrome browser
    driver = webdriver.Chrome()

    # Open the webpage
    url = "https://www.egx.com.eg/en/prices.aspx"
    driver.get(url)

    # Wait for the JavaScript to load the data
    wait = WebDriverWait(driver, 60)
    try:
        # Wait for the element to be visible
        wait.until(EC.visibility_of_element_located((By.ID, "ctl00_C_S_RadGrid2_ctl00")))
    except TimeoutException:
        print("Timed out waiting for element to be visible")

    # Extract the HTML content after JavaScript execution
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table element
    table = soup.find("table", {"class": "MasterTable_Default"})

    if table:
        # Initialize lists to store table data
        headers = []
        data = []

        # Extract table headers
        for th in table.find("thead").find_all("th"):
            headers.append(th.get_text(strip=True))

        # Extract table rows
        for row in table.find("tbody").find_all("tr"):
            row_data = [td.get_text(strip=True) for td in row.find_all("td")]
            data.append(row_data)

        # Convert the data to a DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Print the DataFrame
        print(df)
    else:
        print("Table not found on the webpage.")

fetch_stock_data()
