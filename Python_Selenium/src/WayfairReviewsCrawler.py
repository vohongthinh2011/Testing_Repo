import time, os
import subprocess
import datetime
from random import randint
import yaml
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotVisibleException, NoSuchElementException

from user_agents import get_user_agent
from webdriver_amazon import webdriver_amazon


"""
WayfairReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Walmart retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python WayfairReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.wayfair.com/furniture/pdp/bloomsbury-market-vanzant-storage-platform-bed-bbmt2435.html'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
Results:
    Print the list of product information.
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# WayfairReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class WayfairReviewsCrawler(webdriver_amazon):
    # Open and navigate to product page.
    def open_product_page(self):
        self.driver.get(self.url)
        try:
            search_input = WebDriverWait(self.driver, 50).until(
                #"button" to see all the reviews
                EC.visibility_of_element_located((By.XPATH, '//*[@id="CollapseToggle-6"]')))
        except TimeoutException:
            print("No Review Link Found")

    # Parse data from each review.
    def parse_single_review(self, result):
        selectors = {
            'author': 'ProductReviewHeader-name',
            'date': 'ProductReviewBody-date',
            'verified_buy': 'ProductReviewerComplianceBadge',
            'body': 'ProductReviewBody-comments'
        }

        results = dict()
        for key, selector in selectors.items():
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
            except NoSuchElementException as e:
                results[key] = "None"
        ### Get rating of review
        return results

    # parse_product_html function import default data into csv file.
    def parse_product_html(self, page_num):
        print('webdriver_Wayfair.py - 69')
        data = {
            'product': self.product_url,
            'time': str(datetime.datetime.now()),
            'average_stars': '',
            'total_reviews': '',
            'num_reviews_scraped': 0,
            'reviews': [],
        }

        # parse all reviews on current page
        try:
            all_reviews = self.driver.find_elements_by_class_name('ProductCardList-item')
        # If we could not find data in 'review' container. It will send below message.
        except NoSuchElementException as e:
            print ("can not find reviews")

        ### Loop through each review and parse for data
        for i, result in enumerate(all_reviews):
            data['reviews'].append(self.parse_single_review(result))
            data['num_reviews_scraped'] += 1

        self.data_results['review-page-{}'.format(page_num)] = data

    # The application automatically navigate to review button and extract content from all reviews.
    def scrape_reviews(self):
        try:
            #Choose review section
            review_button = self.driver.find_element_by_xpath('//*[@id="CollapseToggle-6"]')
            review_button.click()
            wait = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/section/div/div/div[12]/button')))
        except:
            print ("Could not find review button...")

        i = 0
        #### TODO: Change xpath to class name paginator-btn paginator-btn-next
        while True:
            i += 1
            if i % 1 == 0:
                print ("PAGE: {}".format(i))

            self.parse_product_html(i)

            if i == 1:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('//*[@id="CollapsePanel-6"]/div/div/div[12]/button/div/div')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('//*[@id="CollapsePanel-6"]/div/div/div[12]/button/div/div[2]')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not go to next button")
                    break

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Wayfair - webdriver starting.')
    driver = webdriver_wayfair(url='https://www.wayfair.com/furniture/pdp/bloomsbury-market-vanzant-storage-platform-bed-bbmt2435.html')
    driver.open_product_page()
    driver.scrape_reviews()
    driver.close_driver()
    results = driver.data_results
    file_string = '../data/File_Wayfair.json'

    with open(file_string,'w') as file:
        file.write(json.dumps(results))