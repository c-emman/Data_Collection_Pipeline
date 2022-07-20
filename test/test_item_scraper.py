from web_scraper.item_scraper import Item_Scraper
from web_scraper import scraper
import os
import unittest

from web_scraper.config import Configuration_XPATH


class Item_ScraperTestCase(unittest.TestCase):

    global test_case_link, product_no, brand, product_info, last_image_link
    test_case_link = 'https://www.harveynichols.com/brand/givenchy/493639-x-josh-smith-leather-and-wool-blend-bomber-jacket/p4288484/'
    product_no = "SC493639"
    brand = "GIVENCHY"
    product_info = "X Josh Smith leather and wool-blend bomber jacket"
    last_image_link = "https://m.hng.io/catalog/product/8/9/895580_burgundy_5.jpg?io=PDP_THUMB"

    def setUp(self) -> None:
        self.item_scraper = Item_Scraper(Configuration_XPATH.WEBSITE)
        return super().setUp()
    
    def test_scrape_item_data(self):
        self.item_scraper.load_and_accept_cookies(Configuration_XPATH.WEBSITE)
        self.item_scraper.load_and_reject_promotion()
        self.item_scraper.driver.get(test_case_link)
        product_dict = self.item_scraper.scrape_item_data()

        self.assertTrue(type(product_dict)==dict, msg='scrape_item_data() method returns dict as expected')
        self.assertTrue(product_dict["product_no"] == product_no)
        self.assertTrue(product_dict["brand"] == brand)
        self.assertTrue(product_dict["product_info"] == product_info)


    def test_get_images(self):
        self.item_scraper.load_and_accept_cookies(Configuration_XPATH.WEBSITE)
        self.item_scraper.load_and_reject_promotion()
        self.item_scraper.driver.get(test_case_link)
        product_dict = dict()
        product_dict["product_no"] = product_no
        PATH = os.getcwd()
        images_list = self.item_scraper.get_images(PATH, product_dict)

        self.assertTrue(type(images_list) == list)
        self.assertEqual(len(images_list), 5, msg='The correct number of images were scraped')
        self.assertEqual(images_list[4]["link"], last_image_link, msg='Random image scraped matches the intended image link')

    def test_create_json(self):
        product_dict = dict()
        PATH = os.getcwd()
        self.item_scraper.create_json(product_dict, PATH)
        if os.path.exists(PATH + '/data.json') == False:
            result = False
        else:
            result = True

        self.assertTrue(result == True, 'data.json file was created.')

    def test_download_images(self):
        PATH = os.getcwd()
        self.item_scraper.download_images(last_image_link, PATH)
        if os.path.exists(PATH + '.jpg') == False:
            result = False
        else:
            result = True

        self.assertTrue(result == True, '.jpg image was saved.')

    def tearDown(self) -> None:
        del self.item_scraper
        return super().tearDown()

if __name__ == '__main__':
    unittest.main(verbosity=2)