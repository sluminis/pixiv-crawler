import requests
import re
import os
import json
import demjson
from bs4 import BeautifulSoup
from user import User


class Artist:

    url = 'https://www.pixiv.net/member_illust.php'
    _parser = User.parser

    def __init__(self, P, uid):
        self.P = P
        self.uid = uid
        self.content = {}

    def crawlWorks(self, selector):
        workdata = selector.find_all('img', class_='_thumbnail ui-scroll-view')
        #print(len(workdata))
        wid_list = []
        for img in workdata:
            wid_list.append(int(img.attrs['data-id']))
        return wid_list

    def crawlWorksList(self, type = 'illust'):
        self.content[type] = []
        params = {'id': self.uid, 'type': type}
        html = self.P.get(url = self.url, params = params)
        selector = BeautifulSoup(html.text, self._parser)

        if 'name' not in self.content:
            self.content['name'] = selector.find('a', class_ = 'user-name').attrs['title']
        self.content[type].extend(self.crawlWorks(selector))

        while True:
            pager = selector.find("div",class_ = "pager-container")
            if pager is None: break
            next_a = pager.find("span", class_ = "next").find("a")
            if next_a is None: break
            next_href = next_a.attrs['href']
            #print(url_base + url_work + next_href)
            html = self.P.get(url = self.url + next_href)
            selector = BeautifulSoup(html.text, self._parser)
            self.content[type].extend(self.crawlWorks(selector))

    def crawl(self):
        print('Getting WorksList(%d): ' % int(self.uid), end="")
        crawl_types = ['illust', 'manga', 'ugoira']
        for ctype in crawl_types:
            self.crawlWorksList(ctype)
        count = 0
        for (k,v) in self.content.items():
            count += len(v)
        print(count)
        return self.content

if __name__ == '__main__':
    P = User('','').getSession()
    at = Artist(P, 605284)
    at.crawl()
    print(at.content)
