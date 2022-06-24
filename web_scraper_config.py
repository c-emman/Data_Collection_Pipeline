WEBSITE = "https://www.harveynichols.com/"
next_page_xpath = '//*[@class="pagination__arrow pagination__arrow--right"]'
search_xpath = '//span[@class="nav-search__trigger-icon"]'
search_input_xpath = '//input[@id="search-input"]'
accept_cookies_xpath = '//*[@class="cookie-notice__button bttn bttn--grey-3"]'
wait_for_promotion1_xpath = '//*[@id="bx-element-1290300-9cZauvB"]'
reject_promotion1_xpath = '//*[@id="bx-element-1290300-9cZauvB"]//button'
wait_for_promotion2_xpath = '//*[@id="bx-element-1671444-vAAMitb"]'
reject_promotion2_xpath = '//*[@id="bx-element-1671444-vAAMitb"]//button'
item_container_xpath = '//div[@class="items__list"]'
product_no_xpath = '//*[@class="sku-style-number"]//span'
brand_xpath = '//div[@class="p-details__content"]//a'
product_info_xpath = '//div[@class="p-details__name-wrap"]//p'
price_xpath = '//p[@class="product-price__regular  price"]'
size_and_fit_xpath = '//div[@class="long-text p-more-info__html p-more-info__html--infocare"]'
brand_bio_xpath = '//div[@class="long-text p-more-info__html p-more-info__html--brandbio"]'
image_link_xpath = '//img[@class="p-images__preview-image"]'
RAW_DATA_PATH = '/home/christian/Desktop/web_scraper_project/raw_data'
IMG_PATH = '/home/christian/Desktop/web_scraper_project/raw_data/images'
DEPARTMENT_XPATH = '//a[@class="nav-cats__link nav-cats__link--lv1"][@data-dept="{}"]'
DEPARTMENT_BUTTON_XPATH = '//a[@class="cms-buttons__button link link--button link--grey-3"]'
CHOOSE_CATEGORIES_XPATH = '//div[@class="filter-group__content filter-group__content--open"]//a'
CHOOSE_SUBCATEGORIES_XPATH = '//section[@class="filter-group pr-filter-group-categories"]//ul[@class="filter-group__list"]//a'
HEADING_INFO_ACTIVE_XPATH = '//h4[@class="p-more-info__heading p-more-info__heading--active"]'
SIZE_AND_FIT_INACTIVE_XPATH = '//h4[@class="p-more-info__heading "][text()="Size & Fit"]'
BRAND_BIO_INACTIVE_XPATH = '//h4[@class="p-more-info__heading "][text()="Brand Bio"]'
price_sale_xpath = '//p[@class="product-price__old  "]'

class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                res = fn(driver)
                if res:
                    return res
                    # Or return res if you need the element found
            except:
                pass