
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
MacysReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Walmart retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python MacysReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.macys.com/shop/product/lacoste-hoodie-jersey-long-sleeve-tee-shirt-with-kangaroo-pocket?ID=4654365&tdp=cm_app~zMCOM-NAVAPP~xcm_zone~zC2FLEX_ZONE_A~xcm_choiceId~zcidM34MFQ-1124c421-f334-4efc-a275-3bf4984be896%40H82%40Now%2BTrending%241%244654365~xcm_pos~zPos4~xcm_srcCatID~z1'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
Results:
    Print the list of product information as shown below.
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# MacysReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class MacysReviewsCrawler(webdriver_amazon):
    def open_product_page(self):
        self.driver.get(self.url)
        try:
            search_input = WebDriverWait(self.driver, 30).until(
                #"button" to see all the reviews
                EC.visibility_of_element_located((By.XPATH, '//*[@id="mainCont"]/div/div[2]/div/div[5]/div/div/div[1]/div[1]/button')))
        except TimeoutException:
            print("No Review Link Found")

    # Parse all data content from each review.
    def parse_single_review(self, result):
        selectors = {
            #use id instead of class. Put Title and author tag in here
            'title': 'bv-content-title',
            'author': 'bv-avatar-popup-target-reviewContentList1-16', 
            'date': 'bv-content-datetime-stamp', 
            'body': 'bv-content-summary-body-text'
        }
        results = dict()

        # Use selector variable to loop through selectors list to extract data by using class name.
        for key, selector in selectors.items():
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
                #Get the Date and Body Text
                print("webdriver_costco.py - 61 - Results[key]: {}".format(element.text))
            except NoSuchElementException as e:
                results[key] = "None"

        ### Get rating of review

        return results

    # Parse all data content from each review.
    def parse_product_html(self, page_num):
        data = {
            'product': self.product_url,
            'time': str(datetime.datetime.now()),
            'average_stars': '',
            'total_reviews': '',
            'num_reviews_scraped': 0,
            'reviews': [],
        }

        # Access review data container by using 'review' class name
        try:
            all_reviews = self.driver.find_elements_by_class_name('bv-content-container')

        # If we could not find data in 'review' container. It will send below message.   
        except NoSuchElementException as e:
            print ("can not find reviews")

        ### Loop through each review and parse for data
        for i, result in enumerate(all_reviews):
            data['reviews'].append(self.parse_single_review(result))
            data['num_reviews_scraped'] += 1
        self.data_results['review-page-{}'.format(page_num)] = data

    # The process of extract reviews data.
    def scrape_reviews(self):
        try:
            review_button = self.driver.find_element_by_xpath('//*[@id="pdp-accordion-header-3"]')
            review_button.click()
            wait = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="BVRRContainer"]/div/div/div/div/div[3]/div/ul/li[2]/a')))
        except:
            print ("Could not find review button...")

        i = 0
        while True:
            i += 1
            if i % 1 == 0:
                print ("PAGE: {}".format(i))

            self.parse_product_html(i)

            if i == 1:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('//*[@id="BVRRContainer"]/div/div/div/div/div[3]/div/ul/li[2]/a')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('//*[@id="BVRRContainer"]/div/div/div/div/div[3]/div/ul/li[2]/a')
                    next_reviews_page.click()
                    time.sleep(randint(10,100))
                except WebDriverException as e:
                    print("can not go to next button after page 3")
                    break

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Macys Reviews Crawler starting...')
    driver = webdriver_Macys(url='https://www.macys.com/shop/product/lacoste-hoodie-jersey-long-sleeve-tee-shirt-with-kangaroo-pocket?ID=4654365&tdp=cm_app~zMCOM-NAVAPP~xcm_zone~zC2FLEX_ZONE_A~xcm_choiceId~zcidM34MFQ-1124c421-f334-4efc-a275-3bf4984be896%40H82%40Now%2BTrending%241%244654365~xcm_pos~zPos4~xcm_srcCatID~z1')
    driver.open_product_page()