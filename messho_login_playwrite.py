import datetime
import sys
import time
from datetime import datetime, timedelta
from selenium import webdriver
# from seleniumbase import Driver

import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, os
import pandas as pd
import pymysql
import pickle
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from selenium_stealth import stealth
import random
import hashlib
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import FingerprintGenerator
from browserforge.injectors.playwright import NewContext



start_time = datetime.now()


scraped_data_count = 1
starting_position = 0
pos = 1
login_successful = False
processing_complete = False

filename = 'session_storage1.json'

def random_waite():
    random_time_list = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    ran_tim = random.choice(random_time_list)
    # time.sleep(ran_tim)

def small_random_waite():
    # random_time_list = [1, 2, 3, 4]
    random_time_list = [0.2,0.3,0.4,0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


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
page_hash varchar(500))''')
local_connect.commit()



def login(page, context):
    global login_successful
    login_successful = False

    def login_handle_traffic(response):
        global login_successful
        if 'verify.json' in response.url:
            print(f"Login verification response received from: {response.url}")
            login_successful = True

    # Listen to all network responses
    page.on('response', login_handle_traffic)

    # Navigate to the login page
    page.goto('https://www.meesho.com/auth')

    phone_number = '9879361219' # hrithik
    # phone_number = '6354521692' # jaymin
    # phone_number = '6359015644' # karan
    # phone_number = '6352290451' # Nirmal
    # phone_number = '9737090010' # Suraj
    # phone_number = '6204387213' # deekshant

    # Fill mobile number
    # page.locator('//input[@type="tel"]').fill('6354786744')  # EDIT THIS
    page.locator('//input[@type="tel"]').fill(phone_number)  # EDIT THIS
    # page.locator('//input[@type="tel"]').fill('6354521692')  # EDIT THIS
    page.locator('//button[@type="submit"]').click()

    # Wait for the user to input the OTP
    otp = input(f'{phone_number} Enter OTP: ')
    for index in range(len(otp)):
        page.locator(f'//input[@type="tel"][{index + 1}]').fill(otp[index])

    # Wait for the login process to complete
    time.sleep(5)
    date = datetime.now().strftime('%Y%m%d')
    # Save cookies after successful login
    if login_successful:
        context.storage_state(path=f"{phone_number}_{date}.json")  # Save session cookies

    return login_successful


def main(pincode, start_id, end_id):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        fingerprints = FingerprintGenerator()
        fingerprint = fingerprints.generate()

        # Use saved cookies/session data if exists
        context = NewContext(browser, fingerprint=fingerprint)  # Create a single browser context

        # Perform login on the first tab
        page = context.new_page()
        logged_in = login(page, context)

        if logged_in:
            print("Login successful!")
        else:
            print("Login failed or no response detected!")
        browser.close()


def create_profile(profile_id):
    base_profile_path = os.path.join(os.getcwd(), "chrome_profiles")
    profile_path = os.path.join(base_profile_path, f"profile_{profile_id}")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    return profile_path


if __name__ == '__main__':
    # start_id = sys.argv[1]
    # end_id = sys.argv[2]
    # pincode = sys.argv[3]
    start_id = 0
    end_id = 1000
    pincode = 560001
    main(pincode=pincode, start_id=start_id, end_id=end_id)

    end_time = datetime.now()

    print('Total taken time :', end_time - start_time)


