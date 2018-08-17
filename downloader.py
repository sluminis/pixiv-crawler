from workfactory import WorkFactory
from user import User
from queue import Queue
from threading import Thread, Event
from exceptions import ActorExit
import shelve

class Actor:
    def __init__(self):
        self._Q = Queue()
        self.thread = 1

    def send(self, msg):
        self._Q.put(msg)

    def recv(self):
        msg = self._Q.get()
        if msg is ActorExit:
            raise ActorExit()
        return msg

    def close(self):
        self.send(ActorExit)

    def start(self, thread=10):
        self.thread = thread
        self._terminated = Event()
        for i in range(self.thread):
            print('Thread',i,'start')
            t = Thread(target=self._bootstrap)
            #t.daemon = True
            t.start()

    def _bootstrap(self):
        try:
            self.run()
        except ActorExit:
            self.close()
        finally:
            self.thread -= 1
            if self.thread == 0:
                self._terminated.set()

    def join(self):
        self._terminated.wait()

    def run(self):
        while True:
            msg = self.recv()
            print(msg)


class Downloader(Actor):
    P = User.getRequest()

    def run(self):
        while True:
            w,to = self.recv()
            w.download(self.P,to)


class WDownloader(Actor):

    def __init__(self, P, actor):
        Actor.__init__(self)
        self.wf = WorkFactory(P)
        self.actor = actor

    def run(self):
        while True:
            wid, to = self.recv()
            work = self.wf.get_work(wid)
            self.actor.send((work, to))


class Runner(Actor):

    def __init__(self, P, db):
        Actor.__init__(self)
        self.db = db
        self.P = P
        self.workf = WorkFactory(self.P)

    def run(self):
        while True:
            wid,path = self.recv()
            work = self.workf.get_work(wid)
            work.download(self.P, path)
            work.record(self.db)

if __name__ =='__main__':
    import artist
    import time

    P = User('','').getSession()
    at = artist.Artist(P, 12949983)
    at.crawl()
    sh = shelve.open('pixivDB')
    r = Runner(P, sh)

    start = time.perf_counter()
    r.start(8)
    ctype = ('illust','manga','ugoira')
    for ty in ctype:
        for wid in at.content[ty]:
            r.send((wid,'C:/Users/JX/Desktop/Pixiv/pp/aa/'+ty+'/'))

    r.close()
    r.join()
    end = time.perf_counter()

    print("time count:",end-start)

"""
63 works
time count: 95.40951084867149 for 1 thread
time count: 36.71637009616449 for 10 threads

time count: 26.58050514689117 for 1 request
time count: 26.74139499617555 for 10 requests
"""

