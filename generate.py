#!/usr/bin/env python
# encoding: utf-8
import random
import string
import virtual_user
import time

__author__ = 'JIAN Xun'


def randstr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def randfloat():
    return random.uniform(1.0, 140.0)

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


if __name__ == '__main__':
    workers = []
    worker_num = 0

    username = 'jianxuntest_' + randstr()
    password = randstr()
    email = 'jianxuntest_%s@%s.com' % (randstr(), randstr())
    boss = virtual_user.Boss(username, password, email)
    campaign_id = 24
    # boss.create_campaign()

    for i in xrange(worker_num):
        username = 'jianxuntest_' + randstr()
        password = randstr()
        email = 'jianxuntest_%s@%s.com' % (randstr(), randstr())
        worker = virtual_user.Worker(username, password, email)
        pos = randpos()
        worker.move_to(pos['longitude'], pos['latitude'], pos['z'])
        # worker.join_campaign(campaign_id)
        # workers.append(worker)

    time.sleep(0)
    for i in range(1):
        location = randpos()
        location = {'longitude': 108.51234122809373, 'latitude': 18.84522971933864}
        # print location
        location_id = boss.create_location(location['longitude'], location['latitude'])
        boss.create_hit(location_id)
