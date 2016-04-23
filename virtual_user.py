#!/usr/bin/env python
# encoding: utf-8
import random
import string
from gmission import *
from requests.exceptions import HTTPError

__author__ = 'JIAN Xun'


def randstr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def randfloat():
    return random.uniform(1.0, 140.0)


class Worker:
    def __init__(self, username, password, email):
        self.__client = GmissionClient()
        try:
            self.__client.user_auth(username, password)
        except HTTPError:
            self.__client.user_register(username, password, email)
            self.__client.user_auth(username, password)
        self.longitude = None
        self.latitude = None
        self.altitude = None
        self.id = self.__client.user['id']

    def set_attributes(self, capacity=1, reliability=1, min_direction=0, max_direction=0, velocity=0,
                       min_lon=0, min_lat=0, max_lon=0, max_lat=0, is_online=0):
        response = post(self.__client.api_host + 'rest/worker_detail', json={'id': self.__client.user['id'],
                                                                             'capacity': capacity,
                                                                             'reliability': reliability,
                                                                             'min_direction': min_direction,
                                                                             'max_direction': max_direction,
                                                                             'velocity': velocity,
                                                                             'region_min_lon': min_lon,
                                                                             'region_min_lat': min_lat,
                                                                             'region_max_lon': max_lon,
                                                                             'region_max_lat': max_lat,
                                                                             'is_online': is_online},
                        token=self.__client.token)
        if not response:
            print 'worker attributes not set'

    def join_campaign(self, campaign_id):
        self.__client.assign_user_to_campaign(campaign_id, CAMPAIGN_USER_ROLE_PARTICIPANT)

    def move_to(self, longitude, latitude, altitude=0.0):
        response = post(self.__client.api_host + 'rest/position_trace', json={'user_id': self.__client.user['id'],
                                                                              'longitude': longitude,
                                                                              'latitude': latitude,
                                                                              'z': altitude},
                        token=self.__client.token)
        if response:
            self.longitude = longitude
            self.latitude = latitude
            self.altitude = altitude
            # print 'moved'

    def move(self):
        if self.longitude is None:
            self.move_to(randfloat(), randfloat())
        longitude_dis = random.uniform(-0.01, 0.01)
        latitude_dis = random.uniform(-0.01, 0.01)
        self.move_to(self.longitude + longitude_dis, self.latitude + latitude_dis)
        # print 'randomly moved'

    def online(self):
        response = post(self.__client.api_host + 'user/online', json={'user_id': self.__client.user['id']},
                        token=self.__client.token)
        if not response:
            print 'online failed'

    def offline(self):
        response = post(self.__client.api_host + 'user/offline', json={'user_id': self.__client.user['id']},
                        token=self.__client.token)
        if not response:
            print 'offline failed'


class Boss:
    def __init__(self, username, password, email):
        self.__client = GmissionClient()
        try:
            self.__client.user_auth(username, password)
        except HTTPError:
            self.__client.user_register(username, password, email)
            self.__client.user_auth(username, password)
        self.__campaign_id = None

    def create_campaign(self):
        self.__campaign_id = self.__client.create_campaign('jianxuntest_' + randstr()).get('id', 0)
        self.__client.assign_user_to_campaign(self.__campaign_id, CAMPAIGN_USER_ROLE_OWNER)
        return self.__campaign_id

    def create_hit(self, location_id, required_answer_count=1, arrival_time=0, expire_time=0):
        if self.__campaign_id is None:
            self.create_campaign()
        hit_id = self.__client.create_hit(HIT_TYPE_TEXT, 'jianxuntest_' + randstr(), 'desc ' + randstr(), None,
                                          self.__campaign_id, credit=10, required_answer_count=required_answer_count,
                                          location_id=location_id, begin_time=arrival_time, end_time=expire_time)\
            .get('id', 0)
        return hit_id

    def create_location(self, longitude, latitude):
        location_id = self.__client.create_location('jianxuntest_' + randstr(), longitude, latitude). \
            get('id', 0)
        return location_id

    def set_hit_attributes(self, hit_id, confidence=0.5, entropy=0.5, is_valid=True):
        response = post(self.__client.api_host + 'rest/hit_detail', json={'id': hit_id,
                                                                          'confidence': confidence,
                                                                          'entropy': entropy,
                                                                          'is_valid': is_valid},
                        token=self.__client.token)
        if not response:
            print 'hit attributes not set'

    def assign(self, method, current_time):
        """
        Assign tasks to workers using one of the algorithms.
        Parameters
        ----------
        method : str
            The name of the method to use, should be on of ['geocrowdgreedy', 'geocrowdllep', 'geocrowdnnp',
             'geotrucrowdgreedy', 'geotrucrowdlo', 'rdbscdivideandconquer', 'rdbscsampling']
        current_time : int
            Current time instance, 0 means 1970-01-01 08:00:00
        """
        return post(self.__client.api_host + 'assignment', json={'method': method, 'time': current_time})
