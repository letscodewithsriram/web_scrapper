"""
Author: Sriram Ramanujam
Date: 14th June 2021
Script Name: grubhub_web_extraction.py
Script Description: Script will extract the food items and its rates from Grubhub.com.
Finally parsed data-points will be pushed into Google Sheets through pre-configured API's.

PyLint Score: Your code has been rated at 8.59/10 (previous run: 8.57/10, +0.02)

"""

import re
import time
from inspect import currentframe, getframeinfo
from googleapiclient.discovery import build
from google.oauth2 import service_account
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



def get_options(item_name):
    """
    get_options function is used get the options details from each possible menu items
    :param item_name: name of the item for which food options need to be extracted
    :return: option_dumps - Array with food item options and rates
    """
    # item_name = "Pita with Tzatziki"
    print (item_name)
    driver.find_element_by_link_text(item_name).click()
    time.sleep(10)
    obj = driver.find_elements(By.TAG_NAME, "label")
    option_dumps = [x.text for x in obj if
                    x.text and not re.search("Special instructions|Search restaurants or dishes",
                                             x.text)]
    driver.find_element_by_xpath("/html/body/ghs-modal-backdrop/ghs-modal-container"
                                 "/div/dialog/ghs-modal-content/span/span/span/ghs-lazy"
                                 "/ghs-menu-item-add/form/div/div/header/nav/button").click()
    # driver.refresh()
    return option_dumps


def selenium_work_load(fn_driver, fn_url_path, fn_x_path):
    """
    selenium_work_load is used to extract the data from GrubHub website using Selenium driver.
    URL: https://www.grubhub.com/restaurant/
    the-mad-greek-cafe-of-charlotte-5011-south-blvd-charlotte/2159864

    :param fn_driver: Chrome Driver Information and Headless mode details; Type - Object
    :param fn_url_path: Grub Hub ; Type - String
    :param xpath: Xpath of the Main Menu; Type - String
    :return: Array of arrays; Type - [[list1][list2]] viz. nested lists
    """
    fn_driver.get(fn_url_path)
    fn_driver.maximize_window()  # For maximizing window
    fn_driver.implicitly_wait(20)  # gives an implicit wait for 20 seconds
    fn_driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

    fn_driver.find_element_by_xpath("//*[@id='Site']/ghs-site-container/span/span/span[3]"
                                 "/ghs-app-content/div[2]/ghs-main-nav/span[2]/span/div"
                                 "/div/button").click()
    fn_driver.find_element_by_xpath("//*[@id='email']").send_keys("sri89jam@gmail.com")
    fn_driver.find_element_by_xpath("//*[@id='password']").send_keys("GrubHub@23")
    fn_driver.find_element_by_xpath("//*[@id='Site']/ghs-modal-backdrop/ghs-modal-container"
                                 "/div/dialog/ghs-modal-content/span/div/div/span/ghs-lazy"
                                 "/span/span/div/div/span/span/span/form/span/div/div[3]"
                                 "/div/button").click()
    # for i in range(0,10,1):
    #     time.sleep(10)

    web_dumps = fn_driver.find_element_by_xpath(fn_x_path).text.split('\n')

    menu_types = ['Top Menu Items', 'Starters', 'The Pita Sandwiches',
                  'The Mad Greek Signature Salads', 'The Dinners',
                  'Pita Burgers, Hoagies, & Sandwiches',
                  'Classic Burgers and On a Bun', 'Drinks',
                  'Sides and Extras',
                  'Desserts', 'Kids Menu']

    master = [[]]
    for i in range(0, len(web_dumps), 1):
        line = web_dumps[i].strip()
        if line in menu_types:
            i = i + 1
            menu_item = line
            continue
        if re.search(r"^\$", line):
            if not re.search(r"^\$", web_dumps[i - 2]) and \
                    not re.search("Top Menu Items", web_dumps[i - 2]):
                item_rate = line.replace(r"\$", "").replace(r"\+", "")
                item_name = web_dumps[i - 2]
                item_info = web_dumps[i - 1]
            else:
                item_rate = line.replace(r"\$", "").replace(r"\+", "")
                item_name = web_dumps[i - 1]
                item_info = ""

            # for option in get_options(item_name):'
            for option in get_options(item_name):
                # print(option)
                if re.search(r"\+", option):
                    option_name = option.split('+')[0]
                    option_rate = option.split('+')[1]
                else:
                    option_name = option
                    option_rate = ""
                master.append([menu_item, item_name,
                               item_info, item_rate,
                               option_name, option_rate])
                print (master)
    return master


def gsheets_endpoint(aoa, creds, spreadsheet_id):
    """
    Prerequistie: Complete the Google API service configuration
    on Dev Console before you start working on Python code

    gsheets_endpoints function used to push Array of Arrays
    to Google Sheets via pre-configured API endpoints

    Authentication using OAuth2
    :param aoa: Array of Arrays for Google Sheet input
    :return: None
    """
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    sheet.values().update(spreadsheetId=spreadsheet_id,
                                           range="Sheet3!A2",
                                           valueInputOption="USER_ENTERED",
                                           body={"values": [["Category","Item Name",
                                                             "Description", "Item Price",
                                                             "Options", "Options Rate"]]})\
                                   .execute()

    sheet.values().update(spreadsheetId=spreadsheet_id,
                                    range="Sheet3!A2",
                                    valueInputOption="USER_ENTERED",
                                    body={"values": aoa})\
                            .execute()


if __name__ == '__main__':
    frameinfo = getframeinfo(currentframe())
    options = Options()
    # options.headless = True
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(executable_path="C:\\Drivers\\chromedriver_win32\\chromedriver.exe",
                              options=options)

    URL_PATH = "https://www.grubhub.com/restaurant/" \
               "the-mad-greek-cafe-of-charlotte-5011-south-blvd-charlotte/" \
               "2159864"
    s = "print(\"Hello, World!\")"
    exec s
    
    def delete_product(product_id, user):
        assert user.is_admin(), 'Must have admin privileges to delete'
        assert store.product_exists(product_id), 'Unknown product id'
        store.find_product(product_id).delete()
    
    f = open("/tmp/hello.yaml", "r")
    f.close()
    X_PATH = "/html/body/ghs-site-container/span/span/span[3]" \
            "/ghs-app-content/div[3]/div/ghs-router-outlet/" \
            "ghs-restaurant-provider/ghs-restaurant-data/" \
            "div/div[1]/div/main/div[4]/span/span/div/div/" \
            "div/div/div/span/ghs-impression-tracker/span/div"
    master_aoa = selenium_work_load(driver, URL_PATH, X_PATH)
    master_aoa = master_aoa[1:]

    gsaoa = get_options(driver, URL_PATH, X_PATH, master_aoa)

    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SAMPLE_SPREADSHEET_ID = "1f6s_q4LKbK12Ar3KMzLj4jiu-iQ6A4_H50f3RIdxIGs"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    gsheets_endpoint(gsaoa, credentials, SAMPLE_SPREADSHEET_ID)
