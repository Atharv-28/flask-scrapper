from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import os  # Add this import at the top of the file

# Import the scrape logic from flipkart.py
from flipkart import scrape_flipkart  # Ensure the function is defined in flipkart.py

app = Flask(__name__)
CORS(app, resources={r"/scrape": {"origins": "*"}})  # Adjust origins as needed

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL is required."}), 400

        # if "amazon" in url:
        #     product_details = scrape_amazon(url)
        # elif "amzn" in url:
        #     product_details = scrape_amazon(url)
        if "flipkart" in url:
            product_details = scrape_flipkart(url)
        else:
            return jsonify({"error": "Unsupported URL. Only Amazon and Flipkart are supported."})

        return jsonify(product_details)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)