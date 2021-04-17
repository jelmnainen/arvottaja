"""
Notes:

Apartment shape is only 'satisfactory' or 'good' (misses 'excelent' which is usually included)
"""

from datetime import datetime
from bs4 import BeautifulSoup
import requests
import os
import csv
import time
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('city', help='Which city should be parsed, capitalized. E.g. "Espoo"')
parser.add_argument('--page', help='Scrape and print data for a single page, useful for debugging')
args = parser.parse_args()

def get_single_page_html(city, page_num):
    """
        return soup of requested page, or test page if env == 'DEV'

        city(string) should be a capitalized city name in Finland, e.g. 'Espoo'
        page_num(string) should be the page number, asuntojen.hintatiedot.fi uses pagination

    """
    if os.environ.get("ENV", False) == 'DEV':
        print("DEV mode, use local test html page")
        with open('static_pages/test.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            return soup
    if os.environ.get("ENV", False) == 'DEBUG':
        print("DEBUG mode, use local test html page")
        with open('static_pages/debug.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            return soup
    url = f'https://asuntojen.hintatiedot.fi/haku/?c={city}&cr=1&t=3&l=0&z={page_num}&search=1&sf=0&so=a&renderType=renderTypeTable&print=0&submit=seuraava+sivu+%C2%BB'
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')
    return(soup)

def first(arr):
    try:
        return arr[0]
    except:
        return None

def parse_lot_type(maybeLotStr):
    if maybeLotStr == None:
        return None
    lotStr = maybeLotStr.replace("\t", "").lower()
    if lotStr == 'oma':
        return 'owned'
    if lotStr == 'vuokra':
        return 'rented'
    return lotStr

def parse_elevator(maybeElevatorStr):
    if not maybeElevatorStr:
        return None
    elevatorStr = maybeElevatorStr.lower()
    if elevatorStr == 'on':
        return True
    elif elevatorStr == 'ei':
        return False
    return elevatorStr

def parse_house_type(maybeHouseTypeStr):
    if not maybeHouseTypeStr:
        return None
    if maybeHouseTypeStr == 'kt':
        return 'apartment'
    elif maybeHouseTypeStr == 'rt':
        return 'rowhouse'
    elif maybeHouseTypeStr == 'ok':
        return 'townhouse'
    return maybeHouseTypeStr

def parse_square_meters(maybeSquareMeterStr):
    if not maybeSquareMeterStr:
        return None
    return float(maybeSquareMeterStr.replace(",", "."))


def parse_energy_classification(maybeEnergyClassificationElem):
    if not maybeEnergyClassificationElem:
        return None
    if len(maybeEnergyClassificationElem) == 1:
        return maybeEnergyClassificationElem[0]
    return f'{maybeEnergyClassificationElem[0]}-{maybeEnergyClassificationElem[1].contents[0]}'

def parseShape(maybeShapeStr):
    if not maybeShapeStr:
        return None
    shapestr = maybeShapeStr.lower().replace('.', '')
    if shapestr == 'tyyd':
        return "satisfactory"
    elif shapestr == 'hyvä':
        return "good"

def extract_house_dict(house_html):
    """
        Take a single <tr> containing house representation,
        return a dict representing house
    """
    elems = [house.contents for house in house_html.select('td')]
    house_dict = {
        "neighborhood": first(elems[0]),
        "room_arrangement": first(elems[1]),
        "house_type": parse_house_type(first(elems[2])),
        "square_meters": parse_square_meters(first(elems[3])),
        "price_including_loans": int(first(elems[4])),
        "price_per_square_meters": int(first(elems[5])),
        "built_in": int(first(elems[6])),
        "floor": first(elems[7]),
        "has_elevator": parse_elevator(first(elems[8])),
        "shape": parseShape(first(elems[9])),
        "lot": parse_lot_type(first(elems[10])),
        "energy_classification": parse_energy_classification(elems[11])
    }
    return house_dict

def extract_houses(soup):
    """
        Output houses as a list of dictionaries

        Takes a soup of asuntojen.hintatiedot.fi page
    """
    houses_tbody = soup.select('table#mainTable tbody')[1]
    houses_html_list = houses_tbody.select('tr')
    houses_html_list_clean = [houses for houses in houses_html_list if len(houses.select('td')) > 1]
    houses_dicts = [extract_house_dict(house_html) for house_html in houses_html_list_clean]
    return houses_dicts

def has_next_page(soup):
    """
        Return True if there is a next page to be scraped, else False

        takes a soup of asuntojen.hintatiedot.fi page
    """
    return len(soup.select('input[value="seuraava sivu »"]')) > 0

def save_data(dict_data):
    csv_columns = list(dict_data[0].keys())
    today = datetime.today().strftime("%Y-%m-%d")
    with open(f'./scraped_data/{today}.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def main(city):
    i = 1
    data = []
    errors = []
    while(True):
        try:
            soup = get_single_page_html(city, i)
            houses = extract_houses(soup)
            data = data + houses
            should_continue = has_next_page(soup)
            if should_continue:
                print(f'Parsed page {i}, sleep 2s and continue.')
                time.sleep(2)
            else:
                break
        except Exception as e:
            print(f"Encountered error on page {i}. Continue without.")
            errors.append({
                "page_number": i,
                "Exception": e
            })
        i = i + 1
    save_data(data)
    print("Done!")
    if len(errors) > 0:
        print("Errors:")
        for error in errors:
            print(error)


def get_single_page(city, page_no):
    """
        This is just for debugging
    """
    soup = get_single_page_html(city, page_no)
    houses = extract_houses(soup)
    for row in houses:
        print(row)

if args.page:
    get_single_page(args.city, args.page)
else:
    main(args.city)
