import numpy as np, pandas as pd
from requests import get
from bs4 import BeautifulSoup

# clean up special characters
def cleanup(x):
    special_chars = {'&auml':'ä', '&ouml':'ö', '&uuml':'ü', '&Auml':'Ä', 'Ouml':'Ö', '&Uuml':'Ü', '&szlig;':'ß', '\xa0':' ', '<p>':'', '</p>':'',
                             '<sub>':'', '</sub>':'', '<br>':'', '<br/>':'', '\n':''}
    for k,v in special_chars.items():
        x = x.replace(k,v)
    return(x)

# function to parse pressetexte from VDA
def parse_vda_texts(url):
    outfile = '../data/vda/vda_' + url.split('/')[-1].strip('.html') + '.txt'
    htmlString = get(url).text
    soup = BeautifulSoup(htmlString, 'lxml')
    clas1 = 'link link--style-camouflage'
    clas2 = 'topics-puzzle__link'
    urls = ['https://www.vda.de' + u.attrs['href'] for u in soup.find_all('a', {'class':[clas1,clas2]})]
    all_texts = ''    
    for url in urls:
        htmlString = get(url).text
        soup = BeautifulSoup(htmlString, 'lxml')
        # filter for text paragraphs, remove images and empty / short paragraphs
        text = [str(s) for s in soup.find_all(['p']) if (s.attrs == {})]
        text = [s for s in text if ('img' not in s) & (len(s.split(' ')) > 2)]
        text = ''.join(str(x) for x in text)
        text = cleanup(text)
        all_texts += text
    with open(outfile, 'w') as f:
        f.write(all_texts)
    return(all_texts)