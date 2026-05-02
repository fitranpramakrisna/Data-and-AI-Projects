from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime

# webdriver inisialization
driver = webdriver.Chrome() 

# web target: Kickavenue
driver.get("https://www.kickavenue.com/search/sneakers?sort_by=featured_item_score_desc&keyword=")

# Auto-scrolling-down simulation
time.sleep(2)  # Allow 2 seconds for the web page to open
scroll_pause_time = 0.5 # Set to 0.5 secs for pause scrolling
screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
max_elements = 250 # the maximum elements to scrap (might be slightly over 250)
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(scroll_pause_time)
    
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")  
    
    elements_found = driver.find_elements(By.XPATH, "//div[contains(@class, 'sneaker') and contains(@class, 'col-6') and contains(@class, 'col-sm-6') and contains(@class, 'col-md-4') and contains(@class, 'col-lg-3')]")  # Replace with appropriate selector
    elements_count = len(elements_found)
    
    # Stop scrolling when the element count gets over 250 elements
    if elements_count > max_elements:
        break 

# web content to scrap
elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'sneaker') and contains(@class, 'col-6') and contains(@class, 'col-sm-6') and contains(@class, 'col-md-4') and contains(@class, 'col-lg-3')]")

# to check how many elements successfully scraped
print(f'Total products scraped: {len(elements)}')

# initializing empty arrays to store values of each element
product_list = []
price_lists = []
link_product_lists = []
currency_lists = []

# searching and storing each element (product name, price list, link_product, and currency)
for element in elements:
    # starting to scrap element for (product name, price list, link_product, and currency)
    name_product = element.find_element(By.XPATH, ".//div[contains(@class, 'wrapper') and contains(@class, 'grey-default') and contains(@class, 'card')]//h2[contains(@class, 'price-tag')]").text
    price_product = element.find_element(By.XPATH, ".//div[contains(@class, 'wrapper') and contains(@class, 'grey-default') and contains(@class, 'card')]//span[contains(@class, 'currency-tag')]").text
    price_product_int = int(price_product.split(' ')[1].replace(",",""))
    
    currency = price_product.split(' ')[0]
    
    link = element.find_element(By.XPATH, ".//a").get_attribute("href")
    
    product_list.append(name_product)
    price_lists.append(price_product_int)
    currency_lists.append(currency)
    link_product_lists.append(link)
    
# store all in dictionary called 'data'
data = {
    "product_name" : product_list,
    "price_tag" : price_lists,
    "currency (IDR)" : currency_lists,
    "link_product" : link_product_lists
}

# convert to pandas dataframe
df = pd.DataFrame(data=data)

# exclude any values except IDR values
product_idr_currency = df[df['currency (IDR)'] == 'IDR']

# sorting the data by price tag from lowest to highest
product_idr_currency.sort_values(by='price_tag', ascending=True, inplace=True)

# exporting to csv file
file_name = f"sneakers_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"
product_idr_currency.to_csv(file_name, index=False)

driver.quit()
