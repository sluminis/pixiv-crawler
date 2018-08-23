import requests
import re
import os
import shelve
import json
import demjson
from bs4 import BeautifulSoup
from user import User

class Work:

    def __init__(self, wid):
        self.wid = wid
        self.content = {}

    def crawl(self, dir):
        print("basic work class's crawl", self.wid)

    def record(self, shelve):
        print("basic work class's record", self.wid)

    def download(self, P, path):
        print("basic work class's download", self.wid)

class Illustration(Work):
    pattern = re.compile(u'.*/(.*)')

    def crawl(self, data):
        work_dir = data['preload']['illust'][self.wid]

        self.content['uid'] = uid = work_dir['userId']
        self.content['name'] = data['preload']['user'][int(uid)]['name']
        self.content['wid'] = work_dir['illustId']
        self.content['title'] = work_dir['illustTitle']
        self.content['type'] = work_dir['illustType']
        self.content['comment'] = work_dir['illustComment']
        self.content['createDate'] = work_dir['createDate']
        self.content['uploadDate'] = work_dir['uploadDate']
        self.content['width'] = work_dir['width']
        self.content['height'] = work_dir['height']
        self.content['pageCount'] = work_dir['pageCount']
        self.content['bookmarkCount'] = work_dir['bookmarkCount']
        self.content['likeCount'] = work_dir['likeCount']
        self.content['commentCount'] = work_dir['commentCount']
        self.content['responseCount'] = work_dir['responseCount']
        self.content['viewCount'] = work_dir['viewCount']
        # self.content['isHowto']         = work_dir['isHowto']
        # self.content['isOriginal']      = work_dir['isOriginal']

        tags = []
        tag_dir = work_dir['tags']['tags']
        for tag in tag_dir:
            tags.append(tag['tag'])
        self.content['tags'] = tags
        self.content['images'] = self._extractImage(work_dir)

    def _extractImage(self, work_dir):
        images = {}
        img_dir = work_dir['urls']
        images['regular'] = img_dir['regular']
        oimg = img_dir['original']
        oimgs = [oimg]

        # if there are multiple images, just replace the index
        pageCount = self.content['pageCount']
        if pageCount > 1:
            result = re.search(r'(.*p)\d+\.(\w+)$', oimg)
            target = result.group(1)
            itype = result.group(2)
            #print(target,itype)
            for p in range(1, pageCount):
                oimgs.append(target + str(p) + '.' + itype)

        images['original'] = oimgs
        return images

    def record(self, db):
        db[str(self.wid)] = self

    def download(self, P, path):
        print('downloading work %d' % self.wid)
        # format: wid_[_page]
        if self.content is None or not self.content:
            print('no content')
            return

        files = []
        page = self.content['pageCount']
        images = self.content['images']['original']
        if page == 1:
            filename = path + self.pattern.search(images[0]).group(1)
            self._part_download(P, images[0], filename)
            files.append(filename)

        else:
            dirname = path + str(self.wid)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            for img in images:
                filename = dirname + '/' + self.pattern.search(img).group(1)
                #print(filename,img)
                self._part_download(P, img, filename)
                files.append(filename)

        self.content['files'] = files

    def _part_download(self, P, url, filename):

        picture = P.get(url)

        with open(filename, 'wb') as file:
            file.write(picture.content)


class Animation(Illustration):

    zip_pattern = re.compile(u'(https?://.*?/).*(/img[\d/]+_ugoira)')

    def _extractImage(self, work_dir):
        images = {}
        img_dir = work_dir['urls']
        images['regular'] = img_dir['regular']
        raw = img_dir['original']
        result = self.zip_pattern.search(raw)
        oimg = result.group(1) + 'img-zip-ugoira' + result.group(2) + '600x600.zip'
        #print('oimg:',oimg)
        images['original'] = [oimg]
        return images


if __name__ == '__main__':
    s = shelve.open('pixivDB')
    print(s != open)