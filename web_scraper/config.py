class Configuration_XPATH:
    """
    A configuration class which stores all the relevant XPATH data for the desired website.

    """
    def __init__(self) -> None:
        pass

    WEBSITE = "https://www.harveynichols.com/"
    DEP_LIST = ['Men', 'Women', 'Kids']
    next_page_xpath = '//*[@class="pagination__arrow pagination__arrow--right"]'
    search_xpath = '//span[@class="nav-search__trigger-icon"]'
    search_input_xpath = '//input[@id="search-input"]'
    accept_cookies_xpath = '//*[@class="cookie-notice__button bttn bttn--grey-3"]'
    wait_for_promotion1_xpath = '//*[@id="bx-element-1290300-9cZauvB"]'
    reject_promotion1_xpath = '//*[@id="bx-element-1290300-9cZauvB"]//button'
    wait_for_promotion2_xpath = '//*[@id="bx-element-1671444-vAAMitb"]'
    reject_promotion2_xpath = '//*[@id="bx-element-1671444-vAAMitb"]//button'
    wait_for_promotion3_xpath = '//div[@id="bx-element-1272786-9cZauvB"]'
    reject_promotion3_xpath = '//div[@id="bx-element-1272786-9cZauvB"]//button'
    wait_for_promotion4_xpath = '//div[@id="bx-element-1679029-9cZauvB"]'
    reject_promotion4_xpath = '//div[@id="bx-element-1679029-9cZauvB"]//button'
    item_container_xpath = '//div[@class="items__list"]'
    product_no_xpath = '//*[@class="sku-style-number"]//span'
    brand_xpath = '//div[@class="p-details__content"]//a'
    product_info_xpath = '//div[@class="p-details__name-wrap"]//p'
    price_xpath = '//p[@class="product-price__regular  price"]'
    size_and_fit_xpath = '//div[@class="long-text p-more-info__html p-more-info__html--infocare"]'
    brand_bio_xpath = '//div[@class="long-text p-more-info__html p-more-info__html--brandbio"]'
    images_xpath = '//ul[@class="p-images__preview-swatches"]//img'
    RAW_DATA_PATH = '/home/christian/Desktop/web_scraper_project/raw_data'
    IMG_PATH = '/home/christian/Desktop/web_scraper_project/raw_data/images'
    DEPARTMENT_XPATH = '//a[@class="nav-cats__link nav-cats__link--lv1"][@data-dept="{}"]'
    DEPARTMENT_BUTTON_XPATH = '//a[@class="cms-buttons__button link link--button link--grey-3"]'
    CHOOSE_CATEGORIES_XPATH = '//section[@class="filter-group pr-filter-group-categories"]//ul[@class="filter-group__list"]//a'
    CHOOSE_SUBCATEGORIES_XPATH = '//section[@class="filter-group pr-filter-group-categories"]//ul[@class="filter-group__list"]//a'
    HEADING_INFO_ACTIVE_XPATH = '//h4[@class="p-more-info__heading p-more-info__heading--active"]'
    SIZE_AND_FIT_INACTIVE_XPATH = '//h4[@class="p-more-info__heading "][text()="Size & Fit"]'
    BRAND_BIO_INACTIVE_XPATH = '//h4[@class="p-more-info__heading "][text()="Brand Bio"]'
    price_sale_xpath = '//p[@class="product-price__old  "]'
    promotion_box = '//div[@id="mf__div"][@aria-hidden="true"]'
    pagination_xpath = '//ul[@class="pagination__links"]//a'
    choose_categories_dropdown_xpath = '//section[@class="filter-group pr-filter-group-categories"]//h3[@class="filter-group__title filter-group__title--closed"]'
    choose_category_button = '//section[@class="filter-group pr-filter-group-categories"]//h3'

class Driver_Configuration:
    """
    A class which contains the relevant arguments required for the WebDriver.
    """

    def __init__(self) -> None:
        pass

    IG_CERT_ERROR = '--ignore-certificate-errors'
    RUN_INSEC_CONTENT = '--allow-running-insecure-content'
    NO_SANDBOX = '--no-sandbox'
    START_MAXIMISED = "--start-maximized"
    DISABLE_DEV_SHM = '--disable-dev-shm-usage'
    HEADLESS = '--headless'
    USER_AGENT = "user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'"
    WINDOW_SIZE = "window-size=1920,1080"

class Db_Config:

    def __init__(self) -> None:
        pass

    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    ENDPOINT = 'webscrape.ctlcajniy2jq.us-west-1.rds.amazonaws.com'
    USER = 'postgres'
    PASSWORD = 'password123'
    PORT = 5432
    DATABASE = 'postgres'

class S3_Config:
    def __init__(self) -> None:
        pass

    REGION = 'us-west-1'
    ACCESS_KEY = 'AKIAWF44ZTMTLPEFWIMM'
    SECRET_KEY = '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'

class AnyEc:
    """ 
    Use with WebDriverWait to combine expected_conditions
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