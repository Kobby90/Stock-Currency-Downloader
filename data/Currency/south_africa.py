import os
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from msedge.selenium_tools import Edge, EdgeOptions

def fetch_exchange_rates():
    # Selenium configurations for Chrome
    chrome_options = Options()
    chrome_options.add_argument('--timeout=30')
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
    chrome_driver_path = ChromeDriverManager().install()
    chrome_driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path)

    # Selenium configurations for Firefox
    firefox_driver_path = GeckoDriverManager().install()
    firefox_driver = webdriver.Firefox(executable_path=firefox_driver_path)

    # Selenium configurations for Edge
    edge_options = EdgeOptions()
    edge_options.use_chromium = True  # Use Chromium-based Edge
    edge_driver = Edge(executable_path="path_to_edgedriver", options=edge_options)

    # Selenium configurations for Safari (Included with Safari on macOS)
    safari_driver = webdriver.Safari()

    # List of all drivers
    drivers = [chrome_driver, firefox_driver, edge_driver, safari_driver]

    for driver in drivers:
        # Open the webpage
        url = "https://www.resbank.co.za/en/home"
        driver.get(url)
    
        # Wait for the page to fully load (adjust wait time as needed)
        time.sleep(5)  # You may need to adjust this wait time
    
        # Get the page source after JavaScript execution
        page_source = driver.page_source
    
        # Parse the HTML content
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the div element with class "row ml-2"
        div_table = soup.find("div", class_="row ml-2")

        if div_table:
            # Find the table element within the div
            table = div_table.find("table", class_="tblRates")

            if table:
                # Initialize lists to store table data
                data = []
                # Extract table rows
                for row in table.find("tbody").find_all("tr"):
                    row_data = [td.get_text(strip=True) for td in row.find_all("td")]
                    data.append(row_data)

                # Convert the data to a DataFrame
                df = pd.DataFrame(data, columns=["Currency", "Rate"])

                print(df)

                # Define the path for saving the PDF file
                output_folder = "output/Currency"
                pdf_path = f"{output_folder}/Currency_south_africa_{date.today()}.pdf"

                # Create the output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)

                # Check if any file with the partial name exists and overwrite it
                for filename in os.listdir(output_folder):
                    if filename.startswith("Currency_south_africa_"):
                        os.remove(os.path.join(output_folder, filename))
                        print(f"Overwriting existing file {filename}")
                        break  # Assuming only one file needs to be overwritten

                # Save the DataFrame as a PDF file
                with PdfPages(pdf_path) as pdf:
                    fig, ax = plt.subplots(figsize=(16, 12))  # Increase figure size
                    ax.axis('tight')
                    ax.axis('off')
                    ax.set_title('Average Exchange rates in South Africa', fontweight="bold")  # Adjust title padding
                    # Calculate column widths based on content
                    col_widths = [max(df[col].apply(lambda x: len(str(x))).max(), len(col)) for col in df.columns]

                    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)  # Adjust font size of column headers
                    table.scale(1.2, 1.2)  # Increase cell size

                    # Adjust column widths
                    for i, width in enumerate(col_widths):
                        table.auto_set_column_width(col=i)

                    pdf.savefig()
                    plt.close()

                print(f"DataFrame saved as PDF: {pdf_path}")
            else:
                print("Table not found on the webpage.")
        else:
            print("Div element with class 'row ml-2' not found on the webpage.")

    # Quit all drivers
    for driver in drivers:
        driver.quit()

# Call the function
fetch_exchange_rates()
