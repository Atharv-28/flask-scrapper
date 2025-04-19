from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import os  # Add this import at the top of the file

# Import the scrape logic from flipkart.py
from flipkart import scrape_flipkart  # Ensure the function is defined in flipkart.py

app = Flask(__name__)
CORS(app, resources={r"/scrape": {"origins": "*"}})  # Adjust origins as needed

def scrape_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            title = soup.find("span", {"id": "productTitle"}).get_text(strip=True)
            brand = soup.find("a", {"id": "bylineInfo"}).get_text(strip=True)

            material = None
            material_row = soup.find("tr", {"class": "a-spacing-small po-material"})
            if material_row:
                material = material_row.find("td", {"class": "a-span9"}).get_text(strip=True)

            if not material:
                tech_details_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
                if tech_details_table:
                    rows = tech_details_table.find_all("tr")
                    for row in rows:
                        header = row.find("th", {"class": "prodDetSectionEntry"})
                        value = row.find("td", {"class": "prodDetAttrValue"})
                        if header and value and "Material" in header.get_text(strip=True):
                            material = value.get_text(strip=True)
                            break
            
            img_tag = soup.find("img", {"id": "landingImage"})
            if img_tag and "data-a-dynamic-image" in img_tag.attrs:
                dynamic_image_data = img_tag["data-a-dynamic-image"]
                # Extract the first image URL from the JSON-like string
                image_url = list(eval(dynamic_image_data).keys())[0]
            else:
                image_url = "Image not found."

            return {
                "title": title,
                "image_url": image_url,
                "brand": brand,
                "material": material if material else "Material information not found."
            }
        except AttributeError:
            return {"error": "Could not extract some details. The structure might have changed."}
    else:
        return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL is required."}), 400

        if "amazon" in url:
            product_details = scrape_amazon(url)
        elif "amzn" in url:
            product_details = scrape_amazon(url)
        elif "flipkart" in url:
            product_details = scrape_flipkart(url)
        else:
            return jsonify({"error": "Unsupported URL. Only Amazon and Flipkart are supported."})

        return jsonify(product_details)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)