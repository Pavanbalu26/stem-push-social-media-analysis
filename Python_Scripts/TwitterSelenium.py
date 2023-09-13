# Import necessary libraries
from selenium import webdriver
from shutil import which
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time  
import pandas as pd
import wget
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles import Alignment

# Function to extract integers from a string
def extract_integers(string):
    result = ""
    for char in string:
        if char.isdigit():
            result += char
    return int(result)

# Set the path for the ChromeDriver extension
chrome_path = which('/usr/local/bin/chromedriver')

# Create a ChromeDriver service
service = Service(executable_path=chrome_path)
driver = webdriver.Chrome(service=service)

# Open Twitter's explore page
driver.get('https://twitter.com/explore')
driver.implicitly_wait(60)

# Handle notification pop-up
notification_pop_up = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Not now')]")))
notification_pop_up.click()

# Click the login button
login_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(), 'Log in')]")))
login_button.click()

# Enter email address
mail = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//input[@name='text']")))
mail.send_keys('pkorlepa@asu.edu')

# Click next
next_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(),'Next')]")))
next_button.click()

time.sleep(10)

# Enter Twitter username
mail2 = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//input[@name='text']")))
mail2.send_keys('@pkorlepa')

time.sleep(5)

# Click next
next_button2 = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(),'Next')]")))
next_button2.click()

time.sleep(5)

# Enter Twitter password
password = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//input[@name='password']")))
input_password = input()
password.send_keys(input_password)
password.send_keys(Keys.ENTER)
time.sleep(30)

# Creating a Workbook
workbook = Workbook()
time.sleep(4)
start = time.time()
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"Twitter_{formatted_datetime}.xlsx"
activeSheetNotUsed = True

# List of keywords to search for
keywordsList =['#Stem Education','#Stem Push']

for keyword in keywordsList:
    # Find the search input box
    search_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text']")))
    
    # Create or activate a sheet for the keyword
    if activeSheetNotUsed:
        sheet = workbook.active
        sheet.title = keyword + " Data"
        activeSheetNotUsed = False
    else:
        sheet = workbook.create_sheet(keyword + ' Data')
        search_input.click()
        cancel_btn = driver.find_element(By.XPATH,"//div[@class = 'css-1dbjc4n r-6koalj r-1777fci']")
        cancel_btn.click()
    
    # Clear the search input box
    search_input.clear()
    time.sleep(2)
    
    # Enter the keyword and submit the search
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.ENTER)
    time.sleep(10)

    # Click on the "Latest" tab
    latest_btn = driver.find_element(By.XPATH,"//span[contains(text(),'Latest')]")
    latest_btn.click()

    counter = 1
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        tweets = driver.find_elements(By.XPATH,'//div[@data-testid="cellInnerDiv"]')
        
        # Loop through tweets and extract information
        for tweet in tweets:
            username = ''
            description = ''
            hashtags = ''
            comments = 0
            retweets = 0
            likes = 0
            views = 0
            
            try:
                usernames = tweet.find_elements(By.XPATH,'.//span[@class = "css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0"]/span')
                for nth_time in range(len(usernames)):
                    if nth_time != len(usernames) - 1:
                        username = username + usernames[nth_time].text + ','
                    else:
                        username = username + usernames[nth_time].text
            except (NoSuchElementException,WebDriverException):
                pass

            try:
                descriptions = tweet.find_elements(By.XPATH,".//div[@data-testid = 'tweetText']")
                for nth_time in range(len(descriptions)):
                    if nth_time != len(descriptions) - 1:
                        description = description + descriptions[nth_time].text + ','
                    else:
                        description = description + descriptions[nth_time].text
            except (NoSuchElementException,WebDriverException):
                 pass

            try:
                anchorTags = tweet.find_elements(By.XPATH,".//div[@data-testid = 'tweetText']//a")
                for nth_time in range(len(anchorTags)):
                    if nth_time != len(anchorTags) - 1:
                        hashtags = hashtags + anchorTags[nth_time].get_attribute("textContent") + ','
                    else:
                        hashtags = hashtags + anchorTags[nth_time].get_attribute("textContent")
            except (NoSuchElementException,WebDriverException):
                pass

            try:
                comments = tweet.find_element(By.XPATH,".//div[@class = 'css-1dbjc4n']/div[@role = 'group']/div[1]//span[@data-testid='app-text-transition-container']")
            except (NoSuchElementException,WebDriverException):
                pass
            wait = WebDriverWait(driver, 10)
            views = wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n']/div[@role='group']/div[4]//span[@data-testid='app-text-transition-container']")))
            try:
                retweets = tweet.find_element(By.XPATH,".//div[@class = 'css-1dbjc4n']/div[@role = 'group']/div[2]//span[@data-testid='app-text-transition-container']")
            except (NoSuchElementException,WebDriverException):
                pass

            try:
                likes = tweet.find_element(By.XPATH,".//div[@class = 'css-1dbjc4n']/div[@role = 'group']/div[3]//span[@data-testid='app-text-transition-container']")
            except (NoSuchElementException,WebDriverException):
                pass

            try:
                views = tweet.find_element(By.XPATH,".//div[@class = 'css-1dbjc4n']/div[@role = 'group']/div[4]//span[@data-testid='app-text-transition-container']")
            except (NoSuchElementException,WebDriverException):
                pass

            comments = int(extract_integers(comments.text)) if comments.text != '' else 0
            retweets = int(extract_integers(retweets.text)) if retweets.text != '' else 0
            likes = int(extract_integers(likes.text)) if likes.text != '' else 0
            views = int(extract_integers(views.text)) if views.text != '' else 0

            # Print extracted information
            print(username)
            print(description)
            print(comments)
            print(retweets)
            print(likes)
            print(views)
            
            # Append the information to the sheet
            sheet.append([username, description, comments, retweets, likes, views])
            workbook.save(filename)
            print("------------------------------------------------------------------")
            counter += 1
            print('counter -> ',counter)
            if counter > 10:
                break
        
        # Scroll down to load more tweets
        driver.execute_script("window.scrollTo(0, {})".format(last_height+500))
        time.sleep(40)
        
        # Check if the page has loaded all available tweets or counter exceeds a limit
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height or counter > 10:
            break
