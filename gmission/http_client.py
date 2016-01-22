#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'
import requests


def get(url, token=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = 'gMission ' + token
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()


def post(url, data=None, json=None, files=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = 'gMission ' + token
    headers['Content-Type'] = 'application/json'
    print json
    response = requests.post(url,data=data, json=json, files=files, headers=headers)
    if response.status_code == requests.codes.ok or response.status_code == requests.codes.created:
        return response.json()
    else:
        response.raise_for_status()

def post_image(url, files=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = 'gMission ' + token
    response = requests.post(url, files=files, headers=headers)
    if response.status_code == requests.codes.ok or response.status_code == requests.codes.created:
        return response.json()
    else:
        response.raise_for_status()
