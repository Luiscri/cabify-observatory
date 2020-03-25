import requests
import logging
import re
import os
from newspaper import Article # Igual hay que usar newspaper3k para usar el de Python3
from datetime import datetime, timedelta

def cleanText(text):
    text = re.sub('\s+\n\s+', '\n', text)
    text = re.sub('\n+', '\n', text)
    text = re.sub(r'(?:\s{2,})', ' ', text)
    cleanTags = re.compile('<.*?>')
    text = re.sub(cleanTags, '', text)
    return(text)

def retrieveAllArticles(query, lang, date):
    key = os.environ.get('NEWS_API_KEY')

    fromDate = date.strftime("%Y-%m-%d")

    url = 'https://newsapi.org/v2/everything'
    # From - El articulo más antiguo que queremos recibir
    params = {
        "q": query,
        "from": fromDate,
        "language": lang,
        "sortBy": "relevancy",
        "pageSize": 100,
        "apiKey": key
    }

    response = requests.get(url, params=params).json()

    if response['status'] == 'error':
        #logging.error('{}.\n{}'.format(response['code'], response['message']), extra={'taskname': 'Scrapper Task'})
        return []
        
    articles=[]
    for idx, article in enumerate(response['articles']):
        aux = {}
        a = Article(article['url'])
        aux["@type"] = "schema:NewsArticle"
        aux["_id"] = article['url']
        aux["id"] = article['url']
        aux["schema:author"] = article['source']['name']
        #aux["schema:author"] = uriResource(article['source']['name'])
        aux["schema:datePublished"] =article['publishedAt']
        aux["schema:headline"] =  article['title']
        try: # Necesitamos el try por si borran algun articulo y la URL ya no esta disponible
            a.download()
            a.parse()
            body = cleanText(a.text)
            if len(body) < 500:
                continue
            aux["schema:articleBody"] = body # Hay que utilizar Article porque NewsApi no te da el cuerpo entero de la noticia
            aux["schema:about"] = a.keywords
        except:
            continue
        aux["schema:description"] = cleanText(article['description'])
        aux["schema:query"] = query
        aux["schema:thumbnailUrl"] = article['urlToImage']
        articles.append(aux)

    #logging.info("{} articles found.".format(len(articles)), extra={'taskname': 'Scrapper Task'})

    return articles