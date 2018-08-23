import requests
import re
from bs4 import BeautifulSoup
import time
from exceptions import SpiderError

class NoProxyErrorSession(requests.Session):

    def get(self, url, **kwargs):
        fail = 0
        while True:
            try:
                P = super().get(url, **kwargs)
            except requests.exceptions.ProxyError:
                print("ProxyError occur")
                fail += 1
                if fail >= 10:
                    raise SpiderError("bad network occurs too many times")
                time.sleep(0.1)
                continue
            break
        return P

class User:

    parser = "html.parser"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "referer": "https://www.pixiv.net"
    }

    params = {
        "lang": "sh",
        "source": "pc",
        "view_type": "page",
        "ref": "wwwtop_accounts_index"
    }

    proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "http://127.0.0.1:1080"
    }

    data = {
        "pixiv_id": "********",
        "password": "********",
        "captcha": "",
        "g_recaptcha_response": "",
        "post_key": "",
        "source": "pc",
        "ref": "wwwtop_accounts_index",
        "return_to": "https://www/pixiv.net/"
    }

    def __init__(self, account, password):
        self.data['pixiv_id'] = account
        self.data['password'] = password

    @classmethod
    def getRequest(cls):
        P = NoProxyErrorSession()
        P.headers = cls.header
        P.proxies = cls.proxies
        return P

    def getSession(self):
        P = self.getRequest()
        self.login(P)
        return P

    def login(self, P):
        login_url = 'https://accounts.pixiv.net/login'
        r = P.get(url=login_url, params=self.params)
        post_key = re.search(r'name="post_key" value="(.*?)">', r.text).group(1)
        self.data['post_key'] = post_key
        #print(self.data['post_key'])
        P.post(url=login_url, data=self.data)
        print('Login')

    def crawlFollowList(self, P):
        print('Getting FollowList: ', end="")
        follow_url = "https://www.pixiv.net/bookmark.php"
        follow_list = []
        html = P.get(url=follow_url + '?type=user&rest=show')
        selector = BeautifulSoup(html.text, self.parser)
        follow_list.extend(self._crawlFollowData(selector))

        while True:
            pager = selector.find("div", class_="_pager-complex")
            if pager is None: break
            next_a = pager.find("a", attrs={'rel': 'next'})
            if next_a is None: break
            next_href = next_a.attrs['href']
            html = P.get(url=follow_url + next_href)
            selector = BeautifulSoup(html.text, self.parser)
            follow_list.extend(self._crawlFollowData(selector))

        print(len(follow_list))
        return follow_list

    def _crawlFollowData(self, selector):
        userdata = selector.find_all('div', class_='userdata')
        #print(len(userdata))
        data = []
        for detail in userdata:
            a = detail.find('a')
            d = {
                'uid': a.attrs['data-user_id'],
                'profile_img': a.attrs['data-profile_img'],
                'user_name': a.attrs['data-user_name']
            }
            data.append(d)
        return data

if __name__ == '__main__':
    u = User('', '')
    P = u.getSession()
    print(u.crawlFollowList(P))