import requests
from lxml import html
import json
import time
import random
import hashlib
import sys

sys.path.insert(0, '/home/chaos/PycharmProjects/Crawler')
from page import user_agent

movie_index = 3878007
sortkey = "new_score"

def get_one_page(url, retry=0):
    while retry >= 0:
        headers = {
            'User-Agent':user_agent.UserAgents.get_agent()
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif retry == 0:
            print("==> response code : " + str(response.status_code))
            return None

        time.sleep(3)
        retry -= 1


def parse_one_page(html):

    data = json.loads(html)['cmts']

    for item in data:
        yield{
            'comment': item['content'],
            'date': item['time'].split(' ')[0],
            'rate': item['score'],
            'city': item['cityName'],
            'nickname': item['nickName']
        }


def save_to_txt(filename):
    with open(filename, 'w+', encoding='utf-8') as f:
        uniq_list = []
        md5str = ''
        md5str.encode(encoding='utf-8')

        i = 0
        while i < 1001:
            i += 1
            url = 'http://m.maoyan.com/mmdb/comments/movie/1216365.json?_v_=yes&offset=' + str(i)
            html = get_one_page(url)
            print('saving %d page' % i)

            for item in parse_one_page(html):
                md5str = hashlib.md5(item['comment'].encode(encoding='utf-8')).hexdigest()

                if md5str not in uniq_list:
                    print(item['date'] + ',' + item['city'] + ',' + item['nickname'] + ',' + str(item['rate'])+','+item['comment'])
                    f.write(item['date'] + ',' + item['city'] + ',' + item['nickname'] + ',' + str(item['rate'])+','+item['comment']+'\n')
                    uniq_list.append(md5str)

            if len(uniq_list) > 10000:
                        uniq_list.clear()

            time.sleep(1 + float(random.randint(1, 100)) / 50)

def get_user_location(urls):
    locations = []
    for url in urls:
        page = get_one_page(url, 5)

        if page is None:
            locations.append("secrect")
            continue

        tree = html.fromstring(page)
        t = tree.xpath('//div[@class="user-info"]/a/text()')
        if len(t) > 0:
            locations += t
        else:
            locations.append("secrect")

        time.sleep(1 + float(random.randint(1, 50) / 50))
    return locations

def fetch_douban(filename):
    step = 20
    page_index = -1

    url_prefix = 'https://movie.douban.com/subject/' + str(movie_index) + '/comments?start='
    with open(filename, 'w+', encoding='utf-8') as f:
        while page_index < 1500:
            page_index += 1
            url = url_prefix + str(page_index*step) + '&limit= 20&sort='+ sortkey +'&status=P'
            url2 = 26985127
            page = get_one_page(url, 5)
            if page is None:
                continue
            tree = html.fromstring(page)

            names = tree.xpath('//div[@class="avatar"]/a/@title')
            comment_times = tree.xpath('//span[@class="comment-info"]/span[last()]/@title')
            locations = get_user_location(tree.xpath('//div[@class="avatar"]/a/@href'))
            comments = tree.xpath('//span[@class="short"]/text()')

            print("==> page " + str(page_index) + ", names: " + str(len(names)) + ", comment_times: " + str(len(comment_times)) + ", locations: " + str(len(locations)) + ", comments: " + str(len(comments)))
            for i in range(0, step - 1):
                print(comment_times[i] + ', ' + names[i] + ', ' + locations[i] + ', ' + comments[i] + '\n')
                f.write(comment_times[i] + ', ' + names[i] + ', ' + locations[i] + ', ' + comments[i] + '\n')

if __name__ == '__main__':
    movie_index = int(sys.argv[1])
    fetch_douban(sys.argv[2])
