from pyecharts import Style
from pyecharts import Geo
from pyecharts.datasets.coordinates import get_coordinate

city = []
with open('parsed_1.txt', mode='r', encoding='utf-8') as f:
    for line in f.read().splitlines():
        a = line.split(',')
        if len(a) == 5 and len(a[1]) > 1:
            city.append(a[1].replace('\n', ''))


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

geo = Geo("movie fans data", "chaos", **style.init_style)
attr, value = geo.cast(data)

"""
no_map_list = []
with open('no_map', 'r') as f:
    no_map_list = f.read().splitlines()
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

geo.add('', attr, value, visual_range=[0, 20],
        visual_text_color='#fff', symbol_size=20,
        is_visualmap=True, is_piecewise=True,
        visual_split_number=4)

geo.render('map.html')