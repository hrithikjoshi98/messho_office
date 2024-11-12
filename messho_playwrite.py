import os
import json
import random
import time
import zipfile
import pymysql
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import FingerprintGenerator
from browserforge.injectors.playwright import NewContext
from datetime import datetime
import hashlib
import time
from undetected_playwright import Tarnished
from evpn import ExpressVpnApi



# DB Connection
connect = pymysql.connect(
    host='172.27.131.60',
    user='root',
    password='actowiz',
    database='meesho_master'
)
cursor = connect.cursor()

local_connect = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='casio'
)
local_cursor = local_connect.cursor()

local_cursor.execute('''CREATE TABLE IF NOT EXISTS pages(id int AUTO_INCREMENT PRIMARY KEY,
url varchar(500),
pincode varchar(10),
page_hash varchar(500),
status varchar(30))''')
local_connect.commit()


# Random wait functions
def random_wait():
    time.sleep(random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]))


def small_random_wait():
    time.sleep(random.choice([0.2, 0.3, 0.4, 0.5]))


# Login function using Playwright
def login(page, context):
    global login_successful
    login_successful = False

    def handle_login_response(response):
        if 'verify.json' in response.url:
            print(f"Login verification response received from: {response.url}")
            global login_successful
            login_successful = True

    # Listen to network responses
    page.on('response', handle_login_response)

    # Navigate to login page
    page.goto('https://www.meesho.com/auth')

    # Fill mobile number
    page.locator('//input[@type="tel"]').fill('9879361219')  # EDIT THIS
    # page.locator('//input[@type="tel"]').fill('6354521692')  # EDIT THIS
    page.locator('//button[@type="submit"]').click()

    # Wait for the user to input the OTP
    otp = input('Enter OTP: ')
    for i, digit in enumerate(otp):
        page.locator(f'//input[@type="tel"][{i + 1}]').fill(digit)

    time.sleep(5)  # Wait for login to complete

    # Save session if login successful
    if login_successful:
        context.storage_state(path="session_storage.json")

    return login_successful



def change_vpn(api, locations):
     # get available locations
    loc = random.choice(locations)
    api.connect(loc["id"])
    time.sleep(5)


# Scraper function using Playwright
def scraper(pincode, start_id, end_id):
    cookies_dic = {}
    scraped_data_count = 1
    for file in os.listdir(os.getcwd()):
        if file.endswith('.json'):
            # print(file)
            with open(file, 'r') as f:
                data = f.read()
                file_name = file.split('.')[0]
                cookie = json.loads(data)
                cookies_dic[file_name] = cookie

    # with open('session_storage.json', 'r') as f:
    #     session_data = json.load(f)
    # session_datas = {}
    # lis = []
    # for p, i in enumerate(session_data['cookies']):
    #     print(i['name'])
    #     i['expires'] = -1
    #     lis.append(i)
    #
    # session_datas['cookies'] = lis


    # Load session cookies
    # context.add_cookies(session_datas['cookies'])

    # Query to fetch data
    # query = f"SELECT meesho_pid FROM product_links_20240926 WHERE status='Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"
    query = f"SELECT meesho_pid FROM product_links_20240927 WHERE status='Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"
    cursor.execute(query)
    rows = cursor.fetchall()
    co_p = 1
    for pos, pid in enumerate(rows):
        fingerprints = FingerprintGenerator()
        fingerprint = fingerprints.generate()
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(headless=False, )
            context = NewContext(browser, fingerprint=fingerprint)

            # Tarnished.apply_stealth(context)

            page = context.new_page()
            # context.clear_cookies()
            if co_p == 4:
                co_p = 1
            key, value = list(cookies_dic.items())[co_p]
            co_p += 1

            context.add_cookies(value['cookies'])

            link = f'https://www.meesho.com/s/p/{pid[0]}'

            local_cursor.execute(f"SELECT * FROM pages WHERE url = '{link}' and status = 'done'")
            local_connect.commit()
            print(f'\n{pos} --- {key} --- {link}')
            if local_cursor.fetchone():
                print('URL already scraped')
                continue
            # page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(link)
            page.evaluate("window.moveTo(0, 0); window.resizeTo(screen.width, screen.height);")

            try:
                if page.locator('//h1[contains(text(), "Access Denied")]').count() > 0:
                    review = page.locator('//h1[contains(text(), "Access Denied")]').first
                    if 'access denied' in review.text_content().lower():
                        print('access denied')
                        change_vpn(api, locations)
                        page_id = hashlib.sha256((page.url + f'_{pincode}').encode()).hexdigest()
                        insert_query = f"""INSERT INTO pages (url, pincode, page_hash, status) VALUES ('{page.url}', '{pincode}', '{page_id}', 'pending')"""
                        local_cursor.execute(insert_query)
                        local_connect.commit()
                        continue
            except:
                pass

            try:
                # Scroll to review element if exists
                if page.locator('//span[contains(@class, "ShopCardstyled__ShopName")]').count() > 0:
                    review = page.locator('//span[contains(@class, "ShopCardstyled__ShopName")]').first
                    review.scroll_into_view_if_needed()
            except:
                pass

            try:
                # Input the pincode
                if page.locator('//input[@id="pin"]').count() > 0:  # If element exists
                    page.locator('//input[@id="pin"]').fill(pincode)
                else:
                    print(f'Input not available for {pincode}')
                    page_id = hashlib.sha256((page.url + f'_{pincode}').encode()).hexdigest()
                    insert_query = f"""INSERT INTO pages (url, pincode, page_hash, status) VALUES ('{page.url}', '{pincode}', '{page_id}', 'pending')"""
                    local_cursor.execute(insert_query)
                    local_connect.commit()
                    continue
            except:
                pass

            try:
                if page.locator('//span[text()="CHECK"]').count() > 0:  # If element exists
                    page.locator('//span[text()="CHECK"]').click()
                else:
                    pass
            except:
                pass

            try:
                if page.locator('//span[@class="sc-eDvSVe dpdDrR ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu"]').count() > 0:
                    review = page.locator('//span[@class="sc-eDvSVe dpdDrR ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu"]')
                    review.scroll_into_view_if_needed()
                else:
                    pass
            except:
                pass

            time.sleep(2)
            try:
                if page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').count() > 0:
                    text_data = page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').first
                    print(text_data.text_content())
                    if 'Enter Pincode for Estimated Delivery Date' in text_data.text_content():
                        change_vpn(api, locations)
                        page_id = hashlib.sha256((page.url + f'_{pincode}').encode()).hexdigest()
                        insert_query = f"""INSERT INTO pages (url, pincode, page_hash, status) VALUES ('{page.url}', '{pincode}', '{page_id}', 'pending')"""
                        local_cursor.execute(insert_query)
                        local_connect.commit()
                        continue
            except:
                pass

            page_id = hashlib.sha256((page.url + f'_{pincode}').encode()).hexdigest()

            local_cursor.execute(f"SELECT * FROM pages WHERE url != '{link}'")
            local_connect.commit()
            if local_cursor.fetchone():

                insert_query = f"""INSERT INTO pages (url, pincode, page_hash, status) VALUES ('{page.url}', '{pincode}', '{page_id}', 'done')"""
                local_cursor.execute(insert_query)
                local_connect.commit()
            else:
                insert_query = f"""UPDATE INTO pages SET page_hash = '{page_id}' AND status = 'done' WHERE url = '{page.url}' VALUES ('{page.url}', '{pincode}', '{page_id}', 'done')"""
                local_cursor.execute(insert_query)
                local_connect.commit()

            with zipfile.ZipFile(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.zip', 'w',
                                 zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f'HTML_{page_id}.html', page.content())
            # random_wait()

# Main function to handle login and scraping
def main(pincode, start_id, end_id):
    if os.path.exists('9737090010_20241112.json'):
        scraper(pincode, start_id, end_id)
    else:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            fingerprints = FingerprintGenerator()
            fingerprint = fingerprints.generate()
            context = NewContext(browser, fingerprint=fingerprint)
            page = context.new_page()

            logged_in = login(page, context)
            if logged_in:
                print("Login successful!")
                scraper(pincode, start_id, end_id)
            else:
                print("Login failed!")
            browser.close()


if __name__ == "__main__":
    start_time = time.time()
    with ExpressVpnApi() as api:
        locations = api.locations
        main("560001", 1, 15000)


    end_time = time.time()

    print("Time :", end_time - start_time)
