import requests
import re
import os
import json
import demjson
from bs4 import BeautifulSoup

import time
from functools import wraps


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r

    return wrapper


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
}

params = {
    'lang':'sh',
    'source':'pc',
    'view_type':'page',
    'ref':'wwwtop_accounts_index'
}

proxies = {
    "http": "http://127.0.0.1:1080",
    "https": "http://127.0.0.1:1080"
}

data = {
    'pixiv_id': '*********',
    'password': '*******8*',
    'captcha':'',
    'g_recaptcha_response':'',
    'post_key':'',
    'source':'pc',
    'ref':'wwwtop_accounts_index',
    'return_to':'https://www/pixiv.net/'
}

parser = 'html.parser'

p = requests.Session()
p.headers = header
p.proxies = proxies
url_base = "https://www.pixiv.net/"
folder_base = "./images/"


def Login():
    url_login = 'https://accounts.pixiv.net/login'
    r = p.get(url = url_login, params = params)
    pattern = re.compile(r'name="post_key" value="(.*?)">')
    result = pattern.findall(r.text)
    data['post_key'] = result[0]
    print(data['post_key'])
    p.post(url = url_login, data = data)
    print('Login success')


def CrawlURL(selector):
    userdata = selector.find_all('div', class_ = 'userdata')
    print(len(userdata))
    urls = []
    for data in userdata:
        a = data.find('a')
        urls.append(a.attrs['href'])
    return urls


def CrawlFollowInfo(selector):
    userdata = selector.find_all('div', class_ = 'userdata')
    print(len(userdata))
    info = []
    for data in userdata:
        a = data.find('a')
        info.append(a.attrs)
    return info


def CrawlFollowList():
    print('getFollowList:')
    url_work = 'bookmark.php'
    info = []
    html = p.get(url = url_base + url_work + '?type=user&rest=show')
    selector = BeautifulSoup(html.text, parser)
    info.extend(CrawlFollowInfo(selector))

    while True:
        pager = selector.find("div",class_ = "_pager-complex")
        if(pager is None): break
        next_a = pager.find("a", attrs = {'rel':'next'})
        if(next_a is None): break
        next_href = next_a.attrs['href']
        html = p.get(url = url_base + url_work + next_href)
        selector = BeautifulSoup(html.text, parser)
        info.extend(CrawlFollowInfo(selector))

    print('length of FollowList: ',len(info))
    return info


class Artist:

    url = 'https://www.pixiv.net/member_illust.php'

    def __init__(self, id):
        self.uid = id
        self.content = { }

    def crawlWorks(self, selector):
        workdata = selector.find_all('img', class_='_thumbnail ui-scroll-view')
        print(len(workdata))
        wid_list = []
        for img in workdata:
            wid_list.append(int(img.attrs['data-id']))
        return wid_list


    def crawlWorksList(self, type = 'illust'):
        print('getWorksList:')
        self.content[type] = []
        params = {'id': self.uid, 'type': type}
        html = p.get(url = self.url, params = params)
        selector = BeautifulSoup(html.text, parser)

        if 'name' not in self.content:
            self.content['name'] = selector.find('a', class_ = 'user-name').attrs['title']
        self.content[type].extend(self.crawlWorks(selector))

        while True:
            pager = selector.find("div",class_ = "pager-container")
            if(pager is None): break
            next_a = pager.find("span", class_ = "next").find("a")
            if(next_a is None): break
            next_href = next_a.attrs['href']
            #print(url_base + url_work + next_href)
            html = p.get(url = self.url + next_href)
            selector = BeautifulSoup(html.text, parser)
            self.content[type].extend(self.crawlWorks(selector))

        print('length of WorksList: ', len(self.content[type]))


    def crawlData(self):
        expected_types = ['illust', 'manga', 'ugoira']
        for ctype in expected_types:
            self.crawlWorksList(ctype)


#===============================Expired=====================================

# def CrawlWorkTags(section):
#     tags = []
#     li = section.find_all('li', class_ = 'tag')
#     for t in li:
#         tag = t.find('a', class_ = 'text js-click-trackable-later')
#         tags.append(list(tag.stripped_strings)[0])
#
#     return tags
#
#
# def CrawlWorkInfo(selector):
#     info = {}
#     work_info = selector.find('section', class_='work-info')
#     # view,rated
#     score = work_info.find('section', class_ = 'score')
#     view_count = score.find('dd', class_ = 'view-count')
#     rated_count = score.find('dd', class_ = 'rated-count')
#     info['view'] = view_count.get_text()
#     info['rated'] = rated_count.get_text()
#     # date,type
#     meta = work_info.find('ul', class_ = 'meta')
#     li = meta.find_all('li')
#     info['date'] = li[0].get_text()
#     info['type'] = li[1].get_text()
#     # R-18
#     r18 = meta.find('li', class_ = 'r-18')
#     if(r18 is not None):
#         info['R-18'] = r18.get_text()
#     # title
#     title = work_info.find('h1', class_ = 'title')
#     info['title'] = title.get_text()
#     #tags
#     work_tags = selector.find('section', class_='work-tags')
#     if(work_tags is not None):
#         info['tags'] = CrawlWorkTags(work_tags)
#
#     return info
#
#
# def CrawlImages(selector, wid):
#     url_work = 'member_illust.php'
#     params_work = {
#         'mode': 'manga',
#         'illust_id': wid
#     }
#     img = []
#     origin_img = selector.find("img", class_="original-image")
#     if origin_img is not None:
#         src = origin_img.attrs['data-src']
#         img.append(src)
#     else:
#         manga = p.get(url = url_base + url_work, params = params_work)
#         select = BeautifulSoup(manga.text, parser)
#         hrefs = select.find_all('a', class_ = 'full-size-container')
#         #prepare regex
#         pattern = re.compile(r'<img src="(.*?)" onclick=')
#
#         for href in hrefs:
#             url_img = url_base + href.attrs['href'][1:]
#             html = p.get(url = url_img)
#             result = pattern.findall(html.text)
#             img.append(result[0])
#
#     return img
#
#
# def QuickCrawlImages(selector, wid):
#     url_work = 'member_illust.php'
#     params_work = {
#         'mode': 'manga',
#         'illust_id': wid
#     }
#     img = []
#     origin_img = selector.find("img", class_="original-image")
#     if origin_img is not None:
#         src = origin_img.attrs['data-src']
#         img.append(src)
#     else:
#         manga = p.get(url = url_base + url_work, params = params_work)
#         select = BeautifulSoup(manga.text, parser)
#         hrefs = select.find_all('img', attrs = {'data-filter': 'manga-image'})
#
#         #prepare regex
#         pattern = re.compile(r'http(s)?://(.*?)master(.*?)_master[0-9]*(.*)')
#         for href in hrefs:
#             zipped = href.attrs['data-src']
#             result = pattern.findall(zipped)[0]
#             original = 'https://' + result[1] + 'original' + result[2] + result[3]
#             img.append(original)
#     return img
#
#
# def CrawlWorkDetail(wid):
#     url_work = 'member_illust.php'
#     params_work = {
#         'mode': 'medium',
#         'illust_id': wid
#     }
#     detail = {}
#
#     html = p.get(url = url_base + url_work, params = params_work)
#     selector = BeautifulSoup(html.text, parser)
#     detail.update(CrawlWorkInfo(selector))
#
#     #crawl images
#     detail['images'] = QuickCrawlImages(selector, wid)
#
#     return detail

#============================End of Expired=================================


class Work:

    url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    wid = 0
    content = None

    def __init__(self, id):
        self.wid = id

    def __fillContent(self, data):
        work_dir = data['preload']['illust'][self.wid]

        #self.content['uid']             = work_dir['userId']
        #self.content['name']            = data['preload']['user'][self.content['uid']]['name']
        self.content['wid']             = work_dir['illustId']
        self.content['title']           = work_dir['illustTitle']
        self.content['type']            = work_dir['illustType']
        self.content['comment']         = work_dir['illustComment']
        self.content['createDate']      = work_dir['createDate']
        self.content['uploadDate']      = work_dir['uploadDate']
        self.content['width']           = work_dir['width']
        self.content['height']          = work_dir['height']
        self.content['pageCount']       = work_dir['pageCount']
        self.content['bookmarkCount']   = work_dir['bookmarkCount']
        self.content['likeCount']       = work_dir['likeCount']
        self.content['commentCount']    = work_dir['commentCount']
        self.content['responseCount']   = work_dir['responseCount']
        self.content['viewCount']       = work_dir['viewCount']
        self.content['isHowto']         = work_dir['isHowto']
        self.content['isOriginal']      = work_dir['isOriginal']

        tags = []
        tag_dir = work_dir['tags']['tags']
        for tag in tag_dir:
            tags.append(tag['tag'])
        self.content['tags'] = tags

        images = {}
        img_dir = work_dir['urls']
        images['regular'] = img_dir['regular']
        oimg = img_dir['original']
        oimgs = [oimg]

        #if there are multiple images, just replace the index
        pageCount = self.content['pageCount']
        if pageCount > 1:
            result = re.search(r'(.*p)\d+\.(\w+)$', oimg)
            target = result.group(1)
            itype = result.group(2)
            # print(target,itype)
            for p in range(1, pageCount):
                oimgs.append(target + str(p) + '.' + itype)

        images['original'] = oimgs
        self.content['images'] = images

    def crawlData(self):
        print('crawling work %d' % self.wid)

        start = time.perf_counter()
        try:
            html = p.get(url = self.url + str(self.wid))
        except requests.exceptions.ProxyError:
            print('Bad Proxy(work ID: %d)' % self.wid)
            return
        end = time.perf_counter()
        print("request cost:",end - start)
        self.content = { }
        djson = re.search(r'}\)\((.*?)\);</script>', html.text).group(1)
        #print('djson:',djson)

        start = time.perf_counter()
        data = demjson.decode(djson)
        self.__fillContent(data)
        del data
        end = time.perf_counter()
        print("decode cost:", end - start)



if __name__ == '__main__':
    Login()

    ar = Artist(1226647)
    ar.crawlData()
    print(ar.content)

    wo = Work(67208347)
    wo.crawlData()
    print(wo.content)

    # header['referer'] = 'https://www.pixiv.net/member_illust.php'
    # html = p.get("https://i.pximg.net/img-original/img/2018/06/01/14/45/39/69005397_p0.jpg")
    # with open('picture10.jpg', 'wb') as file:
    #     file.write(html.content)
    #Login()
    #print(CrawlFollowList())
    #print(CrawlWorksList(1226647, 'ugoira'))
    #print(CrawlWorkDetail(63100480))