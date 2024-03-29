import requests
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os
from datetime import date

def fetch_stock_data():
    # URL of the website
    url = "https://mse.co.mw/#"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with id="table-MAINBOARD"
    table = soup.find("table", {"id": "table-MAINBOARD"})

    # Check if the table is found
    if table:
        # Extract table headers
        headers = [header.text.strip() for header in table.find_all("th")]

        # Extract table rows
        rows = []
        for row in table.find_all("tr"):
            rows.append([cell.text.strip() for cell in row.find_all("td")])

        # Return table headers and rows
        return headers, rows
    else:
        return None, None

def create_pdf(headers, rows):
    if headers and rows:
        # Convert data to DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        output_folder = 'output/Stocks'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_file_path = os.path.join(output_folder, f'Stocks_malawi_{date.today()}.pdf')
        # Check if any file with the partial name exists and overwrite it
        for filename in os.listdir(output_folder):
            if filename.startswith("Stocks_malawi_"):
                os.remove(os.path.join(output_folder, filename))
                print(f"Overwriting existing file {filename}")
                break  # Assuming only one file needs to be overwritten

        # Create a PDF
        with PdfPages(pdf_file_path) as pdf:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('tight')
            ax.axis('off')
            ax.table(cellText=df.values, colLabels=df.columns, loc='center')

            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

        print("PDF saved successfully.")
    else:
        print("Table data is empty.")

# Call the function
headers, rows = fetch_stock_data()
create_pdf(headers, rows)
