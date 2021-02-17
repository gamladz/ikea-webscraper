# Start with imports 

import json 
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
import sys
import boto3
from botocore.exceptions import ClientError
from selenium import webdriver 
import time
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Set up AWS functions
s3 = boto3.resource("s3").Bucket("ikea-dataset")
json.load_s3 = lambda f: json.load(s3.Object(key=f).get()["Body"])
json.dump_s3 = lambda obj, f: s3.Object(key=f).put(Body=json.dumps(obj))
client = boto3.client('s3', region_name='us-east-2')

# Example usage
# Updated
max_time = 10

def open_chrome(port=9220, on_mac=True):
    my_env = os.environ.copy()
    if on_mac:
        print('opening chrome')
        subprocess.Popen(['open', '-a', "Google Chrome", '--args', f'--remote-debugging-port={port}', 'http://www.example.com'], env=my_env)
    else:
        subprocess.Popen(f'google-chrome --remote-debugging-port={port} --user-data-dir=data_dir'.split(), env=my_env)
    print('opened chrome')

class Bot():
    def __init__(self, port_no=9220, headless=True, verbose=False):
        print('initialising bot')

        print(headless)
        options = Options()
        if headless:
            options.add_argument("--headless")
            print('running headless')
        else:
            open_chrome(port=port_no)
            options.add_experimental_option(f"debuggerAddress", f"127.0.0.1:{port_no}")	# attach to the same port that you're running chrome on
        options.add_argument("--no-sandbox")	# without this, the chrome webdriver can't start (SECURITY RISK)
        #options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome('chrome_driver/chromedriver', chrome_options=options)	
        self.verbose = verbose
    
    def scroll(self, x=0, y=10000):
        self.driver.execute_script(f'window.scrollBy({x}, {y})')

    def click_btn(self, text):
        if self.verbose: print(f'clicking {text} btn')
        element_types = ['button', 'div', 'input', 'a', 'label']
        for element_type in element_types:
            btns = self.driver.find_elements_by_xpath(f'//{element_type}')
            # for btn in btns:
            #     print(btn.text)
            
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

    def download_file(self, src_url, local_destination):
        response = requests.get(src_url)
        with open(local_destination, 'wb+') as f:
            f.write(response.content)

if __name__ == '__main__':
    port = random.randint(9000,10000)
    bot = Bot(port_no=port, headless=False)
    
    data_dict = {
        
    }

    searches = {
        "plant pots":[], 
        "bin":[],
        "cookware":[],
        "wardrobes":[], 
        "tables":[],
        "cabinets":[],
        "clothing racks":[],
        "chair":[]
    }
    
    for search in searches:
        bot.driver.get(f'https://www.ikea.com/gb/en/search/products/?q={search}')
        data_dict[search] = {}

        # Get full grid by trying to scroll and press show more button
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

            # Skip promotional links, adverts or non-product links in grid
            if '/p/' not in result:
                continue 

            bot.driver.get(result)
            url = result
            result = result.split('/')[-2]

            # Set up dict for each products result
            results_dict = {
                "id": [],
                "url":[],
                "source":[],
                "name": [],
                "price": [],
                "description": [],
                "dims_image": [],
                "dimensions": [],
                "packaging": [],
                "details": [],
                "sustainability": [],
                "images":[],
                "materials":[]
            }
            
            results_dict['url'] = url
            results_dict['id'] = hash(url)
            results_dict['source'] = 'IKEA'


            # Extract Product Name
            prod_name = bot.driver.find_element_by_xpath('//*[@class="range-revamp-header-section__title--big"]')
            prod_name = prod_name.get_attribute('innerHTML')              
            results_dict['name'] = prod_name
                        
            # Product price
            prod_price = bot.driver.find_element_by_xpath('//*[@class="range-revamp-price__integer"]')
            prod_price = prod_price.get_attribute('innerHTML')
            results_dict['price'] = prod_price


            prod_desc = bot.driver.find_element_by_xpath('//*[@class="range-revamp-header-section__description-text"]')
            prod_desc = prod_desc.get_attribute('innerHTML')
            results_dict['description'] = prod_desc


            os.makedirs(f'data/{search}/{result}', exist_ok=True)

            # First get the image - product dimensions image
            prod_dims_images = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions-content__images"]//img')
            prod_dims_images = [i.get_attribute('src') for i in prod_dims_images]

            for image in prod_dims_images:
                # Loop through each image and save to disk

                for idx, img_url in enumerate(prod_dims_images):

                    # Create filename for each with ID and get the file extension
                    filename = f'dims-{result}-{idx}'
                    file_ext = img_url.split('.')[-1] 
                    file_ext = file_ext[ 0 : 3 ]
                    # Write file locally
                    filepath = f'data/{search}/{result}/{filename}.{file_ext}'
                    try:
                        urllib.request.urlretrieve(img_url, filepath)
                    except ConnectionResetError:
                        print ('Connection Error')
                    else:
                        img_data = requests.get(img_url).content
                        with open(filepath, 'wb') as handler:
                            handler.write(img_data)                         
                    finally:
                        pass
                    # Write image to AWS
                    with open(filepath, 'rb') as data:
                        s3.upload_fileobj(data, filepath)
                    results_dict['dims_image'].append(filepath)
                    # remove comment to stop storing locally
                    # os.remove(filepath)

            # for image in prod_dims_images:
                
            
            # Get Product Details Packaging
            prod_packaging = bot.driver.find_elements_by_xpath('//*[@id="SEC_product-details-packaging"]//span')
            prod_packaging = [item.get_attribute('innerHTML') for item in prod_packaging]
            prod_packaging = [x for x in prod_packaging if "</span>" not in x]
            results_dict['packaging'] = prod_packaging

            # Second get all product dimensions
            prod_dims_name = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions__list-container"]//dt')
            prod_dims_name = [item.get_attribute('innerHTML').split(":")[0] for item in prod_dims_name]
        
            
            prod_dims_measure = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-dimensions__list-container"]//dd')
            prod_dims_measure = [item.get_attribute('innerHTML') for item in prod_dims_measure]
            dims = dict(zip(prod_dims_name, prod_dims_measure))
            results_dict['dimensions'] = dims


            # Cycle through images 
            images = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-media-grid__media-container"]//img') 
            images = [i.get_attribute('src') for i in images]

            # Product Details
            product_details = bot.driver.find_elements_by_xpath('//*[@class="range-revamp-product-details__paragraph"]')
            product_details = [paragraph.get_attribute('innerHTML') for paragraph in product_details]
            product_details = " ".join(product_details)
            results_dict['details'] = product_details

            # Materials
            product_details_materials = bot.driver.find_elements_by_xpath('//*[@id="SEC_product-details-material-and-care"]//span')
            product_details_materials = [paragraph.get_attribute('innerHTML') for paragraph in product_details_materials]
            product_details_materials = ",".join(product_details_materials)
            results_dict['materials'] = product_details_materials

            # Sustainability
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
                    # Write file locally
                    filepath = f'data/{search}/{result}/{filename}.{file_ext}'
                    try:
                        urllib.request.urlretrieve(img_url, filepath)
                    except ConnectionResetError:
                        print ('Connection Error')
                    else:
                        img_data = requests.get(img_url).content
                        with open(filepath, 'wb') as handler:
                            handler.write(img_data)                         
                    finally:
                        pass
                    # Write to cloud
                    with open(filepath, 'rb') as data:
                        s3.upload_fileobj(data, filepath)
                    results_dict['images'].append(filepath)
                    # remove comment to remove file locally
                    # os.remove(filepath)
                    
            # Remove duplicate images
            results_dict['images'] = [i for j, i in enumerate(results_dict['images']) if i not in results_dict['images'][:j]] 
            # Wrte dict to local
            data_dict[search][i] = results_dict 
            with open('data.json', 'w') as json_file:
                json.dump(data_dict, json_file)

            # Write to AWS 
            json.dump_s3(data_dict, "data_json")
