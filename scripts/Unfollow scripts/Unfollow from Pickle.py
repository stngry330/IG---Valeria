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

sys.path.insert(0, 'C:/Users/jamie/PycharmProjects/Instagram/Insta files/scripts/Functions')
from Insta_functions import sleep, twilio, text_me, error_handling, open_chrome, search

def read_pickle():
    # Begin pickle
    global follow_unfollow_df
    data = pickle.load(open("../../data/Instagram_data.p", "rb"))

    bad_status = ['Not_searchable', 'Wrong_search', 'hashtag', 'location', 'deleted_account']
    today = str(datetime.date.today())  # Gets today's date
    follow_unfollow_df = data[data['status'].isin(['Following'])]
    follow_unfollow_df = follow_unfollow_df[~follow_unfollow_df['status'].isin(bad_status)]
    follow_unfollow_df = follow_unfollow_df[~follow_unfollow_df['time_stamp'].isin([today])]
    print('unfollowing:', follow_unfollow_df['username'].tolist())

def no_unfollow():
    if len(follow_unfollow_df) <= 1:
        text_me('nothing to follow?')
        driver.close()
        quit()

def error_log(err):
    error_log = pickle.load(open("../../data/Instagram_error_log.p", "rb"))
    df = pd.DataFrame([[err, 'Unfollow from Pickle', str(datetime.datetime.now())]],
                      columns=['error message', 'script', 'time_stamp'])
    error_log = error_log.append(df)
    pickle.dump(error_log, open("../../data/Instagram_error_log.p", "wb"))

count = 0
error = 3
while error > 0:
    try:
        global driver
        driver = open_chrome('Unfollow_Profile')
        twilio()
        read_pickle()
        no_unfollow()

        for person in follow_unfollow_df['username']:
            driver.get("https://www.instagram.com/" + person)
            sleep()

            if person == 'linethmm':
                continue

            # Private accounts with 'Follow' have a new class name -.- ugh
            try:
                private_account = driver.find_element_by_class_name('rkEop')
                if private_account:
                    print(person, 'already unfollowed and account is private')
                # Begin pickle
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'Unfollowed', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                # End pickle
                time.sleep(3)
                continue
            except:
                pass


            # Check if they are blocked
            try:
                btn_list = driver.find_elements_by_class_name('_5f5mN')
                if btn_list[0].text  == 'Unblock':
                    print(person, 'blocked')
                    data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                    df = pd.DataFrame([[person, 'blocked_account', str(datetime.datetime.now())]],
                                      columns=['username', 'status', 'time_stamp'])
                    data = data.append(df)
                    pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                    time.sleep(3)
                    continue
            except:
                pass

            # Check if they found a Sorry, this page isn't available.
            try:
                driver.find_element_by_class_name('error-container')

                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'deleted_account', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                driver.get("https://www.instagram.com/")
                time.sleep(3)
                continue
            except NoSuchElementException:
                pass

            # Check if they found hashtag
            current_url = driver.current_url

            if "/tags/" in current_url:
                print(person, '= found a hashtag')
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'hashtag', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                continue

            if "/locations/" in current_url:
                print(person, '= location')
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'location', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                continue
            try:
                if driver.find_element_by_class_name('AC5d8').text != person:
                    data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                    df = pd.DataFrame([[person, 'Wrong_search', str(datetime.datetime.now())]],
                                      columns=['username', 'status', 'time_stamp'])
                    data = data.append(df)
                    pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                    continue
            except NoSuchElementException:
                continue



            button = driver.find_element_by_class_name('BY3EC')

            if button.text == 'Following':
                button.click()
                print('unfollowed', person)
                sleep()
                # Begin pickle
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'Unfollowed', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                count += 1
                # End pickle

            elif button.text == 'Requested':
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'Requested', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))

            elif button.text == 'Follow':
                # Begin pickle
                data = pickle.load(open("../../data/Instagram_data.p", "rb"))
                df = pd.DataFrame([[person, 'Unfollowed', str(datetime.datetime.now())]],
                                  columns=['username', 'status', 'time_stamp'])
                data = data.append(df)
                pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
                # End pickle

            # Updates data frame files
            data = pickle.load(open("../../data/Instagram_data.p", "rb"))
            data.drop_duplicates(subset='username', keep='last', inplace=True)
            pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
            # End pickle

            if (count + 1) % 16 == 0:  # Sleeps for 15 minutes every 16 unfollow
                print(count, 'Unfollowed: Waiting 11 minutes')
                time.sleep(11 * 60)

        driver.close()
    except Exception as err:
        issue = error_handling()
        print(issue)
        error_log(issue)
        driver.close()
        print(err)
        error -= 1
        if error == 0:
            #text_me('unfollow ended!')
            quit()
        msg = 'Unfollow issue!'
        #text_me(msg)
