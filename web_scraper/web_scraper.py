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


class Scraper():
    """
    This class is used to scrape item data from clothing stores.
    
    Attributes:
        website (str): The website homepage which is to be scraped
        driver (webdriver): The webdriver function which will allow the program to access the webpage_
    
    """

    global delay
    delay = 20

    def __init__(self, website: str) -> None:
        """
        See help(Scraper) for more information

        
        """
        options = webdriver.ChromeOptions()
        options.add_argument(Driver_Configuration.HEADLESS)
        options.add_argument(Driver_Configuration.USER_AGENT) 
        options.add_argument(Driver_Configuration.USER_AGENT) 
        
        self.driver = webdriver.Chrome(chrome_options=options)
        self.website = website

    def scroll(self) -> None:
        '''
        This function allows the user to scroll a webpage.
        
        Returns:
            None
        '''
        self.driver.execute_script("window.scrollTo(0, 500);")
    
    def browse_next(self) -> webdriver:
        """
        This function allows the user to move from page to page by clicking on the next page button

        Returns:
           self.driver (webdriver): _description_The current webpage so the information is not lost
        """

        self.driver.execute_script("window.scrollTo(0 , document.body.scrollHeight);")
        WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.next_page_xpath)))
        next_page = self.driver.find_element(By.XPATH, Configuration_XPATH.next_page_xpath) 
        next_page.click()
        return self.driver

    def search(self) -> None:
        """
        This function allows the user to search the webpage with a desired search term.

        Returns:
            None
        """

        search_bar = self.driver.find_element(By.XPATH, Configuration_XPATH.search_xpath)
        search_bar.click()
        WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.search_input_xpath)))
        enter_keys = self.driver.find_element(By.XPATH, Configuration_XPATH.search_input_xpath)

        while True:
            search_input = str(input("Enter a search term: "))
            if len(search_input) > 0:
                print(f'.....Program will begin searching for {search_input} ......')
                break
            else:
                print("Please enter a search term")

        enter_keys.send_keys(search_input)
        enter_keys.send_keys(Keys.RETURN)
        print(f'Search for {search_input} has been entered')
    
    def load_and_accept_cookies(self, website: str) -> None:
        """
        This function will wait for the page to load and accept page cookies

        Args:
            website (str): The homepage of the desired website to be scraped.

        Returns:
            None
        """
        self.driver.get(website)
        delay = 20
        try:
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.accept_cookies_xpath)))
            print("Accept Cookies Button is Ready!")
            accept_cookies_button[0].click()
            print("Accept cookies button has been clicked!")
        except TimeoutException:
            print("Loading took too much time!")
    
    def load_and_reject_promotion(self) -> None:
        """
        This function will load promotional pop-ups and close them

        Returns:
            None
        """
        time.sleep(5)
        a=0
        while a < 10:
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.promotion_box)))
                try:
                    WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.wait_for_promotion4_xpath)))
                    reject_promotion_button = self.driver.find_element(By.XPATH, Configuration_XPATH.reject_promotion4_xpath)
                    reject_promotion_button.click()
                    print("Promotion has been closed!")
                    break
                except:
                    try:
                        WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.wait_for_promotion3_xpath)))
                        reject_promotion_button = self.driver.find_element(By.XPATH, Configuration_XPATH.reject_promotion3_xpath)
                        reject_promotion_button.click()
                        print("Promotion has been closed!")
                        break
                    except TimeoutException:
                        print("No promotion pop-up this time!")  
                        
            except:
                a+=1
                continue 
    
    def ask_department(self) -> str:
        """
        This fucntion will ask the department which is desired to be scraped, i.e Men or Women

        Returns:
            department (str): The department which is to be scraped
    
        """

        while True:
            department = str(input("Enter either the Men or Women's department to scrape: ")).lower().capitalize()
            if department == 'Men' or department == 'Women':
                print(f'Program will beginning scraping the {department}s data')
                return department
            else:
                print("Please enter either the Men or Women department")

    def get_categories(self, department: str) -> list:
        """
        This function will take the department and generate of the relevant categories with corresponding links which need to be scraped.

        Args:
            department (str): The departemnt which is to be scraped, i.e Men or Women

        Returns:
            category_dict_list (list): A list which each element contains a dictionary with the main categories
            per department and the links to the category

        """
        WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.DEPARTMENT_XPATH.format(department))))
        department_button = self.driver.find_element(By.XPATH, Configuration_XPATH.DEPARTMENT_XPATH.format(department))
        self.driver.get(department_button.get_attribute('href'))

        # try:
        #     WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.DEPARTMENT_BUTTON_XPATH)))
        #     shop_department_button = self.driver.find_element(By.XPATH, Configuration_XPATH.DEPARTMENT_BUTTON_XPATH)
        #     shop_department_button.click()
        # except: 
        #     pass
        time.sleep(5)

        if len(self.driver.find_elements(By.XPATH, Configuration_XPATH.choose_categories_dropdown_xpath)) >0:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.choose_category_button)))
            category_dropdown = self.driver.find_element(By.XPATH, Configuration_XPATH.choose_category_button)
            category_dropdown.click()
            print('Category dropdown menu clicked')
        else:
            pass

        choose_categories = self.driver.find_elements(By.XPATH, Configuration_XPATH.CHOOSE_CATEGORIES_XPATH)
        category_dict_list = []

        for element in choose_categories:
            category_dict = dict()
            index = int(len(Configuration_XPATH.WEBSITE)) + int(len(department)) + 2
            category_dict["department"] = department
            category_dict["category"] = element.get_attribute('href')[index:-1].replace("-", "_")
            category_dict["link"] = element.get_attribute('href')
            category_dict_list.append(category_dict)
        return category_dict_list
 
    def get_subcategories(self, category_dict_list: list) -> list:
        """
        This function will create a list of all the items to be scraped by creating a list of dicts

        This function takes the input of the categories dict list, visits each category individually and generates dict containing each 
        the relevant department, category, category link, sub-category and the sub-category link. The function will then return this list 
        so each sub-category can be visited individually and scraped for all the respective items.

        Args:
            category_dict_list (list): A list which each element contains a dictionary with the main categories
            per department and the links to the category

        Returns:
            full_scrape_list (list): A list of dicts containing each sub-category name, link and the corresponding category and department data
        """
        full_scrape_list = []
        a=0
        while True:
            if a == 3:
                break
            category_dict = category_dict_list[a]
            self.driver.get(category_dict["link"])
            time.sleep(2)
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.CHOOSE_CATEGORIES_XPATH)))
            choose_subcategories = self.driver.find_elements(By.XPATH, Configuration_XPATH.CHOOSE_SUBCATEGORIES_XPATH)
            
            for element in choose_subcategories:
                full_scrape_dict = dict()
                full_scrape_dict["department"] = category_dict["department"]
                full_scrape_dict["category"] = category_dict["category"]
                full_scrape_dict["category_link"] = category_dict["link"]
                index = int(len(Configuration_XPATH.WEBSITE))+ int(len(category_dict["department"])) +int(len(category_dict["category"])) + 3
                full_scrape_dict["subcategory"] = element.get_attribute('href')[index:-1]
                full_scrape_dict["subcategory_link"] = element.get_attribute('href')
                full_scrape_list.append(full_scrape_dict)
            a+=1
        return full_scrape_list 

    def run_scrape(self) -> None:
        """
        This function ties all the relevant functions needed to scrape the website together

        Returns:
            None

        """
        self.load_and_accept_cookies(Configuration_XPATH.WEBSITE)
        self.load_and_reject_promotion()
        category_dict_list = self.get_categories('Men')
        full_scrape_list = self.get_subcategories(category_dict_list) 
        self.get_subcategories(full_scrape_list)
        print("Website has been scraped")

    def get_subcategories(self, full_scrape_list: list) -> None:
        """
        This function takes the full_scrape_list list of dicts, iterates through the list, visits each dict sub-category data individually
        and scrapes the item data. This function achieves this by calling other functions; first get_links() and then scrape_item_data()

        Args:
            full_scrape_list (list): A list of dicts containing each sub-category name, link and the corresponding category and department data
        """

        for dict in full_scrape_list:
            subcategory_link = dict["subcategory_link"]
            department = dict["department"]
            category = dict["category"]
            subcategory = dict["subcategory"]
            self.driver.get(subcategory_link)
            index = int(len(Configuration_XPATH.WEBSITE)) + int(len(dict["department"])) + int(len(category)) + int(len(subcategory)) + 10
            link_list = self.get_links(index)
            self.scrape_item_data(link_list, department, category, subcategory)
            print(f'All the {subcategory} pages in {category} have been scraped')

    def get_links(self, index :int) -> list:
        """
        This function visits a sub-category and gets a list of all the links to all the items in the subcategory

        Returns:
           link_list (list): A list of links to all the items within a subcategory
        """
        link_list = []
        if len(self.driver.find_elements(By.XPATH, Configuration_XPATH.pagination_xpath)) > 0:
            pagination_xpaths = self.driver.find_elements(By.XPATH, Configuration_XPATH.pagination_xpath)
            pagination = pagination_xpaths[-2].get_attribute('href')
            pagination_no = int(pagination[index:-1]) 
        else:
            pagination_no = 0

        a =0
        if a == pagination_no:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.item_container_xpath)))
            item_container = self.driver.find_element(By.XPATH, Configuration_XPATH.item_container_xpath)
            item_list = item_container.find_elements(By.XPATH, './div')

            for item in item_list:
                a_tag = item.find_element(By.TAG_NAME, 'a')
                _link = a_tag.get_attribute('href')
                link_list.append(_link)
            return link_list
        else:
            while True:

                WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.item_container_xpath)))
                item_container = self.driver.find_element(By.XPATH, Configuration_XPATH.item_container_xpath)
                item_list = item_container.find_elements(By.XPATH, './div')

                for item in item_list:
                    a_tag = item.find_element(By.TAG_NAME, 'a')
                    _link = a_tag.get_attribute('href')
                    link_list.append(_link)
                
                a+= 1
                
                if a == (pagination_no):
                    print("Links on this page have been scraped")
                    return link_list

                paginagion_link = str(pagination[:index]) + f'{a+1}/'    
                self.driver.get(paginagion_link)
            


    def scrape_item_data(self, link_list: list, department: str, category: str, sub_category: str) -> None:
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

        for link in link_list[:1]:
            product_dict = dict()
            self.driver.get(link)
            WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.product_no_xpath)))
            product_dict["product_no"] = self.driver.find_elements(By.XPATH, Configuration_XPATH.product_no_xpath)[0].text
            product_dict["uuid"] = str(uuid.uuid4())
            product_dict["brand"] = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_xpath).text
            product_dict["product_info"] = self.driver.find_element(By.XPATH, Configuration_XPATH.product_info_xpath).text
            product_dict["price"] = WebDriverWait(self.driver, delay).until(AnyEc(EC.presence_of_element_located((By.XPATH,Configuration_XPATH.price_xpath)), EC.presence_of_element_located((By.XPATH, Configuration_XPATH.price_sale_xpath)))).text
            self.scroll()

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

            path = Configuration_XPATH.RAW_DATA_PATH + f'/{department}/{category}/{sub_category}'
            self.create_dir(path)
            item_path = path + f'/{product_dict["product_no"]}'
            self.create_dir(item_path)
            path_img = item_path + '/images'
            self.create_dir(path_img)
            images_list = self.get_images(path_img, product_dict)
            product_dict["image_links"] = images_list
            self.create_json(product_dict, item_path)   

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

if __name__ == "__main__":
    web_scrape = Scraper(Configuration_XPATH.WEBSITE)
    web_scrape.run_scrape()