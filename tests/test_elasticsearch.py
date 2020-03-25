#!/usr/bin/python3

import sys
import requests
import pytest
import yaml
import re
from posixpath import join as urljoin

REQUIRED_DATA = {
	#@id
	'id': str,
	'@type': str,
	'schema:author': str,
	'schema:headline': str,
	'schema:articleBody': str,
	'schema:datePublished': str,
	'entities': list,
	'taxonomies': list,
}
REQUIRED_KEYS = set(REQUIRED_DATA.keys())

OPTIONAL_DATA = {
	'schema:about': list,
	'schema:description': str,
	'schema:query': str,
	'schema:thumbnailUrl': str,
}
OPTIONAL_KEYS = set(OPTIONAL_DATA.keys())

ENTITIES_REQUIRED_DATA = {
	'@type': list,
	#'@id': str,
	'schema:name': str,
	'nif:beginIndex': list,
	'nif:endIndex': list,
	'prov:wasDerivedFrom': dict,
}
ENTITIES_REQUIRED_KEYS = set(ENTITIES_REQUIRED_DATA.keys())
ENTITIES_TYPES = set(['schema:Person', 'schema:Place', 'schema:Organization', 'prov:Entity'])

CATEGORIES_REQUIRED_DATA = {
	'@type': str,
	'@id': str,
	'nif:beginIndex': list,
	'nif:endIndex':list,
	'rdfs:label': str,
}
CATEGORIES_REQUIRED_KEYS = set(CATEGORIES_REQUIRED_DATA.keys())
CATEGORIES_TYPES = "skos:Concept"

with open('./config.yml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

ENDPOINT = config['ES_ENDPOINT']
INDEX = config['index']
TYPE = config['type']

# _search is used for searching is ElasticSearch
ENDPOINT_SEARCH = urljoin(ENDPOINT, '_search')

http_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Check endpoint is alive
def test_aliveness():
    r = requests.get(ENDPOINT_SEARCH, params={'size': 0})
    r_json = r.json()
    assert r.ok == True
    assert isinstance(r_json, dict)
    assert r_json['timed_out'] == False

# Check number of documents is OK
def test_number_docs():
    r = requests.get(ENDPOINT_SEARCH, params={'size': 0})
    r_json = r.json()
    assert r.ok == True
    assert r_json['hits']['total'] > 0

def check_doc_type(doc):
    assert isinstance(doc, dict)

def check_doc_metadata(doc):
    assert doc['_index'] == INDEX
    assert doc['_type'] == TYPE
    assert len(doc['_source'].keys()) > 0

def check_entity(entity):
    assert isinstance(entity, dict)
    entity_keys = set(entity.keys())
    # required keys are in entity
    assert (entity_keys & ENTITIES_REQUIRED_KEYS) == ENTITIES_REQUIRED_KEYS

    for k, v in ENTITIES_REQUIRED_DATA.items():
        # value is of expected type
        assert isinstance(entity[k], v)

        # if string, it is not empty
        if v is str:
            assert len(entity[k]) > 0

        # if it is an @id, it is a URL
        if k == '@id':
            url = entity[k].strip()
            #assert re.match(http_regex, url) is not None

        # if it is a @type, we check if it is one of the expected value
        if k == '@type':
            for _type in entity[k]:
                assert _type in ENTITIES_TYPES

	#beginIndex and endIndex indexes must to be int
    for value in ['nif:beginIndex', 'nif:endIndex']: 
        for num in entity[value]:
            assert isinstance(num, int)

    #beginIndex must have the same length than endIndex
    assert len(entity['nif:beginIndex']) == len(entity['nif:endIndex'])
    #beginIndex must be lower than endIndex
    for pos in range(len(entity['nif:beginIndex'])):
    	assert entity['nif:beginIndex'][pos] < entity['nif:endIndex'][pos]


def check_category(category):
    assert isinstance(category, dict)
    category_keys = set(category.keys())
    # required keys are in entity
    assert (category_keys & CATEGORIES_REQUIRED_KEYS) == CATEGORIES_REQUIRED_KEYS

    for k, v in CATEGORIES_REQUIRED_DATA.items():
        # value is of expected type
        assert isinstance(category[k], v)

        # if string, it is not empty
        if v is str:
            assert len(category[k]) > 0

        # if it is an @id, it is a URL
        if k == '@id':
            url = category[k].strip()
            #assert re.match(http_regex, url) is not None

        # if it is a @type, we check if it is one of the expected value
        if k == '@type':
            for _type in category[k]:
                assert _type in CATEGORIES_TYPES

        #beginIndex and endIndex indexes must to be int
    for value in ['nif:beginIndex', 'nif:endIndex']: 
        for num in category[value]:
            assert isinstance(num, int)

    #beginIndex must have the same length than endIndex
    assert len(category['nif:beginIndex']) == len(category['nif:endIndex'])
    #beginIndex must be lower than endIndex
    for pos in range(len(category['nif:beginIndex'])):
    	assert category['nif:beginIndex'][pos] < category['nif:endIndex'][pos]

def check_doc(doc):
    doc_keys = set(doc.keys())
    # required keys are in document
    assert (doc_keys & REQUIRED_KEYS) == REQUIRED_KEYS

    for k, v in REQUIRED_DATA.items():
        # value is of expected type
        assert isinstance(doc[k], v)

        # if string, it is not empty
        if v is str:
            assert len(doc[k]) > 0

        # if it is an @id, it is a URL
        if k == '@id':
            url = doc[k].strip()
            assert re.match(http_regex, url) is not None

        if k == 'schema:author':
            url = doc[k].strip()
            #assert re.match(http_regex, url) is not None

        if k == 'entities':
            entities = doc[k]
            if len(entities) > 0:
                for entity in entities:
                    check_entity(entity)

        if k == 'taxonomies':
            taxonomies = doc[k]
            if len(taxonomies) > 0:
                for category in taxonomies:
                    check_category(category)
        

r = requests.get(ENDPOINT_SEARCH, params={'size': 0})   
n_docs = r.json()['hits']['total']

r = requests.get(ENDPOINT_SEARCH, params={'size': n_docs + 1})
r = r.json()
hits = r['hits']['hits']

@pytest.mark.parametrize('doc', hits)
def test_docs(doc):
    check_doc_type(doc)
    check_doc_metadata(doc)
    check_doc(doc['_source'])

