import requests
import random
import string
import time


__author__ = 'JIAN Xun'


def randstr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def randfloat():
    return random.uniform(0.5, 1.5)


def randpos():
    """
    18N-20N, 108E-110E
    :return:
    """
    longitude = random.gauss(109, 1)
    while not 108 <= longitude <= 110:
        longitude = random.gauss(109, 1)

    latitude = random.gauss(19, 1)
    while not 18 <= latitude <= 20:
        latitude = random.gauss(19, 1)

    return {'longitude': longitude, 'latitude': latitude, 'z': 0}

HOST = 'http://127.0.0.1:8080/'

pref = HOST + 'Index/actions'

rounds = 1

if __name__ == '__main__':
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    position = randpos()
    r = 0.5
    params = {'longitude1': position['longitude'] - r / 2, 'latitude1': position['latitude'] - r / 2,
              'longitude2': position['longitude'] + r / 2, 'latitude2': position['latitude'] + r / 2}

    start_time = time.time()
    for i in xrange(rounds):
        ids_linear = requests.get(url=pref + '/nodes/rectangle/linear', params=params, headers=headers).json()
    end_time = time.time()
    print "linear", len(ids_linear), end_time - start_time

    start_time = time.time()
    for i in xrange(rounds):
        ids_rtree = requests.get(url=pref + '/nodes/rectangle', params=params, headers=headers).json()
    end_time = time.time()
    print "rtree", len(ids_rtree), end_time - start_time



