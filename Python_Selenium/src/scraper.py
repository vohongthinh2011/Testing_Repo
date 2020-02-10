from webdriver_amazon import webdriver_amazon

import yaml
import json
import datetime
import subprocess
import threading
from threading import Thread
import time
from itertools import zip_longest

### TODO: handle variable length thread in zip_longest
def webdriverthread(url, i):
  print ('webdriver starting...')
  driver = webdriver_amazon(url=url)
  driver.open_product_page()
  driver.scrape_reviews()
  driver.close_driver()
  results = driver.data_results
  file_string = '../data/file_{}.json'.format(i)

  with open(file_string, 'w') as file:
      file.write(json.dumps(results))

with open("../config/amazon_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

torexe = subprocess.Popen(r'{}'.format(cfg['tor_config']['tor_file_path']))
time.sleep(10)

urls = [url for url in cfg['webdriver']['url']]

start_time = datetime.datetime.now()
i = 0

for url_list in zip_longest(*[iter(urls)]*2, fillvalue=''):
    threads = []
    for url in url_list:
       thread = Thread(target=webdriverthread, args=[url, i])
       i+=1
       threads.append(thread)
       thread.start()

    for thread in threads:
       thread.join()

end_time = datetime.datetime.now()

print ("TOTAL RUN TIME: {}".format(end_time-start_time))
