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
TargetReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Target retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python TargetReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.target.com/p/quilted-fleece-electric-blanket-sunbeam-174/-/A-52827113'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.
    
Results:
    Print the list of product information as shown below.
    Examples:
    Reviews     ID     Product ID        Product Name             RetailerID      RetailerName        Title           Author     DateOfWritingReviews       ReviewContent                     ReviewContentWordsCount     ReviewContentCharactersCount   IndividualRating    OverallRating        Scaping Time                    Product URL        
        1       1          1         Quilted Fleece Electric..        6              Target     Electric blanket      MaryS      17-Oct-16             Perfect item!! Fast shipping...                 29                             212                        5                3.8           2019-10-29 17:57:05     https://www.target.com/p/quilted-fleece-electric-blanket-sunbeam-174/-/A-52827113
  
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# TargetReviewsCrawler function parse single review.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class TargetReviewsCrawler(webdriver_amazon):
    def open_product_page(self):
        self.driver.get(self.url)
        try:
            search_input = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="mainContainer"]/div/div/div[2]/div[2]/div[1]/div[3]/div/a[1]/div/div[2]/svg')))
        except TimeoutException:
            print("No Review Link Found")

    def review_selection(self):
        self.driver.get(self.url)
        try:
            review_button = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div[2]/div[2]/div[1]/div[3]/div/a[1]/div')
            review_button.click()
            wait = WebDriverWait(self.driver,20).util(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div/div[4]/div/div/div[2]/div[2]/div[1]/div[3]/div/a[1]/div')))
        except:
            print("Could not find review section.")
    
    def parse_single_review(self,result):
        # Path to store excel file
        path = '../Target_Excel_Data/target_1.csv'
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
            'title': 'Heading__StyledHeading-sc-6yiixr-0 kHEnWt',
            'author': 'review-card--username',
            'date': 'review-card--reviewTime',
            'individual_rating': 'h-sr-only',
            'body': 'h-margin-t-default'
        }

        # An array list variable to import product id, product name, retailer name, product url and date of crawling data.
        productData = {
            'product_id': 1,
            'product_name': 'HP Printer OfficeJet 3830 Black K7V40A_B1H',
            'retailer_name': 'Target',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now())
        }

        results = dict()

        reviewID=0;
        for key, selector in selectors.items():
            reviewID +=1
            print("Review ID: {}".format(reviewID))
            # Get value of product key.
            try:
                element = result.find_element_by_class_name(selector)
                results[key] = element.text
            except NoSuchElementException as e:
                # Return "None" if the product does not have key value.
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
            print("139- Successfully insert to CSV file")

        ### Get rating of review
        return results

    # parse_product_html function import default data into csv file.
    def parse_product_html(self, page_num):        
        data = {
            #'product_name': 'HP OfficeJet 3830 All-in-One Printer',
            #'retailer_name': 'Target',
            'product_url': self.product_url,
            'date_of_crawling': str(datetime.datetime.now()),
            'num_reviews_scraped': 0,
            'reviews': [],
        }

        # Access review data container by using 'review' class name
        try:
            all_reviews = self.driver.find_elements_by_class_name("ReviewCard-sc-1hvj2iv-4 hICCDS h-margin-v-default h-display-flex h-flex-direction-col h-padding-a-wide")
        # If we could not find data in 'review' container. It will send below message.
        except NoSuchElementException as e:
            print("cannot find reviews")

        ### Loop through each review and parse for data
        for i, result in enumerate(all_reviews):
            print("169")
            data['reviews'].append(self.parse_single_review(result))
            print("171")
            data['num_reviews_scraped'] += 1
            print('173')
        self.data_results['review-page-{}'.format(page_num)] = data
        
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
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div/div[9]/div/div[3]/div[3]/button')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not find first next button")
                    break
                    
            else:
                try:
                    next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div[8]/div/div[3]/div[3]/button[2]')
                    next_reviews_page.click()
                    time.sleep(randint(3,5))
                except WebDriverException as e:
                    print("can not go to next button")
                    break
               
# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
    print ('Extract Target Reviews...')
    url='https://www.target.com/p/hp-printer-officejet-3830-black-k7v40a-b1h/-/A-50599233'
    driver = TargetReviewsCrawler(url)
    driver.extract_reviews_process()
    driver.close_driver()
