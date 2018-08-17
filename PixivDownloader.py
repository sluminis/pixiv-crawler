import os
import requests
from queue import Queue
from threading import Thread

class Downloader:

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "referer": "https://www.pixiv.net/member_illust.php"
    }

    proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "http://127.0.0.1:1080"
    }

    def __init__(self, tasks):
        self.P  = requests.Session()
        self.P.headers = self.header
        self.P.proxies = self.proxies
        self.Q = tasks


    def download(self, url, path):
        try:
            picture = self.P.get(url)
        except requests.exceptions.ProxyError:
            print("download bad Proxy(url=%s)" % url)
            self.Q.put((url, path))
            return
        with open(path, 'wb') as file:
            file.write(picture.content)


    def run(self):
        while not self.Q.empty():
            task = self.Q.get()
            self.download(task[0],task[1])


if __name__ == '__main__':

    ( a,b)=(1,2)
    print(a,b)
    #Q = Queue()
    #Q.put(('https://i.pximg.net/img-zip-ugoira/img/2017/09/02/22/37/02/64756116_ugoira600x600.zip','C:/Users/JX/Desktop/Pixiv/wqw.zip'))
    #d = Downloader(Q)
    #d.run()
    #if not os.path.exists('pixiv'):
    #    os.mkdir('pixiv')
    #os.chdir('pixiv')F
    #with open('As109/xx.txt','w') as file:
    #    file.write('asdasdsss')
    #Q = queue.Queue()
    # Q.put(1)
    # Q.put(2)
    # print(1,Q.qsize())
    # Q.get()
    # print(2,Q.qsize())
    # Q.task_done()
    # print(3,Q.qsize())
    # #Q.get()
    # Q.put(3)
    # print(4,Q.qsize())
    # Q.task_done()
    # Q.task_done()
    #
    #
    # Q.join()
    # print(5,Q.qsize())
    # print(Q.get())
    # print(Q.get())
    # try:
    #     print(Q.get(1,3))
    # except queue.Empty:
    #     print('oo')
    # print("end")

