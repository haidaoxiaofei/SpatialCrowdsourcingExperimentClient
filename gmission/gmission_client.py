#!/usr/bin/env python
# encoding: utf-8
import json

__author__ = 'rui'
from datetime import datetime
from http_client import get, post
from logbook import Logger

API_HOST = 'http://127.0.0.1:8080/'

CAMPAIGN_USER_ROLE_OWNER = 1
CAMPAIGN_USER_ROLE_PARTICIPANT = 2

HIT_TYPE_TEXT = 'text'
HIT_TYPE_IMAGE = 'image'
HIT_TYPE_URL = 'url'

ANSWER_TYPE_TEXT = 'text'
ANSWER_TYPE_IMAGE = 'image'


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
            print 'User auth token', self.token

    def user_register(self, username, password, email):
        response = post(self.api_host + 'user/register',
                        json={'username': username, 'password': password, 'email': email}, token=self.token)
        if response:
            self.user = response
            print 'User created', self.user['username']

    def user_verify_email(self, hash_id):
        get(self.api_host + 'user/email_verify/' + hash_id)

    def create_campaign(self, title):
        response = post(self.api_host + 'rest/campaign', json={'title': title}, token=self.token)
        if 'id' in response:
            print 'Campaign created id', response.get('id', 0)
            return response

    # role id 1 : owner
    # role id 2 : participant
    def assign_user_to_campaign(self, campaign_id, role_id=2):
        response = post(self.api_host + 'rest/campaign_user',
                        json={'user_id': self.user['id'], 'campaign_id': campaign_id, 'role_id': role_id},
                        token=self.token)
        if 'id' in response:
            print 'Assign user to campaign id', response.get('id', 0)
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
            print 'Location created', response.get('id', 0)
            return response

    def get_locations(self):
        response = get(self.api_host + 'rest/location', token=self.token)
        return response['objects']

    def create_hit(self, type, brief, attachment_id, campaign_id, credit, required_answer_count, location_id):
        response = post(self.api_host + 'rest/hit',
                        json={'type': type, 'brief': brief, 'attachment_id': attachment_id, 'campaign_id': campaign_id,
                              'credit': credit, 'required_answer_count': required_answer_count,
                              'location_id': location_id, 'requester_id': self.user['id']}, token=self.token)
        if response:
            print 'HIT created', response.get('id', 0)
            return response

    def get_hits(self):
        response = get(self.api_host + 'rest/hit', token=self.token)
        return response['objects']

    def create_answer(self, hit_id, brief, attachment_id, type, location_id):
        response = post(self.api_host + 'rest/answer',
                        json={'type': type, 'brief': brief, 'attachment_id': attachment_id, 'hit_id': hit_id,
                              'location_id': location_id, 'worker_id': self.user['id']}, token=self.token)
        if response:
            print 'Answer created', response.get('id', 0)
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
