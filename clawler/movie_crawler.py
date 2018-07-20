import requests
import json
import time
import random
import hashlib
import sys

def get_one_page(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko)'
                      ' Chrome/64.0.3282.140 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


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
        for i in range(1, 1001):
            url = 'http://m.maoyan.com/mmdb/comments/movie/248566.json?_v_=yes&offset=' + str(i)
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

            time.sleep(3 + float(random.randint(1, 100)) / 50)


if __name__ == '__main__':
    save_to_txt(sys.argv[1])