from alertbot import AlertBot
from pipeline import compare_watchlist_to_shop_items
import pytest


def test_compare_watchlist_to_shop_items_for_items_wanted():
    watchlist = ['octane', 'twinzer', 'dominus']
    daily_items = [
        {'name': 'Octane ZSR', 'category': 'RareBody', 'credits': 500},
        {'name': 'fennec', 'category': 'ImportDecal', 'credits': 500}
    ]

    actual = compare_watchlist_to_shop_items(watchlist, daily_items)
    expected = 'send_slack_alert'

    assert actual == expected


def test_compare_watchlist_to_shop_items_and_not_find_anything_wanted():
    watchlist = ['zippy', 'twinzer', 'dominus']
    daily_items = [
        {'name': 'Octane ZSR', 'category': 'RareBody', 'credits': 500},
        {'name': 'fennec', 'category': 'ImportDecal', 'credits': 500}
    ]

    actual = compare_watchlist_to_shop_items(watchlist, daily_items)
    expected = 'log_to_slack'

    assert actual == expected


def test_compare_watchlist_to_shop_items_without_daily_items():
    with pytest.raises(Exception):
        watchlist = ['octane', 'twinzer', 'dominus']
        compare_watchlist_to_shop_items(watchlist, None)


def test_alertbot_with_items():
    alert_bot = AlertBot('#test', data = [
        {'name': 'Octane ZSR', 'category': 'RareBody', 'credits': 500},
        {'name': 'fennec', 'category': 'ImportDecal', 'credits': 500}
    ])

    result = alert_bot.get_message_payload()

    assert type(result) == dict
    assert list(result.keys()) == ['channel', 'text', 'blocks']


def test_alertbot_with_wrong_data():
    with pytest.raises(TypeError):
        alert_bot = AlertBot('#test-fail', 'failing test')