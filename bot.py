# Start with imports 

import json
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep, time
import random
import re
import subprocess, os
import urllib.request

import time


# open_chrome function
def open_chrome(port=9220, on_mac=True):
    my_env = os.environ.copy()
    if on_mac:
        subprocess.Popen(['open', '-a', "Google Chrome", '--args', f'--remote-debugging-port={port}', 'http://www.example.com'], env=my_env)
    else:
        subprocess.Popen(f'google-chrome --remote-debugging-port={port} --user-data-dir=bots'.split(), env=my_env)

class Bot():
    def __init__(self, port_no = 9220, headless = False, verbose = False):
        print('initialising bot')

        open_chrome()

        options = Options()
        options.add_argument("--no-sandbox")	# without this, the chrome webdriver can't start (SECURITY RISK)
        options.add_experimental_option(f"debuggerAddress", f"127.0.0.1:{port_no}")	# attach to the same port that you're running chrome on
        if headless:
            options.add_argument("--headless") # headless option allows scraper to run in the background
        #options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome('chrome_driver/chromedriver')			# create webdriver
        self.verbose = verbose

    def click_btn(self, text):
        if self.verbose: print(f'clicking {text} btn')
        element_types = ['button', 'div', 'input', 'a', 'label']
        
        for element_type in element_types:
            btns = self.driver.find_elements_by_xpath(f'//{element_type}')
            # for btn in btns:
            #   print(btn.text)

            # SEARCH BY TEXT
            try:
                btn = [b for b in btns if b.text.lower() == text.lower()][0]
                btn.click()
                return
            except IndexError:
                pass

            # SEARCH BY VALUE ATTRIBUTE IF NOT YET FOUND
            try:
                btn = self.driver.find_elements_by_xpath(f'//{element_type}[@value="{text}"]')[0]
                btn.click()
                return
            except:
                continue

        raise ValueError(f'button containing "{text}" not found')

    def _search(self, query, _type='search', placeholder=None):
        sleep(1)
        s = self.driver.find_elements_by_xpath(f'//input[@type="{_type}"]')
        print(s)
        if placeholder:
            s = [i for i in s if i.get_attribute('placeholder').lower() == placeholder.lower()][0]
        else:
            s = s[0]
        s.send_keys(query) 

    def toggle_verbose(self):
        self.verbose = not self.verbose


if __name__ == '__main__':
    # EXAMPLE USAGE
    bot = Bot()

    # data_dict = {"plant pots": [], "plates": [], "bin": []}
    data_dict = {}

    searches = {'plates': [], 'plant pots':[], 'bin':[]}
    
    for search in searches:
        bot.driver.get(f'https://www.ikea.com/gb/en/search/products/?q={search}')
        data_dict[search] = {}

        # add a dict to a dict

        # How to scroll on selenium

        while True:
            try:
                bot.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                show_more_button = bot.driver.find_elements_by_xpath('//*[@class="show-more__button button button--secondary button--small"]')[0]
                show_more_button.click()
            except IndexError:
                break


        # Go into the main grid and find the link for each result
        results = bot.driver.find_elements_by_xpath('//*[@id="search-results"]/div/a')  
        print (f'found {len(results)}) results for search "{search}" ')


        results = [r.get_attribute('href') for r in results]

        for i, result in enumerate(results):

            print(result)
            print(i)

            if '/p/' not in result:
                continue 

            bot.driver.get(result)
            result = result.split('/')[-2]

            results_dict = {"id": [],"prod_name": [], "prod_price": [], "prod_desc": [], "prod_dimensions": [], "packaging": [], "prod_details": [], "sustainability": [], "images":[], "materials": [], "sustainability":[]}
            

            results_dict['id'] = i


            # Extract Product Description


            prod_name = bot.driver.find_element_by_xpath('//*[@class="range-revamp-header-section__title--big"]')
            prod_name = prod_name.get_attribute('innerHTML')              
            results_dict['prod_name'] = prod_name
                        

            prod_price = bot.driver.find_element_by_xpath('//*[@class="range-revamp-price__integer"]')
            prod_price = prod_price.get_attribute('innerHTML')
            results_dict['prod_price'] = prod_price


            prod_desc = bot.driver.find_element_by_xpath('//*[@class="range-revamp-header-section__description-text"]')
            prod_desc = prod_desc.get_attribute('innerHTML')
            results_dict['prod_desc'] = prod_desc


            os.makedirs(f'data/{search}/{result}', exist_ok=True)

            # First get the image - product dimensions image
            prod_dims_images = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions-content__images"]//img')
            prod_dims_images = [i.get_attribute('src') for i in prod_dims_images]

            for image in prod_dims_images:
                

                for idx, img_url in enumerate(prod_dims_images):
                    filename = f'dims-{result}-{idx}'
                    file_ext = img_url.split('.')[-1] 
                    file_ext = file_ext[ 0 : 3 ]
                    urllib.request.urlretrieve(img_url, f'data/{search}/{result}/{filename}.{file_ext}')
                    results_dict['dims_images'] = f'data/{search}/{result}/{filename}.{file_ext}'


            
            # Get Product Details Packaging
            prod_packaging = bot.driver.find_elements_by_xpath('//*[@id="SEC_product-details-packaging"]//span')
            prod_packaging = [item.get_attribute('innerHTML') for item in prod_packaging]
            prod_packaging = [x for x in prod_packaging if "</span>" not in x]
            results_dict['packaging'] = prod_packaging

            # Second get the description text
            prod_dims_name = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions__list-container"]//dt')
            prod_dims_name = [item.get_attribute('innerHTML').split(":")[0] for item in prod_dims_name]
        
            
            prod_dims_measure = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions__list-container"]//dd')
            prod_dims_measure = [item.get_attribute('innerHTML') for item in prod_dims_measure]
            dims = dict(zip(prod_dims_name, prod_dims_measure))
            results_dict['prod_dimensions'] = dims


            # Cycle through information on each page starting with images   
            images = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-media-grid__media-container"]//img') 
            images = [i.get_attribute('src') for i in images]

            # Product Details
            product_details = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-details__paragraph"]')
            

            # Materials
            product_details = [paragraph.get_attribute('innerHTML') for paragraph in product_details]
            product_details = " ".join(product_details)
            results_dict['prod_details'] = product_details

            product_details_materials = bot.driver.find_elements_by_xpath('//*[@id="SEC_product-details-material-and-care"]//span')
            product_details_materials = [paragraph.get_attribute('innerHTML') for paragraph in product_details_materials]
            product_details_materials = ",".join(product_details_materials)
            results_dict['materials'] = product_details_materials


            product_details_sustain = bot.driver.find_elements_by_xpath('//*[@id="SEC_product-details-sustainability-and-environment"]//span')
            product_details_sustain = [paragraph.get_attribute('innerHTML') for paragraph in product_details_sustain]
            product_details_sustain = ",".join(product_details_sustain)
            results_dict['sustainability'] = product_details_sustain

            

            # Get reviews
            
            for image in images:
                # Loop through each image and save to disk

                for idx, img_url in enumerate(images):

                    # Create filename for each with ID and get the file extension
                    filename = f'{result}-{idx}'
                    file_ext = img_url.split('.')[-1] 
                    file_ext = file_ext[ 0 : 3 ]
                    # Write to file
                    filepath = f'data/{search}/{result}/{filename}.{file_ext}'
                    urllib.request.urlretrieve(img_url, filepath)
                    results_dict['images'].append(filepath)
                    
            # Remove duplicate images
            results_dict['images'] = [i for j, i in enumerate(results_dict['images']) if i not in results_dict['images'][:j]] 

            data_dict[search][i] = results_dict


            print(results_dict['images'])

            # 
            with open('data_json.txt', 'w') as json_file:
                json.dump(data_dict, json_file)
            
            

