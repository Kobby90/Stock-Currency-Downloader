import requests
from datetime import date, timedelta
import os


def fetch_stock_data(default_date=None):
    def generate_url(user_date):
        formatted_date = user_date.strftime("%Y-%m-%d")
        month_year = user_date.strftime("%m/%Y")
        return f"https://apis.bse.co.bw/storage/reports/{month_year}/{formatted_date}.pdf"

    def get_user_date(default_date=None):
        if default_date is None:
            default_date = date.today()
        return default_date

    def scrape_website(url, retries=1):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 404 and retries > 0:
                yesterday = date.today() - timedelta(days=1)
                return scrape_website(generate_url(yesterday), retries - 1)
            else:
                print(f"Failed to retrieve the PDF. Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    user_date = get_user_date(default_date)
    url = generate_url(user_date)
    pdf_content = scrape_website(url)

    if pdf_content:
        directory = 'output/Stocks'
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = f"Stocks_botswana_{user_date.strftime('%Y-%m-%d')}.pdf"
        complete_file_path = os.path.join(directory, file_name)

        for filename in os.listdir(directory):
            if filename.startswith("Stocks_botswana_"):
                os.remove(os.path.join(directory, filename))
                print(f"Overwriting existing file {filename}")
                break

        with open(complete_file_path, "wb") as pdf_file:
            pdf_file.write(pdf_content)
        print(f"PDF downloaded successfully as {complete_file_path}.")
    else:
        print("PDF download unsuccessful.")


if __name__ == "__main__":
    fetch_stock_data()
