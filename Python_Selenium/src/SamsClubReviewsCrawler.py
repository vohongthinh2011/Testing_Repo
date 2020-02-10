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
SamsClubReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Walmart retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python SamsClubReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.samsclub.com/p/hp-officejet-38380-all-in-one-printer-thermal-inkjet/prod23121737'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
Results:
    Print the list of product information as shown below.
    Examples:
    Reviews     ID     Product ID        Product Name             RetailerID      RetailerName     Title        Author     DateOfWritingReviews       ReviewContent                     ReviewContentWordsCount  ReviewContentCharactersCount IndividualRating   OverallRating      Scaping Time                                Product URL        
        1       1     HP OfficeJet      HP OfficeJet 3830 All..       6             Sam's Club     HP.printer   Tim Smith      7 days ago             everything came in the Box plu...            59                          312                     5               4.2         9/19/2019 17:41     https://www.samsclub.com/p/hp-officejet-38380-all-in-one-printer-thermal-inkjet/prod23121737               
"""
#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# SamsClubReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class SamsClubReviewsCrawler(webdriver_amazon):
    # Navigate to the selected product.
    def open_product_page(self):
        self.driver.get(self.url)
        try:
            search_input = WebDriverWait(self.driver,30).until(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[3]/div/div[1]/div[1]/button')))
        except TimeoutException:
            print("No Review Link Found")

    # Navigate to the review section.
    def review_selection(self):
        try:
            review_button = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[3]/div/div[1]/div[1]/button')
            review_button.click()
            wait = WebDriverWait(self.driver,30).util(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[3]/div/div[1]/div[1]/button')))
        except:
            print("Could not find review section.")

    # Wait for the next button to load before navigating.
    def wait_for_next_button(self):
        try:
            search_input = WebDriverWait(self.driver,50).until(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div/div/div[3]/div/ul/li[2]/button')))
        except TimeoutException:
            print("No Find Next Button")

    # Parse all data content from each review.
    def parse_single_review(self,result):
        path = '../SamsClub_Excel_Data/SamClub_1.csv'
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

        selectors = {
            #'title': 'bv-content-title',
            'author': 'bv-author',
            'date': 'bv-content-datetime-stamp',
            'individual_rating': 'bv-off-screen',
            'body': 'bv-content-summary-body-text'
        }

        productData = {
            'product_id': 1,
            'product_name': 'HP OfficeJet 3830 All-in-One Printer, Thermal Inkjet',
            'retailer_name': 'SamsClub',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now())
        }

        results = dict()
        ### Get Title
        try:
            element = result.find_element_by_css_selector("h3[itemprop='headline']") 
            results['title'] = element.text
            title=element.text
            print('Review Title: {}'.format(element.text))
        except:
            results['title'] = "None"
            pass
        extractReviewData=dict()
        reviewID=0;
        for key, selector in selectors.items():
            reviewID +=1
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
            except NoSuchElementException as e:
                results[key] = "None"

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

    # Parse all data content from each review.
    def parse_product_html(self, page_num):        
        data = {
            'product_name': 'HP OfficeJet 3830 All-in-One Printer, Thermal Inkjet',
            'retailer_name': 'SamsClub',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now()),
            'num_reviews_scraped': 0,
            'reviews': []
        }

        try:
            all_reviews = self.driver.find_elements_by_class_name('bv-content-container')
            print("Reviews Length: {}".format(len(all_reviews)))#print("97")
        except NoSuchElementException as e:
            print ("can not find reviews")

        ### Loop through each review and parse for data
        for i, result in enumerate(all_reviews):
            data['num_reviews_scraped'] += 1
            data['reviews'].append(self.parse_single_review(result)) 
        print("outside")

    def extract_reviews_process(self):
        i = 0
        while True:
            #print("119")
            i += 1
            #print("121")
            if i % 1 == 0:
                print ("PAGE: {}".format(i))
            self.parse_product_html(i)
            #self.wait_for_next_button()
            if i == 1:
                try:
                    print("191")
                    self.wait_for_next_button()
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div/div/div[3]/div/ul/li[2]/button')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div/div/div[3]/div/ul/li[2]/button[2]')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not go to next button")
                    #pass
                    break

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Sams Club Reviews starting...')
    url='https://www.samsclub.com/p/hp-officejet-38380-all-in-one-printer-thermal-inkjet/prod23121737'
    driver = SamsClubReviewsDriver(url)
    driver.open_product_page()
    driver.review_selection()
    driver.extract_reviews_process()