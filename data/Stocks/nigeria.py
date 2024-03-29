from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import io
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend

def fetch_stock_data():
    # Launch Chrome browser
    driver = webdriver.Chrome()

    # Open the webpage
    url = "https://ngxgroup.com/exchange/data/equities-price-list/"
    driver.get(url)

    # Wait for the JavaScript to load the data
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "latestdiclosuresEquities")))

    # Select "All" from the dropdown menu
    dropdown = driver.find_element(By.NAME, "latestdiclosuresEquities_length")
    options = dropdown.find_elements(By.TAG_NAME, "option")
    for option in options:
        if option.text == "All":
            option.click()
            break

    # Initialize lists to store table data
    headers = []
    data = []

    # Extract the HTML content after JavaScript execution
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table element
    table = soup.find("table", {"id": "latestdiclosuresEquities"})

    if table:
        # Extract table headers
        for th in table.find("thead").find_all("th"):
            headers.append(th.get_text(strip=True))

        # Extract table rows
        for row in table.find("tbody").find_all("tr"):
            row_data = [td.get_text(strip=True) for td in row.find_all("td")]
            data.append(row_data)

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Check if DataFrame is empty
    if df.empty:
        # Look for data from yesterday or the day before yesterday
        for i in range(1, 3):
            # Calculate date for yesterday or the day before yesterday
            date_to_check = datetime.now() - timedelta(days=i)
            date_str = date_to_check.strftime("%d %b %y")

            # Check if data exists for the calculated date
            filtered_data = [row for row in data if row[-1] == date_str]
            if filtered_data:
                df = pd.DataFrame(filtered_data, columns=headers)
                break

    # Print the DataFrame
    print(df)

    if not df.empty:
        # Save the DataFrame as a PDF file with increased font size
        pdf_content = io.BytesIO()
        pdf_pages = pdf_backend.PdfPages(pdf_content)
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.axis('tight')
        ax.axis('off')
        col_widths = [max(df[col].apply(lambda x: len(str(x))).max(), len(col)) for col in df.columns]
        # Increase font size
        table = ax.table(cellText=df.values,
                        colLabels=df.columns,
                        cellLoc='left',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)  # Adjust font size of column headers
        table.scale(1.2, 1.2)  # Increase cell size

        pdf_pages.savefig(fig, bbox_inches='tight')
        pdf_pages.close()
        
        folder_path = 'output/Stocks'

        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        pdf_filename = f'Stocks_nigeria_{datetime.now().strftime("%Y-%m-%d")}.pdf'
        complete_file_path = os.path.join(folder_path, pdf_filename)

        # Check if any file with the partial name exists and overwrite it
        for filename in os.listdir(folder_path):
            if filename.startswith("Stocks_nigeria_"):
                os.remove(os.path.join(folder_path, filename))
                print(f"Overwriting existing file {filename}")
                break  # Assuming only one file needs to be overwritten
        
        # Save the PDF file
        with open(complete_file_path, 'wb') as f:
            f.write(pdf_content.getvalue())

        print(f"PDF file saved as: {complete_file_path}")
    else:
        print("No data found for today, yesterday, or the day before yesterday.")

fetch_stock_data()
