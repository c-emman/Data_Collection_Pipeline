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
    def __init__(self, full_scrape_list) -> None:
        pass


