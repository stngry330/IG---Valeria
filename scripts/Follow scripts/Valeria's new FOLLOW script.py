from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from twilio.rest import Client
import datetime
import pickle
import pandas as pd
from random import *
import sys, logging


def open_chrome():
    global driver
    global client
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-data-dir=C:/Users/jamie/PycharmProjects/Instagram/Profiles/Follow_Profile")  # Path to your chrome profile
    driver = webdriver.Chrome(executable_path='../../assets/chromedriver', chrome_options=options)
    driver.get("https://www.instagram.com/")
    sleep()

def log_into_instagram(username, password):
    driver.find_element_by_xpath('''//*[@id="react-root"]/section/main/article/div[2]/div[2]/p/a''').click()
    time.sleep(3)

    # Input username
    user = driver.find_element_by_xpath(
        '''//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[1]/div/input''')
    user.clear()
    user.send_keys(username)

    # Input password
    pw = driver.find_element_by_xpath(
        '''//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[2]/div/input''')
    pw.clear()
    pw.send_keys(password)

    pw.send_keys(Keys.ENTER)
    time.sleep(3)

def remove_k_m_periods_commas(value):
    value = value.replace('k', '')
    value = value.replace('m', '')
    value = value.replace('.', '')
    value = value.replace(',', '')
    return value

def repeat_space_bar(number_of_times):
    count = 0
    while count < number_of_times:
        driver.find_element_by_class_name('_2g7d5').send_keys(Keys.SPACE)
        time.sleep(1)
        count += 1

def check_if_account_is_private():
    try:
        if driver.find_element_by_xpath('''//*[@id="react-root"]/section/main/article/div/h2'''):
            print('Account is Private')
            return True
    except NoSuchElementException:
        return False

def check_if_image_is_not_a_video():
    try:
        driver.find_element_by_class_name('''_gu6vm''').click()
        return True
    except NoSuchElementException:
        # Skips the video and goes to the next image to check if it's not a video
        driver.find_element_by_class_name('''coreSpriteRightPaginationArrow''').click()
        sleep()
        return False

def follow_people(num_of_people, num_of_their_followers, sleep_time_minutes):
    for people in range(num_of_people):
        name = driver.find_elements_by_class_name('_2g7d5')
        user_followers_list.append(name[people].text)

    driver.back()
    sleep()
    ################################Get's list of people to follow COMPLETE############################################

    for x in user_followers_list:
        count = 0
        # Search bar
        search = driver.find_element_by_xpath('''//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input''')
        search.clear()
        search.send_keys(x)
        count += 1
        search.send_keys(Keys.ENTER)
        sleep()
        # Goes to first person in search
        search_results = driver.find_elements_by_class_name('_ndl3t')
        search_results[0].click()
        sleep()

        if check_if_account_is_private():
            continue

        # clicks followers
        try:
            driver.find_element_by_xpath('''//*[@id="react-root"]/section/main/article/header/section/ul/li[2]''').click()
            sleep()
        except: 
            continue

        repeat_space_bar(30)

        for future_followers in range(num_of_their_followers):

            data_names = pickle.load(open("../../data/Instagram_data.p", "rb"))
            username_list = data_names['username'].tolist()

            name = driver.find_elements_by_class_name('_2g7d5')
            buttons = "../../../../div[2]/span"

            if name[future_followers].text == 'linethmm':
                continue

            if name[future_followers].text in username_list:
                continue

            if name[future_followers].find_element_by_xpath(buttons).text == 'Follow':
                name[future_followers].find_element_by_xpath(buttons).click()
                sleep()
            else:
                continue

            # if name[future_followers].find_element_by_xpath(buttons).text == 'Follow':  # Makes sure we aren't banned from following people
            #     print('Are we banned?')
            #     quit()

            print("Now following: ", name[future_followers].text)

            # Begin pickle
            data = pickle.load(open("../../data/Instagram_data.p", "rb"))
            df = pd.DataFrame(
                [[name[future_followers].text, 'Following', str(datetime.datetime.now()), 'Friends_of_friends']],
                columns=['username', 'status', 'time_stamp', 'acquisition'])
            data = data.append(df)
            pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
            # End pickle

            sleep()

            if (future_followers + 1) % 11 == 0:  # Sleeps for 6 minutes every 10 unfollow
                print(future_followers, 'Followed: Waiting', sleep_time_minutes, 'minutes')
                time.sleep(sleep_time_minutes * 60)
            else:
                continue

        driver.back()
        sleep()
        driver.back()
        sleep()

def error_log(err):
    error_log = pickle.load(open("../../data/Instagram_error_log.p", "rb"))
    df = pd.DataFrame([[err, 'new FOLLOW script', str(datetime.datetime.now())]],
                      columns=['error message', 'script', 'time_stamp'])
    error_log = error_log.append(df)
    pickle.dump(error_log, open("../../data/Instagram_error_log.p", "wb"))

sys.path.insert(0, 'C:/Users/jamie/PycharmProjects/Instagram/Insta files/scripts/Functions')
from Insta_functions import twilio, text_me, error_handling, sleep

errors = 4
followings = 0
while errors > 0:
    try:
        open_chrome()
        twilio()
        # go to profile
        driver.find_element_by_xpath('''//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[3]/a''').click()
        sleep()
        # old xpath for followers
        '''//*[@id="react-root"]/section/main/article/header/section/ul/li[2]/a'''
        # Get's people to follow!
        driver.find_element_by_xpath('''//*[@id="react-root"]/section/main/article/header/section/ul/li[2]''').click()
        sleep()
        driver.back()
        driver.find_element_by_xpath('''//*[@id="react-root"]/section/main/article/header/section/ul/li[2]''').click()
        sleep()


        repeat_space_bar(15)

        # Create new list of people to follow!
        user_followers_list = []

        follow_people(40, 12, 16)  # Number of people, number of followings, time to wait
        print(user_followers_list)

        # ###################################Check # of followings##########################################################
        # go to profile
        driver.find_element_by_xpath('''//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[3]''').click()
        sleep()

        f = driver.find_element_by_xpath(
            '''//*[@id="react-root"]/section/main/article/header/section/ul/li[3]/a/span''').text

        f = remove_k_m_periods_commas(f)
        followings = int(f)
        print(followings)
        #driver.close()

    except Exception as err:
        print(err)
        issue = error_handling()
        error_log(issue)
        driver.close()

        errors -= 1
        if errors == 0:
            text_me('new follow script quit!')
            quit()
        message = 'Follow error = #' + str(errors)
        text_me(message)



