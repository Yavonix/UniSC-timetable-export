import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from ics import Calendar, Event
import arrow
from time import strptime
from dotenv import load_dotenv

import os

load_dotenv()

username=os.getenv('USERNAME_USC')
password=os.getenv('PASSWORD_USC')

driver = webdriver.Chrome()

driver.get("https://usccentral.usc.edu.au")

wait = WebDriverWait(driver, 15, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])

signInButton = wait.until(EC.element_to_be_clickable((By.ID, "signin")))

driver.find_element(By.ID, "userid").send_keys(username)
driver.find_element(By.ID, "pwd").send_keys(password)
signInButton.click()

timetableButton = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Timetable')]")))

timetableButton.click()

byDateButton = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'By Date')]")))

byDateButton.click()

toDateButton = wait.until(EC.presence_of_element_located((By.ID, "SSR_DER0_CAL_FL_SSR_TO_DATE")))

toDateButton.clear()
toDateButton.send_keys(f"01/01/{datetime.now().year + 5}")

driver.find_element(By.ID, "SSR_DER0_CAL_FL_SSR_FROM_DATE").click()

time.sleep(1)

body = driver.find_element(By.TAG_NAME, "body")

while True:
    text = body.get_attribute("style")
    print("Waiting for page to load...")
    if "pointer-events: none" in text:  
        time.sleep(1)
    else:
        break

c = Calendar()

iterationDay = 0
while True:
    try:
        dateElement = driver.find_element(By.ID, f"SSR_DER1_CAL_FL_SSR_DESCR80${iterationDay}")
    except NoSuchElementException:
        break
    date = dateElement.text

    iterationRow = 0
    while True:
        try:
            tableElement = driver.find_element(By.ID, f"STDNT_ENRL_SSVW1${iterationDay}_row_{iterationRow}")
        except NoSuchElementException:
            break
        
        rowCells = tableElement.find_elements(By.TAG_NAME, 'td')
        
        time = rowCells[0].find_element(By.CLASS_NAME, 'ps_box-value').text
        course = rowCells[1].find_element(By.TAG_NAME, 'a').text
        location = rowCells[2].find_element(By.CLASS_NAME, 'ps_box-value').text

        
        year = datetime.now().year
        month = strptime(date.split(" ")[1],'%B').tm_mon
        day = int(date.split(" ")[2])
        startTime, endTime = time.split("-")
        startHour = int(startTime.split(":")[0])
        endHour = int(endTime.split(":")[0])

        if "AM" in startTime.split(":")[1]:
            startMinute = int(startTime.split(":")[1].replace("AM", ""))
            if startHour == 12:
                startHour = 0
        elif "PM" in startTime.split(":")[1]:
            startMinute = int(startTime.split(":")[1].replace("PM", ""))
            if startHour != 12:
                startHour = startHour + 12

        if "AM" in endTime.split(":")[1]:
            endMinute = int(endTime.split(":")[1].replace("AM", ""))
            if endHour == 12:
                endHour = 0
        elif "PM" in endTime.split(":")[1]:
            endMinute = int(endTime.split(":")[1].replace("PM", ""))
            if endHour != 12:
                endHour = endHour + 12

        print(time, year, month, day, startHour, startMinute)
        # datetime(year, month, day, hour, minute, second, microsecond)
        dts = arrow.get(year, month, day, startHour, startMinute, 0, 0, tzinfo='Australia/Queensland')
        dte = arrow.get(year, month, day, endHour, endMinute, 0, 0, tzinfo='Australia/Queensland')
        
        e = Event()
        e.begin = dts
        e.end = dte
        e.name = course
        e.location = location

        c.events.add(e)

        iterationRow += 1


    iterationDay += 1

driver.quit()

with open(f'timetable.ics', 'w') as f:
    f.writelines(c.serialize_iter())