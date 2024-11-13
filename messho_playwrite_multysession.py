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


def session1():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)
    with open('6204387213_20241112.json', 'r') as f:
        data = f.read()
        cookie = json.loads(data)
    context.add_cookies(cookie['cookies'])
    page = context.new_page()
    return page

def session2():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)
    with open('6352290451_20241112.json', 'r') as f:
        data = f.read()
        cookie = json.loads(data)
    context.add_cookies(cookie['cookies'])
    page = context.new_page()
    return page

def session3():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)
    with open('6359015644_20241112.json', 'r') as f:
        data = f.read()
        cookie = json.loads(data)
    context.add_cookies(cookie['cookies'])
    page = context.new_page()
    return page

def session4():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)
    with open('9737090010_20241112.json', 'r') as f:
        data = f.read()
        cookie = json.loads(data)
    context.add_cookies(cookie['cookies'])
    page = context.new_page()
    return page


def scrapping(page, pincode, pos, pid):
    link = f'https://www.meesho.com/s/p/{pid[0]}'

    local_cursor.execute(f"SELECT * FROM pages WHERE url = '{link}' and status = 'done'")
    local_connect.commit()
    print(f'\n{pos} --- {link}')
    if local_cursor.fetchone():
        print('URL already scraped')
        return
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
                return
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
            return
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
        if page.locator(
            '//span[@class="sc-eDvSVe dpdDrR ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu"]').count() > 0:
            review = page.locator(
                '//span[@class="sc-eDvSVe dpdDrR ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu ShopCardstyled__ShopName-sc-du9pku-6 bdcHGu"]')
            review.scroll_into_view_if_needed()
        else:
            pass
    except:
        pass

    time.sleep(2)
    try:
        if page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').count() > 0:
            text_data = page.locator(
                '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').first
            print(text_data.text_content())
            if 'Enter Pincode for Estimated Delivery Date' in text_data.text_content():
                change_vpn(api, locations)
                page_id = hashlib.sha256((page.url + f'_{pincode}').encode()).hexdigest()
                insert_query = f"""INSERT INTO pages (url, pincode, page_hash, status) VALUES ('{page.url}', '{pincode}', '{page_id}', 'pending')"""
                local_cursor.execute(insert_query)
                local_connect.commit()
                return
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


def create_session(browser, cookie_file):
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    context = NewContext(browser, fingerprint=fingerprint, user_agent=user_agent)

    # Load cookies for the session
    with open(cookie_file, 'r') as f:
        cookie_data = json.load(f)
    context.add_cookies(cookie_data['cookies'])

    # Open a new page with the current context
    page = context.new_page()
    return context, page

# Scraper function using Playwright
def scraper(pincode, start_id, end_id):


    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        # context = browser.new_context(
        #     user_agent=user_agent
        # )
        # Create multiple sessions using different cookies
        context1, page1 = create_session(browser, '6204387213_20241112.json')
        context2, page2 = create_session(browser, '6352290451_20241112.json')
        context3, page3 = create_session(browser, '6359015644_20241112.json')
        context4, page4 = create_session(browser, '9737090010_20241112.json')


        query = f"SELECT meesho_pid FROM product_links_20240927 WHERE status='Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"
        cursor.execute(query)
        rows = cursor.fetchall()
        co_p = 1
        for pos, pid in enumerate(rows):

            if co_p == 1:
                scrapping(page1, pincode, pos, pid)
            if co_p == 2:
                scrapping(page2, pincode, pos, pid)
            if co_p == 3:
                scrapping(page3, pincode, pos, pid)
            if co_p == 4:
                scrapping(page4, pincode, pos, pid)
                co_p = 0
            co_p += 1



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
