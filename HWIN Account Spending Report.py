import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

def HWIN_Spending_Report(GeneratorID, Username, Password, Max_Pages):

    url = 'https://www.hwin.ca/hwin/index.jsp'

    browser = webdriver.Firefox()
    browser.get(url)

    max_pages = Max_Pages
    # Sign into each individual account
    for i in range(0, len(Username)):

    # Input Login information into form
        username = browser.find_element_by_name("userName")
        username.send_keys(Username[i])
        password = browser.find_element_by_name("password")
        password.send_keys(Password[i])
        form = browser.find_element_by_name("btnLogin")
        form.click()

        # Find Generator ID
        html = browser.page_source
        GeneratorID = html.split('<b>Generator ID:</b>')[1].split('</span>')[0]

        # Find Address
        Address = html.split('</span></font><br /><span class="body10">')[1].split('</span></td><td height="43">')[0]

        # Navigate to Account Status Tab
        browser.find_element_by_link_text("Account status").click()

        # Find number of pages
        clickable_pages = browser.find_elements_by_css_selector("a[onclick*='return frmSubmit']")

        if len(browser.find_elements_by_css_selector("a[onclick*='return frmSubmit(26)']")) == 1:
            total_pages = max_pages
        else:
            total_pages = len(clickable_pages)+1

        all_page_data = []
        for page in range(0, total_pages):

            wait = WebDriverWait(browser, 10)

            # Extract Account Status Tab
            html = browser.page_source
            soup = BeautifulSoup(html)
            table = soup.find('table', border="0", cellpadding="2")
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            single_page_data =[]

            for row in rows[1:-2]:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                single_page_data.append([ele for ele in cols if ele])

            for item in single_page_data:
                item.insert(0, GeneratorID)
                item.insert(1, Address)

            all_page_data.append(single_page_data)

             # go to next page
            try:
                next_page = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "a[onclick*='return frmSubmit("+str(page+2)+")']")))
                next_page.click()
            except Exception as e:
                pass

        # flatten list and convert to pandas dataframe
        all_page_data = [item for sublist in all_page_data for item in sublist]
        data = pd.DataFrame(all_page_data)
        data.rename(columns={0: 'Generator ID', 1: 'Address', 2: 'Date',
                                     3: 'Transaction Type', 4: 'Manifest No.',
                                     5: 'Date Shipped',
                                     6: 'Payment Type', 7: 'Amount', 8: 'Prepaid Balance'}, inplace=True)

        # Export to csv file
        if i==0:
            data.to_csv("Account Status "+"{:%B %d, %Y}".format(datetime.now())+".csv", index=False, mode='a')
        else:
            data.to_csv("Account Status "+"{:%B %d, %Y}".format(datetime.now())+".csv", index=False, header=False, mode='a')

        # Navigate to Payments Tab
        browser.find_element_by_name("payments").click()
        # Extract Payment data
        html = browser.page_source
        soup = BeautifulSoup(html)

        if soup.find(text="There is no pending manifest payment") is not None:
            payment_data = [["$0", GeneratorID]]
        else:
            amount = soup.find('td', {'class': 'bodytext'}, width="35%")
            payment_data = [[amount.text.replace("Total amount due:", ""), GeneratorID]]

        # Export Payment Data to spreadsheet
        data2 = pd.DataFrame(payment_data, columns=["Payment Due?", "Generator ID"])
        if i==0:
            data2.to_csv("Payment Due "+"{:%B %d, %Y}".format(datetime.now())+".csv", index=False, mode="a", header=True)
        else:
            data2.to_csv("Payment Due "+"{:%B %d, %Y}".format(datetime.now())+".csv", index=False, mode="a", header=False)

        # go back to main page
        browser.get(url)

    # close browser
    browser.quit()

#Read account information from spreadsheet
data = pd.read_csv("Logins.csv")
data.columns = ['Generator ID', 'Username', 'Password']
data.dropna(inplace=True)

# Parameters to be called
Username = data['Username']
Password = data['Password']
ID = data['Generator ID']

HWIN_Spending_Report(ID, Username, Password, 50)
