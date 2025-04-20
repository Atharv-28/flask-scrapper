import requests
from bs4 import BeautifulSoup

def scrape_flipkart(url):
    # Set up headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Send a GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

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

