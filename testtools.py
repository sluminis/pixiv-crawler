import time
from functools import wraps
import shelve
import workfactory
import work
import user

def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r

    return wrapper

if __name__ == '__main__':
    s = shelve.open('E:/pixiv/pixivDB')

    ck = 0
    for k in s.keys():
        try:
            s[k]
        except Exception:
            print(k)
            ck += 1

    print('ck:',ck)