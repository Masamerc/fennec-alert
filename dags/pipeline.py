#!usr/bin/python
# -*- coding: utf-8 -*-

import requests

from airflow.models import DAG, Variable
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago

from alertbot import AlertBot
from bs4 import BeautifulSoup
from datetime import date, timedelta
from pymongo import MongoClient
from slack import WebClient


# Airflow DAG setup
default_args = {
    'owner': 'fennec-alert-project'
}

dag = DAG(
    'fennec-alert',
    start_date=days_ago(1),
    schedule_interval='@daily',
)


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'referer': 'https://www.google.com/'
    }

URL = 'https://rocket-league.com/items/shop'



def scrape_daily_items(**context):

    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.content, 'lxml')

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
            'credits': int(soup_result.get('credits', 'Not Found').text),
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        daily_items.append(item)
    
    context['ti'].xcom_push(key='daily_items', value=daily_items)


def compare_watchlist_to_shop_items(watchlist: list, daily_items: list) -> bool:
    """Helper function that checks if items on watchlist are on sale and return applicable task_id"""

    if type(daily_items) != list or len(daily_items) <= 0:
        raise Exception('daily_items has to be a list of strings and cannot be empty')

    for item in daily_items:
        for body in watchlist:
            if body in item['name'].lower():
                is_wanted = True
                break            
            else:
                is_wanted = False
        
        if 'body' in item['category'].lower():
            is_body = True
        else:
            is_body = False
        
        # if any item on wathclist is on sale & its type is "body" return task for sending slack alert
        if is_wanted and is_body:
            return 'send_slack_alert'
    
    # if the condition above is not met, just log the result to slack
    return 'log_to_slack'


def check_shop_item(**context):
    bodies = ['fennec', 'octane', 'twinzer', 'mudcat', 'sentinel']
    daily_items = context['ti'].xcom_pull(key='daily_items', task_ids=['scrape_daily_items'])[0]

    return compare_watchlist_to_shop_items(bodies, daily_items)


def load_to_mongo(**context):
    # Mongo setup
    uri = Variable.get('mongo_db_uri')
    client = MongoClient(uri)
    db = client.rl_items
    daily_items_collec = db.daily_items

    daily_items = context['ti'].xcom_pull(key='daily_items', task_ids=['scrape_daily_items'])[0]
    daily_items_collec.insert_many(daily_items)


def send_slack_alert(channel_name, **context):
    # slack setup
    slack = WebClient(Variable.get('SLACK_BOT_TOKEN'))

    daily_items = context['ti'].xcom_pull(key='daily_items', task_ids=['scrape_daily_items'])[0]
    alert_bot= AlertBot(channel_name, daily_items)
    message = alert_bot.get_message_payload()
    slack.chat_postMessage(**message)


with dag:

    scrape_daily_items_task = PythonOperator(
        task_id='scrape_daily_items',
        python_callable=scrape_daily_items,
        provide_context=True,
        execution_timeout=timedelta(minutes=30),
        retries=5
    )

    load_to_mongo_task = PythonOperator(
        task_id='load_to_mongo',
        python_callable=load_to_mongo,
        provide_context=True,
        execution_timeout=timedelta(minutes=30),
        retries=5
    )


    check_shop_item_task = BranchPythonOperator(
        task_id='check_shop_item',
        python_callable=check_shop_item,
        provide_context=True,
        execution_timeout=timedelta(minutes=30),
        retries=5
    )

    send_slack_alert_task = PythonOperator(
        task_id='send_slack_alert',
        python_callable=send_slack_alert,
        op_kwargs={'channel_name': '#rl-alert'},
        provide_context=True,
        execution_timeout=timedelta(minutes=30),
        retries=5
    )

    log_to_slack_task = PythonOperator(
        task_id='log_to_slack',
        python_callable=send_slack_alert,
        op_kwargs={'channel_name': '#rl-logs'},
        provide_context=True,
        execution_timeout=timedelta(minutes=30),
        retries=5
    )

    scrape_daily_items_task >> load_to_mongo_task >> check_shop_item_task >> [send_slack_alert_task, log_to_slack_task]
