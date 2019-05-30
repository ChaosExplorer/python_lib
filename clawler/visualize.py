# -*- coding: utf-8 -*-
from pyecharts import Style
from pyecharts import Geo
from pyecharts.datasets.coordinates import get_coordinate
from urllib import parse
import hashlib
from urllib.request import urlopen
import requests
import json


city = []
with open('hospital.txt', mode='r', encoding='utf-8') as f:
    for line in f.read().splitlines():
        a = line.split(',')
        #if len(a) >= 3 and len(a[2]) > 1:
        #    city.append(a[2].replace('\n', '')[1:3])
        if len(a[0]) > 1:
            city.append(a[0].replace('\n', ''))


def get_url(address):
    queryStr = '/geocoder/v2/?address=%s&output=json&ak=9yBkwt4hoGWX7h06y8mTDDEgMUfHqle5' % address
    encodeStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodeStr + 'IM0C6122N8U5wIYYCooi1i7xfhK2n7qs'
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf-8")).hexdigest())
    url = parse.quote("http://api.map.baidu.com"+queryStr+"&sn="+sn, safe="/:=&?#+!$,;'@()*[]")
    return url

def all_list(arr):
    result = {}
    for i in set(arr):
        result[i] = arr.count(i)

    return result

data = []
alist = all_list(city)
for item in alist:
    data.append((item, alist[item]))

style = Style(
    title_color="#fff",
    title_pos="center",
    width=1800,
    height=920,
    background_color="#404a59"
)

geo = Geo("Nifty Hospitals", "chaos", **style.init_style)

lat,lng = geo.get_coordinate("深圳市")

def add_pos_to_geo(geo):
    for item in data:
        url = get_url(item[0])
        req = urlopen(url)
        res = req.read().decode()
        result = json.loads(res)
        if int(result['status']) == 0 and result['result']['confidence'] > 40:
            geo.add_coordinate(item[0], result['result']['location']['lng'], result['result']['location']['lat'])
        else:
            #print(item[0] + "   : " + str(result['result']['location']['lng']) + " -- " + str(result['result']['location']['lat']) + " -- " + str(result['result']['confidence']))
            data.remove(item)


"""
invalid = []
for index,location in enumerate(attr):
    if get_coordinate(location) is None:
        invalid.append(index)

invalid.reverse()
for index in invalid:
    del attr[index]
    del value[index]

# attr = filter(lambda item: get_coordinate(item) != None, attr)
"""

add_pos_to_geo(geo)

attr, value = geo.cast(data)
geo.add('', attr, value, visual_range=[0, 20],
        visual_text_color='#fff', symbol_size=20,
        is_visualmap=True, is_piecewise=True,
        visual_split_number=4)

geo.render('map3.html')