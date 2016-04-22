#!/usr/bin/env python
# encoding: utf-8
import json
import platform

__author__ = 'rui'
from http_client import get, post, post_image

sysstr = platform.system()
API_HOST = 'http://127.0.0.1:9091/'
if sysstr == 'Darwin':
    API_HOST = 'http://192.168.99.100:9091/'

CAMPAIGN_USER_ROLE_OWNER = 1
CAMPAIGN_USER_ROLE_PARTICIPANT = 2

HIT_TYPE_TEXT = 'text'
HIT_TYPE_IMAGE = 'image'
HIT_TYPE_URL = 'url'
HIT_TYPE_SELECTION = 'selection'

ANSWER_TYPE_TEXT = 'text'
ANSWER_TYPE_IMAGE = 'image'
ANSWER_TYPE_SELECTION = 'selection'


class GmissionClient(object):
    def __init__(self, api_host=API_HOST):
        self.api_host = api_host
        self.user = None
        self.token = None

    def user_auth(self, username, password):
        response = post(self.api_host + 'user/auth', json={'username': username, 'password': password},
                        token=self.token)
        if 'token' in response:
            self.token = response['token']
            self.user = response
            # print 'User auth token', self.token
            return True
        return False

    def user_register(self, username, password, email):
        response = post(self.api_host + 'user/register',
                        json={'username': username, 'password': password, 'email': email}, token=self.token)
        if response:
            self.user = response
            # print 'User created', self.user['username']

    def user_verify_email(self, hash_id):
        get(self.api_host + 'user/email_verify/' + hash_id)

    def create_campaign(self, title, desp=""):
        response = post(self.api_host + 'rest/campaign', json={'title': title, 'brief': desp}, token=self.token)
        if 'id' in response:
            # print 'Campaign created id', response.get('id', 0)
            return response

    # role id 1 : owner
    # role id 2 : participant
    def assign_user_to_campaign(self, campaign_id, role_id=2):
        response = post(self.api_host + 'rest/campaign_user',
                        json={'user_id': self.user['id'], 'campaign_id': campaign_id, 'role_id': role_id},
                        token=self.token)
        if 'id' in response:
            # print 'Assigned user(%d) to campaign(%d)'%(self.user['id'], campaign_id)
            return response

    def get_campaigns(self, open_only=False):
        params = {}
        if open_only:
            filters = [dict(name='status', op='eq', val='open')]
            params['q'] = json.dumps(dict(filters=filters))
        response = get(self.api_host + 'rest/campaign', params=params, token=self.token)
        return response['objects']

    def get_campaign_role(self, campaign_id):
        params = {}
        filters = [dict(name='user_id', op='eq', val=str(self.user['id'])),
                   dict(name='campaign_id', op='eq', val=str(campaign_id))]
        params['q'] = json.dumps(dict(filters=filters))
        response = get(self.api_host + 'rest/campaign_user', params=params, token=self.token)
        return response['objects']

    def create_location(self, name, longitude, latitude, altitude=0.0):
        response = post(self.api_host + 'rest/location', json={'name': name, 'coordinate': {'longitude': longitude,
                                                                                            'latitude': latitude,
                                                                                            'altitude': altitude}},
                        token=self.token)
        if response:
            # print 'Location created', response.get('id', 0)
            return response

    def get_locations(self):
        response = get(self.api_host + 'rest/location', token=self.token)
        return response['objects']

    def create_hit(self, type, title, description, attachment_id, campaign_id, credit, required_answer_count,
                   location_id=1, min_selection_count=1, max_selection_count=1, begin_time=1, end_time=1):
        response = post(self.api_host + 'rest/hit',
                        json={'type': type, 'title': title, 'description': description, 'attachment_id': attachment_id,
                              'campaign_id': campaign_id, 'credit': credit,
                              'required_answer_count': required_answer_count, 'location_id': location_id,
                              'requester_id': self.user['id'], 'min_selection_count': min_selection_count,
                              'max_selection_count': max_selection_count,
                              'begin_time': begin_time,
                              'end_time': end_time},
                        token=self.token)
        if response:
            # print 'HIT created', response.get('id', 0)
            return response

    def get_hits(self):
        response = get(self.api_host + 'rest/hit', token=self.token)
        return response['objects']

    def create_answer(self, hit_id, brief, attachment_id, type, location_id):
        response = post(self.api_host + 'rest/answer',
                        json={'type': type, 'brief': brief, 'attachment_id': attachment_id, 'hit_id': hit_id,
                              'location_id': location_id, 'worker_id': self.user['id']}, token=self.token)
        if response:
            # print 'Answer created', response.get('id', 0)
            return response

    def get_answer(self, hit_id):
        params = {}
        filters = [dict(name='hit_id', op='eq', val=str(hit_id))]
        params['q'] = json.dumps(dict(filters=filters))
        response = get(self.api_host + 'rest/answer', params=params, token=self.token)
        return response['objects']

    def get_attachments(self):
        response = get(self.api_host + 'rest/attachment', token=self.token)
        return response['objects']

    def new_attchment_with_image(self, image_fname):
        name_from_server = post_image(self.api_host+'image/upload', files={'file':file(image_fname, 'rb')}, token=self.token)["filename"]
        resp = post(self.api_host + 'rest/attachment', json={'type': 'image', 'value':name_from_server}, token=self.token)
        # print resp
        return resp

    def create_selection(self, hit_id, brief):
        response = post(self.api_host + 'rest/selection',
                        json={'hit_id': hit_id, 'brief': brief},
                        token=self.token)
        if response:
            # print 'Selection created', response.get('id', 0)
            return response.get('id', 0)

    def get_selections(self):
        response = get(self.api_host + 'rest/selection', token=self.token)
        return response['objects']

    def get_credit_by_campaign(self, campaign_id):
        response = get(self.api_host + 'user/credit/campaign/'+str(campaign_id), token=self.token)
        return response
