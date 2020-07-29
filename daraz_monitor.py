from selenium import webdriver
import time, os
import pandas as pd
from smtplib import SMTP_SSL
from email.message import EmailMessage
import notify2

monitor_interval_time = 1 # hour
icon_path = '/home/xitiz007/Documents/Python Projects/daraz price monitoring/daraz_logo.png'
title = 'python daraz price monitor'

def get_email_password():
    global sender_email, sender_password
    sender_email = os.environ.get('email')
    sender_password = os.environ.get('google_password')

def send_email(email_to, initial_price, expected_price, current_price, product_title, url):
    with SMTP_SSL('smtp.gmail.com', 465) as smtp:
        subject = 'Daraz product price has dropped down'
        body= f'''
        Dear customer, the product from Daraz that you had monitored price has dropped down to your expected price
        Initial price: {initial_price}
        Expected price : {expected_price}
        Current price : {current_price}
        Product : {product_title}
        Product url : {url}
        '''

        message = EmailMessage()
        message['To'] = email_to
        message['From'] = sender_email
        message['Subject'] = subject
        message.set_content(body)

        try:
            smtp.login(sender_email, sender_password)
            smtp.send_message(message)
        except Exception:
            print('failed to send email to', email_to)
            return False
        else:
            print('email sent successfully to', email_to)
            return True


def to_price(price_text):
    price = 0
    for letter in price_text:
        if letter.isdigit():
            price = price * 10 + int(letter)
    return price

def get_title_price(driver, url):
    try:
        driver.get(url)
        product_title = driver.find_element_by_class_name('pdp-mod-product-badge-title').text
        price_class = driver.find_element_by_class_name('pdp-product-price')
        price_text = price_class.find_element_by_css_selector('span').text
    except Exception:
        print('something went wrong..')
        return None, None
    else:
        current_price = to_price(price_text)
        return current_price, product_title

def get_chrome_driver():
    driver_path = 'chromedriver/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    try:
        driver = webdriver.Chrome(driver_path, options= options)
    except Exception:
        raise Exception('something went wrong with the chrome driver')
    else:
        return driver

def monitor_price(driver, url, initial_price, expected_price, email_to):
    current_price, product_title = get_title_price(driver, url)
    if current_price == None and product_title == None: return None
    if current_price <= expected_price:
        return send_email(email_to, initial_price, expected_price, current_price, product_title, url)
    return False



def monitor_csv_exist():
    return os.path.exists('monitor.csv')

def read_csv():
    if monitor_csv_exist():
        if not os.path.getsize('monitor.csv') == 0:
            df = pd.read_csv('monitor.csv')
            if not df.empty:
                while True:
                    driver = get_chrome_driver()

                    for index, row in df.iterrows():
                        print('monitoring product ', index)
                        url = row['url']
                        initial_price = row['initial_price']
                        expected_price = row['expected_price']
                        email_to = row['email_to']

                        tof = monitor_price(driver, url, initial_price, expected_price, email_to)

                        if tof == True:
                            df.drop(index= index, inplace= True)
                            notify2.init('python daraz price monitor')
                            message ='''
                            daraz product price has dropped down
                            check your email...
                            '''
                            notify = notify2.Notification(title, message, icon=icon_path)
                            notify.set_urgency(notify2.URGENCY_NORMAL)
                            notify.set_timeout(20000)
                            notify.show()

                    df.to_csv('monitor.csv', index= False)
                    driver.close()
                    print(f'\nsleeping for {monitor_interval_time} hour...\n')
                    time.sleep(60 * monitor_interval_time)
            else:
                print('monitor.csv is empty....')
        else:
            print('monitor.csv is empty....')
    else:
        print('monitor.csv file is missing....')

if __name__ == '__main__':
    get_email_password()
    read_csv()

