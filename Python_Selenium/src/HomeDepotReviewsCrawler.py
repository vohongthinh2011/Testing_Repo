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
HomeDepotReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Walmart retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python HomeDepotReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.homedepot.com/p/NewAir-320-CFM-3-Speed-Portable-Evaporative-Air-Cooler-Swamp-Cooler-and-Tower-Fan-with-Remote-for-100-sq-ft-AF-310/205402060?MERCH=REC-_-hp_sponsored-_-NA-_-205402060-_-N'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
Results:
    Print the list of product information as shown below. 
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 

with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# HomeDepotReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class HomeDepotReviewsCrawler(webdriver_amazon):
    # Open and navigate to product page.
    def open_product_page(self):
        self.driver.get(self.url)
        try:
            search_input = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="BVRRDisplayContentSortID"]/span[2] ')))
        except TimeoutException:
            print("No Review Link Found")

    # Parse all data from each review.
    def parse_single_review(self, result):
        selectors = {
            'author': 'BVRRNickname',
            'date': 'BVRRReviewDateContainer',
            'title': 'BVRRReviewTitleContainer',
            'body': 'collapsable-content-container',
        }

        results = dict()

        ### Get title
        for key, selector in selectors.items():
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
            except NoSuchElementException as e:
                results[key] = "None"

        return results

    # Parse all data from the provided product url.
    def parse_product_html(self, page_num):
        data = {
            'product': self.product_url,
            'time': str(datetime.datetime.now()),
            'average_stars': '',
            'total_reviews': '',
            'num_reviews_scraped': 0,
            'reviews': [],
        }

        ### Parse all reviews on current page
        try:
            all_reviews = self.driver.find_elements_by_class_name('BVRRReviewDisplayStyle5')
        except NoSuchElementException as e:
            print ("can not find reviews")

        ### Loop through each review and parse for data
        for i, result in enumerate(all_reviews):
            data['reviews'].append(self.parse_single_review(result))
            data['num_reviews_scraped'] += 1

        self.data_results['review-page-{}'.format(page_num)] = data

    # The process of extract reviews data.
    def scrape_reviews(self):
        i = 0
        while True:
            i += 1
            if i % 1 == 0:
                print ("PAGE: {}".format(i))

            self.parse_product_html(i)

            if i == 1:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('//*[@id="BVRRDisplayContentFooterID"]')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_css_selector('#BVRRDisplayContentFooterID > div > span.BVRRPageLink.BVRRNextPage')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not go to next button")
                    break

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Home Depot Reviews Crawler starting...')
    driver = webdriver_homedepot(url='https://www.homedepot.com/p/NewAir-320-CFM-3-Speed-Portable-Evaporative-Air-Cooler-Swamp-Cooler-and-Tower-Fan-with-Remote-for-100-sq-ft-AF-310/205402060?MERCH=REC-_-hp_sponsored-_-NA-_-205402060-_-N')
    driver.open_product_page()
    driver.scrape_reviews()
    driver.close_driver()
