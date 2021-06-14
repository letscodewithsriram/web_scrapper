import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googleapiclient.discovery import build
from google.oauth2 import service_account
from selenium.webdriver.common.by import By
from inspect import currentframe, getframeinfo


# def get_options(driver, url, xpath, master):
#     print (master)
#     for line in master:
#         ITEM_NAME = line[1]
#         print (ITEM_NAME)
#         driver.find_element_by_link_text(ITEM_NAME).click()
#         time.sleep(10)
#         obj = driver.find_elements(By.TAG_NAME, "label")
#         OPTION_DUMPS = [x.text for x in obj if x.text and not re.search("Special instructions|Search restaurants or dishes", x.text)]
#         print(OPTION_DUMPS)
#         driver.quit()
#         time.sleep(30)
#         exit(0)
#     return None

def get_options(item_name):
    # item_name = "Pita with Tzatziki"
    print (item_name)
    # driver.find_element_by_xpath("//*[@id='chiri-modal']/div/div/div[2]/div[3]/a").click()
    driver.find_element_by_link_text(item_name).click()
    print(driver.current_url)
    time.sleep(10)
    obj = driver.find_elements(By.TAG_NAME, "label")
    OPTION_DUMPS = [x.text for x in obj if
                    x.text and not re.search("Special instructions|Search restaurants or dishes", x.text)]
    # print (OPTION_DUMPS)
    driver.find_element_by_xpath("/html/body/ghs-modal-backdrop/ghs-modal-container/div/dialog/ghs-modal-content/span/span/span/ghs-lazy/ghs-menu-item-add/form/div/div/header/nav/button").click()
    return OPTION_DUMPS


def selenium_work_load(driver, url, xpath):
    """
    :param driver: Chrome Driver Information and Headless mode details; Type - Object
    :param url: Grub Hub ; Type - String
    :param xpath: Xpath of the Main Menu; Type - String
    :return: Array of arrays; Type - [[list1][list2]] viz. nested lists
    """
    driver.get(url)
    driver.maximize_window()  # For maximizing window
    driver.implicitly_wait(20)  # gives an implicit wait for 20 seconds
    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

    driver.find_element_by_xpath("//*[@id='Site']/ghs-site-container/span/span/span[3]/ghs-app-content/div[2]/ghs-main-nav/span[2]/span/div/div/button").click()
    driver.find_element_by_xpath("//*[@id='email']").send_keys("sri89jam@gmail.com")
    driver.find_element_by_xpath("//*[@id='password']").send_keys("GrubHub@23")
    driver.find_element_by_xpath("//*[@id='Site']/ghs-modal-backdrop/ghs-modal-container/div/dialog/ghs-modal-content/span/div/div/span/ghs-lazy/span/span/div/div/span/span/span/form/span/div/div[3]/div/button").click()
    for i in range(0,10,1):
        time.sleep(10)

    web_dumps = driver.find_element_by_xpath(xpath).text.split('\n')

    menu_types = ['Top Menu Items', 'Starters', 'The Pita Sandwiches', 'The Mad Greek Signature Salads', 'The Dinners',
                  'Pita Burgers, Hoagies, & Sandwiches', 'Classic Burgers and On a Bun', 'Drinks', 'Sides and Extras',
                  'Desserts', 'Kids Menu']

    master = [[]]
    for i in range(0, len(web_dumps), 1):
        line = web_dumps[i].strip()
        if line in menu_types:
            i = i + 1
            menu_item = line
            continue
        if re.search("^\$", line):
            if not re.search("^\$", web_dumps[i - 2]) and not re.search("Top Menu Items", web_dumps[i - 2]):
                item_rate = line.replace("$","").replace("+","")
                item_name = web_dumps[i - 2]
                item_info = web_dumps[i - 1]
            else:
                item_rate = line.replace("$","").replace("+","")
                item_name = web_dumps[i - 1]
                item_info = ""

            # for option in get_options(item_name):'
            for option in get_options(item_name):
                # print(option)
                if re.search ("\+", option):
                    option_name = option.split('+')[0]
                    option_rate = option.split('+')[1]
                else:
                    option_name = option
                    option_rate = ""
                master.append([menu_item, item_name, item_info, item_rate, option_name, option_rate])
                print (master)

    # driver.find_element_by_link_text('Dismiss').click()
    return master


def gsheets_endpoint(aoa, creds, SAMPLE_SPREADSHEET_ID):
    """
    :param aoa:
    :return:
    """
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    headers = [[]]

    header_request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range="Sheet3!A2",
                                           valueInputOption="USER_ENTERED",
                                           body={"values": [["Category","Item Name", "Description", "Item Price", "Options", "Options Rate"]]})\
                                   .execute()

    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Sheet3!A2",
                                    valueInputOption="USER_ENTERED",
                                    body={"values": aoa})\
                            .execute()


if __name__ == '__main__':
    """
    Main Function - Calling two sub functions viz, selenium_work_load & gsheets_endpoints
    Function 1: selenium_work_load 
    Function 2: gsheets_endpoint
    """
    frameinfo = getframeinfo(currentframe())
    options = Options()
    # options.headless = True
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(executable_path="C:\Drivers\chromedriver_win32\chromedriver.exe", options=options)

    url = "https://www.grubhub.com/restaurant/the-mad-greek-cafe-of-charlotte-5011-south-blvd-charlotte/2159864"

    xpath = "/html/body/ghs-site-container/span/span/span[3]/ghs-app-content/div[3]/div/ghs-router-outlet/ghs-restaurant-provider/ghs-restaurant-data/div/div[1]/div/main/div[4]/span/span/div/div/div/div/div/span/ghs-impression-tracker/span/div"
    master_aoa = selenium_work_load(driver, url, xpath)
    print (master_aoa)
    print (master_aoa[1:])

    aoa = get_options(driver, url, xpath, master_aoa[1:])

    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SAMPLE_SPREADSHEET_ID = "1f6s_q4LKbK12Ar3KMzLj4jiu-iQ6A4_H50f3RIdxIGs"

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gsheets_endpoint(master_aoa, credentials, SAMPLE_SPREADSHEET_ID)

