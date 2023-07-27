#!/usr/local/bin/python3
# coding=utf-8
from calendar import c
import re
from time import time, localtime
from bs4 import BeautifulSoup
import lxml
import requests
import random
from city_dict import city_dict
from city_dict import longitude_latitude_dict
import weather_dict
import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from chinese_calendar import is_holiday, is_workday
from requests.api import get
import chinese_calendar
from zhdate import ZhDate
import json
import urllib
from fake_useragent import UserAgent
import random
import sys
# 获取环境变量
# 手动设置环境变量
# sys.argv = ['main.py', '2023-03-19', '3.19', '双鱼座', '蔡甸区', '']

# 告白日 形如xxxx-xx-xx
LOVE_DAY = sys.argv[1]
# 女朋友生日  形如x.xx
BIRTHDAY = sys.argv[2]
# 女朋友星座(中文)
CONSTELLATION = sys.argv[3]
# 女朋友目前所在地(中文)   只支持city_dict中收录的地区
AREA = sys.argv[4]
# 彩云密钥
CAIYUN_TOKEN = sys.argv[5]

# 生成每日问候 (dist文件夹)

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

google_chrome_ua_list: list = UserAgent().data_browsers['chrome']

utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)

beijing_now = utc_now.astimezone(SHA_TZ)

# 计算农历
nongli_date = ZhDate.from_datetime(
    datetime(beijing_now.year, beijing_now.month, beijing_now.day))

# 获取24节气
jieqis = chinese_calendar.get_solar_terms(datetime(
    beijing_now.year, 1, 1).date(), datetime(beijing_now.year+1, 1, 1).date())

# 判断今天是不是某个节气
jieqi = '无'
for jieqi_date in jieqis:
    if jieqi_date[0] == beijing_now.date():
        jieqi = jieqi_date[1]
        break

weekday = beijing_now.weekday()

# 是否法定节假日
holiday_flag = '否'

is_holi = is_holiday(beijing_now.date())
if is_holi:
    holiday_flag = '是'
    holi_detail = chinese_calendar.get_holiday_detail(beijing_now.date())
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
                  '起床啦~ 今天也很喜欢你',
                  '美好的一天开始啦',
                  '早上好 打工人',
                  '早安 打工人',
                  '起床啦 打工人',
                  '早上好呀 打工人',
                  '早安呀 打工人',
                  '早呀 打工人',
                  '早早早',
                  '早上好呀']

# 颜文字集合
kaomoji_list = ['(͡o‿O͡)',
                '( ͡°³ ͡°)',
                '( ͡°⊖ ͡°)',
                '( ͡°Ɛ ͡°)',
                '( ͡°з ͡°)',
                '( ͡°- ͡°)',
                '( ͡°👅 ͡°)',
                '( ͡°〓 ͡°)',
                '( ͡° ͜ ͡°)',
                '( ͡° ᴥ ͡°)',
                'ヽ(͡◕ ͜ʖ ͡◕)ﾉ',
                '(◕ᴗ◕✿)',
                '(◕◡◕✿)',
                '( ⁼̴̀ .̫ ⁼̴ )✧',
                '(◔◡◔✿)',
                '(｡◕‿◕｡✿)',
                '(◡‿◡✿)',
                '(◠‿◠✿)',
                '(◕ܫ◕✿)',
                '(◕▿◕✿)',
                '(◕ ワ ◕✿)',
                '╰(✿´⌣`✿)╯♡',
                '٩(๑˃̵ᴗ˂̵๑)۶',
                'σ(o’ω’o)',
                '╲(｡◕‿◕｡)╱',
                '(｡◕ ∀ ◕｡)',
                '(✿╹◡╹)',
                '(δωδ)」',
                '(◍´ಲ`◍)',
                'ฅ ̳͒•ˑ̫• ̳͒ฅ♡',
                '(,,◕ ⋏ ◕,,)',
                '⁙ὸ‿ό⁙',
                '(..＞◡＜..)',
                'ოර⌄රო'
                ]


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


def get_morning_greet(festival_name):
    '''
    生成每日问候语
    :return:
    '''
    print('获取早安问候语..')

    kaomoji_random_num = random.randint(0, len(kaomoji_list)-1)
    # 如果是节日
    if festival_name != '无':
        return f'{festival_name}快乐呀{kaomoji_list[kaomoji_random_num]}'

    # 如果是周末
    if weekday == 5 or weekday == 6:
        return f'周末快乐呀{kaomoji_list[kaomoji_random_num]}'

    # 其余的 生成10以内的随机数 获取早安语
    random_num = random.randint(0, len(morning_greets)-1)
    # # 有50%的概率获取土味情话
    # if random.randint(0, 1) == 1:
    #     return get_lovelive_info().replace('。', '')
    return f'{morning_greets[random_num]}{kaomoji_list[kaomoji_random_num]}'

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
        return '早安啊'


def get_weather_info(city_code):
    '''
    每天8点获取天气信息
    '''
    res = {}
    headers = {
        'Referer': f'http://www.weather.com.cn/weather1dn/{city_code}.shtml',
        'User-Agent': random.choice(google_chrome_ua_list)
    }
    # 天气基本信息

    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_code, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    res['weather'] = weatherinfo["weather"]
    # 最高气温
    res['high'] = weatherinfo["temp"]
    # 最低气温
    res['low'] = weatherinfo["tempn"]
    # 风力
    res['fl'] = weatherinfo["ws"]
    # 风向
    res['fx'] = weatherinfo["wd"]

    # 天气小助手
    url = f'http://www.weather.com.cn/weathern/{city_code}.shtml'
    resp = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(str(resp.content, 'utf-8'), 'lxml')
    # 生活助手
    lv = soup.find_all('div', class_='lv')[0]

    # 紫外线
    uv_level = lv.contents[1].contents[1].text.replace(
        '\n', '')
    res['uv_level'] = uv_level
    # 炎热/寒冷程度
    dress_level = lv.contents[7].contents[1].text.replace(
        '\n', '')
    res['dress_level'] = dress_level
    # 空气污染扩散
    air_pollution_level = lv.contents[11].contents[1].text.replace(
        '\n', '')
    res['air_pollution_level'] = air_pollution_level
    # 温馨提示

    # 紫外线提示
    res['uv_notice'] = lv.contents[1].contents[3].text.replace(
        '。', '')
    # 穿衣提示
    res['dress_notice'] = lv.contents[7].contents[3].text.replace('。', '')

    # 运动提示
    res['sport_notice'] = lv.contents[3].contents[3].text.replace('。', '')

    # 过敏提示
    res['allergy_notice'] = lv.contents[5].contents[3].text.replace('。', '')

    return res


def get_caiyun_weather_info(longitude_latitude):
    '''
    根据经纬度获取彩云天气
    '''
    res = {}
    url = f"https://api.caiyunapp.com/v2.6/{CAIYUN_TOKEN}/{longitude_latitude}/weather?alert=true&hourlysteps=15"

    MAX_RETRY = 3
    retry_times = 0
    while retry_times <= MAX_RETRY:
        try:
            response = get(url)
            if response.ok:
                response_json = response.json()
                # 今日天气
                daily = response_json['result']['daily']
                alert = response_json['result']['alert']
                # 实况
                real_time = response_json['result']['realtime']
                # 小时级别预告
                hourly = response_json['result']['hourly']

                # 天气
                res['weather'] = weather_dict.weather[real_time['skycon']]
                # 最高气温
                res['high'] = daily['temperature'][0]['max']
                # 最低气温
                res['low'] = daily['temperature'][0]['min']
                # 降水概率
                res['precipitation_probability'] = daily['precipitation'][0]['probability']
                # 风力
                res['fl'] = get_fl_desc(
                    daily['wind'][0]['max']['speed'])
                # 风向
                res['fx'] = get_fx_desc(
                    daily['wind'][0]['max']['direction'])
                # 空气质量(国标)
                res['aqi'] = get_aqi_desc(
                    daily['air_quality']['aqi'][0]['avg']['chn'])
                # 紫外线
                res['uv_level'] = daily['life_index']['ultraviolet'][0]['desc']
                # 舒适度
                res['dress_level'] = daily['life_index']['comfort'][0]['desc']
                #  天气预警
                # res['alert'] = alert['content'][0]['description']
                # 温馨提示
                res['notice'] = hourly['description']
                return res
        except Exception:
            print("failed")
            retry_times += 1
            time.sleep(retry_times*retry_times)

    print('获取彩云天气失败')
    return None


def get_fl_desc(fl):
    """获取风力中文描述

    Args:
        fl (_type_): _description_
    """
    if fl >= 0 and fl < 1:
        return '无风'
    elif fl >= 1 and fl < 6:
        return '微风徐徐'
    elif fl >= 6 and fl < 12:
        return '轻风'
    elif fl >= 12 and fl < 20:
        return '树叶摇摆'
    elif fl >= 20 and fl < 29:
        return '树枝摇动'
    elif fl >= 29 and fl < 39:
        return '风力强劲'
    elif fl >= 39 and fl < 50:
        return '风力狂飙'
    elif fl >= 50 and fl < 62:
        return '风力超强'
    elif fl >= 62 and fl < 75:
        return '狂风大作'
    elif fl >= 75 and fl < 89:
        return '狂风呼啸'
    elif fl >= 89 and fl < 103:
        return '暴风毁树'
    elif fl >= 103 and fl < 118:
        return '暴风毁树'
    elif fl >= 118 and fl < 134:
        return '飓风'
    elif fl >= 134 and fl < 150:
        return '台风'
    elif fl >= 150 and fl < 167:
        return '强台风'
    elif fl >= 167 and fl < 184:
        return '强台风'
    elif fl >= 184 and fl < 202:
        return '超强台风'
    elif fl >= 202 and fl < 221:
        return '超强台风'


def get_fx_desc(direction):
    """获取风向中文描述

    Args:
        fx (_type_): _description_
    """
    if direction >= 0 and direction < 45:
        return '北风'
    elif direction >= 45 and direction < 90:
        return '东北风'
    elif direction >= 90 and direction < 135:
        return '东风'
    elif direction >= 135 and direction < 180:
        return '东南风'
    elif direction >= 180 and direction < 225:
        return '南风'
    elif direction >= 225 and direction < 270:
        return '西南风'
    elif direction >= 270 and direction < 315:
        return '西风'
    elif direction >= 315 and direction < 360:
        return '西北风'


def get_aqi_desc(aqi):
    """获取空气质量中文描述

    Args:
        aqi (_type_): _description_
    """
    if aqi >= 0 and aqi <= 50:
        return '优'
    elif aqi >= 51 and aqi <= 100:
        return '良'
    elif aqi >= 101 and aqi <= 150:
        return '轻度污染'
    elif aqi >= 151 and aqi <= 200:
        return '中度污染'
    elif aqi >= 201 and aqi <= 300:
        return '重度污染'
    elif aqi >= 301:
        return '严重污染'


def get_history_info():
    '''
    获取历史上的今天
    '''
    result = {}
    headers = {
        'Host': 'baike.baidu.com',
        'Referer': f'https://baike.baidu.com/calendar/',
        'Sec-Ch-Ua-Platform': 'Windows',
        'User-Agent': random.choice(google_chrome_ua_list)
    }
    month_fmt = beijing_now.strftime("%m")
    month_day_fmt = beijing_now.strftime("%m%d")
    # 获取时间戳
    t = (int(round(time() * 1000)))
    # 获取月份
    url = f'https://baike.baidu.com/cms/home/eventsOnHistory/{beijing_now.strftime("%m")}.json?_={t}'
    res = get(url, headers)
    res.encoding = "utf-8"
    res_json = res.json()
    days = res_json[month_fmt][month_day_fmt]
    # 获取cover为true的
    for day in days:
        if day['cover'] == True:
            # 去处字符串<a>链接
            result['title'] = re.sub(r'<a.*?>|</a>', '',
                                     day['title'])
            result['desc'] = day['desc']
            if day['festival'] == '' or day['festival'] == None:
                result['festival'] = '无'
            else:
                result['festival'] = day['festival']
            return result
    return result


def diff_love_days():
    '''
    计算恋爱天数
    '''
    date1 = dt.datetime(
        beijing_now.year, beijing_now.month, beijing_now.day)
    love_day_ele = LOVE_DAY.split('-')
    date2 = dt.datetime(int(love_day_ele[0]), int(
        love_day_ele[1]), int(love_day_ele[2]))
    return (date1-date2).days


def diff_birthday_days():
    '''
    计算生日天数
    '''
    date1 = dt.datetime(beijing_now.year, beijing_now.month, beijing_now.day)
    birthday_ele = BIRTHDAY.split('.')
    date2 = dt.datetime(beijing_now.year+1,
                        int(birthday_ele[0]), int(birthday_ele[1]))
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


def get_good_and_evil():
    """吉凶宜忌

    Returns:
        _type_: _description_
    """
    url = 'http://v.juhe.cn/laohuangli/d'

    paramas = {
        "key": "21cb6fe53b58a27e4718aa0459167974",  # 您申请的接口API接口请求Key
        "date": beijing_now.strftime(
            '%Y-%m-%d')  # 日期，格式2020-11-24
    }
    querys = urllib.parse.urlencode(paramas).encode(  # type: ignore
        encoding='UTF8')  # type: ignore

    request = urllib.request.Request(url, data=querys)  # type: ignore
    response = urllib.request.urlopen(request)  # type: ignore
    content = response.read()
    if (content):
        try:
            result = json.loads(content)
            error_code = result['error_code']
            if (error_code == 0):
                return result['result']
            else:
                print("请求失败：%s:%s" % (result['error_code'], result['reason']))
        except Exception as e:
            print('解析结果异常：%s' % e)
    else:
        #  可能网络异常等问题，无法获取返回内容，请求异常
        print("请求异常")
        pass


def create_morning(love_days, birthday_days):
    icons = ['✨✨', '🌟🌟', '⭐⭐', '🌼🌼', ' 🐇 🐇 ', ' 🍀 🍀 ', ' 🌻🌻 ', '🌸🌸']
    # 随机选择一个
    icon = random.choice(icons)

    # 历史上的今天
    history_info = get_history_info()
    # 早安问候
    morning_greet = get_morning_greet(history_info['festival'])
    # 天气信息
    # weather_info: dict = get_weather_info(city_dict[AREA])  # type: ignore
    # 彩云天气信息
    caiyun_weather_info = get_caiyun_weather_info(
        longitude_latitude_dict[AREA])
    if not caiyun_weather_info:
        print('获取彩云天气失败')
        sys.exit(1)
    # 星座运势
    constellation_info = get_constellation_info(CONSTELLATION)
    # 吉凶宜忌
    good_evil = get_good_and_evil()
    if good_evil:
        good = good_evil['yi']
        evil = good_evil['ji']
    else:
        good = '无'
        evil = '无'
    # 获取格式化日期
    if jieqi == '无':
        date = beijing_now.strftime(
            '%Y-%m-%d')+' 星期'+week_dict[weekday]
    else:
        date = beijing_now.strftime(
            '%Y-%m-%d')+' 星期'+week_dict[weekday] + ' ' + jieqi

    # 构建微信消息
    msg = f'{morning_greet}\n' + \
        f'今天是我们恋爱的第{love_days}天\n' +\
        f'距离亲爱的生日还有{birthday_days}天\n\n' +\
        f'{icon}今日简报{icon}\n' +\
        f'{date}\n' +\
        f'法定节假日: {holiday_flag}\n' +\
        f'节日: {history_info["festival"]}\n' +\
        f'地区: 武汉市 蔡甸区\n' +\
        f'天气: {caiyun_weather_info["weather"]}\n' +\
        f'气温: {caiyun_weather_info["low"]}°C ~ {caiyun_weather_info["high"]}°C\n' +\
        f'降水概率: {caiyun_weather_info["precipitation_probability"]}%\n' +\
        f'舒适度: {caiyun_weather_info["dress_level"]}\n' +\
        f'风向: {caiyun_weather_info["fx"]}\n' +\
        f'风力: {caiyun_weather_info["fl"]}\n' +\
        f'空气质量: {caiyun_weather_info["aqi"]}\n' +\
        f'紫外线: {caiyun_weather_info["uv_level"]}\n' +\
        f'温馨提示: {caiyun_weather_info["notice"]}\n\n' +\
        f'{icon}双鱼座今日运势{icon}\n' +\
        f'综合运势: {constellation_info["comprehensive_stars_icon"]}\n' +\
        f'事业学业: {constellation_info["study_stars_icon"]}\n' +\
        f'幸运数字: {constellation_info["lucky_num"]}\n' +\
        f'幸运颜色: {constellation_info["lucky_color"]}\n' +\
        f'短评: {constellation_info["short_comment"]}\n\n' +\
        f'{icon}吉凶宜忌{icon}\n' +\
        f'{nongli_date}\n' +\
        f'宜: 【{good}】\n' +\
        f'忌: 【{evil}】\n\n' +\
        f'{icon}历史上的今天{icon}\n' +\
        f'{history_info["title"]}\n\n' +\
        f'{get_ciba_info()}\n\n'

    with open('./dist/morning.txt', 'w+', encoding='utf-8') as f:
        f.write(msg)


if __name__ == '__main__':
    love_days = diff_love_days()
    birthday_days = diff_birthday_days()
    create_morning(love_days, birthday_days)
