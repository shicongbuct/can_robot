import sys
from bs4 import BeautifulSoup
import requests
import re

def fetchAllPriceIndex():
    sys.setrecursionlimit(2000)
    index_dict = {}
    r = requests.get('https://www.feixiaohao.com/list_1.html')
    last_page = re.search(r'\.\.\.</a>.+ href=/list_\d+.html>(.*?)</a><a class="btn btn-white" href=/list_2.html>', r.text).group(1)
    for i in range(1, int(last_page) + 1):
        url = 'https://www.feixiaohao.com/list_' + str(i) + '.html'
        r = requests.get(url)
        html = re.search(r'<table class="new-table new-coin-list" id=table>(.*?)</table>', r.text).group(0)
        soup = BeautifulSoup(html)
        table = soup.find(id="table").find('tbody')
        for tr in table.find_all('tr'):
            print(tr["id"])
            td = tr.select("td:nth-of-type(2)")
            name = td[0].find('a').contents[2]
            print(name)
            name_str = name.rstrip().lower().split('-')
            link = td[0].find('a')["href"]
            index_dict[name_str[0]] = link
    return index_dict

if __name__ == '__main__':
    index_dict = fetchAllPriceIndex()
    print(index_dict)
    with open('./token_index', 'a+') as f:
        for key, value in index_dict.items():
            f.write(key + ' ' + value + '\n')
