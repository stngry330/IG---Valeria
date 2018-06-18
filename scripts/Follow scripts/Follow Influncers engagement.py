from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time, datetime, pickle, sys
import pandas as pd
from random import *

sys.path.insert(0, 'C:/Users/jamie/PycharmProjects/Instagram/Insta files/scripts/Functions')
from Insta_functions import sleep, twilio, text_me, error_handling, open_chrome, search, remove_k_m_periods_commas
from Insta_functions import isEnglish, click_posts_followers_followings, click_first_post, repeat_down_arrow

def write_to_database(names, person):
    # Begin pickle
    data = pickle.load(open("../../data/Instagram_data.p", "rb"))
    df = pd.DataFrame(
        [[names[person].text, 'Following', str(datetime.datetime.now()),
          'Follow_influencer_person_' + str(influencer)]],
        columns=['username', 'status', 'time_stamp', 'acquisition'])
    data = data.append(df)
    pickle.dump(data, open("../../data/Instagram_data.p", "wb"))
    # End pickle
    sleep()

def follow_people_who_interacted(num_people = 12):
    if num_people > 12:
        # TODO - doesnt work yet
        repeat_down_arrow(round(num_people/6))

    follow_btns = driver.find_elements_by_class_name('_5f5mN')
    names = driver.find_elements_by_class_name('FPmhX')

    for person in range(num_people):
        print(names[person].text)
        print(follow_btns[person+2].text)
        if isEnglish(names[person].text) == False:
            continue

        if follow_btns[person+2].text != 'Follow':
            continue

        follow_btns[person+2].click()
        print("Now following: ", names[person].text)

        write_to_database(names, person)

errors = 5
while errors > 0:
    try:
        global driver
        driver = open_chrome('Follow_Famous_Profile')
        twilio()

        influencers_list = ['vdethe', 'ashleesummer', 'snitchery', 'mamapeach_',
                            'sichenmakeupholic', 'nyane', 'michellephan', 'hudabeauty','wengie']
        randomized_list = sorted(influencers_list, key=lambda x:random())
        for influencer in influencers_list:
            print('following:', influencer)
            driver.get("https://www.instagram.com/" + influencer)
            sleep()

            click_first_post()
            time.sleep(2)
            # Click likes amount to get to people who've liked their picture
            driver.find_element_by_class_name('zV_Nj').click()
            sleep()
            follow_people_who_interacted()  # Number of people to follow
            sleep()
            print('#######sleeping for 15 minutes!########')
            time.sleep(60*15)

        # Completed
        driver.close()
        print('########time to start over#######waiting 2 hours########')
        time.sleep(120*60)  # Wait 2 hours to start over

    except Exception as err:
        errors -= 1
        print(err)
        issue = error_handling()
        driver.close()

        if errors == 0:
            text_me('Influencer following people who interact QUIT!')
            quit()
        message = 'Influencer+engagement follow error...' + str((errors)) + ' errors remaining'
        #text_me(message)
        time.sleep(60 * 10)