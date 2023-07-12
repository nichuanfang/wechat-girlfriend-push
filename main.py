#!/usr/local/bin/python3
# coding=utf-8
from re import S
from bs4 import BeautifulSoup
import requests
import random
import datetime
from city_dict import city_dict

# 生成每日问候 (dist文件夹)
today = datetime.date.today()
weekday = today.weekday()
week_dict: dict[int, str] = {
    0: '一',
    1: '二',
    2: '三',
    3: '四',
    4: '五',
    5: '六',
    6: '日'
}

morning_greets = ['早上好呀 今天也是元气满满的一天哦！',
                  '小才女 早上好!',
                  '找安 crush!',
                  '早安 宝☀☀',
                  '长得帅的先说早 早早早',
                  '早鸭',
                  '早安呀',
                  '早呀',
                  '别睡了 起来做早操 现在勤锻炼 幸福过晚年',
                  '早上好!!!',
                  '起床啦 宝宝',
                  '美好的一天又开始啦',
                  f'早呀 今天是七天中难得一遇的星期{week_dict[weekday]}耶',
                  '中国14亿人我只跟你说早安哦 臭宝~',
                  '早上好',
                  '早安啊才女',
                  '宝宝 早早早',
                  '早安 小美女',
                  '早早早呀仙女',
                  '早上好呀宝',
                  '起床啦~ 汇报一下 今天也很喜欢你❤']

# 早安问候


def get_morning_greet():
    '''
    生成每日问候语
    :return:
    '''
    print('获取早安问候语..')

    # 生成10以内的随机数
    random_num = random.randint(0, morning_greets.__len__())
    return morning_greets[random_num]

# 获取格言信息


def get_dictum_info():
    '''
    获取格言信息（从『一个。one』获取信息 http://wufazhuce.com/）
    :return: str 一句格言或者短语
    '''
    print('获取格言信息..')
    user_url = 'http://wufazhuce.com/'
    resp = requests.get(user_url)
    soup_texts = BeautifulSoup(resp.text, 'lxml')
    # 『one -个』 中的每日一句
    every_msg = soup_texts.find_all(
        'div', class_='fp-one-cita')[0].find('a').text
    return every_msg

# 金山词霸


def get_ciba_info():
    '''
    从词霸中获取每日一句，带英文。
    :return:
    '''
    resp = requests.get('http://open.iciba.com/dsapi')
    if resp.status_code == 200:
        conentJson = resp.json()
        content = conentJson.get('content')
        note = conentJson.get('note')
        # print(f"{content}\n{note}")
        return f"{content}\n{note}\n"
    else:
        print("没有获取到数据")
        return None


def get_lovelive_info():
    '''
    从土味情话中获取每日一句。
    '''
    resp = requests.get("https://api.lovelive.tools/api/SweetNothings")
    if resp.status_code == 200:
        return resp.text + "\n"
    else:
        print('每日一句获取失败')
        return None

# 获取每日天气


def get_weather_info(city_code=''):
    weather_url = f'http://t.weather.sojson.com/api/weather/city/{city_code}'
    resp = requests.get(url=weather_url)
    if resp.status_code == 200 and resp.json().get('status') == 200:
        weatherJson = resp.json()
        # 今日天气
        today_weather = weatherJson.get('data').get('forecast')[0]
        return today_weather


def create_morning1():
    morning_greet = get_morning_greet()
    # 写入文件
    with open('./dist/morning1.md', 'w', encoding='utf-8') as f:
        f.write(morning_greet)


def create_morning2():
    weather_info: dict = get_weather_info(city_dict['武汉'])  # type: ignore
    # 获取格式化日期
    date = datetime.datetime.now().strftime(
        '%Y-%m-%d')+' 星期'+week_dict[weekday]

    msg = f'美好的一天开始啦~\n' + \
        f'{today.month}月{today.day}日 \n\n' +\
        f'{date}\n' +\
        f'地区: 武汉市\n' +\
        f'天气: {weather_info["type"]}\n' +\
        f'气温: {weather_info["low"]} ~ {weather_info["high"]}\n' +\
        f'风向: {weather_info["fx"]}\n' +\
        f'风力: {weather_info["fl"]}\n' +\
        f'空气质量: {weather_info["aqi"]}\n' +\
        f'温馨提示: {weather_info["notice"]}\n\n' +\
        f'每日一句: {get_ciba_info()}\n\n'

    # f'今天是我们恋爱的第{}天' +\
    # f'距离亲爱的生日还有{}天' +\
    with open('./dist/morning2.md', 'w', encoding='utf-8') as f:
        f.write(msg)


if __name__ == '__main__':
    know_days = 10
    love_days = 100
    birthday_days = 10

    create_morning1()
    create_morning2()
    pass
