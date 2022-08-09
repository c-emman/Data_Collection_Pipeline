from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from web_scraper.config import AnyEc, Configuration_XPATH, Db_Config, S3_Config
from web_scraper.scraper import Scraper
import tempfile
import argparse
import sqlalchemy
import boto3
import uuid
import os
import json
import urllib.request


class Item_Scraper(Scraper):

    def __init__(self, *args, **kwargs) -> False:

        super().__init__(*args, **kwargs)
        self.link_list = list()
        self.department = str()
        self.category = str()
        self.subcategory = str()
        # Sets the S3 client connection and credentials
        self.bucketname = 'chris-aircore-s3bucket'
        self.s3_client = boto3.client('s3', region_name=S3_Config.REGION, aws_access_key_id=S3_Config.ACCESS_KEY, aws_secret_access_key=S3_Config.SECRET_KEY)
        self.s3_resource = boto3.resource('s3', region_name=S3_Config.REGION, aws_access_key_id=S3_Config.ACCESS_KEY, aws_secret_access_key=S3_Config.SECRET_KEY)
        self.s3_bucket = self.s3_resource.Bucket(self.bucketname)
        # Sets the optional arguments to pass to the scraper to scrape a specific category, whether to save locally or on the cloud and the maximum number 
        # of items to scrape
        self.parser = argparse.ArgumentParser(description='Item Scraper class which will scrape products from website.')
        self.parser.add_argument( "-m", "--men", help='Scrape only the Mens department.', default=False, action='store_true')
        self.parser.add_argument("-w", "--women", help='Scrape only the Womens department.', default=False, action='store_true')
        self.parser.add_argument("-k", "--kids", help='Scrape only the Kids department.', default=False, action='store_true')
        self.parser.add_argument("-l", "--locally", help='Save scraped data on local machine only.', default=False, action='store_true')
        self.parser.add_argument("-c", "--cloud", help='Upload data to S3 and AWS RDS only.', default=False, action='store_true')
        self.parser.add_argument("-n", "--number", help='Maximum number of items per category to scrape.', default=20, action='store')
        self.args = self.parser.parse_args()
        self.list_max = int(self.args.number)
        self.flag = False
        # If locally isn't selected sets the connection to the AWS RDS PostgreSQL Database
        if self.args.locally is False:
            self.engine = sqlalchemy.create_engine(f'{Db_Config.DATABASE_TYPE}+{Db_Config.DBAPI}://{Db_Config.USER}:{Db_Config.PASSWORD}@{Db_Config.ENDPOINT}:{Db_Config.PORT}/{Db_Config.DATABASE}')
        # Sets the list of items to scrape on the cloud
        self.products_scraped_cloud = list()
        self.images_scraped_cloud = list()
        self.dep_list = Configuration_XPATH.DEP_LIST
        if self.args.men is True:
            self.dep_list = [Configuration_XPATH.DEP_LIST[0]]
            print('Will scrape only the Mens department.')
        elif self.args.women is True:
            self.dep_list = [Configuration_XPATH.DEP_LIST[1]]
            print('Will scrape only the Womens department.')
        elif self.args.kids is True:
            self.dep_list = [Configuration_XPATH.DEP_LIST[2]]
            print('Will scrape only the Kids department.')
        else:
            print('Will scrape Mens, Womens and Kids departments.')
        
        if self.args.cloud is True:
            print('Documents will save to AWS S3 and RDS only.')
        elif self.args.locally is True:
            print('Documents will save locally only.')
        else:
            print('Documents will be saved both locally and on AWS cloud.')
        
        print(f'Scraper will scrape {self.list_max} items per category')

    def run_full_scrape(self) -> None:
        """
        This function runs the full scrape of the website of interest.

        Return:
            None
        """
        self.load_and_accept_cookies(Configuration_XPATH.WEBSITE)
        self.load_and_reject_promotion()    
        # Iterates through the list of departments to scrape
        for i in range(len(self.dep_list)):
            department = self.dep_list[i]
            self.department = department
            # If locally is False will connect to the RDS Database and create a schema for the department
            if self.args.locally is False:
                self.engine.execute(f'''CREATE SCHEMA IF NOT EXISTS {self.department}_data''')
                print(f'The {self.department}_data schema has been made')
            category_dict_list = self.get_categories(self.department)
            full_scrape_list = self.get_subcategories_links(category_dict_list) 
            self.run_subcategory_scrape(full_scrape_list)
            print(f"{self.department} department has been scraped")
    
    def run_subcategory_scrape(self, full_scrape_list) -> None:
        """
        This function runs a full scrape of a particular subcategory on the website of interest

        Args:
            full_scrape_list (list): A list of dicts containing each sub-category name, link and the corresponding category and department data

        Return:
            None
        """
        # Will iterate through the full_scrape_list to scrape the data
        for full_scrape_dict in full_scrape_list:
            subcategory_link = full_scrape_dict["subcategory_link"]
            self.category = full_scrape_dict["category"]
            self.subcategory = full_scrape_dict["subcategory"]
            self.driver.get(subcategory_link)
            self.link_list = self.get_links(self.subcategory, self.department)
            self.max_items = min(self.list_max, len(self.link_list))
            # Will create a table in the RDS Database if it doesn't exist
            if self.args.locally is False:
                self.engine.execute(f'''CREATE TABLE IF NOT EXISTS {self.department}_data.{self.subcategory} (
                                            uuid VARCHAR(36) PRIMARY KEY,
                                            product_no VARCHAR(8) NOT NULL,
                                            brand VARCHAR(30), 
                                            product_info VARCHAR(100),
                                            price FLOAT NOT NULL,
                                            size_and_fit VARCHAR(1000),
                                            brand_bio VARCHAR(2000),
                                            image_links VARCHAR(1000)
                                            );''')
                print(f'The {self.subcategory} table in the {self.department}_data schema has been made.')
                # Gets the products already in the Databse and creates a list of the products already scraped
                result = self.engine.execute(f'''SELECT product_no FROM {self.department}_data.{self.subcategory}''')
                for product_no in result:
                    self.products_scraped_cloud.append(str(product_no).replace("(", "").replace(")", "").replace(",", "").replace("'", ""))
            self.run_item_scrape()
            print(f"{self.subcategory} links in the {self.department}'s department have been retrieved")

    def run_item_scrape(self) -> None:
        """
        This function runs an scrape on a list of items provided. 

        Return:
            None
        """
        for link in self.link_list[:self.max_items]:
            # Checks whether the product to be scraped has already been added to the Database, if so then will move onto the next product
            if self.args.locally is False:
                if link["product_no"] in self.products_scraped_cloud:
                    print(f'Product information for item {link["product_no"]} has already been scraped')
                    continue
            self.driver.get(link["link"])
            product_dict = self.scrape_item_data()
            product_dict["product_no"] = link["product_no"]
            if self.flag == True:
                continue
            path_tuple = self.item_scrape_mkdirs(product_dict)
            path_img = path_tuple[0]
            item_path = path_tuple[1]
            images_tuple = self.get_images(path_img, product_dict)
            images_list = images_tuple[0]
            images_link_list = images_tuple[1]
            product_dict["image_links"] = images_list
            if self.args.locally is False:
                if_scraped = self.check_on_s3_json(product_dict)
                # If no optional argument for storage selected will default save both locally and on cloud
                if self.args.cloud is False:
                    self.create_json(product_dict, item_path)
                    print(f'...Saving .json file locally for product: {product_dict["product_no"]}...')
                    if if_scraped == True:
                        print(f'Product: {product_dict["product_no"]} .json file has already been uploaded to S3')
                        continue
                    self.upload_data_s3(f'{item_path}/data.json', self.bucketname, f'{product_dict["product_no"]}.json')
                    print(f'...Uploading .json file for product: {product_dict["product_no"]} to S3...')
                # If cloud argument is seleced will upload data directly to AWS
                if self.args.cloud is True:
                    if if_scraped == True:
                        print(f'Product: {product_dict["product_no"]} .json file has already been uploaded to S3')
                        continue
                    self.s3_client.put_object(Body=json.dumps(product_dict), Bucket=self.bucketname, Key=f'{product_dict["product_no"]}.json')
                    print(f'...Uploading .json file for product {product_dict["product_no"]} directly to S3...')
                # Will upload the data to RDS databse
                table_insert = self.clean_product_data(product_dict, images_link_list)
                self.engine.execute(sqlalchemy.text(f'''INSERT INTO {self.department}_data.{self.subcategory}(uuid, product_no, brand, product_info, price, size_and_fit, brand_bio, image_links) VALUES{table_insert}'''))
                print(f'...Inserting the data into the PostgreSQL AWS RDS database in the {self.department}_data.{self.subcategory} table for product: {product_dict["product_no"]}...')   
            else:
                self.create_json(product_dict, item_path)
                print(f'...Saving .json file locally for product: {product_dict["product_no"]}...')    
        print(f"All the {self.subcategory} data in the {self.department}'s department has been scraped.")
        
    def scrape_item_data(self) -> dict:
        """
        This function scrapes the data for an individual item into a dict

        Returns:
            product_dict (dict): Dictionary of the product details which have been scraped
        """
        product_dict = dict()
        a = 0
        # Will run loop on data 3 times to check whether page has loaded
        while True:
            # If not able to scrape after loops will move onto next record
            if a == 3:
                print(f'Item page did not load. Unable to scrape item data for item in {self.department} {self.subcategory} department.')
                self.flag =  True
                return product_dict
            try:
                # Creates a dict of the relevant item data to be scraped
                WebDriverWait(self.driver, self.delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.product_no_xpath)))
                product_dict["uuid"] = self.get_uuid()     
                product_dict["brand"] = self.get_brand()
                product_dict["product_info"] = self.get_product_info()
                product_dict["price"] = self.get_price()
                self.driver.execute_script("window.scrollTo(0, 500);")
                product_dict["size_and_fit"] = self.get_size_and_fit()
                product_dict["brand_bio"] = self.get_brand_bio() 
                return product_dict
            except TimeoutException:
                a+=1

    def clean_product_data(self, product_dict: dict, images_link_list: list) -> str:
        """A function which cleans the data from the product_dict to allow it to be uploaded to AWS RDS PostgreSQL

        Args:
            product_dict (dict): Dictionary of the product details which have been scraped
            images_link_list (list): A list containing the links to images of the product

        Returns:
            table insert (str): A str of the cleaned data which can be inserted into the Database via SQL
        """
        value_1 = f"'{product_dict['uuid']}'"
        value_2 = f"'{product_dict['product_no']}'"
        tranform_3 = product_dict['brand'].replace("'s", "s").replace("'", ".")
        value_3 = f"'{tranform_3}'"
        transform_4 = product_dict['product_info'].replace("'s", "s").replace("'", ".")
        value_4 = f"'{transform_4}'"
        value_5 = float(product_dict['price'][1:].replace(",", "").replace("\u200c", ""))
        if 'size_and_fit' in product_dict:
            transform_6 = product_dict['size_and_fit'].replace("'s", "s").replace("'", ".")
            value_6 = f"'{transform_6}'"
        else:
            value_6 = "''"
        if 'brand_bio' in product_dict:
            transform_7 = product_dict['brand_bio'].replace("'s", "s").replace("'", ".")
            value_7 = f"'{transform_7}'"
        else:
            value_7 = "''"
        transform_8 = str(images_link_list).replace("'", "*")
        value_8 = f"'{transform_8}'"
        table_insert = f'({value_1}, {value_2}, {value_3}, {value_4}, {value_5}, {value_6}, {value_7}, {value_8})'
        return table_insert
    
    def get_images(self, path_img: str, product_dict: dict) -> tuple[ list[dict], list]:
        """The function will get all the images for an item and call a function to download the image

        Args:
            path_img (str): The PATH for the /images directory within the specified item directory
            product_dict (dict): Dictionary of the data for a specfic item.

        Returns:
            images_list (list): A list of dicts for the image links for a specific item and the corresponding image name.
            images_link_list (list): A list of links to the images.
        """
        # Obtains list of xpaths to images
        images_list = []
        images_link_list = []
        images_xpath = self.driver.find_elements(By.XPATH, Configuration_XPATH.images_xpath)

        a = 1 # Counter for pictures used for naming the picture
        b = 0 # Counter for how many pictures were uploaded to S3
        c = 0 # Counter for how many pictures were saved  locally
        # Iterates through the list of images xpaths
        for image in images_xpath:
            # Creates the images dict with the image name and the link to the corresponding image
            self.images_scraped_cloud = list()
            image_dict = dict()
            img_name = path_img + str(f'/{product_dict["product_no"]}_{a}')
            image_dict["image_no"] = str(f'{product_dict["product_no"]}_{a}')
            image_dict["link"] = image.get_attribute('src')
            images_link_list.append(image.get_attribute('src'))
            images_list.append(image_dict)
            # If not specified to cloud then will download images and upload to S3 if product no in list of items already scraped.
            if self.args.cloud is False:
                if os.path.exists(img_name) == False:
                    self.download_images(image_dict["link"], img_name)
                    c += 1
                else:
                    print('Image has already been saved locally')

                if_scraped = self.check_on_s3_images(product_dict, image_dict)
                if if_scraped == True:
                    continue
                self.upload_data_s3(f'{img_name}.jpg', self.bucketname, f'{image_dict["image_no"]}.jpg')
                b += 1
            # If cloud is specified then will create a temporary directory download image, upload to S3 then close the temporary directory
            else:
                if_scraped = self.check_on_s3_images(product_dict, image_dict)
                if if_scraped == True:
                    continue
                self.cloud_image_download(product_dict, image_dict, a)
                b += 1
            a+=1
        if self.args.locally is False:
            print(f'{b} images for product: {product_dict["product_no"]} have been uploaded to S3')
        if self.args.cloud is False:
            print(f'{c} images for product: {product_dict["product_no"]} have been saved locally')
        return images_list, images_link_list

    def cloud_image_download(self, product_dict: dict, image_dict: dict, a:int):
        """Will directly download an image to AWS S3 and not save permanently to locall device

        Args:
            product_dict (dict): Dictionary of the product details which have been scraped
            image_dict (dict): Dictionary of image name and links for a product
            a (int): The image number of a specific image
        """
        with tempfile.TemporaryDirectory() as tempdir:
            self.download_images(image_dict["link"], f'{tempdir}/{product_dict["product_no"]}_{str(a)}')
            tempdir_img = f'{tempdir}/{product_dict["product_no"]}_{str(a)}'
            self.upload_data_s3(f'{tempdir_img}.jpg', self.bucketname, f'{image_dict["image_no"]}.jpg')
    
    def check_on_s3_images(self, product_dict: dict, image_dict: dict) -> bool:
        """Will visit S3 and check whether the image has been put on S3

        Args:
            product_dict (dict): Dictionary of the product details which have been scraped
            image_dict (dict): 

        Returns:
            bool
        """
        self.update_s3_key_list(product_dict)

        if f'{image_dict["image_no"]}.jpg' in self.images_scraped_cloud:
            print(f'Product: {image_dict["image_no"]} image has already been uploaded to S3')
            return True
        else:
            return False

    def check_on_s3_json(self, product_dict: dict) -> bool:
        """Will visit S3 and check whether the .json has been put on S3

        Args:
            product_dict (dict): Dictionary of the product details which have been scraped

        Returns:
            bool
        """
        self.update_s3_key_list(product_dict)

        if f'{product_dict["product_no"]}.json' in self.images_scraped_cloud:
            print(f'Product: {product_dict["product_no"]} .json file has already been uploaded to S3')
            return True
        else:
            return False
    
    def update_s3_key_list(self, product_dict: dict):
        """Will update the list of the keys of objects in S3

        Args:
            product_dict (dict): _description_
        """
        objects = self.s3_bucket.objects.filter(Prefix=f'{product_dict["product_no"]}')
        for object in objects:
            self.images_scraped_cloud.append(object.key)

    def item_scrape_mkdirs(self, product_dict: dict):
        path = Configuration_XPATH.RAW_DATA_PATH + f'/{self.department}/{self.category}/{self.subcategory}'
        self.create_dir(path)
        item_path = path + f'/{product_dict["product_no"]}'
        self.create_dir(item_path)
        path_img = item_path + '/images'
        self.create_dir(path_img)
        return path_img, item_path

    def create_dir(self, PATH: str) -> None:
        """This function will create a directory which does not exist

        Args:
            PATH (str): The desired PATH to create the directory

        Return:
            None
        """
        if self.args.cloud is False:
            if os.path.exists(PATH) == False:
                os.makedirs(PATH)

    def create_json(self, product_dict: dict, item_path: str) -> None:
        """The function will create a JSON file for a dictionary in a desired PATH

        Args:
            product_dict (dict): Dictionary of the data for a specfic item
            item_path (str): The PATH where the data for a specified item will be located

        Returns:
            None
        """
        with open(f'{item_path}/data.json', 'w') as fp:
            json.dump(product_dict, fp)

    def download_images(self, image_link: str, img_name: str) -> None:
        """This function downloads an image from a URL

        Args:
            image_link (str): The link to the image to be downloaded
            img_name (str): The reference name for the image

        Returns:
            None
        """
        path  = img_name + '.jpg'
        urllib.request.urlretrieve(image_link, path)

    def upload_data_s3(self, filename, bucketname, object_name) -> None:
        """A function which uploads an object to the AWS S3 bucket.

        Args:
            filename (str): The filename on the local machine
            bucketname (str): The name of the S3 bucket where the object is to be dumped
            object_name (str): The name to save the object as.
        
        Returns:
            None
        """
        self.s3_client.upload_file(filename, bucketname, object_name)    
        
    def get_uuid(self) -> str:
        """Function to generate a unique user id number

        Returns:
            product_uuid (str): The unique user id
        """
        product_uuid = str(uuid.uuid4())
        return product_uuid

    def get_brand(self) -> str:
        """Function to return the brand of a product

        Returns:
            brand (str): The product brand
        """
        brand  = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_xpath).text
        return brand

    def get_product_info(self) -> str:
        """Function which gets a description of the product information

        Returns:
            product_info (str): The product information
        """
        product_info = self.driver.find_element(By.XPATH, Configuration_XPATH.product_info_xpath).text
        return product_info

    def get_price(self) -> str:
        """Function which gets the product price.

        Returns:
            price (str): The product price
        """
        price = WebDriverWait(self.driver, self.delay).until(AnyEc(EC.presence_of_element_located((By.XPATH,Configuration_XPATH.price_xpath)), EC.presence_of_element_located((By.XPATH, Configuration_XPATH.price_sale_xpath)))).text
        return price
    
    def get_size_and_fit(self) -> str:
        """Function to get the size & fit description of a product

        Returns:
            size_and_fit (str): A description of the size and fit of a product 
        """
        # First checks whether the size & fit category has been selected, if so will save the data. 
        if self.driver.find_element(By.XPATH, Configuration_XPATH.HEADING_INFO_ACTIVE_XPATH).text.lower() == "size & fit":
            size_and_fit = self.driver.find_element(By.XPATH, Configuration_XPATH.size_and_fit_xpath).text    
        else:
            # If has not been selected will click on the size & fit and scrape the data. If there is no size & fit will set to None
            try:
                WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.SIZE_AND_FIT_INACTIVE_XPATH)))
                size_and_fit_button = self.driver.find_element(By.XPATH, Configuration_XPATH.SIZE_AND_FIT_INACTIVE_XPATH)
                size_and_fit_button.click()
                size_and_fit = self.driver.find_element(By.XPATH, Configuration_XPATH.size_and_fit_xpath).text
            except:
                size_and_fit = ''
        return size_and_fit

    def get_brand_bio(self) -> str:
        """Function which gets the brand bio information for a product should it exist

        Returns:
            brand_bio (str): A str of the brand bio of a product
        """
        # First checks whether the brand bio category has been selected, if so will save the data. 
        if self.driver.find_element(By.XPATH, Configuration_XPATH.HEADING_INFO_ACTIVE_XPATH).text.lower() == "brand bio":
            brand_bio = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_bio_xpath).text   
        else:
            # If has not been selected will click on the brand bio and scrape the data. If there is no brand bio will set to None
            try:
                WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.BRAND_BIO_INACTIVE_XPATH)))
                brand_bio_button =  self.driver.find_element(By.XPATH, Configuration_XPATH.BRAND_BIO_INACTIVE_XPATH)
                brand_bio_button.click()
                brand_bio = self.driver.find_element(By.XPATH, Configuration_XPATH.brand_bio_xpath).text
            except:
                brand_bio = ''
        return brand_bio