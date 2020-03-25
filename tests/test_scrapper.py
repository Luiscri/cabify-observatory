#!/usr/bin/python3
# coding: utf-8

import sys
import yaml
from datetime import datetime, timedelta
import re
import pytest
import json

with open('./config.yml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

sys.path.append(config['ORCHESTRATOR_PATH'])

from scrapper.news_scrapper import retrieveAllArticles

http_regex = re.compile(
		r'^(?:http|ftp)s?://'  # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

REQUIRED_DATA = {
	#@id
	'@type': str,
	'_id': str,
	'id': str,
	'schema:author': str,
	'schema:headline': str,
	'schema:articleBody': str,
	'schema:datePublished': str,
}
REQUIRED_KEYS = set(REQUIRED_DATA.keys())

OPTIONAL_DATA = {
	'schema:about': list,
	'schema:description': str,
	'schema:query': str,
	'schema:thumbnailUrl': str,
}
OPTIONAL_KEYS = set(OPTIONAL_DATA.keys())

def check_articles_format(doc):
	assert len(doc) >= 0
	assert isinstance(doc, dict)


#Es un array con todos los articulos. hay que recorrer cada articulo
def check_articles_data(doc):

	article_keys = set(doc.keys())
    # required keys are in articleument
	assert (article_keys & REQUIRED_KEYS) == REQUIRED_KEYS

	for k, v in REQUIRED_DATA.items():
        # value is of expected type
		assert isinstance(doc[k], v)

        # if string, it is not empty
		if v is str:
			assert len(doc[k]) > 0

        # if it is an @id, it is a URL
		if k in ['_id','id']:
			url = doc[k].strip()
			assert re.match(http_regex, url) is not None

		if k == 'schema:author':
			url = doc[k].strip()
            #assert re.match(http_regex, url) is not None

        #body must contain at least 500 words
		if k == 'schema:articleBody':
			assert len(doc[k]) >= 500

query1 = '"movilidad sostenible" OR "transporte sostenible" OR ((contaminacion OR contaminación) AND (no2 OR "dioxido de nitrogeno" OR "dióxido de nitrógeno" OR nox))'
query2 = '"sustainable mobility" OR "sustainable transport" OR ((pollution) AND (no2 OR "stickstoffdioxid" OR "stickstoff-dioxid" OR nox))'
lang1 = 'es'
lang2 = 'en'
now = datetime.today()
yesterday = now - timedelta(days=1)

#You need to set as an environment variable a Google News Api Key
articles1 = retrieveAllArticles(query1, lang1, yesterday)
articles2 = retrieveAllArticles(query2, lang2, yesterday)



@pytest.mark.parametrize('doc', articles1)
def test_articles1(doc):
	check_articles_format(doc)
	check_articles_data(doc)


@pytest.mark.parametrize('doc', articles2)
def test_articles2(doc):
	check_articles_format(doc)
	check_articles_data(doc)