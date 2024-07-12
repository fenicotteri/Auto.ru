from bs4 import BeautifulSoup
import os
import csv
from typing import List, Union
import requests 
from requests import get, Response
from dotenv import load_dotenv
import time
# Load environment variables from .env file
load_dotenv()

PATH = 'Kia.csv'
URL = os.getenv('URL')
COOKIE = os.getenv('COOKIE')
HEADERS = {
    
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding' : 'gzip, deflate, br, zstd',
    'Accept-Language' : 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'Cache-Control' : 'max-age=0',
    'Cookie' : COOKIE,
    'Priority' : 'u=0, i',
    'Sec-Ch-Ua' : '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    'Sec-Ch-Ua-Mobile' : '?0',
    'Sec-Ch-Ua-Platform' : '"Windows"',
    'Sec-Fetch-Dest' : 'document',
    'Sec-Fetch-Mode' : 'navigate',
    'Sec-Fetch-Site' : 'same-origin',
    'Sec-Fetch-User' : '?1',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}

def get_content(html: bytes) -> List[dict]:

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem__description')
    cars = []
    for item in items:
        price = item.find('div', 'ListingItemPrice')
        if not price :
            price = item.find('a', 'ListingItemPriceNew__link-cYuLr')
            if not price:
                print(1)
                break
        
        desc = item.find_all('div', 'ListingItemTechSummaryDesktop__cell')
        desc1 = desc[0].get_text().split('/')
        car = {
            'brand': item.find('div', 'ListingItemTitle').get_text().split()[0],   
            'litr' : desc1[0].split()[0],
            'horse' : desc1[1].split()[0],
            'toplivo' : desc1[2].split()[0],
            'korob' : desc[1].get_text(),
            'type' : desc[2].get_text().split()[0],
            'price': price.get_text().replace(' ', '').replace('₽', '').replace('от', ''),
            'year': item.find('div', 'ListingItem__year').get_text(),
        }
        cars.append(car)
    return cars


def get_html(url: str, headers: dict, params: Union[None, dict] = None) -> Response:
 
    try:
        return get(url, headers=headers, params=params)
    except Exception as error:
        raise ConnectionError(f'При выполнении запроса произошла ошибка: {error}')


def parse() -> List[dict]:

    url = URL
    print(url)
    html = get_html(url, HEADERS)

    if html.status_code == 200:

        cars = []
        for i in range(1, 70):
            print(f'PArsing {i} page')
            html = get_html(url, HEADERS, params={'page': i})
            cars.extend(get_content(html.content))

            time.sleep(3)

        return cars
    else:
        print(f'Сайт вернул статус-код {html.status_code}')


def save_to_file(data) -> None:
    """Saving data to file."""
    with open(PATH, 'w', newline='', encoding='utf-8') as file:
        w = csv.writer(file, delimiter=';')
        w.writerow(['brand', 'litr', 'horse', 'toplivo', 'korob', 'type', 'year', 'price'])
        for car in data:
            w.writerow([
                car['brand'],
                car['litr'],
                car['horse'],
                car['toplivo'],
                car['korob'],
                car['type'],
                car['year'],
                car['price']
            ])
        os.startfile(PATH)


def main():
    data = parse()
    save_to_file(data)


if __name__ == '__main__':
    main()