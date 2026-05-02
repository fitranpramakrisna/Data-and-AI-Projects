  # Sneaker Products Scraper on Kick Avenue Website

This script uses Python and Selenium to scrape sneaker product data from the [Kickavenue](https://www.kickavenue.com/search/sneakers?sort_by=featured_item_score_desc&keyword=) website. It collects product names, prices, currency, and links for products listed on the page. The results are filtered to include only products priced in Indonesian Rupiah (IDR), sorted by price in ascending order, and exported to an CSV file.

## Features
- Automated web scraping of sneaker product data.
- Handles dynamic page loading using auto-scrolling simulation.
- Filters and processes the scraped data to include only IDR-based prices.
- Outputs the processed data to an CSV file with a timestamped filename.

## Requirements
- Python 3.x
- [Selenium](https://pypi.org/project/selenium/)
- [Pandas](https://pandas.pydata.org/)
- Google Chrome browser and [ChromeDriver](https://sites.google.com/chromium.org/driver/)

## Installation
1. Clone this repository or copy the script.
2. Install the required Python packages:
   ```bash 
    pip install selenium
    pip install pandas
    ```

 ## How to Use
 1. Launch the script:
    ```bash 
    python apps.py
    ```
2. The script will:
- Open the Kickavenue website.
- Scroll down to load more products.
- Scrape product details including name, price, currency, and links.
- Filter products priced in IDR, sort them by price, and save the results in an CSV file.
3. The output file will be saved in the current directory with a name in the format:
sneakers_products_YYYYMMDD_HHMMSS.csv

## Code Workflow
1. Webdriver Initialization: Opens the Kickavenue sneaker page using ChromeDriver.
2. Auto-scrolling Simulation: Scrolls down the page to dynamically load more products.
3. Data Extraction: Collects product name, price, currency, and link for each product using XPath selectors.
4. Data Processing:
    - Filters out non-IDR priced items.
    - Sorts products by price (ascending).
5. Export: Saves the cleaned and sorted data into an CSV file.

## Output Example
The CSV file will contain the following columns:
- product_name: The name of the sneaker.
- price_tag: The price of the sneaker in IDR.
- currency (IDR): The currency, filtered to include only IDR.
- link_product: The URL to the sneaker product page.

## Notes
- Ensure you have a stable internet connection while running the script.
- Adjust the max_elements variable to limit the number of products to scrape.
- Use this script responsibly and in accordance with the terms of service of the website.
