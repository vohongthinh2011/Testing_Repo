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
AmazonReviewsCrawler.py  by Secure A.I. Laboratory and Autonomy at The University of Texas at San Antonio
Purpose:
    This program crawl data from the specific products on Amazon retail website. It will include retailer name,
    title, author, date of writing reviews, review content, review content words count, review content characters count,
    individual rating, overall rating, scraping time, product url.

Command Line Arguments:
    python AmazonReviewsCrawler.py  

Input:  
    Provide specific product link to the program by using variable "url"
        For example: url= 'https://www.amazon.com/'
    Using Google Chrome to inspect html page to find class tag, xpath and etc. for the requirements of application.

Results:
    Print the list of product information as shown below.
    Examples:
    Reviews     Product ID        Product Name             RetailerID      RetailerName          Title                           Author              DateOfWritingReviews              ReviewContent                     ReviewContentWordsCount  ReviewContentCharactersCount IndividualRating   OverallRating      Scaping Time                    Product URL        
        1           1         HP OfficeJet 3830...             1              Amazon     Works great for what I need     Kristen Dawn Gardner             17-Oct-16             Works great for what I need...                     159                          512                     4                3.7         9/19/2019 17:41     https://www.amazon.com/HP-OfficeJet-Wireless-Replenishment-K7V40A/product-reviews/B013SKI4EM/ref=cm_cr_arp_d_paging_btm_248?ie=UTF8&pageNumber=248&reviewerType=all_reviews               
  
"""

#Load config.yml to implement tor for anonymous communication. Link: https://www.torproject.org/ 
with open("../config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# AmazonReviewsCrawler function parse reviews of the provided product.
# Parameter: webdriver_amazon is imported from webdriver_amazon.py file to apply several functions from that file.
class AmazonReviewsCrawler(webdriver_amazon):
	# Automatic click to department
	def department_icon(self):
		self.driver.get(self.url)
		try:
			review_button = self.driver.find_element_by_xpath('/html/body/div[1]/header/div/div[2]/div[3]/div[1]/a/span[2]')
			review_button.click()
			wait = WebDriverWait(self.driver, 20).until(
				EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/header/div/div[2]/div[3]/div[1]/a/span[2]')))
		except:
			print ("2 Could not find review button...")

	# Automatic click to menu options
	def department_menu_options(self):
		try:
			review_button = self.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[4]/div[1]/div/a[9]')
			review_button.click()
			wait = WebDriverWait(self.driver, 20).until(
				EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[1]/div/div[4]/div[1]/div/a[9]')))
		except:
			print ("3 Could not find review button...")

	# Automatic choose Nomatic Travel Messenger
	def product_selection(self):
		try:
			review_button = self.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[1]/div[2]/div/span[3]/div[1]/div[4]/div/div/div/div[2]/div[3]/div/div[1]/h2/a/span')
			review_button.click()
			wait = WebDriverWait(self.driver, 30).until(
				EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[1]/div[1]/div[2]/div/span[3]/div[1]/div[4]/div/div/div/div[2]/div[3]/div/div[1]/h2/a/span')))
		except:
			print ("4 Could not find review button...")

	# Extract product name by using class tag in html
	def extract_product_name():
		try:
			all_reviews = self.driver.find_elements_by_class_name('a-section celwidget')
		except NoSuchElementException as e:
			print ("can not find reviews")

	# Automatic open reviews section by using xpath tag. 
	def open_reviews_section(self):
		try:
			search_input = WebDriverWait(self.driver,30).until(
				EC.visibility_of_element_located((By.XPATH,'//*[@id="acrCustomerReviewText"]')))
		except TimeoutException:
			print("1 No Review Link Found")

	# The application automatically navigate to review button and extract content from all reviews.
	def click_see_all_reviews_section(self):
		try:
			review_button = self.driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[4]/div[20]/div/div[2]/div/div[2]/span[3]/div/div/div[4]/div[2]/a')
			review_button.click()
			wait = WebDriverWait(self.driver, 50).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[4]/div[20]/div/div[2]/div/div[2]/span[3]/div/div/div[4]/div[2]/a')))
		except:
			print ("5 Could not find review section...")

		i = 0
		while True:
			i += 1
			if i % 1 == 0:
				print ("PAGE: {}".format(i))
			self.parse_product_html(i)

			if i == 1:
				try:
					next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/div[3]/div[11]/span/div/ul/li[2]/a')
					next_reviews_page.click()
					time.sleep(randint(10,100))
				except WebDriverException as e:
					print("can not find first next button")
					break
			else:
				try:
					next_reviews_page = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/div[3]/div[11]/span/div/ul/li[2]/a[2]')
					next_reviews_page.click()
					time.sleep(randint(10,100))
				except WebDriverException as e:
					print("can not go to next button after page 3")
					break

	# parse_product_html function import default data into csv file.
	def parse_product_html(self, page_num):
		data = {
			'product': self.product_url,
			'time': str(datetime.datetime.now()),
			'average_stars': '',
			'total_reviews': '',
			'num_reviews_scraped': 0,
			'reviews': []
		}

		# Access review data container by using 'review' class name
		try:
			all_reviews = self.driver.find_elements_by_class_name('a-section celwidget')
		
		# If we could not find data in 'review' container. It will send below message.
		except NoSuchElementException as e:
			print ("can not find reviews")

		### Loop through each review and parse for data
		for i, result in enumerate(all_reviews):
			data['reviews'].append(self.parse_single_review(result))
			data['num_reviews_scraped'] += 1
		self.data_results['review-page-{}'.format(page_num)] = data

	# Parse all data content from each review.
	def parse_single_review(self, result):
		selectors = {
			'author': 'a-profile-name',
			'date': 'a-size-base a-color-secondary review-date',
			'title': 'a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold',
			'body': 'a-size-base review-text review-text-content'
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

# Starting the application by importing the url link to extract reviews data for certain product.
if __name__ == "__main__":
	print('Amazon Reviews Crawler starting...')
	# Alternative way, specific product url="https://www.amazon.com/Nomatic-Travel-Messenger-Bag-Black/dp/B07JNCTWK7/ref=sr_1_3?_encoding=UTF8&qid=1567060254&s=apparel&sr=1-3"
	driver = AmazonDriverTemplate(url='https://www.amazon.com/')
	driver.department_icon()
	driver.department_menu_options()
	driver.product_selection()
	results = driver.data_results
	file_string = '../data/Amazon_Data.json'
	with open(file_string,'w') as file:
		file.write(json.dumps(results))