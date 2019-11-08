import requests
import json
import re
from unidecode import unidecode
from newspaper import Article # Igual hay que usar newspaper3k para usar el de Python3
from datetime import datetime, timedelta
import os

def cleanText(text):
    text = re.sub(r'(?:\s{2,})', ' ', text)
    text = re.sub('\n\n', '\n', text)
    cleanTags = re.compile('<.*?>')
    text = re.sub(cleanTags, '', text)
    text = unidecode(text)
    return(text)

'''
def uriResource(source):
    if(source == 'Al Jazeera English'):
        source = 'Al Jazeera'
    reply = requests.get('https://api.dbpedia-spotlight.org/en/annotate?text={}'.format(source),headers={"Accept":"application/json"})
    try:
        uri = reply.json()["Resources"][0]["@URI"]
    except Exception as e:
        uri = "http://dbpedia.org/resource/Google_News"
        pass
    return uri
'''

def retrieveAllNews(query, lang, date):
    # key = os.environ.get('NEWS_API_KEY')
    key = 'f4e0f6078d7b4c35b2ff77bc09bc6aff'

    fromDate = date.strftime("%Y-%m-%d")

    # From - El articulo más antiguo desde el que queremos coger
    url = ('https://newsapi.org/v2/everything?q=' + query + '&from=' + fromDate +
           '&language=' + lang +'&sortBy=relevancy&pageSize=100&apiKey=' + key)
    response = requests.get(url).json()

    if response['status'] == 'error':
        print('ERROR - {}.\n{}'.format(response['code'], response['message']))
        return []

    print("{} articles found. Formatting {} of them...".format(response['totalResults'], min(response['totalResults'], 100)))
        
    news=[]
    for idx, article in enumerate(response['articles']):
        aux = {}
        a = Article(article['url'])
        aux["@type"] = "schema:NewsArticle"
        aux["@id"] = article['url']
        aux["id"] = article['url']
        aux["schema:author"] = article['source']['name']
        #aux["schema:author"] = uriResource(article['source']['name'])
        aux["schema:datePublished"] =article['publishedAt']
        aux["schema:headline"] =  article['title']
        print("{}. {}".format(idx+1, article['title']))
        try: # Necesitamos el try por si borran algun articulo y la URL ya no esta disponible
            a.download()
            a.parse()
            aux["schema:articleBody"] = cleanText(a.text) # Hay que utilizar Article porque NewsApi no te da el cuerpo entero de la noticia
            if not a.keywords: # Si keywords es una lista vacia
                aux["schema:about"] = query
            else:
                aux["schema:about"] = a.keywords
        except:
            aux["schema:articleBody"] = cleanText(article['content'])
            aux["schema:about"] = query
            pass
        aux["schema:description"] = cleanText(article['description'])
        aux["schema:query"] = query
        aux["schema:thumbnailUrl"] = article['urlToImage']
        news.append(aux)

    # return news
    with open('./news.txt', 'a') as f:
        for new in news:
            saving_json = json.dumps(new, ensure_ascii=False)
            f.write(saving_json)
            f.write('\n')

if __name__ == "__main__":
    # Cabify, sostenibilidad, sostenible, movilidad, medio ambiente, transporte
    #query = 'Cabify AND (((sostenibilidad OR sostenible) OR movilidad) OR "medio ambiente")'
    #query = 'movilidad AND (sostenibilidad OR sostenible)' # Asi da 35 / 9 / 10 / 14 articulos/dia
    #query = '(movilidad OR transporte) AND (sostenibilidad OR sostenible)' # Asi da 22 / 31 / 24 articulos/dia
    #query = 'movilidad AND (sostenibilidad OR sostenible) OR "medio ambiente"' # Asi da 175 / 112 / 131 / 161 articulos/dia
    #query = 'movilidad OR sostenibilidad OR sostenible OR "medio ambiente"' # Asi da 474 / 339 / 411 / 464 articulos/dia
    
    query = '"movilidad sostenible" OR "transporte sostenible" OR (contaminacion AND (no2 OR "dioxido de nitrogeno" OR nox))'
    #query = '"sustainable mobility" OR "sustainable transport" OR (contamination AND (no2 OR "nitrogen dioxide"))'
    lang = 'es'
    #lang = 'en'
    yesterday = datetime.today() - timedelta(days=1)
    retrieveAllNews(query, lang, yesterday)