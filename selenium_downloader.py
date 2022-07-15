import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import pyautogui
import pytesseract
import cv2
import numpy as np
import os
import shutil


def sign_in(username, password, login_url, browser):
    browser.get(login_url)
    browser.set_window_position(2000, 0)
    browser.maximize_window()
    username_input = browser.find_element(By.NAME, 'username')
    username_input.send_keys(username)
    password_input = browser.find_element(By.NAME, 'password')
    password_input.send_keys(password)
    login_button = browser.find_element(By.NAME, 'submit-to-login')
    login_button.click()
    return

def navigate_to_url(url, browser):
    browser.get(url)
    time.sleep(5)
    screenshot_filename = 'screenshot.png'
    if os.path.exists(screenshot_filename):
        os.remove(screenshot_filename)
    screenshot = pyautogui.screenshot(screenshot_filename)
    nimg = np.array(screenshot)
    #incase second monitor attached. only works if second monitor is on the left
    # if nimg.shape[1] == 3840:
    #     nimg = nimg[0:1080, 1920:3840]
    #     nimg.imwrite(screenshot_filename)
    img = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)
    #img = cv2.imread('scrot.png') #find a way to avoid saving image file
    # change screenshot to selenium screenshot 
    # make this wait until page is loaded instead of 5 seconds which may be too much or not enough time
    return img 

def get_page_number(browser):
    page_text = browser.find_element(By.XPATH, "//span[@class='BRcurrentpage']").text
    unwanted_characters = "() ,"
    current_page = int(page_text.split()[0].strip(unwanted_characters))
    total_pages = int(page_text.split()[2].strip(unwanted_characters))
    return (current_page, total_pages)
   
 
def find_button_coordinates(button_text, img, subsection):
    # find coordinates of button using text recognition to get coordinates.
    # click button at coordinates 
    if subsection:
        prefix = 'cropped_'
    else:
        prefix = ''
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    button_coordinats = (0,0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    #THRESH_BINARY works for black background. THRESH_BINARY_INV works for white background. 
    #detect background. cut screenshot, use appropriate algo then stitch back together.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    im2 = img.copy()
    center_of_pages = ((0,0),(0,0))
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # finds box where content images are
        if 1000 > h > 100:
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # if on back cover page
            # center_of_pages = ((int(x + 0.5 * w), int(y + 0.5 * h)), (int(x + 1.5 * w), int(y + 0.5 * h)))
            # if anywhere where 2 pages are displayed
            # center_of_pages = ((int(x + 0.25 * w), int(y + 0.5 * h)), (int(x + 0.75 * w), int(y + 0.5 * h)))
            # if on cover page
            center_of_pages = ((int(x - 0.5 * w), int(y + 0.5 * h)), (int(x + 0.5 * w), int(y + 0.5 * h)))
            cv2.circle(im2, (center_of_pages[0]), 5, (255, 0, 0), -1)
            cv2.circle(im2, (center_of_pages[1]), 5, (255, 0, 0), -1)
        else:
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cropped = im2[y:y + h, x:x + w]
        text = pytesseract.image_to_string(cropped)
        if button_text in text:
            button_coordinats = (x + 0.5*w, y + 0.5*h)
            print('MATCH!: ' + str(button_coordinats) + text)
            print('**********************************************************************')
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            break
        else:
            coordinates = (x + 0.5*w, y + 0.5*h)
            print('Not a match: ' + str(coordinates) + text)
            print('**********************************************************************')
    name = f'{prefix}img_with_boxes.png'
    cv2.imwrite(name, im2) 
    print('Center of pages: ' + str(center_of_pages))
    return button_coordinats, center_of_pages

def rent_book(coordinates):
    pyautogui.moveTo(coordinates)
    pyautogui.click()
    return

def navigate_book(browser, title, page_title, page_centers, directory_path):
    page_back_button = browser.find_element(By.XPATH, "//button[@title='Flip left']")
    page_next_button = browser.find_element(By.XPATH, "//button[@title='Flip right']")
    current_page, total_pages = get_page_number(browser)
    print('Current page: ' + str(current_page))
    print('Total pages: ' + str(total_pages))
    while(current_page > 1):
        page_back_button.click()
        current_page, total_pages = get_page_number(browser)
        print('Current page: ' + str(current_page))
        print('Total pages: ' + str(total_pages))
    current_page, total_pages = get_page_number(browser)
    for x in range(current_page, total_pages):
        current_page, _ = get_page_number(browser)
        print('Current page: ' + str(current_page))
        print('Total pages: ' + str(total_pages) + '. This would be passed to the download function!')
        time.sleep(1.5)
        downoad_page(browser, title, page_title, page_centers, directory_path, total_pages)
        if current_page == total_pages:
            break
        page_next_button.click()
    return

def downoad_page(browser, title, page_title, page_centers, directory_path, total_pages):
    current_page, _ = get_page_number(browser)
    if current_page == total_pages:
        left_page_name = page_title + 'back_cover'
    else:
        left_page_name = page_title + str(current_page).rjust(4, '0')
    if current_page == 1:
        right_page_name = page_title + 'front_cover'
    else:
        right_page_name = page_title + str(current_page + 1).rjust(4,'0')
    default_location = '/home/joe/Downloads/'
    # left_page_element = browser.find_element(By.XPATH, "//div[@data-side='L']").find_element(By.XPATH, "//img[@alt='Book page image']")
    # right_page_element = browser.find_element(By.XPATH, "//div[@data-side='R']").find_element(By.XPATH, "//img[@alt='Book page image']")
    if current_page != 1:
        pyautogui.rightClick(x=page_centers[0][0], y=page_centers[0][1])
        pyautogui.moveRel(50,50)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.moveRel(0,-250)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.typewrite(left_page_name + '\n')
        time.sleep(0.5)
        destination = shutil.move(default_location + left_page_name + '.jpg', directory_path + 'pages/' + left_page_name + '.jpg')

    if current_page != total_pages:
        pyautogui.rightClick(x=page_centers[1][0], y=page_centers[1][1])
        pyautogui.moveRel(50,50)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.moveRel(0,-250)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.typewrite(right_page_name + '\n')
        time.sleep(0.5)
        destination = shutil.move(default_location + right_page_name + '.jpg', directory_path + 'pages/' + right_page_name + '.jpg')
    
    
    # with open(left_page_name, 'wb') as file:
    #     file.write(left_page_element.screenshot_as_png)
    # with open(right_page_name, 'wb') as file:
    #     file.write(left_page_element.screenshot_as_png)
    return

def set_user_variables():
    #turn some of these into arguments
    username = input("Enter archive.org username: ")
    password = input("Enter archive.org password: ")
    title = input("Create a title. This will create a directory in the current directory where the content goes.\nEnter title: ")
    page_title = input("Enter page title template: ")
    directory_path = title + '/' 
    content_url = input("Enter content url: ")
    return username, password, title, page_title, directory_path, content_url

def download_page_images():
    username, password, title, page_title, directory_path, content_url = set_user_variables()
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    if not os.path.exists(directory_path + 'pages'):
        os.makedirs(directory_path + 'pages')

    browser = webdriver.Chrome(executable_path="/home/joe/code/ArchiveDotOrgDownloader/chromedriver")

    button_text = 'Borrow for 1 hour'
    login_url = 'https://archive.org/account/login'

    sign_in(username, password, login_url, browser)
    time.sleep(5)
    img = navigate_to_url(content_url, browser)

    coordinates, page_centers = find_button_coordinates(button_text, img, False)
    # print(coordinates)
    # # downoad_page(browser, title, page_centers, directory_path, total_pages=290)
    if coordinates != (0,0):
        rent_book(coordinates)
    time.sleep(10)
    #downoad_page(browser, test_title, page_centers, directory_path, total_pages=290)
    navigate_book(browser, title, page_title, page_centers, directory_path)
    browser.quit()

    return

def main():
    download_page_images()

if __name__=='__main__':
    main()