from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import tempfile
from datetime import date
import io
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for simplicity

@app.route('/')
def index():
    html_content = generate_html()  # Call generate_html() here
    return html_content

@app.route('/output/<path:filename>', methods=['GET'])
def download_file(filename):
    directory = 'output'
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        data_type = request.form['dataType']
        country = request.form['countrySelect']

        # Define the directory based on DataType
        if data_type == 'Currency' or data_type == 'Stocks':
            directory = os.path.join('data', data_type)
        else:
            return jsonify({'error': 'Invalid DataType'})

        print(f"Received data: {data_type}, {country}")
        print(f"Directory: {directory}")  # Print the directory

        # Build the path to the Python program
        program_path = os.path.join(directory, f"{country}.py")

        print(f"Program path: {program_path}")

        # Check if the program file exists
        if not os.path.exists(program_path):
            return jsonify({
                'error': f"No program found for {data_type} in {country}",
                'directory': directory.replace(os.path.sep, '/')
            })

        try:
            # Run the Python program using subprocess
            subprocess.run(['python', program_path], check=True)

            return jsonify({'message': 'Data fetched successfully'})

        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Error running {program_path}: {str(e)}'})

    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})


def generate_html():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Currency and Stock Downloader</title>

    <style>
        body {
            background-image: url('https://onlineservice.databankgroup.com/redemptions/Images/bg5.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            margin: 0;
            font-family: 'Arial', sans-serif;
        }

        .container {
            border: 2px solid;
            height: 650px;
            background-color: rgba(241, 241, 241, 0.7); 
            text-align: center;
            margin: 20px;
        }

        .container img {
            overflow-clip-margin: content-box;
            height: auto;
            max-width: 10%;
            border: 0;
            position: absolute;
            top: 40px; 
            left: 30px;
        }

        h1 {
            margin-top: 20px;
            font-size: 40px;
            margin: 100px 0 50px;
        }

        label {
            display: block;
            margin-top: 10px;
            font-size: 18px;
            font-weight: bold;
        }

        .row {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 10px;
            height: 5%;
        }

        .input-container {
            margin-right: 20px;
            height: 120px;
            width: 300px;
            font-weight: bold;
        }

        select, button {
            margin-top: 5px;
            height: 50px;
            width: 310px;
            font-size: 15px;
            border-radius: 15px;
        }

        button {
            padding: 10px 20px;
            font-size: 18px;
            background-color: #116647;
            height:70px;
            color: #fff;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease-in-out;
        }

        button:hover {
            background-color: rgb(149, 196, 72);
        }

        #status {
            font-size: 18px;
            margin-bottom: 20px;
        }

        #loading {
            display: none;
            margin-top: 20px;
        }

        #loading img {
            width: 50px;
            height: 50px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Logo added to the upper left corner -->
        <img src="https://onlineservice.databankgroup.com/redemptions/Images/databank.png" alt="Databank Logo">

        <h1>Currency and Stock Data Downloader</h1>

        <!-- First row: Input selectors -->
        <div class="row">
            <div class="input-container">
                <label for="dataType">Select Data Type:</label>
                <select id="dataType">
                    <option value="select">Select data type</option>
                    <option value="Currency">Currency</option>
                    <option value="Stocks">Stocks</option>
                </select>
            </div>
            
            <div class="input-container">
                <label for="countrySelect">Select a country:</label>
                <select id="countrySelect">
                    <option value="select">Select A Country</option>
                    <option value="botswana">Botswana</option>
                    <option value="cote_divoire">Cote D'Ivoire</option>
                    <option value="egypt">Egypt</option>
                    <option value="kenya">Kenya</option>
                    <option value="malawi">Malawi</option>
                    <option value="mauritius_off">Mauritius Official</option>
                    <option value="mauritius_dem">Mauritius Dem</option>
                    <option value="nigeria">Nigeria</option>
                    <option value="south_africa">South Africa</option>
                    <option value="tanzania">Tanzania</option>
                    <option value="uganda">Uganda</option>
                    <option value="zambia">Zambia</option>

                </select>
            </div>
        </div>

        <!-- Second row: Status -->
        <div class="row">
            <p id="status"></p>
        </div>

        <!-- Third row: Buttons -->
        <div class="row">
            <button id="fetchData">Fetch Data</button>
            <span style="margin: 0 10px;"></span> <!-- Space between buttons -->
            <button id="downloadFile" style="display:none;">Download File</button>
        </div>

        <div id="loading">
            <img src="https://cdnjs.cloudflare.com/ajax/libs/galleriffic/2.0.1/css/loader.gif" alt="Loading">
            <p>Loading...</p>
        </div>
    </div>
    <div class="web-container"></div>

    <!-- Include the Fetch API Polyfill for older browsers -->
    <script src="https://unpkg.com/unfetch/polyfill"></script>

    <script>
        document.getElementById('fetchData').addEventListener('click', function() {
            var dataType = document.getElementById('dataType').value;
            var country = document.getElementById('countrySelect').value;

            // Create a FormData object and append the data
            var formData = new FormData();
            formData.append('dataType', dataType);
            formData.append('countrySelect', country);

            // Show loading spinner
            document.getElementById('loading').style.display = 'block';

            // Fetch API to send the data to the Flask app
            fetch('/fetch_data', { // Using a relative URL
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
              })
            .then(data => {
                // Hide loading spinner
                document.getElementById('loading').style.display = 'none';

                if (data.error && data.error.includes('No program found')) {
                    console.log(`Directory: ${data.directory}`);
                }
  
                console.log(data); // Log the response from the Flask app
                document.getElementById('status').innerText = data.message || data.error;

                // If data.message is present, assume it contains the file content
                if (data.message) {
                  // Create a Blob from the file content
                  var blob = new Blob([data.message], { type: 'application/pdf' });

              }
            })
            .catch(error => {
                // Hide loading spinner on error
                document.getElementById('loading').style.display = 'none';

                console.error('Fetch Error:', error);
                document.getElementById('status').innerText = 'Error occurred. Please check console for details.';
            });

            // Save the last selected values to localStorage
            localStorage.setItem('lastSelectedDataType', dataType);
            localStorage.setItem('lastSelectedCountry', country);
        }); 
      
        document.getElementById('downloadFile').addEventListener('click', function() {
            var dataType = document.getElementById('dataType').value;
            var country = document.getElementById('countrySelect').value;
            var today = new Date().toISOString().slice(0,10); // Get today's date in format "YYYY-MM-DD"

            // Construct the URL for the file download
            var downloadUrl = `/output/${dataType}/${dataType}_${country}_${today}.pdf`;

            // Create a temporary anchor element
            var downloadLink = document.createElement("a");
            downloadLink.href = downloadUrl;
            downloadLink.download = `${dataType}_${country}_${today}.pdf`;
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);

            // Trigger the download by programmatically clicking the link
            downloadLink.click();

            // Remove the temporary link after triggering the download
            document.body.removeChild(downloadLink);
        });

        // Set initial values for user selections from localStorage or use default values
        document.getElementById('dataType').value = localStorage.getItem('lastSelectedDataType') || 'select';
        document.getElementById('countrySelect').value = localStorage.getItem('lastSelectedCountry') || 'select';

        // Display the download file button
        document.getElementById('downloadFile').style.display = 'block';
    </script>
</body>
</html>

"""
    return html

if __name__ == '__main__':
    html_content = generate_html()  # Call generate_html() here before running the app
    app.run(host="0.0.0.0", port=10000, debug=True)
