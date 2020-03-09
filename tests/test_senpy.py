#!/usr/bin/python3

import pytest
import requests
import yaml

with open('./config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

TEXT = open('test_text.txt','r').read()

ENDPOINT = config['SENPY_ENDPOINT']

def test_aliveness():
	r = requests.get(ENDPOINT)
	assert r.ok == True
	assert r.status_code == 200

def senpy_request(text, algo, outformat):
	payload = {
	'algo': algo,
	'i': text,
	'conversion': 'full',
	'expanded-jsonld': False,
	'informat': 'text',
	'intype': 'direct',
	'outformat': outformat,
	'urischeme': 'RFC5147String',
	'with_parameters': False
	}
	r = requests.get(ENDPOINT + 'api/', params=payload)
	assert r.ok == True
	assert r.status_code == 200
	return r

def check_jsonld_response(r):
    assert isinstance(r, dict)
    assert '@context' in r
    #assert '@id' in r
    assert 'entries' in r

def check_turtle_response(r):
    assert r.text is not None
    assert len(r.text) > 0

def  test_taxonomiesPlugin():
    # json-ld format
    r = senpy_request(TEXT, 'taxonomiesPlugin', 'json-ld')
    json_r = r.json()
    check_jsonld_response(json_r)

    # turtle format
    r = senpy_request(TEXT, 'taxonomiesPlugin', 'turtle')
    check_turtle_response(r)

def  test_nerPlugin():
    # json-ld format
    r = senpy_request(TEXT, 'nerSpacyPlugin', 'json-ld')
    json_r = r.json()
    check_jsonld_response(json_r)

    # turtle format
    r = senpy_request(TEXT, 'nerSpacyPlugin', 'turtle')
    check_turtle_response(r)
