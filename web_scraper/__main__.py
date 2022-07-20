from web_scraper.item_scraper import Item_Scraper
from web_scraper.config import Configuration_XPATH

scrape = Item_Scraper(Configuration_XPATH.WEBSITE)

scrape.run_full_scrape()

