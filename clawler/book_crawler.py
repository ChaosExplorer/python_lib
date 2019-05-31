import requests
from lxml import html
import json
import time
import random
import hashlib
import sys

sys.path.insert(0, '../Crawler')
from page import user_agent

reach_end_count = 0;

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

        time.sleep(1)
        retry -= 1


def fetch_book(filename):
    page_index = -1
    reach_end_count = 0

    url_prefix = 'http://mebook.cc/download.php?id='
    with open(filename, 'w+', encoding='utf-8') as f:
        while reach_end_count < 1000:
            page_index += 1
            url = url_prefix + str(page_index)
            page = get_one_page(url, 5)
            if page is None:
                continue
            tree = html.fromstring(page)

            name = tree.xpath('//h1/a/text()')
            location = tree.xpath('//div[@class="list"]/a[1]/@href')
            if not name or not location:
                reach_end_count += 1
                continue
            else:
                reach_end_count = 0

            name = name[0].strip()
            format_index = name.find('epub')
            if format_index != -1:
                name = name[:format_index]

            passwd = tree.xpath('//div[@class="desc"]/p[last()-1]/text()')[0].strip()
            space_index = passwd.find('&nbsp')
            passwd = passwd[passwd.find('：')+1:] if space_index == -1 else passwd[passwd.find('：')+1:space_index-1]

            location = location[0].strip()
            if get_one_page(location, 3) is None:
                continue

            print(str(page_index) + " , " + name + " , " + passwd + " , " + location)
            f.write(str(page_index) + " , " + name + " , " + passwd + " , " + location + '\n')

if __name__ == '__main__':
    fetch_book(sys.argv[1])
