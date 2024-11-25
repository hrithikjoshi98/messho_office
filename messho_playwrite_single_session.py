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
        if '9879361219_20241121.json' in response.url:
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
        context.storage_state(path="9879361219_20241121.json")

    return login_successful



def change_vpn(api, locations):
    loc = random.choice(locations)
    api.connect(loc["id"])
    time.sleep(5)
    print(f'{loc} VPN connected')


def wait_for_h1_update(page, selector, old_text, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_text = page.text_content(selector)
        if current_text and current_text != old_text:
            return current_text
        time.sleep(0.5)
    # raise TimeoutError("H1 did not update within the timeout period")
    return "Enter Pincode for Estimated Delivery Date"

# Scraper function using Playwright
def scraper(pincode, start_id, end_id):

    with open('9879361219_20241121.json', 'r') as f:
        session_data = json.load(f)
    session_datas = {}
    lis = []
    for p, i in enumerate(session_data['cookies']):
        print(i['name'])
        i['expires'] = -1
        lis.append(i)

    session_datas['cookies'] = lis


    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=False, )
        context = NewContext(browser, fingerprint=fingerprint)
        # context = NewContext(browser)
        # Tarnished.apply_stealth(context)
        page = context.new_page()
        # Load session cookies
        context.add_cookies(session_datas['cookies'])

        query = f"SELECT Product_Url_MEESHO FROM `template_20241017_distinct_status` WHERE In_Stock_Status_MEESHO  = 'true'"
        cursor.execute(query)
        rows = cursor.fetchall()

        for pos, link_ in enumerate(rows):

            link = link_[0]

            local_cursor.execute("SELECT * FROM pages WHERE url = %s AND status = %s", (link, 'done'))
            local_connect.commit()
            print(f'\n{pos} --- {link}')
            if local_cursor.fetchone():
                print('url already scraped...', '\n')
                continue

            page.goto(link)

            try:
                if page.locator('//h1[contains(text(), "Access Denied")]').count() > 0:
                    review = page.locator('//h1[contains(text(), "Access Denied")]').first
                    if 'access denied' in review.text_content().lower():
                        print('access denied')
                        # change_vpn(api, locations)
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

            try:
                if page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').count() > 0:
                    # with page.expect_navigation():
                    text_data = page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').first

                    new_text = wait_for_h1_update(page, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]', text_data.text_content(), timeout=10)
                    print(new_text)
                    if 'Enter Pincode for Estimated Delivery Date' in new_text:
                        # change_vpn(api, locations)
                        continue
                    page_id = str(link).split('/')[-1] + f'_{pincode}'

                    insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
                    local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
                    local_connect.commit()
                    # update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
                    # cursor.execute(update_query, (link,))
                    # connect.commit()

                    with zipfile.ZipFile(fr'C:\project_files\meesho_project\shipping_page\{page_id}' + '.zip', 'w',
                                         zipfile.ZIP_DEFLATED) as zip_file:
                        zip_file.writestr(f'HTML_{page_id}.html', page.content())
            except Exception as e:
                print("Known Exception", e)




# Main function to handle login and scraping
def main(pincode, start_id, end_id):
    scraper(pincode, start_id, end_id)


if __name__ == "__main__":
    start_time = time.time()
    with ExpressVpnApi() as api:
        locations = api.locations
        # change_vpn(api, locations)
        main("560001", 1, 15000)


    end_time = time.time()

    print("Time :", end_time - start_time)