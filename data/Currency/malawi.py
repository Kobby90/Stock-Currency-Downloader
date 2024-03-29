import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import os

def fetch_exchange_rates():
    url = "https://www.rbm.mw/"
    countryName = "malawi"

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the div containing the exchange rate data
        exchange_rate_div = soup.find("div", class_="home-rates")

        if exchange_rate_div:
            # Extract the date
            date_element = exchange_rate_div.find("span", id="exhangeRateDate")
            date = date_element.text.strip()

            # Find the exchange rate table
            exchange_rate_table = exchange_rate_div.find("table", id="exchange-rates_home")

            if exchange_rate_table:
                # Extract table data
                rows = exchange_rate_table.find_all("tr")
                currencies = {}

                for row in rows[1:]:  # Skip the header row
                    columns = row.find_all("td")
                    if len(columns) >= 3:
                        currency = columns[0].text.strip()
                        buying = float(columns[1].text.strip())
                        selling = float(columns[2].text.strip())

                        currencies[currency] = {"Buying": buying, "Selling": selling}

                # Convert data to DataFrame
                df = pd.DataFrame.from_dict(currencies, orient='index')

                # Rename the index to 'Currency' and reset the index
                df.index.name = 'Currency'
                df.reset_index(inplace=True)

                # Create PDF with DataFrame
                current_Date = datetime.now().strftime("%Y-%m-%d")
                pdf_filename = f"output/Currency/Currency_{countryName}_{current_Date}.pdf"

                with PdfPages(pdf_filename) as pdf:
                    title = "Malawi Exchange Rate"
                    ax = plt.subplot(111, frame_on=False)
                    ax.xaxis.set_visible(False)
                    ax.yaxis.set_visible(False)

                    # Add title to the table
                    plt.title(title, fontsize=14, loc='center', pad=20)

                    table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(1, 1.5)
                    pdf.savefig()
                    plt.close()
                
                return f"Exchange rate data saved as {pdf_filename}"
            else:
                return "Exchange Rate Table Not Found on the Page"
        else:
            return "Exchange Rate Data Not Found on the Page"
    else:
        return "Error accessing the website. Please try again later."

# Call the function
result = fetch_exchange_rates()
print(result)
