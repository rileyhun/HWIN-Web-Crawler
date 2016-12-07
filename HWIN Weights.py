import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dateutil import parser

def HWIN_Weights_Extract(Logins, maximum_pages=40):

    Accounts = len(Logins)

    # URL address of site to be scraped
    url = 'https://www.hwin.ca/hwin/index.jsp'

    browser = webdriver.Firefox()

    # Loop through each individual account
    for i in range(0, Accounts):
        browser.get(url)
        username = browser.find_element_by_name("userName")
        username.send_keys(Logins[i][0])
        password = browser.find_element_by_name("password")
        password.send_keys(Logins[i][1])
        form = browser.find_element_by_name("btnLogin")
        form.click()

    # Find Generator ID
        html = browser.page_source
        GeneratorID = html.split('<b>Generator ID:</b>')[1].split('</span>')[0]

    # Find Address
        Address = html.split('</span></font><br /><span class="body10">')[1].split('</span></td><td height="43">')[0]

    # Navigate to the Closed Manifest tab
        browser.find_element_by_name("closedMan").click()

    # Find number of pages
        clickable_pages = browser.find_elements_by_css_selector("a[onclick*='return frmSubmit']")

        if len(browser.find_elements_by_css_selector("a[onclick*='return frmSubmit(26)']")) == 1:
            total_pages = maximum_pages
        else:
            total_pages = len(clickable_pages)+1

    # Scroll through pages
        for page in range(0, total_pages):

        # For each manifest link, retrieve the Waste Information
            waste_information = []

            wait = WebDriverWait(browser, 10)

            # Find all the Manifest Links
            TotalManifest_Links = len(browser.find_elements_by_css_selector("a[href*='rec_manifest']"))

            # Click into each manifest link to extract data
            for link in range(0, TotalManifest_Links):
                Manifest_Links = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR,
                                                                             "a[href*='rec_manifest']")))
                Manifest_Links[link].click()

                # extract table data from html source
                html = browser.page_source
                soup = BeautifulSoup(html)

                table = soup.find_all('table')[-4]
                table_body = table.find('tbody')
                rows = table_body.find_all('tr')
                waste_info = []

                for row in rows[4:-5]:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    waste_info.append([ele for ele in cols if ele])

                # extract "Date Shipped" for each manifest
                Date_Shipped = browser.find_elements_by_tag_name('b')[7].text

                # concatenate table data with Date, Generator ID, and Address
                for item in waste_info:
                    item.insert(0, Date_Shipped)
                    item.insert(1, GeneratorID)
                    item.insert(2, Address)

                waste_information.append(waste_info)

                # go back to page that lists all manifest links
                backbutton = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                          "a[href*='?CurrPage=']")))
                backbutton.click()

            # flatten list and convert to pandas dataframe
            waste_information = [item for sublist in waste_information for item in sublist]
            data = pd.DataFrame(waste_information)
            data.rename(columns={0: 'Date', 1: 'Generator ID', 2: 'Address',
                                 3: 'Waste Class', 4: 'Generator Quantity Shipped',
                                 5: 'Generator Units Shipped',
                                 6: 'Quantity Received', 7: 'Units Received', 8: 'Handling Code',
                                 9: 'Packaging Content', 10: 'Vehicle'}, inplace=True)

            # Convert Date String to Datetime Stamp
            data['Date'] = data['Date'].apply(lambda x: parser.parse(x, dayfirst=True))

            # Export to csv file
            if i==0 and page==0:
                data.to_csv("HWIN Manifest Data.csv", index=False, mode='a')
            else:
                data.to_csv("HWIN Manifest Data.csv", index=False, header=False, mode='a')

            # go to next page
            try:
                next_page = wait.until(EC.visibility_of_element_located((
                    By.CSS_SELECTOR, "a[onclick*='return frmSubmit("+str(page+2)+")']")))
                next_page.click()
            except Exception as e:
                pass

        # go back to login page
        browser.get(url)

# This is the Login information
Logins = [("riley123", "test"), ("riley456", "test")]

# Call function
HWIN_Weights_Extract([('roh57', 'cml')], 1)






