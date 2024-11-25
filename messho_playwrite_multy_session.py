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
import gzip
from undetected_playwright import Tarnished
from evpn import ExpressVpnApi
from sys import argv


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


def change_vpn(api, locations):
     # get available locations
    loc = random.choice(locations)
    api.connect(loc["id"])
    time.sleep(5)

def wait_for_h1_update(page, selector, old_text, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_text = page.text_content(selector)
        if current_text and current_text != old_text:
            return current_text
        # time.sleep(0.1)
    # raise TimeoutError("H1 did not update within the timeout period")
    return "Enter Pincode for Estimated Delivery Date"

val_list = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000]

def scrapping(page, context, cookie_file, pincode, pos, link_):
    # link = f'https://www.meesho.com/s/p/{pid[0]}'
    link = link_[0]
    local_cursor.execute("SELECT * FROM pages WHERE url = %s AND status = %s", (link, 'done'))
    local_connect.commit()
    print(f'\n{pos} --- {cookie_file} --- {link}')
    if local_cursor.fetchone():
        print('url already scraped...', '\n')
        return
    # page.goto(link)
    # page.set_cache_enabled(True)
    # page.goto(link.replace('https', 'http'), wait_until="domcontentloaded")
    page.goto(link.replace('https', 'http'))
    try:
        if page.locator('//h1[contains(text(), "Access Denied")]').count() > 0:
            review = page.locator('//h1[contains(text(), "Access Denied")]').first
            if 'access denied' in review.text_content().lower():
                print('access denied')
                # change_vpn(api, locations)
                return
    except:
        pass

    # val = random.choice(val_list)
    # page.mouse.wheel(0, val)

    try:
        # Input the pincode
        if page.locator('//input[@id="pin"]').count() > 0:  # If element exists
            page.locator('//input[@id="pin"]').fill(pincode)
            # page.wait_for_selector('//input[@id="pin"]').fill(pincode)
        else:
            print(f'Input not available for {pincode}')
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

    # val = random.choice(val_list)
    # page.mouse.wheel(0, val)


    try:
        if page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').count() > 0:
            # with page.expect_navigation():
            text_data = page.locator(
                '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').first

            new_text = wait_for_h1_update(page,
                                          '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]',
                                          text_data.text_content(), timeout=3)
            print(new_text)
            if 'Enter Pincode for Estimated Delivery Date' in new_text:
                # change_vpn(api, locations)
                return
            page_id = str(link).split('/')[-1] + f'_{pincode}'

            insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
            local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
            local_connect.commit()
            # update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
            # cursor.execute(update_query, (link,))
            # connect.commit()

            with gzip.open(fr'C:\project_files\meesho_project\shipping_page\{page_id}' +'.html.gz', 'w') as save:
                save.write(bytes(page.content().encode()))

    except Exception as e:
        print("Known Exception", e)


def create_session(browser, cookie_file):
    fingerprints = FingerprintGenerator()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    # fingerprint = fingerprints.generate()
    fingerprint = fingerprints.generate(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')


    context = NewContext(browser, fingerprint=fingerprint)

    # Load cookies for the session
    with open(cookie_file, 'r') as f:
        cookie_data = json.load(f)
    context.add_cookies(cookie_data['cookies'])

    def block_assets(route, request):
        if request.resource_type in ["stylesheet", "font", "image"] or request.url.endswith(".css") or request.url.endswith(".webp") or request.url.endswith(".woff2"):
            route.abort()
        else:
            route.continue_()

    page = context.new_page()
    page.route("**/*", block_assets)
    return context, page, cookie_file

# Scraper function using Playwright
def scraper(pincode, start_id, end_id, pos):


    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        # Create multiple sessions using different cookies
        try:
            if pos == 1:
                context1, page1, cookie_file1 = create_session(browser, '6204387213.json')
                # context2, page2, cookie_file2 = create_session(browser, '6359015644.json')
                # context3, page3, cookie_file3 = create_session(browser, '7096488183.json')
                # context4, page4, cookie_file4 = create_session(browser, '7226063206.json')
            if pos == 2:
                context1, page1, cookie_file1 = create_session(browser, '7359427389.json')
                # context2, page2, cookie_file2 = create_session(browser, '7359757545.json')
                # context3, page3, cookie_file3 = create_session(browser, '7567926255.json')
                # context4, page4, cookie_file4 = create_session(browser, '7600511244.json')
            if pos == 3:
                context1, page1, cookie_file1 = create_session(browser, '7802074179.json')
                # context2, page2, cookie_file2 = create_session(browser, '9106737598.json')
                # context3, page3, cookie_file3 = create_session(browser, '9404408848.json')
                # context4, page4, cookie_file4 = create_session(browser, '9420848973.json')
            if pos == 4:
                context1, page1, cookie_file1 = create_session(browser, '9665146718.json')
                # context2, page2, cookie_file2 = create_session(browser, '9725719468.json')
                # context3, page3, cookie_file3 = create_session(browser, '9824818225.json')
                # context4, page4, cookie_file4 = create_session(browser, '9879361219.json')
            if pos == 5:
                context1, page1, cookie_file1 = create_session(browser, '9404408848.json')
                # context2, page2, cookie_file2 = create_session(browser, '9420848973.json')
                # context3, page3, cookie_file3 = create_session(browser, '9404408848.json')
                # context4, page4, cookie_file4 = create_session(browser, '9420848973.json')
            if pos == 6:
                context1, page1, cookie_file1 = create_session(browser, '9824818225.json')
                # context2, page2, cookie_file2 = create_session(browser, '9879361219.json')
                # context3, page3, cookie_file3 = create_session(browser, '9824818225.json')
                # context4, page4, cookie_file4 = create_session(browser, '9879361219.json')
        except Exception as e:
            print(e)

        # query = f"SELECT meesho_pid FROM product_links_20240927 WHERE status='Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"
        # query = f"SELECT Product_Url_MEESHO FROM `template_20241017_distinct_status` WHERE In_Stock_Status_MEESHO  = 'true'"
        query = f"SELECT Product_Url_MEESHO FROM `template_20241017_distinct_status` WHERE In_Stock_Status_MEESHO  = 'true' AND id BETWEEN {start_id} AND {end_id}"
        cursor.execute(query)
        rows = cursor.fetchall()
        co_p = 1
        for poss, link_ in enumerate(rows):

            if co_p == 1:
                scrapping(page1, context1, cookie_file1, pincode, poss, link_)
                co_p = 0
            # if co_p == 2:
            #     scrapping(page2, context2, cookie_file2, pincode, poss, link_)
            #     co_p = 0
            # if co_p == 3:
            #     scrapping(page3, context3, cookie_file3, pincode, pos, link_)
            # if co_p == 4:
            #     scrapping(page4, context4, cookie_file4, pincode, pos, link_)
            #     co_p = 0
            co_p += 1

        browser.close()



# Main function to handle login and scraping
def main(pincode, start_id, end_id, pos):
    scraper(pincode, start_id, end_id, pos)


if __name__ == "__main__":
    start_time = time.time()

    try:
        start = int(argv[1])
        end = int(argv[2])
        pos = int(argv[3])
        # print(start, end, pos)
    except:
        start = 1
        end = 50
        pos = 1

    with ExpressVpnApi() as api:
        locations = api.locations
        main("560001", start, end, pos)


    end_time = time.time()

    print("Time :", end_time - start_time)