from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from web_scraper_config import AnyEc, Configuration_XPATH, Driver_Configuration
import concurrent.futures as cf
import multiprocessing
import itertools
import time
import uuid
import os
import json
import urllib.request

class Item_Scraper:

    global delay
    delay = 20
    def __init__(self, link_list: list, department: str, category: str, sub_category: str) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument(Driver_Configuration.HEADLESS)
        options.add_argument(Driver_Configuration.USER_AGENT) 
        options.add_argument(Driver_Configuration.USER_AGENT) 
        self.driver = webdriver.Chrome(chrome_options=options)
        self.link_list = link_list
        self.department = department
        self.category = category
        self.sub_category = sub_category
        self.max_items = min(1, len(link_list))
        pass

    def run_item_scrape(self):

        for link in self.link_list[:self.max_items]:
            self.driver.get(link)
            path = Configuration_XPATH.RAW_DATA_PATH + f'/{self.department}/{self.category}/{self.sub_category}'
            self.create_dir(path)
            product_dict = self.scrape_item_data()
            item_path = path + f'/{product_dict["product_no"]}'
            self.create_dir(item_path)
            path_img = item_path + '/images'
            self.create_dir(path_img)
            images_list = self.get_images(path_img, product_dict)
            product_dict["image_links"] = images_list
            self.create_json(product_dict, item_path)   
        print(f"All the {self.sub_category} data in the {self.department}'s department has been scraped.")
        

    def scrape_item_data(self) -> dict:
        """
        This function scrapes the data for an individual item into a dict and saves that dict as a json file

        Args:
            link_list (list): A list of links to all the items within a subcategory
            department (str): The department which is being scraped
            category (str): The category the item is located in
            sub_category (str): The sub-category the item is located in

        Returns:
            None
        """
        product_dict = dict()
        WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.product_no_xpath)))
        product_dict["product_no"] = self.driver.find_elements(By.XPATH, Configuration_XPATH.product_no_xpath)[0].text
        product_dict["uuid"] = str(uuid.uuid4())
        product_dict["brand"] = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_xpath).text
        product_dict["product_info"] = self.driver.find_element(By.XPATH, Configuration_XPATH.product_info_xpath).text
        product_dict["price"] = WebDriverWait(self.driver, delay).until(AnyEc(EC.presence_of_element_located((By.XPATH,Configuration_XPATH.price_xpath)), EC.presence_of_element_located((By.XPATH, Configuration_XPATH.price_sale_xpath)))).text
        self.driver.execute_script("window.scrollTo(0, 500);")
        if self.driver.find_element(By.XPATH, Configuration_XPATH.HEADING_INFO_ACTIVE_XPATH).text.lower() == "size & fit":
            product_dict["size_and_fit"] = self.driver.find_element(By.XPATH, Configuration_XPATH.size_and_fit_xpath).text    
        else:
            try:
                WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.SIZE_AND_FIT_INACTIVE_XPATH)))
                size_and_fit_button = self.driver.find_element(By.XPATH, Configuration_XPATH.SIZE_AND_FIT_INACTIVE_XPATH)
                size_and_fit_button.click()
                product_dict["size_and_fit"] = self.driver.find_element(By.XPATH, Configuration_XPATH.size_and_fit_xpath).text
            except:
                pass
        
        if self.driver.find_element(By.XPATH, Configuration_XPATH.HEADING_INFO_ACTIVE_XPATH).text.lower() == "brand bio":
            product_dict["brand_bio"] = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_bio_xpath).text   
        else:
            try:
                WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.BRAND_BIO_INACTIVE_XPATH)))
                brand_bio_button =  self.driver.find_element(By.XPATH, Configuration_XPATH.BRAND_BIO_INACTIVE_XPATH)
                brand_bio_button.click()
                product_dict["brand_bio"] = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_bio_xpath).text
            except:
                pass

        return product_dict
      
    def get_images(self, path_img: str, product_dict: dict) -> list:
        """
        The function will get all the images for an item and call a function to download the image

        Args:
            path_img (str): The PATH for the /images directory within the specified item directory
            product_dict (dict): Dictionary of the data for a specfic item.

        Returns:
            images_list (list): A list of the image links for a specific item.
        """
        images_list = []
        images_xpath = self.driver.find_elements(By.XPATH, Configuration_XPATH.images_xpath)

        a = 1
        for image in images_xpath:
            image_dict = dict()
            image_dict["image_no"] = str(f'{product_dict["product_no"]}_{a}')
            image_dict["link"] = image.get_attribute('src')
            img_name = path_img + str(f'/{product_dict["product_no"]}_{a}')
            images_list.append(image_dict)
            self.download_images(image_dict["link"], img_name)
            a+=1
        
        return images_list

    def create_dir(self, PATH: str) -> None:
        """
        This function will create a directory which does not exist

        Args:
            PATH (str): The desired PATH to create the directory

        Return:
            None
        """
        if os.path.exists(PATH) == False:
                os.makedirs(PATH)

    def create_json(self, product_dict: dict, item_path: str) -> None:
        """
        The function will create a JSON file for a dictionary in a desired PATH

        Args:
            product_dict (dict): Dictionary of the data for a specfic item
            item_path (str): The PATH where the data for a specified item will be located

        Returns:
            None
        """
        with open(f'{item_path}/data.json', 'w') as fp:
            json.dump(product_dict, fp)

    def download_images(self, image_link: str, img_name: str) -> None:
        """
        This function downloads an image from a URL

        Args:
            image_link (str): The link to the image to be downloaded
            img_name (str): The reference name for the image
        """
        path  = img_name + '.jpg'
        urllib.request.urlretrieve(image_link, path)