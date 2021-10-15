import logging
from datetime import datetime
import uuid
import hmac
import requests
import json
from time import mktime
from hashlib import sha256

class public_api:

    def __init__(self, host, verbose=False):
        self.host = host
        self.verbose = verbose

    def request(self, method, path, query, body):
        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            logging.info(f"{method}, {url}")

        s = requests.Session()
        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_current_global_stats(self):
        return self.request('GET', '/main/api/v2/public/stats/global/current/', '', None)

    def get_global_stats_24(self):
        return self.request('GET', '/main/api/v2/public/stats/global/24h/', '', None)

    def get_active_orders(self):
        return self.request('GET', '/main/api/v2/public/orders/active/', '', None)

    def get_active_orders2(self):
        return self.request('GET', '/main/api/v2/public/orders/active2/', '', None)

    def buy_info(self):
        return self.request('GET', '/main/api/v2/public/buy/info/', '', None)

    def get_algorithms(self):
        return self.request('GET', '/main/api/v2/mining/algorithms/', '', None)

    def get_markets(self):
        return self.request('GET', '/main/api/v2/mining/markets/', '', None)

    def get_currencies(self):
        return self.request('GET', '/main/api/v2/public/currencies/', '', None)

    def get_multialgo_info(self):
        return self.request('GET', '/main/api/v2/public/simplemultialgo/info/', '', None)

    def get_exchange_markets_info(self):
        return self.request('GET', '/exchange/api/v2/info/status', '', None)

    def get_exchange_trades(self, market):
        return self.request('GET', '/exchange/api/v2/trades', 'market=' + market, None)

    def get_candlesticks(self, market, from_s, to_s, resolution):
        return self.request('GET', '/exchange/api/v2/candlesticks', "market={}&from={}&to={}&resolution={}".format(market, from_s, to_s, resolution), None)

    def get_exchange_orderbook(self, market, limit):
        return self.request('GET', '/exchange/api/v2/orderbook', "market={}&limit={}".format(market, limit), None)

class client:

    def __init__(self, host, organisation_id, key, secret, verbose=False):
        self.key = key
        self.secret = secret
        self.organisation_id = organisation_id
        self.host = host
        self.verbose = verbose

    def request(self, method, path, query, body):

        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(str(xtime), 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(xnonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(method, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(path, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(query, 'utf-8')

        if body:
            body_json = json.dumps(body)
            message += bytearray('\x00', 'utf-8')
            message += bytearray(body_json, 'utf-8')

        digest = hmac.new(bytearray(self.secret, 'utf-8'), message, sha256).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            'X-Time': str(xtime),
            'X-Nonce': xnonce,
            'X-Auth': xauth,
            'Content-Type': 'application/json',
            'X-Organization-Id': self.organisation_id,
            'X-Request-Id': str(uuid.uuid4())
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            logging.info(f"{method}, {url}")

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def get_payouts(self, start: datetime, end: datetime, size : int = None):
        _size = size
        if size is None:
            time_diff = end.timestamp() - start.timestamp()
            _size = int(time_diff / float(4 * 60 * 60))  # payouts are made every 4 hour

        query = f"beforeTimestamp={int(end.timestamp() * 1000)}&size={_size}"
        return self.request('GET', '/main/api/v2/mining/rigs/payouts', query, None)

    def get_unpaid(self, start: datetime, end: datetime):
        query = f"afterTimestamp={int(start.timestamp() * 1000)}&beforeTimestamp={int(end.timestamp() * 1000)}"
        return self.request('GET', '/main/api/v2/mining/rigs/stats/unpaid', query, None)

    def get_active_workers(self):
        query = ""
        return self.request('GET', '/main/api/v2/mining/rigs/activeWorkers', query, None)

def create_client(options, verbose = False):
    api = client(options.base, options.organization, options.api_key, options.api_secret, verbose=verbose)
    return api