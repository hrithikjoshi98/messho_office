import time
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import seleniumbase
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

random_time_list = [1, 2, 3]



def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


connect = pymysql.connect(
    host='172.27.131.60',
    user='root',
    password='actowiz',
    database='fk_meesho_mapping'
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

def create_session(file_name, user_agent):

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-extensions")  # Disable extensions
    options.add_argument("--disable-images")  # Disable images
    options.add_argument("--disable-logging")
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
    options.add_argument("--disk-cache-size=524288000")
    options.page_load_strategy = 'eager'
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    # driver = seleniumbase.get_driver()

    # driver.set_driver_options(options)
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

        local_cursor.execute("SELECT * FROM pages WHERE url = %s AND status = %s", (link, 'done'))
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


        try:
            text_data = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]'))).text
            # text_data = driver.find_element(By.XPATH, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').text
            if 'Delivery by' not in text_data:
                xpath = '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]'
                new_text = wait_for_h1_update(driver, xpath, text_data, timeout=5)
                print(new_text)
                if 'Enter Pincode for Estimated Delivery Date' in new_text:
                    return
                else:
                    page_id = str(driver.current_url).split('/')[-1] + f'_{pincode}'

                    with gzip.open(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.html.gz',
                                   'w') as save:
                        save.write(bytes(driver.page_source.encode()))
                    insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
                    local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
                    local_connect.commit()
                    # update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
                    # cursor.execute(update_query, (link,))
                    # connect.commit()
            else:
                print(text_data)
                page_id = str(driver.current_url).split('/')[-1] + f'_{pincode}'

                with gzip.open(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.html.gz', 'w') as save:
                    save.write(bytes(driver.page_source.encode()))
                insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
                local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
                local_connect.commit()
                # update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
                # cursor.execute(update_query, (link,))
                # connect.commit()
        except Exception as e:
            print('text :::', e)



        scraped_data_count += 1


    except Exception as e:
        print("Main Exp", e)

start_time = time.time()

try:
    start = int(argv[1])
    end = int(argv[2])
    posi = int(argv[3])
except:
    start = 1
    end = 500
    posi = 1

user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    ]


if posi == 1:
    driver1 = create_session('6204387213.json', user_agents[0])
    driver2 = create_session('6359015644.json', user_agents[1])
    driver3 = create_session('7802074179.json', user_agents[2])
    driver4 = create_session('9106737598.json', user_agents[3])
elif posi == 2:
    driver1 = create_session('7096488183.json', user_agents[4])
    driver2 = create_session('7226063206.json', user_agents[5])
    driver3 = create_session('9404408848.json', user_agents[6])
    driver4 = create_session('9420848973.json', user_agents[7])
elif posi == 3:
    driver1 = create_session('7359427389.json', user_agents[8])
    driver2 = create_session('7359757545.json', user_agents[9])
    driver3 = create_session('9665146718.json', user_agents[10])
    driver4 = create_session('9725719468.json', user_agents[11])
else:
    driver1 = create_session('7567926255.json', user_agents[12])
    driver2 = create_session('7600511244.json', user_agents[13])
    driver3 = create_session('9824818225.json', user_agents[14])
    driver4 = create_session('9879361219.json', user_agents[15])


query = f"SELECT SKU_id_MEESHO FROM `meesho_pdp_data_20241126` WHERE In_Stock_Status_MEESHO  = 'true' AND id BETWEEN {start} AND {end}"
cursor.execute(query)
rows = cursor.fetchall()
co_p = 1
for pos, link_ in enumerate(rows):
    # link = link_[0]
    link = f'https://www.meesho.com/s/p/{link_[0]}'

    if co_p == 1:
        scrapping(link, driver1)
    if co_p == 2:
        scrapping(link, driver2)
    if co_p == 3:
        scrapping(link, driver3)
    if co_p == 4:
        scrapping(link, driver4)
        co_p = 0
    co_p += 1


end_time = time.time()

print("Time :", end_time - start_time)







