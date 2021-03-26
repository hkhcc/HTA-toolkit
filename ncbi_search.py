# -*- coding: utf-8 -*-
"""
ncbi_search.py: a script for automated abstract search on PubMed

author: Tom C.C. Ho (hcc604@ha.org.hk)
affiliation: Central Technology Office, HAHO, HKSAR of PRC
"""
import atexit
import gzip
import json
import os
import time
import sys

import urllib.request

import xml.etree.ElementTree as ET

from urllib.parse import quote as safequote

CACHE_DIR = 'pubmed-cache'
DB_NAME = 'pubmed.json'
BATCH_SIZE = 100
RETMAX = 100000
MINDATE = '2000/01/01'
DEBUG = True
JSON_DB = dict()

def check_create_dir(directory, cache_file):
    """Create a storage directory if not already present."""
    dir_path = os.path.join(os.path.abspath(os.path.curdir), directory)
    if not os.path.isdir(dir_path):
        try:
            os.mkdir(dir_path)
        except:
            raise PermissionError(dir_path, 'could not be created!')
        print(dir_path, 'successfully created.', file=sys.stderr)
    print(dir_path, '... OK!', file=sys.stderr)
    if not os.path.isfile(os.path.join(dir_path, cache_file)):
        try:
            with open(os.path.join(dir_path, cache_file), mode='w') as f:
                print(json.dumps(JSON_DB), file=f)
        except:
            raise PermissionError(os.path.join(dir_path, cache_file), 'could not be created!')
    print(os.path.join(dir_path, cache_file), '... OK!', file=sys.stderr)
    

def load_database(db_path):
    """Return the extracted JSON data from db_bath"""
    with open(db_path, 'r') as f:
        return json.loads(f.read())
    
def save_database(db_path):
    """Save database to db_bath"""
    with open(db_path, mode='w') as f:
        f.write(json.dumps(JSON_DB))
    print('Database saved.', file=sys.stderr)

def wget(url):
    """Return plain text response from a URL"""
    d = None
    passed = False
    while not passed:
        try:
            with urllib.request.urlopen(url) as response:
                d = response.read().decode('utf-8')
            passed = True
        except:
            print('# Waiting...', file=sys.stderr)
            time.sleep(5)
    return d

def esearch_pmid(term, maxdate, mindate=MINDATE, retmax=RETMAX):
    """Return a list of PMID"""
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&datetype=pdat'
    url = base_url + '&mindate=' + mindate
    url += '&maxdate=' + maxdate
    url += '&term=' + term
    url += '&retmax=' + str(retmax)
    if DEBUG:
        print(url, file=sys.stderr)
    print('# Performing PubMed search with query "{term}" from {mindate} to {maxdate}'.format(term=term, mindate=mindate, maxdate=maxdate),
          file=sys.stderr)
    xml_result = wget(url)
    xml_tree = ET.fromstring(xml_result)
    id_list = list()
    result_count = 0
    for node in xml_tree:
        if node.tag == 'Count':
            result_count = int(node.text)
            print('# Total {number} entries in PubMed'.format(number=result_count), file=sys.stderr)
            if result_count > retmax:
                print('# Number of results ({result}) > retmax ({retmax})!!'.format(result=result_count, retmax=retmax), file=sys.stderr)
        if node.tag == 'IdList':
            for pmid in node:
                id_list.append(pmid.text)
    return id_list

def pmid_batch(pmid_list, n=BATCH_SIZE):
    """Return batches of PMID for retrieval"""
    for i in range(0, len(pmid_list), n):
        yield pmid_list[i:i+n]

def fetch_abstract(pmid_list):
    """Return a list of abstracts from PubMed"""
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract'
    url = base_url + '&id=' + ','.join(str(x) for x in pmid_list)
    if DEBUG:
        print(url, file=sys.stderr)
    d = wget(url)
    return d

def load_abstract(pmid_list, separate_title=True):
    """Return a list of abstracts from local cache and PubMed"""
    global JSON_DB
    require_remote_fetch = list()
    # try to see if abstracts are available locally
    local_abstracts = dict()
    for pmid in pmid_list:
        print('## Retrieving PMID ' + str(pmid), file=sys.stderr)
        if pmid in JSON_DB:
            local_abstracts[pmid] = JSON_DB[pmid]
        else:
            require_remote_fetch.append(pmid)
    # download abstracts that are not available locally
    print('# {number} abstracts require remote download.'.format(number=len(require_remote_fetch)), file=sys.stderr)
    for batch in pmid_batch(require_remote_fetch):
        xml_result = fetch_abstract(batch)
        xml_tree = ET.fromstring(xml_result)
        for pubmed_article in xml_tree.findall('PubmedArticle'):
            pubmed_data = pubmed_article.findall('MedlineCitation')
            assert len(pubmed_data) == 1
            pmid = pubmed_data[0].findall('PMID')
            assert len(pmid) == 1
            extracted_pmid = pmid[0].text
            print('extracted_pmid', extracted_pmid, file=sys.stderr)
            cache_file_path = os.path.join(os.path.abspath(os.path.curdir), CACHE_DIR, str(extracted_pmid) + '.txt')
            article = pubmed_data[0].findall('Article')
            assert len(article) == 1
            article_title = article[0].findall('ArticleTitle')
            assert len(article_title) == 1
            extracted_article_title = article_title[0].text
            abstract = article[0].findall('Abstract')
            assert len(abstract) <= 1
            content = ''
            # output the title
            content += extracted_article_title + '\n'
            # print a separator
            content += '=====separator line=====\n'
            if len(abstract) == 1:
                abstract_text = abstract[0].findall('AbstractText')
                assert len(abstract_text) >= 1
                extracted_abstract_text = list()
                # output the abstract
                for paragraph in abstract_text:
                    if paragraph.text is not None:
                        content += paragraph.text + '\n'
            if len(abstract) == 0:
                content += '[No abstract available.]'
            # add the newl downloaded abstract to JSON_DB
            print('# Adding', extracted_pmid, content, file=sys.stderr)
            JSON_DB[extracted_pmid] = content
    # read the newly downloaded abstracts
    newly_downloaded_abstracts = dict()
    for pmid in require_remote_fetch:
        print('# Newly downloaded', pmid, file=sys.stderr)
        print(JSON_DB.keys(), file=sys.stderr)
        if pmid in JSON_DB:
            newly_downloaded_abstracts[pmid] = JSON_DB[pmid]
        else:
            JSON_DB[pmid] = 'Not a PubMed article.\n=====separator line=====\n[Abstract not retrieved.]'
            newly_downloaded_abstracts[pmid] = JSON_DB[pmid]
    # prepare the output
    assert len(newly_downloaded_abstracts) + len(local_abstracts) == len(pmid_list)
    output_list = list()
    for pmid in pmid_list:
        if pmid in local_abstracts:
            output_list.append([pmid, local_abstracts[pmid]])
        else:
            output_list.append([pmid, newly_downloaded_abstracts[pmid]])
    # separate the title and abstract
    if separate_title:
        new_output_list = list()
        for item in output_list:
            pmid, abstract_and_title = item
            title, abstract = abstract_and_title.split('=====separator line=====')
            title = title.lstrip().rstrip()
            abstract = abstract.lstrip().rstrip()
            new_output_list.append([pmid, title, abstract])
        return new_output_list
    return output_list
        
def pubmed_search(phrase, maxdate):
    """Return a list of abstracts"""
    safe_phrase = safequote(phrase)
    pmid_list = esearch_pmid(safe_phrase, maxdate)
    abstracts = load_abstract(pmid_list)
    return abstracts

check_create_dir(CACHE_DIR, DB_NAME)
JSON_DB = load_database(os.path.join(CACHE_DIR, DB_NAME))
atexit.register(save_database, db_path=os.path.join(CACHE_DIR, DB_NAME))
    
if __name__ == '__main__':
    result = pubmed_search('tuberculosis', '2010/01/01')
