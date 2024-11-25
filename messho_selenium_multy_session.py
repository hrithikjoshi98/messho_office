import time

import dateparser
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, os
import pymysql
import zipfile
import gzip
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import random
import hashlib
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sys import argv
from datetime import datetime

random_time_list = [1, 2, 3]



def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


local_connect = pymysql.connect(
    host='172.27.131.60',
    user='root',
    password='actowiz',
    database='fk_meesho_mapping'
)
local_cursor = local_connect.cursor()

local_cursor.execute("""CREATE TABLE IF NOT EXISTS `meesho_pc_data_20241122` (
              `id` int NOT NULL AUTO_INCREMENT,
              `SKU_id_MEESHO` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
              `Pincode` varchar(255) DEFAULT NULL,
              `City` varchar(255) DEFAULT NULL,
              `Delivery_Date_MEESHO` varchar(255) DEFAULT NULL,
              `status` varchar(30) DEFAULT 'pending',
              `No_Delivery_Days_from_Scrape_Date_MEESHO` varchar(255) DEFAULT NULL,
              PRIMARY KEY (`id`)
            )""")
local_connect.commit()

main_url = 'https://www.meesho.com/?srsltid=AfmBOopbEEo_Uie8c9cnbQQQRlxyQuK0r9EjrTI2ac0aDz6RkOmwZX81&source=profile&entry=header&screen=HP'

path = 1

pincode = '560001'
scraped_data_count = 1
starting_position = 0
pos = 1


def block_assets(driver):
    driver.execute_cdp_cmd("Network.enable", {})  # Enable Network monitoring
    driver.execute_cdp_cmd(
        "Network.setBlockedURLs",
        {
            "urls": [
                "*.css",  # Block CSS files
                "*.webp",  # Block WEBP images
                "*.woff2",  # Block WOFF2 fonts
            ]
        },
    )

def create_session(file_name):

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument("--headless=new")  # Optional: Run in headless mode if needed
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
    options.add_argument("--disk-cache-size=524288000")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options, )
    block_assets(driver)
    driver.get(main_url)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    with open(file_name, 'r') as f:
        cookies = json.loads(f.read())

    for cookie in cookies['cookies']:
        driver.add_cookie(cookie)
    driver.refresh()
    return driver

def wait_for_h1_update(driver, selector, old_text, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_text = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, selector))).text
            if current_text and current_text != old_text:
                # print('got date')
                return current_text
        except Exception as e:
            pass
            # print('ele error')
        time.sleep(0.5)
    # print('blocked')
    return "Enter Pincode for Estimated Delivery Date"


def scrapping(link, driver):
    global scraped_data_count
    try:
        print('\n')
        SKU_id_MEESHO = link.split('/')[-1]
        local_cursor.execute("SELECT * FROM `meesho_pc_data_20241122` WHERE SKU_id_MEESHO = %s AND status = %s", (SKU_id_MEESHO, 'done'))
        local_connect.commit()
        print(link)
        if local_cursor.fetchone():
            print('url already scraped...', '\n')
            return

        driver.execute_script(f'''window.open("{link}","_self");''')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            review = driver.find_element(By.XPATH, '//h1[contains(text(), "Access Denied")]')
            if 'access denied' in review.text.lower():
                print('access denied')
                return
        except:
            pass

        try:
            review = driver.find_element(By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')
            driver.execute_script("arguments[0].scrollIntoView();", review)
        except:
            pass

        try:
            pin_input = driver.find_element(By.XPATH, '//input[@id="pin"]')
            if pincode == pin_input.get_attribute('value'):
                print(pin_input.get_attribute('value'))
            else:
                for _ in range(int(pin_input.get_attribute('maxlength'))):
                    pin_input.send_keys(Keys.BACKSPACE)
                    small_random_waite()
                pin_input.send_keys(pincode)
        except Exception as e:
            print('Input is not available')
            return

        try:
            element = driver.find_element(By.XPATH, '//*[@id="pin"]//button')
            ActionChains(driver).click(element).perform()
        except Exception as e:
            pass



        # time.sleep(2)
        # try:
        #     WebDriverWait(driver, 1).until(
        #         EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[2]')))
        #     print("error alert visible")
        #     return
        # except Exception as e:
        #     print('No error alert')

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            # review = WebDriverWait(driver, 5).until(
            #     EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
            review = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]')))
            ActionChains(driver).scroll_to_element(review).perform()
            # driver.execute_script("arguments[0].scrollIntoView();", review)
        except Exception as e:
            print('No error alert')

        pincode_city = {
            "560001": "BANGALORE",
            "110001": "DELHI",
            "400001": "MUMBAI",
            "700020": "KOLKATA",
            # "212011": "Varanasi",
        }

        def get_date(string_obj, difference=0):
            arrival = dateparser.parse(string_obj.lower().split("by")[-1], settings={'DATE_ORDER': 'DMY'})
            return (arrival - datetime.now()).days

        final_date = ''
        try:
            text_data = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]'))).text
            # text_data = driver.find_element(By.XPATH, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').text
            if 'Delivery by' not in text_data:
                xpath = '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]'
                new_text = wait_for_h1_update(driver, xpath, text_data, timeout=20)
                print(new_text)
                if 'Enter Pincode for Estimated Delivery Date' in new_text:
                    return
                else:
                    final_date = new_text
                    no_of_days = get_date(new_text)
            else:
                final_date = text_data
                no_of_days = get_date(text_data)
        except Exception as e:
            print('text :::', e)
            final_date = ''
            no_of_days = ''

        page_id = str(driver.current_url).split('/')[-1] + f'_{pincode}'

        # with zipfile.ZipFile(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.zip', 'w',
        #                      zipfile.ZIP_DEFLATED) as zip_file:
        #     zip_file.writestr(f'HTML_{page_id}.html', driver.page_source)

        with gzip.open(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.html.gz', 'w') as save:
            save.write(bytes(driver.page_source.encode()))


        insert_query = f"""INSERT INTO meesho_pc_data_20241122(SKU_id_MEESHO, pincode, City, Delivery_Date_MEESHO, status, No_Delivery_Days_from_Scrape_Date_MEESHO) VALUES (%s, %s, %s, %s, %s, %s)"""
        local_cursor.execute(insert_query, (link.split('/')[-1], pincode, pincode_city[pincode], final_date, 'done', no_of_days))
        local_connect.commit()
        update_query = f"""UPDATE `meesho_pdp_data_20241122` SET pin_pagesave_status = 'done' WHERE SKU_id_MEESHO = %s"""
        local_cursor.execute(update_query, (link.split('/')[-1],))
        local_connect.commit()

        scraped_data_count += 1


    except Exception as e:
        print("Main Exp", e)

start_time = time.time()

try:
    start = int(argv[1])
    end = int(argv[2])
    posi = int(argv[3])
except:
    start = 700
    end = 750
    posi = 1

if posi == 1:
    driver1 = create_session('6204387213.json')
    # driver2 = create_session('6359015644.json')
elif posi == 2:
    driver1 = create_session('7096488183.json')
    # driver2 = create_session('7226063206.json')
elif posi == 3:
    driver1 = create_session('7359427389.json')
    # driver2 = create_session('7359757545.json')
elif posi == 4:
    driver1 = create_session('7567926255.json')
    # driver2 = create_session('7600511244.json')
elif posi == 5:
    driver1 = create_session('7802074179.json')
    # driver2 = create_session('9106737598.json')
elif posi == 6:
    driver1 = create_session('9404408848.json')
    # driver2 = create_session('9420848973.json')
elif posi == 7:
    driver1 = create_session('9665146718.json')
    # driver2 = create_session('9725719468.json')
else:
    driver1 = create_session('9824818225.json')
    # driver2 = create_session('9879361219.json')


# query = f"SELECT Product_Url_MEESHO FROM `template_20241017_distinct_status` WHERE In_Stock_Status_MEESHO  = 'true' AND id BETWEEN {start} AND {end}"
query = f"SELECT SKU_id_MEESHO FROM `meesho_pdp_data_20241122` WHERE In_Stock_Status_MEESHO  = 'true' AND id BETWEEN {start} AND {end}"
local_cursor.execute(query)
rows = local_cursor.fetchall()
co_p = 1
for pos, link_ in enumerate(rows):
    link = "https://www.meesho.com/s/p/" + link_[0]
    # link = link_[0]

    if co_p == 1:
        scrapping(link, driver1)
        co_p = 0
    # if co_p == 2:
    #     scrapping(link, driver2)
    #     co_p = 0
    # if co_p == 3:
    #     scrapping(link, driver3)
    # if co_p == 4:
    #     scrapping(link, driver4)
    #     co_p = 0
    co_p += 1


end_time = time.time()

print("Time :", end_time - start_time)







