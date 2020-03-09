#!/usr/bin/python3

import pytest
import requests
import yaml

with open('./config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

ENDPOINT = config['DASHBOARD_ENDPOINT']

def test_aliveness():
    r = requests.get(ENDPOINT)
    assert r.ok == True
    assert r.status_code == 200
