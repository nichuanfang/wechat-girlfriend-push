#!/usr/local/bin/python3
# coding=utf-8
from bs4 import BeautifulSoup
import lxml
import requests
import random
from city_dict import city_dict
import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from chinese_calendar import is_holiday, is_workday
import chinese_calendar


# 生成每日问候 (dist文件夹)

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)

beijing_now = utc_now.astimezone(SHA_TZ)

weekday = beijing_now.weekday()

# 是否法定节假日

holiday_flag = '否'
festival_name = '无'

is_holi = is_holiday(beijing_now.date())
if is_holi:
    holiday_flag = '是'
    holi_detail = chinese_calendar.get_holiday_detail(beijing_now.date())
    if holi_detail[0] and holi_detail[1]:
        festival_name = holi_detail[1]
week_dict: dict[int, str] = {
    0: '一',
    1: '二',
    2: '三',
    3: '四',
    4: '五',
    5: '六',
    6: '天'
}

morning_greets = ['早上好呀 今天也是元气满满的一天哦',
                  '小才女 早上好',
                  '早安呀 crush',
                  '早安 宝',
                  '早鸭',
                  '早安呀',
                  '早呀',
                  '早上好',
                  '起床啦 宝宝',
                  '美好的一天又开始啦',
                  f'早呀 今天是七天中难得一遇的星期{week_dict[weekday]}耶',
                  '中国14亿人我只跟你说早安哦 臭宝',
                  '早上好',
                  '早安啊小才女',
                  '宝宝 早早早',
                  '早安 小美女',
                  '早早早呀仙女',
                  '早上好呀宝',
                  '起床啦~ 汇报一下 今天也很喜欢你❤',
                  '美好的一天开始啦']

constellation_dict = {
    "水瓶座": "Aquarius",
    "双鱼座": "Pisces",
    "白羊座": "Aries",
    "金牛座": "Taurus",
    "双子座": "Gemini",
    "巨蟹座": "Cancer",
    "狮子座": "Leo",
    "处女座": "Virgo",
    "天秤座": "Libra",
    "天蝎座": "Scorpio",
    "射手座": "Sagittarius",
    "摩羯座": "Capricorn"
}


def get_morning_greet():
    '''
    生成每日问候语
    :return:
    '''
    print('获取早安问候语..')

    # 生成10以内的随机数
    random_num = random.randint(0, len(morning_greets)-1)
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


def diff_love_days():
    '''
    计算恋爱天数
    '''
    date1 = dt.datetime(
        beijing_now.year, beijing_now.month, beijing_now.day)
    date2 = dt.datetime(2023, 3, 20)
    return (date1-date2).days


def diff_birthday_days():
    '''
    计算生日天数
    '''
    date1 = dt.datetime(beijing_now.year, beijing_now.month, beijing_now.day)
    date2 = dt.datetime(beijing_now.year+1, 3, 19)
    return (date2-date1).days


def get_star_icon(stars):
    if stars == 0:
        return '☆☆☆☆☆'
    elif stars == 1:
        return '★☆☆☆☆'
    elif stars == 2:
        return '★★☆☆☆'
    elif stars == 3:
        return '★★★☆☆'
    elif stars == 4:
        return '★★★★☆'
    elif stars == 5:
        return '★★★★★'


def get_constellation_info(constellation_name):
    '''
    从星座屋中获取星座运势
    :param constellation_name: 星座名称
    :return:
    '''
    print('获取星座运势..')
    res = {}
    user_url = f'http://www.xzw.com/fortune/{constellation_dict[constellation_name]}'
    resp = requests.get(user_url)
    soup_texts = BeautifulSoup(resp.text, 'lxml')
    fortune = soup_texts.find_all('dd')[1].contents[1].contents

    # 综合运势
    comprehensive_stars = int(fortune[0].contents[1].contents[0]
                              ['style'].split(':')[1][:-3])/16
    comprehensive_stars_icon = get_star_icon(comprehensive_stars)
    # 事业学业
    study_stars = int(fortune[2].contents[1].contents[0]
                      ['style'].split(':')[1][:-3])/16
    study_stars_icon = get_star_icon(study_stars)
    # 幸运数字
    lucky_num = fortune[7].contents[1]
    # 幸运颜色
    lucky_color = fortune[6].contents[1]
    # 短评
    short_comment = fortune[9].contents[1]

    res['comprehensive_stars_icon'] = comprehensive_stars_icon
    res['study_stars_icon'] = study_stars_icon
    res['lucky_num'] = lucky_num
    res['lucky_color'] = lucky_color
    res['short_comment'] = short_comment
    return res


def create_morning(love_days, birthday_days):
    morning_greet = get_morning_greet()
    weather_info: dict = get_weather_info(city_dict['蔡甸区'])  # type: ignore
    constellation_info = get_constellation_info('双鱼座')
    # 获取格式化日期
    date = beijing_now.strftime(
        '%Y-%m-%d')+' 星期'+week_dict[weekday]

    msg = f'{morning_greet}~\n' + \
        f'今天是我们恋爱的第【{love_days}】天\n' +\
        f'距离亲爱的生日还有【{birthday_days}】天\n\n' +\
        f'⭐⭐今日简报⭐⭐\n' +\
        f'{date}\n' +\
        f'法定节假日: 【{holiday_flag}】\n' +\
        f'节日: 【{festival_name}】\n' +\
        f'地区: 武汉市 蔡甸区\n' +\
        f'天气: {weather_info["type"]}\n' +\
        f'气温: {weather_info["low"]} ~ {weather_info["high"]}\n' +\
        f'风向: {weather_info["fx"]}\n' +\
        f'风力: {weather_info["fl"]}\n' +\
        f'空气质量: {weather_info["aqi"]}\n' +\
        f'温馨提示: {weather_info["notice"]}~\n\n' +\
        f'⭐⭐双鱼座今日运势⭐⭐\n' +\
        f'综合运势: {constellation_info["comprehensive_stars_icon"]}\n' +\
        f'事业学业: {constellation_info["study_stars_icon"]}\n' +\
        f'幸运数字: {constellation_info["lucky_num"]}\n' +\
        f'幸运颜色: {constellation_info["lucky_color"]}\n' +\
        f'短评: {constellation_info["short_comment"]}\n\n' +\
        f'⭐⭐每日一句⭐⭐\n' +\
        f'{get_ciba_info()}\n\n'

    with open('./dist/morning.txt', 'w+', encoding='utf-8') as f:
        f.write(msg)


if __name__ == '__main__':
    love_days = diff_love_days()
    birthday_days = diff_birthday_days()
    create_morning(love_days, birthday_days)
