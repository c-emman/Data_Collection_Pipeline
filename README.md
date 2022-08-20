# Data_Collection_Pipeline
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
