from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from web_scraper.config import Configuration_XPATH, Driver_Configuration
from typing import List, Dict, Tuple
import time
import regex

class Scraper:
    """
    This class is used to scrape item data from clothing stores.
    
    Attributes:
        website (str): The website homepage which is to be scraped
        driver (webdriver): The webdriver function which will allow the program to access the webpage_
    
    """
    def __init__(self, website: str) -> None:
        """See help(Scraper) for more information
        """
        # The necessary Chrome options to pass to the webdriver. This will configure the webdriver.
        options = webdriver.ChromeOptions()
        options.add_argument(Driver_Configuration.DISABLE_DEV_SHM)
        options.add_argument(Driver_Configuration.NO_SANDBOX)
        options.add_argument(Driver_Configuration.HEADLESS)
        options.add_argument(Driver_Configuration.USER_AGENT) 
        options.add_argument(Driver_Configuration.WINDOW_SIZE) 
        self.driver = webdriver.Chrome(options=options)
        self.website = website
        self.delay = 20
        
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
    
    def load_and_reject_promotion(self) -> None:
        """This function will load promotional pop-ups and close them

        Returns:
            None
        """
        time.sleep(2)
        a=0
        while True:
            # Function will run loop 10 times checking whether the promotion box is up
            if a == 10:
                print("No promotion pop-up this time!")
                break
            try:
                # Will check if a promotion box is up using webdriverwait
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.promotion_box)))
                try:
                    # Checks for promotion 1, if present will close 
                    WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.wait_for_promotion4_xpath)))
                    reject_promotion_button = self.driver.find_element(By.XPATH, Configuration_XPATH.reject_promotion4_xpath)
                    reject_promotion_button.click()
                    print("Promotion has been closed!")
                    break
                except:
                    try:
                        # Will check for promotion 2 if promotion 1 is not present
                        WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.wait_for_promotion3_xpath)))
                        reject_promotion_button = self.driver.find_element(By.XPATH, Configuration_XPATH.reject_promotion3_xpath)
                        reject_promotion_button.click()
                        print("Promotion has been closed!")
                        break
                    except TimeoutException:
                        a+=1         
            except:
                a+=1
                continue 
    
    def get_categories(self, department:str) -> List[Dict]:
        """This function will take the department and generate of the relevant categories with corresponding links which need to be scraped.

        Args:
            department (str): The departemnt which is to be scraped, i.e Men, Women or Kids

        Returns:
            category_dict_list (list): A list which each element contains a dictionary with the main categories
            per department and the links to the category
        """
        WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.DEPARTMENT_XPATH.format(department))))
        department_button = self.driver.find_element(By.XPATH, Configuration_XPATH.DEPARTMENT_XPATH.format(department))
        self.driver.get(department_button.get_attribute('href'))
        print(f'Scraper has clicked on the {department} department.')
        time.sleep(5)

        # Function will check if there is a second button to press depending on the department which is clicked
        self.locate_department_page(department)
            
        # Will check if the category department dropdown is open, if not will click it to open it.
        self.category_dropdown()

        # Will set the categories links to a list
        choose_categories = self.driver.find_elements(By.XPATH, Configuration_XPATH.CHOOSE_CATEGORIES_XPATH)
        category_dict_list = []

        # Iterates through the list of category xpaths and obtains a list of dicts with the category name and link
        for element in choose_categories:
            category_dict = dict()
            category_dict["department"] = department
            regex_list = regex.split('/', element.get_attribute('href')) 
            category_dict["category"] = regex_list[-2].replace("-", "_")
            category_dict["link"] = element.get_attribute('href')
            category_dict_list.append(category_dict)
        return category_dict_list

    def get_subcategories_links(self, category_dict_list: List) -> List[Dict]:
        """This function will create a list of all the items to be scraped by creating a list of dicts

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
            # Function will iterate 3 times through the categories, visit each category link and obtain xpath list of categories
            if a == 3:
                break
            category_dict = category_dict_list[a]
            self.driver.get(category_dict["link"])
            time.sleep(2)
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.CHOOSE_CATEGORIES_XPATH)))
            choose_subcategories = self.driver.find_elements(By.XPATH, Configuration_XPATH.CHOOSE_SUBCATEGORIES_XPATH)
            # Will iterate through the xpath list of categories and create a dict with subcategory name, link and category link, name and department
            for element in choose_subcategories:
                full_scrape_dict = dict()
                full_scrape_dict["department"] = category_dict["department"]
                full_scrape_dict["category"] = category_dict["category"]
                full_scrape_dict["category_link"] = category_dict["link"]
                regex_list = regex.split('/', element.get_attribute('href'))
                full_scrape_dict["subcategory"] = regex_list[-2].replace("-", "_")
                full_scrape_dict["subcategory_link"] = element.get_attribute('href')
                full_scrape_list.append(full_scrape_dict)
            a+=1
        return full_scrape_list 

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

    def locate_department_page(self, department:str) -> None:
        """Will navigate to the correct department page if not currently on that page.

        Args:
            department (str): The department which is being scraped

        Returns:
            None
        """
        if len(self.driver.find_elements(By.XPATH, Configuration_XPATH.DEPARTMENT_BUTTON_XPATH))>0:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_all_elements_located((By.XPATH, Configuration_XPATH.DEPARTMENT_BUTTON_XPATH)))
            shop_department_button = self.driver.find_elements(By.XPATH, Configuration_XPATH.DEPARTMENT_BUTTON_XPATH)
            try:
                # If kids department is clicked will locate the unisex department button.
                shop_department_button[3].click()
                print(f'The {department} department button has been clicked.')
                time.sleep(2)
            except: 
                # Otherwise will click on the department button.
                shop_department_button[0].click()
                print(f'The {department} department button has been clicked.')
                time.sleep(2)
        else:
            pass
        
    def category_dropdown(self) -> None:
        """Will click the category dropdown button to display categories if categories are not currently being shown.

        Returns:
            None
        """
        if len(self.driver.find_elements(By.XPATH, Configuration_XPATH.choose_categories_dropdown_xpath)) >0:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, Configuration_XPATH.choose_category_button)))
            category_dropdown = self.driver.find_element(By.XPATH, Configuration_XPATH.choose_category_button)
            category_dropdown.click()
            print('Category dropdown menu clicked')
        else:
            pass
    
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

    def ask_department(self) -> str:
        """This fucntion will ask the department which is desired to be scraped, i.e Men or Women

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