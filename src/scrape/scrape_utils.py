import base64
import os
import time

import requests

web_session = requests.Session()
web_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0"
})


def retry_web(method, args=[], retries=[10, 60, 600], valid_status_codes=[200]):
    for sleep_amount in retries:
        try:
            r = method(*args)
            if r.status_code not in valid_status_codes:
                raise Exception('Request in network_wrapper failed!')
            return r
        except Exception as e:
            print(e)
            time.sleep(sleep_amount)


def get(url: str):
    def fetch():
        return retry_web(web_session.get, [url]).text
    cache_dir = os.environ.get('DEBUG_CACHE_DIRECTORY')
    if cache_dir is not None:
        cache_file = os.path.join(cache_dir, base64.b64encode(url.encode("utf-8")).decode("utf-8").replace('/', '-'))
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                return f.read()
        else:
            res = fetch()
            with open(cache_file+".tmp", "w") as f:
                f.write(res)
            os.rename(cache_file+".tmp", cache_file)
            return res
    else:
        return fetch()
