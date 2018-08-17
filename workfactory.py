import requests
import re
import demjson
from work import Work, Illustration, Animation
from user import User


class WorkFactory:

    url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='

    def __init__(self, P):
        self.P = P

    def get_work(self, wid):
        print('crawling work %d' % wid)
        try:
            html = self.P.get(url=self.url + str(wid))
        except requests.exceptions.ProxyError:
            print('Bad Proxy(work ID: %d)' % wid)
            return Work(wid)

        djson = re.search(r'}\)\((.*?)\);</script>', html.text).group(1)
        #print('djson:',djson)
        data = demjson.decode(djson)
        _type = data['preload']['illust'][wid]['illustType']

        if _type < 2:
            w = Illustration(wid)
        elif _type == 2:
            w = Animation(wid)
        else:
            w = Work(wid)

        w.crawl(data)

        del data
        return w


if __name__ == "__main__":
    pass
