# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 14:45:07 2019

@author: Sasank Maganti

Module to scrape the Idaho search portal
"""



from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import logging

#Log file config
logging.basicConfig(filename='scraper_logs.log',
                    filemode='w',
                    format='%(levelname)s - %(message)s')

def extract_table_contents(driver, original_window, output, current_trs):
    '''
    funtion to extract the required fields from the trs
    :param: output file handler, trs (used to extract the data)
    :return: None. The funtion writes the output directly to file 
    (No memory usage for forming tables in memory)
    '''
    
    #Extraction process for each tr
    for tr in current_trs:
        
        #Get the tds
        td = tr.find_elements_by_xpath(".//td")
        
        #Proceed only if the tds available are 9. Based on manual lookup
        #This check also makes sure error is not encountered when the page is not loaded
        if len(td)==9:
            
            #Extract license number, license type and status
            lic_no = td[6].text
            lic_typ = td[7].text
            status = td[8].text
            name = td[1].text
            
            #Click on the name to get further details
            try:
                td[0].find_element_by_link_text(name).click()
            except Exception as e:
                logging.error('Error clicking name {}. Exception: {}'.format(name,
                              e))
            
            #DOM path to name fields
            names_tr_path = "/html/body/form/table/tbody/tr[2]/td[2]/"+\
            "table[2]/tbody/tr[4]/td/span/table/tbody/tr/td/table/tbody/tr[1]"
            
            #Wait until another window (tab) opens for further details
            WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
            #New window handle
            window_after = driver.window_handles[1]
            
            #switch to new window
            driver.switch_to.window(window_after)
            
            #Wait until all page is loaded
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located\
                         ((By.XPATH, names_tr_path)))

            #Get the tr for name fields
            names = driver.find_elements_by_xpath(names_tr_path)
            
            #Get the tds for name fields and extract them
            error_names = True
            try:
                name_tds = names[0].find_elements_by_xpath(".//td")
                error_names = False
            except IndexError:
                logging.error('Details page not loaded for name: {}'.\
                              format(name))
            
            if not error_names:
                first = name_tds[3].text
                middle = name_tds[5].text
                last = name_tds[7].text
            
            #DOM path for tr containing issue and expiry dates
            issue_expiry_tr_path = "/html/body/form/table/tbody/tr[2]/"+\
            "td[2]/table[2]/tbody/tr[10]/td/span/table/tbody/tr/td/table/tbody/tr[3]"
            
            #Extract the dates
            dates = driver.find_elements_by_xpath(issue_expiry_tr_path)
            
            error_dates = True
            try:
                date_tds = dates[0].find_elements_by_xpath(".//td")
                error_dates = False
            except IndexError:
                logging.error('Details page not loaded for name: {}'.\
                              format(name))
            
            if not error_dates:
                issue = date_tds[3].text
                expiry = date_tds[5].text
            
            #DOM path for tr containing renewal dates
            renew_tr_path = "/html/body/form/table/tbody/tr[2]/td[2]/"+\
            "table[2]/tbody/tr[10]/td/span/table/tbody/tr/td/table/tbody/tr[4]"
            
            #Extract the dates
            renew_dates = driver.find_elements_by_xpath(renew_tr_path)
            
            error_renew = True
            try:
                renew_tds = renew_dates[0].find_elements_by_xpath(".//td")
                error_renew = False
            except IndexError:
                logging.error('Details page not loaded for name: {}'.\
                              format(name))
               
            if not error_renew:
                renew = renew_tds[5].text
            
            #Close the tab and switch to original window
            driver.close()
            driver.switch_to.window(original_window)
            
            #Write the extracted fields to the output file
            if (not error_names) & (not error_dates) & (not error_renew):
                record_line = first + ',' + middle + ',' + last + ',' +\
                                lic_no +','+\
                                lic_typ +','+\
                                status +','+\
                                issue + ',' + expiry + ',' +\
                                renew                
                output.write(record_line+'\n')

def scrape_idaho():
    '''
    Function to scrape data from Idaho webite
    :param: None
    :return: None
    '''
    #open firefox in headless mode
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    #Get the search page
    driver.get("https://idbop.mylicense.com/verification/Search.aspx")

    #Select the license type - Pharmacist
    lic_type = Select(driver.find_element_by_xpath("//*[@id='t_web_lookup__license_type_name']"))
    lic_type.select_by_value("Pharmacist")

    #Give the search criteria- Last name starts with L
    lst_name = driver.find_element_by_xpath("//*[@id='t_web_lookup__last_name']")
    lst_name.send_keys("L*")

    #Click the search button
    search_button = driver.find_element_by_xpath("//*[@id='sch_button']")
    search_button.click()

    #Get the trs for the result page - 1
    table_trs_path = "/html/body/form/table/tbody/tr[2]/td[2]/"+\
    "table[2]/tbody/tr[3]/td/table/tbody/tr"
    table_trs = driver.find_elements_by_xpath(table_trs_path)

    #Create a output file to write into
    output = open("results.csv",'a+')
    
    #Write the header to the output file
    label_line = ''
    label_line += 'First Name'+','+\
                    'Middle Name'+','+\
                    'Last Name'+','+\
                    'License #'+','+\
                    'License Type'+','\
                    'Status'+','+\
                    'Original Issued Date'+','+\
                    'Expiry'+','+\
                    'Renewed'
                    
    output.write(label_line+'\n')
    
    #original window handle
    original_window = driver.window_handles[0]
    
    #Get the result pages yet to see
    pages = table_trs[-1].find_elements_by_xpath(".//td/a")
    
    #Iterate over result pages and extract the required information using 
    #"extract_table_contents" function
    current_page = 1
    while current_page <= len(pages)+1:
        if current_page==1:
            extract_table_contents(driver, original_window, output, table_trs)
        
        else:
            table_trs = driver.find_elements_by_xpath(table_trs_path)
            extract_table_contents(driver, original_window, output, table_trs)
    
        current_page += 1
        if current_page <= len(pages)+1:
            table_trs[-1].find_elements_by_xpath(".//td/a[text()={}]".format(current_page))[0].click()
            #Wait until the page is loaded
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, table_trs_path)))
    
    #Close the output file handler
    output.close()
    
    #Quit the driver
    driver.quit()
