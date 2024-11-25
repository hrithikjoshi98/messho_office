import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pymysql
import zipfile
import random
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

random_time_list = [1, 2, 3]


def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


connect = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='meesho_page_save'
)
cursor = connect.cursor()

local_connect = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='meesho_page_save'
)
local_cursor = local_connect.cursor()

local_cursor.execute('''CREATE TABLE IF NOT EXISTS pages(id int AUTO_INCREMENT PRIMARY KEY,
url varchar(1000),
pincode varchar(50),
page_hash varchar(1000),
status varchar(100))''')
local_connect.commit()

main_url = 'https://www.meesho.com/?srsltid=AfmBOopbEEo_Uie8c9cnbQQQRlxyQuK0r9EjrTI2ac0aDz6RkOmwZX81&source=profile&entry=header&screen=HP'

path = 1

pincode = '560001'
scraped_data_count = 1
starting_position = 0
pos = 1


headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'meesho-iso-country-code': 'IN',
    'origin': 'https://www.meesho.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.meesho.com/famshu-electronics-water-sensor-reusable-led-diyas-for-home-decor-festivals-decoration-diwali-light-plastic-table-diya-set-pack-of-12/p/6c2xy9',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}


def create_session(file_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    driver.get(main_url)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    with open(file_name, 'r') as f:
        cookies = json.loads(f.read())

    for cookie in cookies['cookies']:
        driver.add_cookie(cookie)
    driver.refresh()
    return driver

def scrapping(link, driver):
    global scraped_data_count
    try:
        local_cursor.execute("SELECT * FROM pages WHERE url = %s AND status = %s", (link, 'done'))
        local_connect.commit()
        print(link)
        if local_cursor.fetchone():
            print('url already scraped...', '\n')
            return

        driver.execute_script(f'''window.open("{link}","_self");''')
        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        product_id = str(driver.current_url).split('/')[-1]


        json_data = {
            'include_catalog': True,
            'ad_active': False,
        }

        response = requests.post(f'https://www.meesho.com/api/v1/product/{product_id}', cookies=cookies, headers=headers,
                                 json=json_data)

        # supplier_id = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        #     (By.XPATH, '//*[@id="__NEXT_DATA__"]'))).text

        supplier_id = json.loads(response.text)['result']['product']['suppliers'][0]['id']
        print(supplier_id)

        json_data = {
            'dest_pin': '560001',
            'product_id': product_id,
            'supplier_id': supplier_id,
            'quantity': 1,
        }
        response = requests.post(
            'https://www.meesho.com/api/v1/check-shipping-delivery-date',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        print(response.status_code)
        date = json.loads(response.text)['shipping']['estimated_delivery_date']
        print(date)
        # page_id = product_id + f'_{pincode}'
        # with zipfile.ZipFile(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.zip', 'w',
        #                      zipfile.ZIP_DEFLATED) as zip_file:
        #     zip_file.writestr(f'HTML_{page_id}.html', driver.page_source)
        #
        # insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
        # local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
        # local_connect.commit()

        # update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
        # cursor.execute(update_query, (link,))
        # connect.commit()

        scraped_data_count += 1

    except Exception as e:
        print("Main Exp", e)


driver1 = create_session('9737090010_20241112.json')

query = f"SELECT Product_Url_MEESHO FROM `template_20241017_distinct_status` WHERE In_Stock_Status_MEESHO  = 'true'"
cursor.execute(query)
rows = cursor.fetchall()
co_p = 1
for pos, link_ in enumerate(rows):
    link = link_[0]

    if co_p == 1:
        scrapping(link, driver1)