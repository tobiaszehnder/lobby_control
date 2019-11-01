import numpy as np, pandas as pd, xml.etree.ElementTree as ET, sys, urllib.request
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

# parse XML
def parse_xml(url):
    tree = ET.parse(urllib.request.urlopen(url))
    root = tree.getroot() # root consists of 4 elements: vorspann, sitzungsverlauf, anlagen, rednerliste
    return root

# save redner and their ids
def get_redner_dict(root, redner):
    for r in root.find('rednerliste'):
        try:
            titel = r.find('name').find('titel').text
        except AttributeError:
            titel = ''
        try:
            vorname = r.find('name').find('vorname').text
        except AttributeError:
            vorname = ''
        try:
            nachname = r.find('name').find('nachname').text
            if type(nachname) == type(None):
                continue # Some weird case of the name being None. Skip.
        except AttributeError:
            nachname = ''
        try:
            fraktion = ', ' + r.find('name').find('fraktion').text
        except AttributeError:
            fraktion = ''
        redner[r.attrib['id']] = cleanup(' '.join([titel, vorname, nachname+fraktion]).strip())
    return redner

# extract text from 'reden' and save them with their redner_id in a dict
def get_reden(root, d):
    for r in root.find('sitzungsverlauf'):
        reden = r.findall('rede')
        if len(reden) == 0:
            continue
        try:
            redner_ids = [[p.find('redner') for p in rede.findall('p') if p.attrib['klasse'] == 'redner'][0].attrib['id'] for rede in reden]
            texte = [' '.join([p.text for p in rede.findall('p') if not p.attrib['klasse'] == 'redner']) for rede in reden]
        except (KeyError, TypeError): # some xml files contain empty elements with no 'klasse' or None-type elements. skip them.
            continue
        for redner_id, text in zip(redner_ids, texte):
            text = cleanup(text)
            if not redner_id in d.keys():
                d[redner_id] = [text]
            else:
                d[redner_id].append(text)
    return d
