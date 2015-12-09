#!/usr/bin/env python
# encoding: utf-8
import random
import string
from gmission import *

__author__ = 'rui'


def randstr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def randfloat():
    return random.uniform(1.0, 140.0)


if __name__ == '__main__':
    # client = GmissionClient('http://lccpu3.cse.ust.hk/gmission-dev/')
    client = GmissionClient()
    username = randstr()
    password = randstr()
    email = '%s@%s.com' % (randstr(), randstr())
    print 'random user', username, password, email

    # create new user
    client.user_register(username, password, email)

    # auth with user
    client.user_auth(username, password)

    # create campaign
    campaign_id = client.create_campaign('test campaign ' + randstr()).get('id', 0)
    client.assign_user_to_campaign(campaign_id, CAMPAIGN_USER_ROLE_OWNER)  # assign owner role

    # create Location
    location_id = client.create_location('test location ' + randstr(), randfloat(), randfloat(), randfloat()).get('id',
                                                                                                                  0)

    # create HIT
    hit_id = client.create_hit(HIT_TYPE_TEXT, 'test HIT ' + randstr(), 'HIT description' + randstr(), None, campaign_id,
                               10, 3, location_id)

    hit_id = client.create_hit(HIT_TYPE_SELECTION, 'test selection HIT ' + randstr(), 'HIT description' + randstr(), None, campaign_id,
                               10, 3, location_id, 1, 1)
    # create Selection HIT
    selection = client.create_selection(hit_id, 'selection ' + randstr())
    selection = client.create_selection(hit_id, 'selection ' + randstr())
    selection = client.create_selection(hit_id, 'selection ' + randstr())
    selection = client.create_selection(hit_id, 'selection ' + randstr())



    # get campaign list
    campaigns = client.get_campaigns()

    # get user's campaign roles
    for campaign in campaigns:
        role = client.get_campaign_role(campaign['id'])
        # be a participant
        if len(role) == 0:
            client.assign_user_to_campaign(campaign_id, CAMPAIGN_USER_ROLE_PARTICIPANT)  # assign participant role
            hits = client.get_hits()
            for hit in hits:
                answered = False
                for answer in client.get_answer(hit['id']):
                    if answer['worker_id'] == client.user['id']:
                        answered = True
                        break
                if not answered:
                    # create a random text answer
                    if hit['type'] == HIT_TYPE_TEXT:
                        client.create_answer(hit['id'], 'test answer ' + randstr(), None, ANSWER_TYPE_TEXT, location_id)
                    elif hit['type'] == HIT_TYPE_SELECTION:
                        selections = [s for s in client.get_selections() if s['hit_id'] == hit['id']]
                        if len(selections)>0:
                            client.create_answer(hit['id'], str(random.choice(selections).get('id', 0)), None, ANSWER_TYPE_SELECTION, location_id)

    # get my task's answer
    hits = client.get_hits()
    for hit in hits:
        if hit['campaign_id'] == campaign_id:
            for answer in client.get_answer(hit['id']):
                attachment_str = ''
                if answer['attachment_id'] is not None:
                    for attachment in client.get_attachments():
                        if attachment['id'] == answer['attachment_id']:
                            attachment_str = 'with attachment %s' % (client.api_host + attachment['value'])
                            break
                print 'HIT[%d:%s] answer [%s] %s' % (hit['id'], hit['title'], answer['brief'], attachment_str)

    for campaign in campaigns:
        print campaign['id'], client.get_credit_by_campaign(campaign['id'])['credit']