from bs4 import BeautifulSoup
import requests
import csv
import time
import random

# Define the URL pattern for Flipkart products
url_pattern = "https://www.flipkart.com/search?q={product_name}&otracker searchuni={page_number}"


def scrape_product_data(product_name, page_number):
    # Make a GET request to the product page
    response = requests.get(url_pattern.format(
        product_name=product_name, page_number=page_number))
    print(response)

    # Handle potential errors (e.g., 404 Not Found)
    if response.status_code == 404:
        print(f"Product not found: {product_name}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)

    # Find all product cards on the page
    products = soup.find_all('div', {'class': '_3MlEpv'})
    print(products)

    for product in products:
        print("Product", product)
        # Extract product title
        product_title = product.find('div', {'class': '_25HC_u'}).text.strip()

        # Extract product price
        product_price = product.find('div', {'class': '_3MRUqW'}).text.strip()

        # Extract product rating and reviews
        product_rating = product.find('div', {'class': '_3h_s7a'}).text.strip()
        product_reviews = product.find(
            'div', {'class': '_3LijlP'}).text.strip()

        # Extract product image URL (if available)
        product_image_url = product.find('img', {'class': 'JebZue'})
        if product_image_url:
            product_image_url = "https://www.flipkart.com" + \
                product_image_url['src']

        # Save data to a CSV file
        with open('flipkart_products.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Product Name', 'Price',
                          'Rating', 'Reviews', 'Image URL']
            writer = csv.DictWriter(
                csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow({'Product Name': product_title,
                             'Price': product_price,
                             'Rating': product_rating,
                             'Reviews': product_reviews,
                             'Image URL': product_image_url})


def main():
    # Replace this with your actual list of product names
    products_to_scrape = ["Laptop", "Smartphone", "T-Shirt"]

    for product_name in products_to_scrape:
        for page_number in range(1, 3):  # Scrape first two pages
            scrape_product_data(product_name=product_name,
                                page_number=page_number)
            time.sleep(random.uniform(1, 2))  # Avoid overwhelming the server


if __name__ == "__main__":
    main()
