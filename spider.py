from downloader import Runner
from artist import Artist
from user import User
import shelve
import os

class Spider:

    def __init__(self, account, password):
        self.user = User(account, password)
        self.base_path = ''

    def setPath(self, path):
        if path[-1] != '/':
            path += '/'
        self.base_path = path

    def start(self):
        self.P = self.user.getSession()
        self.db = shelve.open(self.base_path + 'pixivDB')
        self.R = Runner(self.P, self.db)
        self.R.start(8)

    def close(self):
        self.R.close()
        self.R.join()
        self.db.close()
        self.P.close()

    def crawlArtist(self, uid):
        path = self.base_path + str(uid) + '/'
        artist = Artist(self.P, uid)
        content = artist.crawl()
        if not os.path.exists(path):
            os.mkdir(path)
        ctype = ('illust', 'manga', 'ugoira')
        for _type in ctype:
            wpath = path + _type + '/'
            if not os.path.exists(wpath):
                os.mkdir(wpath)

            for wid in content[_type]:
                self.R.send((wid,wpath))

    def crawlFollow(self):
        ulist = self.user.crawlFollowList(self.P)
        for uinfo in ulist:
            self.crawlArtist(uinfo['uid'])

    import testtools

    @testtools.timethis
    def run(self):
        self.start()
        #self.crawlArtist(12949983)
        self.crawlFollow()
        self.close()

    #TODO: 下载进度

if __name__ == '__main__':
    import json
    with open("account.dat") as file:
        cfg = json.load(file)

    sp = Spider(cfg['account'], cfg['password'])
    sp.setPath('E:/pixiv')
    sp.run()
    '''
    22003.354938222223s
    '''