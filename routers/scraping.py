from TikTokApi import TikTokApi
import pandas as pd
import json

def get_cookies_from_file():
    with open('cookies.json') as f:
        cookies = json.load(f)

    cookies_kv = {}
    for cookie in cookies:
        cookies_kv[cookie['name']] = cookie['value']

    return cookies_kv


cookies = get_cookies_from_file()


def get_cookies(**kwargs):
    return cookies


api = TikTokApi()

api._get_cookies = get_cookies

for video in api.trending.videos():
  print(print)
  break