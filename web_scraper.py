from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import concurrent.futures as cf
import multiprocessing
import itertools
import time
import uuid
import os
import json
import urllib.request
import web_scraper_config

class Scraper():
    def __init__(self, website) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.website = website

    def scroll(self):
        self.driver.execute_script("window.scrollTo(0, 500);")
    
    def browse_next(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        next_page = self.driver.find_element(By.XPATH, web_scraper_config.next_page_xpath) 
        next_page.click()
        return self.driver

    def search(self, search_input):
        search_bar = self.driver.find_element(By.XPATH, web_scraper_config.search_xpath)
        search_bar.click()
        time.sleep(1)
        enter_keys = self.driver.find_element(By.XPATH, web_scraper_config.search_input_xpath)
        enter_keys.send_keys(search_input)
        enter_keys.send_keys(Keys.RETURN)
        print(f'Search for {search_input} has been entered')
    
    def load_and_accept_cookies(self, website):
        self.driver.get(website)
        delay = 10
        try:
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, web_scraper_config.accept_cookies_xpath)))
            print("Accept Cookies Button is Ready!")
            accept_cookies_button[0].click()
            time.sleep(2)
            print("Accept cookies button has been clicked!")
        except TimeoutException:
            print("Loading took too much time!")
    
    def load_and_reject_promotion(self):
        delay = 10
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, web_scraper_config.wait_for_promotion1_xpath)))
            reject_promotion_button = self.driver.find_element(By.XPATH, web_scraper_config.reject_promotion1_xpath)
            reject_promotion_button.click()
            print("Promotion has been closed!")
            time.sleep(2)
        except:
            try:
                WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, web_scraper_config.wait_for_promotion2_xpath)))
                reject_promotion_button = self.driver.find_element(By.XPATH, web_scraper_config.reject_promotion2_xpath)
                reject_promotion_button.click()
                print("Promotion has been closed!")
                time.sleep(2)
            except TimeoutException:
                print("No promotion pop-up this time!")   
    
    def ask_department(self):

        while True:
            department = input("Enter either the Men or Women's department to scrape: ") 
            if str(department).lower().capitalize() == 'Men' or str(department).lower().capitalize() == 'Women':
                print(f'Program will beginning scraping the {department}s data')
                return str(department).lower().capitalize()
            else:
                print("Please enter either the Men or Women department")

    def get_categories(self, department):
        department_button = self.driver.find_element(By.XPATH, web_scraper_config.DEPARTMENT_XPATH.format(department))
        department_button.click()

        shop_department_button = self.driver.find_element(By.XPATH, web_scraper_config.DEPARTMENT_BUTTON_XPATH)
        shop_department_button.click()

        choose_categories = self.driver.find_elements(By.XPATH, web_scraper_config.CHOOSE_CATEGORIES_XPATH)
        category_dict_list = []

        for element in choose_categories:
            category_dict = dict()
            index = int(len(web_scraper_config.WEBSITE)) + int(len(department)) + 2
            category_dict["department"] = department
            category_dict["category"] = element.get_attribute('href')[index:-1].replace("-", "_")
            category_dict["link"] = element.get_attribute('href')
            category_dict_list.append(category_dict)
        return category_dict_list
 
    def get_subcategories(self, category_dict_list):
        full_scrape_list = []
        a=0
        while True:
            if a == 3:
                break
            category_dict = category_dict_list[a]
            self.driver.get(category_dict["link"])
            choose_subcategories = self.driver.find_elements(By.XPATH, web_scraper_config.CHOOSE_SUBCATEGORIES_XPATH)
            
            for element in choose_subcategories:
                full_scrape_dict = dict()
                full_scrape_dict["department"] = category_dict["department"]
                full_scrape_dict["category"] = category_dict["category"]
                full_scrape_dict["category_link"] = category_dict["link"]
                index = int(len(web_scraper_config.WEBSITE))+ int(len(category_dict["department"])) +int(len(category_dict["category"])) + 3
                full_scrape_dict["subcategory"] = element.get_attribute('href')[index:-1]
                full_scrape_dict["subcategory_link"] = element.get_attribute('href')
                full_scrape_list.append(full_scrape_dict)
            a+=1
        # print(full_scrape_list)
        return full_scrape_list 

    def run_scrape(self):
        self.load_and_accept_cookies(web_scraper_config.WEBSITE)
        self.load_and_reject_promotion()
        department = self.ask_department()
        category_dict_list = self.get_categories(department)
        full_scrape_list = self.get_subcategories(category_dict_list)
        # with multiprocessing.Pool() as pool:
        #     pool.map(self.scrape_subcategories, full_scrape_list)
        print(full_scrape_list)
        return full_scrape_list

    def scrape_subcategories(self, full_scrape_list):
        for dict in full_scrape_list:
            new_scrape = Scraper(web_scraper_config.WEBSITE)
            new_scrape.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.COMMAND + 't')
            new_scrape.driver.get(dict["subcategory_link"])
            link_list = new_scrape.get_links()
            product_dict_list = new_scrape.scrape_item_data(link_list, dict["category"], dict["subcategory"])
            new_scrape.download_images(product_dict_list, dict["category"], dict["subcategory"])
            print(f'All the {dict["subcategory"]} pages in {dict["category"]} have been scraped')
            new_scrape.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.COMMAND + 'w')
            time.sleep(2)

    def get_links(self):
        item_container = self.driver.find_element(By.XPATH, web_scraper_config.item_container_xpath)
        link_list = []
        item_list = item_container.find_elements(By.XPATH, './div')

        for item in item_list:
            a_tag = item.find_element(By.TAG_NAME, 'a')
            _link = a_tag.get_attribute('href')
            link_list.append(_link)

        print("Links on this page have been scraped")
        return link_list

    def scrape_item_data(self, link_list, category, sub_category) -> list:
        product_dict_list = []

        for link in link_list:
            product_dict = dict()
            self.driver.get(link) 
            product_dict["product_no"] = self.driver.find_elements(By.XPATH, web_scraper_config.product_no_xpath)[0].text
            PATH = web_scraper_config.RAW_DATA_PATH + f'/{category}/{sub_category}'

            if os.path.exists(PATH) == False:
                os.makedirs(PATH)
                print(f'raw_data has been made in the ~/{category}/{sub_category} directory')

            item_path = PATH + f'/{product_dict["product_no"]}'

            try:
                os.mkdir(item_path)   
            except:
                print("product info has already been saved")
                continue

            product_dict["uuid"] = str(uuid.uuid4())
            product_dict["brand"] = self.driver.find_element(By.XPATH, web_scraper_config.brand_xpath).text
            product_dict["product_info"] = self.driver.find_element(By.XPATH, web_scraper_config.product_info_xpath).text
            product_dict["price"] = self.driver.find_element(By.XPATH, web_scraper_config.price_xpath).text
            self.scroll()
            time.sleep(1)
            if self.driver.find_element(By.XPATH, web_scraper_config.HEADING_INFO_ACTIVE_XPATH).text.lower() == "size & fit":
                product_dict["size_and_fit"] = self.driver.find_element(By.XPATH, web_scraper_config.size_and_fit_xpath).text    
            else:
                try:
                    size_and_fit_button = self.driver.find_element(By.XPATH, web_scraper_config.SIZE_AND_FIT_INACTIVE_XPATH)
                    size_and_fit_button.click()
                    product_dict["size_and_fit"] = self.driver.find_element(By.XPATH, web_scraper_config.size_and_fit_xpath).text
                except:
                    pass
            
            if self.driver.find_element(By.XPATH, web_scraper_config.HEADING_INFO_ACTIVE_XPATH).text.lower() == "brand bio":
                product_dict["brand_bio"] = self.driver.find_element(By.XPATH, web_scraper_config.brand_bio_xpath).text   
            else:
                try:   
                    brand_bio_button = self.driver.find_element(By.XPATH, web_scraper_config.BRAND_BIO_INACTIVE_XPATH)
                    brand_bio_button.click()
                    product_dict["brand_bio"] = self.driver.find_element(By.XPATH, web_scraper_config.brand_bio_xpath).text
                except:
                    pass

            product_dict["image_link"] = self.driver.find_element(By.XPATH, web_scraper_config.image_link_xpath).get_attribute('src')
            product_dict_list.append(product_dict)

            with open(f'{item_path}/data.json', 'w') as fp:
                    json.dump(product_dict, fp)

        return product_dict_list

    def download_images(self, product_dict_list, category, sub_category):
        path_img = web_scraper_config.RAW_DATA_PATH + f'/{category}/{sub_category}' + '/images'

        if os.path.exists(path_img) == False:
            os.makedirs(path_img)
            print('image directory has been made')

        a=0

        for item in product_dict_list:
            path  = path_img + f'/{item["product_no"]}_{a}.jpg'
            urllib.request.urlretrieve(item["image_link"], path)
            a+=1
        print('all images have been saved locally')

if __name__ == "__main__":
    web_scrape = Scraper(web_scraper_config.WEBSITE)
    full_scrape_list = web_scrape.run_scrape()
    with multiprocessing.Pool() as pool:
        pool.map(web_scrape.scrape_subcategories, full_scrape_list)