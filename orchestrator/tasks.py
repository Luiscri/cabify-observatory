import sys
sys.dont_write_bytecode = True

# logging
import logging

# orchestration
import luigi
from luigi.contrib.esindex import CopyToIndex

# scrapper
from scrapper.news_scrapper import retrieveAllArticles
from datetime import datetime, timedelta
import os, subprocess, shutil, json
from elasticsearch import Elasticsearch

# analyzer
from urllib.parse import urlunsplit
import requests

logger = logging.getLogger(__name__)

class ScrapperTask(luigi.Task):
    run_date = luigi.parameter.DateParameter()
    index = luigi.parameter.Parameter()
    doc_type = luigi.parameter.Parameter()
    output_directory = ''

    def run(self):
        self.output_directory = os.path.join(os.getcwd(), 'data', self.run_date.strftime('%Y-%m'), 'scrapper')
        
        previous_month = (self.run_date-timedelta(days=30)).strftime('%Y-%m')
        previous_month_directory = os.path.join(os.getcwd(), 'data', previous_month)
        if os.path.exists(previous_month_directory):
            subprocess.check_output(['tar','-zcf','{}.tar.gz'.format(previous_month_directory), previous_month_directory])
            shutil.rmtree(previous_month_directory, ignore_errors=True)

        two_months_ago = (self.run_date-timedelta(days=60)).strftime('%Y-%m')
        two_months_ago_tar = os.path.join(os.getcwd(), 'data', '{}.tar.gz'.format(two_months_ago))
        if os.path.isfile(two_months_ago_tar):
            os.remove(two_months_ago_tar)

        query = '"movilidad sostenible" OR "transporte sostenible" OR ((contaminacion OR contaminación) AND (no2 OR "dioxido de nitrogeno" OR "dióxido de nitrógeno" OR nox))'
        lang = 'es'
        now = datetime.today()
        yesterday = now - timedelta(days=1)

        articles = retrieveAllArticles(query, lang, yesterday)

        filtered = []
        host = os.environ.get('ES_HOST')
        try:
            es = Elasticsearch(hosts=host)
            for article in articles:
                if es.exists(index=self.index, doc_type=self.doc_type, id=article['id']):
                    logger.info('Duplicated article found.', extra={'methodname': self.__class__.__name__})
                    continue
                else:
                    filtered.append(article)
        except:
            logger.error("Error performing exists() query to ElasticSearch.", extra={'methodname': self.__class__.__name__})
            filtered = articles

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        with self.output().open('w') as outfile:
            for article in filtered:
                saving = json.dumps(article, ensure_ascii=False)
                outfile.write(saving+'\n')
            logger.info("{} articles retrieved.".format(len(filtered)), extra={'methodname': self.__class__.__name__})

    def output(self):
        file_path = os.path.join(self.output_directory, '{}.txt'.format(self.run_date))
        return luigi.LocalTarget(file_path)        

class AnalyzerTask(luigi.Task):
    run_date = luigi.parameter.DateParameter()
    index = luigi.parameter.Parameter()
    doc_type = luigi.parameter.Parameter()
    output_directory = ''

    def requires(self):
        return ScrapperTask(run_date=self.run_date, index=self.index, doc_type=self.doc_type)

    def run(self):
        self.output_directory = os.path.join(os.getcwd(), 'data', self.run_date.strftime('%Y-%m'), 'analyzer')

        articles = []
        with self.input().open('r') as infile:
            for line in infile.readlines():
                article = json.loads(line)
                
                senpy_endpoint = os.environ.get("SENPY_NETWORK_LOCATION")
                url = urlunsplit(['http', senpy_endpoint, '/api', '', ''])
                params = {
                    'algo': 'taxonomiesPlugin',
                    'i': article['schema:articleBody']
                }
                response = requests.get(url, params=params).json()
                if response['@type'] == 'Error' and 'message' in response:
                    logger.error(response['message'], extra={'methodname': self.__class__.__name__})
                    continue
                elif response['@type'] == 'Results' and 'entries' in response:
                    if response['entries'][0]:
                        article['taxonomies'] = response['entries'][0]
                    else:
                        logger.info('Article discarded: it did not match any of the categories.', extra={'methodname': self.__class__.__name__})
                        continue

                params['algo'] = 'nerSpacyPlugin'
                response = requests.get(url, params=params).json()
                if response['@type'] == 'Error' and 'message' in response:
                    logger.error(response['message'], extra={'methodname': self.__class__.__name__})
                    continue
                elif response['@type'] == 'Results' and 'entries' in response:
                    article['entities'] = response['entries'][0]

                articles.append(article)

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        with self.output().open('w') as outfile:
            for article in articles:
                saving = json.dumps(article, ensure_ascii=False)
                outfile.write(saving+'\n')

    def output(self):
        file_path = os.path.join(self.output_directory, '{}.txt'.format(self.run_date))
        return luigi.LocalTarget(file_path) 

class SearchAndStoreTask(CopyToIndex):
    run_date = luigi.parameter.DateParameter()
    index = luigi.parameter.Parameter()
    doc_type = luigi.parameter.Parameter()
    host = os.environ.get('ES_HOST')

    def requires(self):
        return AnalyzerTask(run_date=self.run_date, index=self.index, doc_type=self.doc_type)

class MainTask(luigi.Task):
    run_date = luigi.parameter.DateParameter(default=datetime.today())
    index = luigi.parameter.Parameter(default="articles")
    doc_type = luigi.parameter.Parameter(default="article")

    def requires(self):
        loggers = [logging.getLogger(), logging.getLogger('luigi-interface')]
        for l in loggers:
            formatter = None
            for h in l.handlers:
                if type(h) == logging.FileHandler:
                    formatter = h.formatter
                    l.removeHandler(h)

            if formatter:
                logs_directory = os.path.join(os.getcwd(), 'data', self.run_date.strftime('%Y-%m'), 'logs')
                file_path = os.path.join(logs_directory, '{}.log'.format(self.run_date))

                if not os.path.exists(logs_directory):
                    os.makedirs(logs_directory)

                fh = logging.FileHandler(file_path, 'a')
                fh.setFormatter(formatter)
                l.addHandler(fh)

        logger.info('Starting pipeline.', extra={'methodname': self.__class__.__name__})

        return SearchAndStoreTask(run_date=self.run_date, index=self.index, doc_type=self.doc_type)