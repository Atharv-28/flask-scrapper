from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/scrape": {"origins": "*"}})  # Adjust origins as needed

def scrape_flipkart(url):
    start_time = time.time()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=5)
    print(f"Request time: {time.time() - start_time} seconds")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        print(f"Parsing time: {time.time() - start_time} seconds")

        try:
            # Extract product details
            title = soup.find("span", {"class": "VU-ZEz"}).get_text(strip=True)  # Product title

            # Extract image URL
            img_tag = soup.find("img", {"class": "DByuf4 IZexXJ jLEJ7H"})
            img_url = img_tag["src"] if img_tag else "Image not found."

            # Extract price
            price_tag = soup.find("div", {"class": "Nx9bqj CxhGGd"})
            price = price_tag.get_text(strip=True) if price_tag else "Price not found."

            # Extract material information
            material = None
            spec_tables = soup.find_all("table", {"class": "_0ZhAN9"})  # Find all tables with the same class
            for spec_table in spec_tables:
                rows = spec_table.find_all("tr")
                for row in rows:
                    header = row.find("td", {"class": "+fFi1w col col-3-12"})
                    value = row.find("td", {"class": "Izz52n col col-9-12"})
                    if header and value:
                        text = header.get_text(strip=True).lower()
                        if "material" in text or "fabric" in text:
                            # Use .find() to go directly into <li> tag if it exists
                            li_tag = value.find("li")
                            if li_tag:
                                material = li_tag.get_text(strip=True)
                            else:
                                material = value.get_text(strip=True)
                            break
                if material:  # Break outer loop if material is found
                    break

            return {
                "title": title,
                "image_url": img_url,
                "price": price,
                "material": material if material else "Material information not found."
            }
        except AttributeError:
            return {"error": "Could not extract details."}
    else:
        return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL is required."}), 400

        if "flipkart" in url:
            product_details = scrape_flipkart(url)
        else:
            return jsonify({"error": "Unsupported URL. Only Flipkart is supported."})

        return jsonify(product_details)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)