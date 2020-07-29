import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions

def get_input():
    print('*' * 50)
    url = input('URL of the product: ')
    expected_price = int(input('Expected price: '))
    email_to = input('Email address: ')
    print('*' * 50)
    url = url_shortner(url)
    return [url, expected_price, email_to]


def to_price(price_text):
    price = 0
    for letter in price_text:
        if letter.isdigit():
            price = price * 10 + int(letter)
    return price


def get_initial_price(url):
    driver_path = 'chromedriver/chromedriver'
    options = ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(driver_path, options= options)
    try:
        driver.get(url)
        price_class = driver.find_element_by_class_name('pdp-product-price')
        price_text = price_class.find_element_by_css_selector('span').text
    except Exception:
        print('Something went wrong ....')
        driver.close()
        return None
    else:
        driver.close()
        return to_price(price_text)


def url_shortner(url):
    symbol_index = url.find('?')
    if symbol_index == -1: return url
    return url[:symbol_index]


def url_valid(url):
    pattern = re.compile(r'^(https://www.daraz.com.np/products/)[a-z0-9-]+(\.html)$')
    _search = pattern.search(url)
    return not _search == None


def email_valid(email):
    email_list = email.split(',')
    for email in email_list:
        pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        _search = pattern.search(email)
        if _search == None: return False
    return True


def inputs_valid(row_data):
    url, expected_price, email_to = row_data
    return url_valid(url) and email_valid(email_to)


def duplicated_row(row_data):
    try:
        df = pd.read_csv('monitor.csv')
    except Exception:
        print('monitor.csv file not found...')
        return None
    else:
        for _, _series in df.iterrows():
            csv_email_to = _series['email_to']
            if list(_series[['url', 'expected_price']]) == [row_data[0], row_data[2]]:
                email = []
                csv_email_to_list = csv_email_to.split(',')
                row_data_email_list =  row_data[-1].split(',')
                for row_email in row_data_email_list:
                    if not row_email in csv_email_to_list:
                        email.append(row_email)
                        
                if len(email) == 0:
                    print('duplicated rows found...')
                    return True
                else:
                    print(','.join(set(row_data_email_list) - set(email)), 'found duplicate')
                    print(','.join(email), 'found unique')
                    return ','.join(email)
        return False


def check_url_expected_price(row_data):
    df = pd.read_csv('monitor.csv')
    email = row_data[3]
    for _row in df.iterrows():
        index, _series = _row
        if [row_data[0], row_data[2]] == list(_series[['url', 'expected_price']]):
            df.loc[index, ['email_to']] = ','.join([_series['email_to'], email])
            df.to_csv('monitor.csv', index= False)
            print('Saved in the monitor.csv file...')
            quit()
    

def save_to_csv():
    row_data = get_input()
    if inputs_valid(row_data):
        initial_price = get_initial_price(url= row_data[0])
        if initial_price == None: return None
        if row_data[1] >= initial_price:
            print('your expected price is higher or equal than the actual price of the product')
            return None
        row_data.insert(1, initial_price)
        fieldnames = ['url', 'initial_price', 'expected_price', 'email_to']
        if not os.path.exists('monitor.csv'):
            df = pd.DataFrame(columns= fieldnames)
            df.to_csv('monitor.csv', index= False)

        tof = duplicated_row(row_data)

        if tof == True :
            return None
        elif tof == False:
            pass
        else:
            row_data[-1] = tof

        check_url_expected_price(row_data)

        df = pd.read_csv('monitor.csv', sep= ',')
        df = df.append(pd.Series(row_data, index= fieldnames), ignore_index= True)
        df.to_csv('monitor.csv', index= False)

        print('Saved in the monitor.csv file...')
    else:
        print('inputs were given wrong...')        

def main():
    save_to_csv()


if __name__ == '__main__':
    main()