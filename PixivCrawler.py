import PixivModel
import PixivDownloader
import queue
import re
import os

class PixivCrawler:

    def __init__(self):
        self.Q = queue.Queue()
        self.pattern = re.compile(u'.*/(.*)')
        self.downloader = PixivDownloader.Downloader(self.Q)

    def Work2Tasks(self, work, path = ''):
        #format: wid_[_page]
        if work.content is None:
            print('no content')
            return

        type = work.content['type']
        page = work.content['pageCount']
        images = work.content['images']['original']
        if type == 0 or type > 0:
            if(page == 1):
                filename = path + self.pattern.search(images[0]).group(1)
                self.Q.put((images[0],filename))
            else:
                dirname = path + str(work.wid)
                if not os.path.exists(dirname):
                    os.mkdir(dirname)
                for img in images:
                    filename = dirname + '/' + self.pattern.search(img).group(1)
                    self.Q.put((img, filename))


    def Artist2Tasks(self, artist, path = ''):
        #format: artist/type/
        types = ['illust','manga']#,'ugoira']
        works_dir = path + str(artist.uid) + '_' + artist.content['name'] + '/'
        if not os.path.exists(works_dir):
            os.mkdir(works_dir)

        for ctype in types:
            if ctype in artist.content:
                cdir = works_dir + str(ctype) + '/'
                if not os.path.exists(cdir):
                    os.mkdir(cdir)

                for wid in artist.content[ctype]:
                    work = PixivModel.Work(id=wid)
                    work.crawlData()
                    self.Work2Tasks(work=work, path=cdir)

    def download(self):
        self.downloader.run()


if __name__ == '__main__':
    #os.chdir('pixiv')
    PixivModel.Login()

    pc = PixivCrawler()
    artist = PixivModel.Artist(170597)
    artist.crawlData()
    pc.Artist2Tasks(artist,'pixiv/')
    pc.download()
    #work = PixivModel.Work(69001507)
    #work.crawlData()
    #pc.Work2Tasks(work, 'As109/illust/')
    #while not pc.Q.empty():

        #print(pc.Q.get())