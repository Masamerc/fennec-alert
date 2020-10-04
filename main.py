from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator

import requests
import pickle

from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'referer': 'https://www.google.com/'
    }

URL = 'https://rocket-league.com/items/shop'

# # scrape
# res = requests.get(URL, headers=HEADERS)
# soup = BeautifulSoup(res.content, 'lxml')

# # Mongo
# conn = BaseHook.get_connection('mongo_db')
# uri = conn.get_uri()
# client = MongoClient(uri)
# db = client.RL_items
# subreddit_collec = db.daily_shop_items



with open('rl_soup_dump.pkl', 'rb') as p:
    soup = pickle.load(p)


default_args = {
    'owner': 'fennec-alert',
    'schedule_intervals': '@daily'
}



def scrape_daily_items(**context):
    daily_items = []

    for div in soup.find_all('div', attrs={'class': 'rlg-item-shop__item-content'}):
        
        item_name = div.find('h1', attrs={'class': 'rlg-item-shop__name'})
        item_category = div.find('div', attrs={'class': 'rlg-item-shop__item-category'})
        item_credits = div.find('div', attrs={'class': 'rlg-item-shop__item-credits'})
        
        if not item_name:
            item_name = div.find('h1', attrs={'class': 'rlg-h2 rlg-item-shop__name --daily'}) 
        
        soup_result = {
            'name': item_name,
            'category': item_category,
            'credits': item_credits
        }
        
        item = {
            'name': soup_result.get('name', 'Not Found').text.strip(),
            'category': soup_result.get('category', 'Not Found').text.strip(),
            'credits': int(soup_result.get('credits', 'Not Found').text)
        }
        
        daily_items.append(item)


def check_shop_item():
    for item in daily_items:
        
        for body in bodies:
            if body in item['name'].lower():
                print(f'Item Found: {item["name"]} -> {body}')
                is_wanted = True
                break
                
            else:
                is_wanted = False
        
            
        if 'body' in item['category'].lower():
            print('it is a body')
            is_body = True
        else:
            is_body=False
            
        
        if is_wanted and is_body:
            print(f'there it is! lets go spend some money on {item["name"]}: {item["credits"]} credits')
            # xcom_push
            # return 'send alert'
    


    with DAG('fennec_alert', default_args=default_args,):
        pass
    