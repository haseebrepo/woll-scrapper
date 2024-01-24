import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import logging

class WollplatzScraper:
    def __init__(self, excel_file_path='software.xlsx', json_file_path='data.json', log_file_path='scrape_wollplatz.log'):
        self.excel_file_path = excel_file_path
        self.json_file_path = json_file_path
        self.log_file_path = log_file_path
        self.scraped_data = []

        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def save_in_json(self):
        json_output = json.dumps(self.scraped_data, ensure_ascii=False, indent=4)
        with open(self.json_file_path, 'w', encoding='utf-8') as file:
            file.write(json_output)

    def get_page_source(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.END)
        page_source = driver.page_source
        driver.quit()
        return page_source

    def extract_price(self, soup):
        price_tag = soup.find('span', class_='product-price-amount')
        return price_tag.get_text(strip=True) if price_tag else None

    def extract_availability(self, soup):
        availability_tag = soup.find('span', class_='stock-green')
        return 'Available' if availability_tag else None

    def extract_specs(self, soup):
        specs_table = soup.find('div', id='pdetailTableSpecs').find('table').find('tbody').findAll('tr')
        specs = {}
        for tr in specs_table:
            key = tr.findAll('td')[0].get_text(strip=True)
            value = tr.findAll('td')[1].get_text(strip=True)
            specs[key] = value
        return specs

    def find_product_on_page(self, page_source, global_product_name):
        soup = BeautifulSoup(page_source, 'html.parser')
        product_holders = soup.find_all('div', class_='innerproductlist')

        for product_holder in product_holders:
            product_name = product_holder['data-productname'].strip().lower()

            if global_product_name.lower() in product_name.lower():
                product_link = product_holder.find('a', class_='productlist-imgholder')['href']
                self.logger.info(f"Product '{product_name}' found. Link: {product_link}")

                product_page_source = self.get_page_source(product_link)
                product_soup = BeautifulSoup(product_page_source, 'html.parser')

                product_price = self.extract_price(product_soup)
                self.logger.info(f"Product Price: {product_price}" if product_price else "Product price not found on the product page.")

                product_availability = self.extract_availability(product_soup)
                self.logger.info(f"Product Availability: {product_availability}" if product_availability else "Product availability not found on the product page.")

                product_specs = self.extract_specs(product_soup)

                product_data = {
                    'name': product_name,
                    'link': product_link,
                    'price': product_price,
                    'availability': product_availability,
                    'Needle Size': product_specs.get('Nadelstärke'),
                    'Composition': product_specs.get('Zusammenstellung'),
                    'Website': 'Wollplatz',
                }
                self.scraped_data.append(product_data)
                self.save_in_json()
                self.logger.info("Production information added in array")

                return True

        return False

    def scrape_wollplatz(self, global_brand_name, global_product_name):
        url = "https://www.wollplatz.de/"
        main_page_source = self.get_page_source(url)
        main_soup = BeautifulSoup(main_page_source, 'html.parser')

        nav_menu = main_soup.find('nav', id='menubar101')

        if nav_menu and global_brand_name.lower() in nav_menu.get_text().lower():
            brand_link = nav_menu.find('a', text=lambda text: text and global_brand_name.lower() in text.lower(), href=True)

            if brand_link:
                brand_page_source = self.get_page_source(brand_link.get('href'))

                if self.find_product_on_page(brand_page_source, global_product_name):
                    pass
                else:
                    self.logger.debug("Product not found in the current page")
                    brand_soup = BeautifulSoup(brand_page_source, 'html.parser')
                    next_page_link = brand_soup.find('link', {'rel': 'next', 'href': True})

                    while next_page_link:
                        next_page_source = self.get_page_source(next_page_link['href'])

                        if self.find_product_on_page(next_page_source, global_product_name):
                            break

                        next_page_soup = BeautifulSoup(next_page_source, 'html.parser')
                        next_page_link = next_page_soup.find('link', {'rel': 'next', 'href': True})
                    else:
                        self.logger.info(f"Product '{global_product_name}' not found on any page.")


class Scrappers:

    def __init__(self) -> None:
        self.wollplatz = WollplatzScraper()
        """
        here make instance of other class in future which will be scrapping data from another website
        """
        

    def run_scraper(self):
        df = pd.read_excel(self.wollplatz.excel_file_path)

        for index, row in df.iterrows():
            global_brand_name = row['Brand']
            global_product_name = row['Name']
            self.wollplatz.logger.info('Searching for product: %s', global_product_name)

            try:
                self.wollplatz.scrape_wollplatz(global_brand_name, global_product_name)
            except Exception as e:
                self.wollplatz.error(f"Error while scraping (Product -> {global_product_name}): {str(e)}")

            """
            here call the scrapper method of other class which will be scrapping data from other website in future
            """


if __name__ == "__main__":
    wollplatz_scraper = Scrappers()
    wollplatz_scraper.run_scraper()
