# Data Collection Pipeline
This projects aim was to create a data collection pipelin centred around obtaining data from a website via a web scraper I would create. 

> ![image](https://user-images.githubusercontent.com/105006854/183435800-ce3ef3ca-d146-4612-9c6b-6a46b0a22c76.png)

## Milestone 1
![image](https://user-images.githubusercontent.com/105006854/183435967-c6f27dfb-9c24-498a-967f-e87deb377aee.png)

This miletone focused around choosing a web site to scrape data, what kind of data would be obtained and what potential challenges could I face. I choose 
Harvey Nichols as this was a clothing store which I liked and thought had an interesting selection of data. Potentially challenges identified were the cookie pop-ups and the promotional pop-up box which would appear after visiting the page. The main data I was interested in getting for each item was the:
 - Product number
 - Product Info
 - Brand
 - Brand Bio
 - Price
 - Size & Fit
 
 ## Milestone 2 
 This milestone focused on creating a general scraoer class which would use the selenium module to open a webpage (in this case Harvey Nichols) and a method which would close the cookie pop-up once on the page. 
 
See below a copy of the accept cookies method:
 
>>> python
``` python
def load_and_accept_cookies(self, website: str) -> None:
        """This function will wait for the page to load and accept page cookies

        Args:
            website (str): The homepage of the desired website to be scraped.

        Returns:
            None
        """
        self.driver.get(website)
        self.delay = 20
        try:
            accept_cookies_button = WebDriverWait(self.driver, self.delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.accept_cookies_xpath)))
            print("Accept Cookies Button is Ready!")
            accept_cookies_button[0].click()
            print("Accept cookies button has been clicked!")
        except TimeoutException:
            print("Loading took too much time!")
```
I also created other methods which would do general things expected when web-browsing. See below a copy of these:

>>> python
``` python
def scroll(self) -> None:
        '''This function allows the user to scroll a webpage.
        
        Returns:
            None
        '''
        self.driver.execute_script("window.scrollTo(0, 500);")
    
    def browse_next(self) -> webdriver:
        """This function allows the user to move from page to page by clicking on the next page button

        Returns:
           self.driver (webdriver): _description_The current webpage so the information is not lost
        """
        self.driver.execute_script("window.scrollTo(0 , document.body.scrollHeight);")
        WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.next_page_xpath)))
        next_page = self.driver.find_element(By.XPATH, Configuration_XPATH.next_page_xpath) 
        next_page.click()
        return self.driver

    def search(self) -> None:
        """This function allows the user to search the webpage with a desired search term.

        Returns:
            None
        """
        search_bar = self.driver.find_element(By.XPATH, Configuration_XPATH.search_xpath)
        search_bar.click()
        WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.search_input_xpath)))
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
```

Another key step in this milestone was to create a method which would be able to get all the links to products on the current webpage and product numbers and store these in a list. I also made sure this method once on a partticular category, would find the total number of pages in the category and iteratively visit each page of products and append these to the list of product links. 

>>> python
``` python
def get_links(self, subcategory:str, department:str) -> List[Dict]:
        """This function visits a sub-category and gets a list of all the links to all the items in the subcategory

        Args:
            subcategory (str): The current subcategory to be scraped
            department (str): The department which is being scraped

        Returns:
           link_list (list): A list of links to all the items within a subcategory
        """
        link_list = []
        time.sleep(2)
        # Checks whether the page length is 1 or more, if more than one will obtain the total number of pages, if 1 then will set the pagination_no to 0
        pagination_tuple = self.get_pagination()
        pagination_no = pagination_tuple[0]
        pagination = pagination_tuple[1]

        a =0
        # If the pagination_no is 0 then will only get the links to the items on the page
        if a == pagination_no:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.item_container_xpath)))
            page_link_list = self.get_page_links()
            link_list += page_link_list
            return link_list
        # If the pagination_no is greater than zero will iterate through the pages and obtain the links on each page.
        else:
            while True:
                WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.item_container_xpath)))
                page_link_list = self.get_page_links()
                link_list += page_link_list
                a+= 1
                # Once reached the final page will stop iterating 
                if a == (pagination_no):
                    print(f"Links on the {department} {subcategory} department pages have been scraped")
                    return link_list

                index = str(pagination).index('=')
                paginagion_link = str(pagination[:index+1]) + f'{a+1}/'    
                self.driver.get(paginagion_link)
```
It was key to ensure this method was as general as possible to allow it to be used on multiple different categories and to be able to also work should the category contain only one page.

I used concepts such as abstraction frequently in the projct for example the get_links() method called two other methods get_page_links() and get_pagination() in order to function. These methods would get the links of the products on a single and retrieve the total number of pages to visit respectively.

>>> python
``` python
def get_page_links(self) -> List[Dict]:
        """Function to get the links on a single page and form into a list.

        Returns:
            page_link_list ( list[dict] ): A list of dictionaries with the link to an item and the items corresponding item number.
        """
        page_link_list = []
        item_container = self.driver.find_element(By.XPATH, Configuration_XPATH.item_container_xpath)
        item_list = item_container.find_elements(By.XPATH, './div')

        for item in item_list:
            link_dict = dict()
            a_tag = item.find_element(By.TAG_NAME, 'a')
            link_dict["link"] = a_tag.get_attribute('href')
            link_dict["product_no"] = a_tag.get_attribute('data-secondid')
            page_link_list.append(link_dict)
        return page_link_list
    
    def get_pagination(self) -> Tuple[int, str]:
        """Will obtain the number of pages to iterate through and the base URL which can be concatenated.

        Returns:
            pagination_no, pagination ( tuple[int, str] ): Will give the pagination_no which is the total number of pages and the pagination
            which is the base URL to be concatenated.
        """
        if len(self.driver.find_elements(By.XPATH, Configuration_XPATH.pagination_xpath)) > 0:
            pagination_xpaths = self.driver.find_elements(By.XPATH, Configuration_XPATH.pagination_xpath)
            pagination = pagination_xpaths[-2].get_attribute('href')
            regex_list = regex.split('/', pagination)
            pagination_no = int(regex_list[-2][5:]) 
        else:
            pagination = ''
            pagination_no = 0    
        return pagination_no, pagination
```

## Milestone 3
This method focused on retrieving the information for each product, storing this data into a dictionary, saving this locally, obtaining any product image links and downloading this image. 

Upon reflection I decided a better way to structure my scraper was to create a second Item_Scraper class which would be more specific to my intended website. The original Scraper class was intended to be very general and be applicable to most websites. 

See the method which would extract the relevant information from each product and turn into a dictionary.

>>> python 
``` python
def scrape_item_data(self) -> Dict:
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
 ```
I also added a feature to the function where it would iteratively try to access the information on the webpage 3 times and if was unsuccessful would move onto the next item. This would ensure the scraper wouldn't just stop if for some reason a particular item link was faulty or did not respond correctly.

The following methods were used to download images and turn the dictionaries into .json files locally:

>>> python 
``` python
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
        
def create_json(self, product_dict: Dict, item_path: str) -> None:
        """The function will create a JSON file for a dictionary in a desired PATH

        Args:
            product_dict (dict): Dictionary of the data for a specfic item
            item_path (str): The PATH where the data for a specified item will be located

        Returns:
            None
        """
        with open(f'{item_path}/data.json', 'w') as fp:
            json.dump(product_dict, fp)
```

## Milestone 4
This milestones focus was on documentation and testing of the scraper. It was important to test the methods in the Item_Scraper class to ensure they were runing fine. The unit testing module was utilised primarily for this. 

It was important to only test the methods which were "public" and private methods would be hidden and should remain so for security reasons. Here is an example of one of the many tests carried out which focused on gettting the product information:

>>> python
``` python
def test_scrape_item_data(self):
        self.item_scraper.load_and_accept_cookies(Configuration_XPATH.WEBSITE)
        self.item_scraper.load_and_reject_promotion()
        self.item_scraper.driver.get(test_case_link)
        product_dict = self.item_scraper.scrape_item_data()

        self.assertTrue(type(product_dict)==dict, msg='scrape_item_data() method returns dict as expected')
        self.assertTrue(product_dict["product_no"] == product_no)
        self.assertTrue(product_dict["brand"] == brand)
        self.assertTrue(product_dict["product_info"] == product_info)
```

This milestone also included adding docstrings to all the functions so that the code was easy to follow and understand to others who were to view it. 


