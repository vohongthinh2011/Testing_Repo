#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import re
from time import time
import json
import argparse

def get_store(store):
	store_name = store['Name']
	store_timings = store['OperatingHours']['Hours']
	street = store['Address']['AddressLine1']
	city = store['Address']['City']
	county = store['Address'].get('County')
	zipcode = store['Address']['PostalCode']
	state = store['Address']['Subdivision']
	country = store['Address'].get('CountryName')
	
	try:
		contact = store['TelephoneNumber'][0]['PhoneNumber']
	except:
		contact = store['TelephoneNumber'].get('PhoneNumber')
	
	open_timing = []
	stores_open = []
	
	for store_timing in store_timings:
		timing = store_timing['TimePeriod']['Summary']
		weekDay = store_timing['FullName']
		stores_open.append(weekDay)
		open_timing.append({"Week Day":weekDay,"Open Hours":timing})

	data = {
			'Store_Name' : store_name,
			'Street' : street,
			'City' : city,
			'County' : county,
			'Zipcode' : zipcode,
			'State' : state,
			'Contact' : contact,
			'Timings' : open_timing,
			'Stores_Open' : stores_open,
			'Country' : country
	}
	return data

def parse(zipcode):
	#sending requests to get the accesskey for the store listing page url
	stores_url = 'https://www.target.com/store-locator/find-stores?address={0}&capabilities=&concept='.format(zipcode)
	front_page_response = requests.get(stores_url)
	raw_access_key = re.findall("accesskey\s+?\:\"(.*)\"",front_page_response.text)

	if raw_access_key:
		accesskey = raw_access_key[0]
	else:
		print("Access key not found")

	access_time = int(time()) 
	stores_listing_url = 'https://api.target.com/v2/store?nearby={0}&range=100&locale=en-US&key={1}&callback=jQuery2140816666152355445_1500385885308&_={2}'.format(zipcode,accesskey,access_time)
	storeing_response = requests.get(stores_listing_url)
	content =re.findall("\((.*)\)",storeing_response.text)
	Locations = []
	
	try:
		json_data = json.loads(content[0])
		total_stores = json_data['Locations']['@count']

		if not total_stores == 0:
			stores = json_data["Locations"]["Location"]
			# Handling multiple Locations 
			if total_stores > 1:
				for store in stores:
					Locations.append(get_store(store))
			# Single Location
			else:
				Locations.append(get_store(stores))
			return Locations
	
	except ValueError:
		print("No json content found in response")
			   
if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('zipcode', help='Zip code')

	args = argparser.parse_args()
	zipcode = args.zipcode

	print("Fetching Location details")
	scraped_data = parse(zipcode)
	print("Writing data to output file")
	with open('%s-locations.json'%(zipcode),'w') as fp:
		json.dump(scraped_data,fp,indent = 4)