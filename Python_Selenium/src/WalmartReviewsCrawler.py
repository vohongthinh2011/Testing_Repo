import time, os
import subprocess
import datetime
from random import randint
import yaml
import json
import pandas as pd
import csv

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
WalmartReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Walmart retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python WalmartReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.walmart.com/reviews/product/46605942'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
Results:
    Print the list of product information as shown below.
    Examples:
    Reviews     ID     Product ID        Product Name             RetailerID      RetailerName     Title        Author     DateOfWritingReviews       ReviewContent                     ReviewContentWordsCount  ReviewContentCharactersCount IndividualRating   OverallRating      Scaping Time                    Product URL        
        1       1     HP OfficeJet      3830 All-in-One Printer       2              Walmart     Great Buy      HPGoals,      17-Oct-16             This printer has served purpose...            59                          312                     5                4.1         9/19/2019 17:41     https://www.walmart.com/reviews/product/46605942               
  
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# WalmartReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class WalmartReviewsCrawler(webdriver_amazon):
    # Parse all data content from each review
    def parse_single_review(self,result):
        # Path to store excel file
        path = '../Walmart_Excel_Data/walmart_data.csv'
        # The list of variables to store data during crawling.
        title=''
        author =''
        dateOfWritingReview=''
        individualRating=''
        reviewTitle =''
        reviewContent=''
        productID=''
        productName = ''
        retailerName=''
        productURL=''
        dateOfCrawling=''
        reviewContentSplit = ''
        reviewContentWordsCount=''
        reviewContentCharactersCount=''

        # Create the array list variable selectors to store id tag to drawl data.
        selectors = {
            #'title': 'review-title font-bold',
            'author': 'review-footer-userNickname',
            'date': 'review-footer-submissionTime',
            'individual_rating': 'seo-avg-rating',
            'body': 'collapsable-content-container'
        }

        # An array list variable to import product id, product name, retailer name, product url and date of crawling data.
        productData = {
            'product_id': 241,
            'product_name': 'The Sound Of Music (50th Anniversary Edition) (Widescreen)',
            'retailer_name': 'Walmart',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now())
        }

        results = dict()

        # Get title of product.
        try:
            element = result.find_element_by_css_selector("h3[itemprop='name']")
            results['title'] = element.text
            title=element.text
        except:
        # Return "None" if the product does not have title.
            results['title'] = "None"
            pass
        reviewID=0;

        # Use selector variable to loop through selectors list to extract data by using class name.
        for key, selector in selectors.items():
            reviewID +=1
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
            except NoSuchElementException as e:
                results[key] = "None"

        # A list of variables to store extracted data and fill them in csv file row by row.
        productID = productData['product_id']
        productName = productData['product_name']
        retailerName = productData['retailer_name']
        productURL = productData['product_url']
        dateOfCrawling = productData['date_of_crawling']
        author=results['author']
        dateOfWritingReview=results['date']
        individualRating = results['individual_rating']
        reviewTitle = results['title']
        reviewContent = results['body']
        reviewContentSplit = len(reviewContent.split())
        reviewContentWordsCount = str(reviewContentSplit)
        reviewContentCharactersCount = len(reviewContent)
        with open(path,'a',newline='',encoding='utf-8') as csvFile:            
            writer = csv.writer(csvFile)
            writer.writerow([productID,productName,retailerName,author,title,dateOfWritingReview,reviewContent,reviewContentWordsCount,reviewContentCharactersCount,individualRating,dateOfCrawling,productURL])
            
        ### Get rating of review
        return results

    # parse_product_html function import default data into csv file.
    def parse_product_html(self, page_num):        
        data = {
            'product_name': 'HP OfficeJet 3830 All-in-One Printer',
            'retailer_name': 'Walmart',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now()),
            'num_reviews_scraped': 0,
            'reviews': [],
        }

        # Access review data container by using 'review' class name
        try:
            all_reviews = self.driver.find_elements_by_class_name('review')
        # If we could not find data in 'review' container. It will send below message.
        except NoSuchElementException as e:
            print ("can not find reviews")

        ### Loop through each review and parse for data
        csvData = []
        extractDataResult = dict()
        for i, result in enumerate(all_reviews):
            data['num_reviews_scraped'] += 1
            data['reviews'].append(self.parse_single_review(result))

    # Write data to csv file.
    def write_to_csv_file(self,csvData):
        product_header=["review_id","product_name","retailer_name","product_url","date_of_crawling","title","author","date_of_writing_review","individual_rating","reviewContent"]

    # The process of extract reviews data.
    def extract_reviews_process(self):
        self.driver.get(self.url)
        i = 0
        while True:
            i += 1
            if i % 1 == 0:
                print ("PAGE: {}".format(i))
            self.parse_product_html(i)
            if i == 1:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div/div[4]/div[2]/div/div/button')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div/div[4]/div[2]/div/div/button')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not go to next button")
                    break

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Walmart Reviews Crawler starting...')
    url='https://www.walmart.com/reviews/product/42423359'
    driver = WalmartReviewsCrawler(url)
    driver.extract_reviews_process()
    driver.close_driver()