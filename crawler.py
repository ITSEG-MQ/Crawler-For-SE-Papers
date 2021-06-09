from numpy.lib.twodim_base import mask_indices
import requests
import urllib.request
import pandas as pd 
from bs4 import BeautifulSoup 
import time
import os
import random
import numpy as np
import xml.etree.ElementTree as ET
from selenium import webdriver
from pyvirtualdisplay import Display

def get_doi(p):
    doi = None
    dblp_link = 'https://dblp.org/search/publ/api?q='

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    search_link = dblp_link + p
    try:
        response = requests.get(search_link,timeout=40,headers=headers)
        response.raise_for_status()

        response.encoding = response.apparent_encoding
        # print(response.text)
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()
        for ee in root.iter('ee'):
            doi = ee.text
            break
    except:
        pass

    return doi


def process_csv():
    df_av = pd.read_csv('list_av.csv', names=['conf', 'year', 'publisher', 'title'])
    df_all = pd.read_csv('list_all.csv', names=['conf', 'year', 'title', 'track', 'doi'])

    df = df_all[df_all['title'].isin(df_av['title'].values)]

    # df_av = df_av[df_av['title'].isin(df['title'].values)]

    dois = []
    df_values = df[['title', 'doi']].values
    df_av_values = df_av['title'].values
    for i in range(len(df_av_values)):
        found = False
        for j in range(len(df_values)):
            if df_values[j, 0] == df_av_values[i]:
                dois.append(df_values[j, 1])
                found = True
                break
        if not found:
            dois.append('')

    df_av['doi'] = dois
    df_av.to_csv('list_av.csv')


link = 'https://dl.acm.org/doi/pdf/10.1145/3368089.3417918'

def getHtml(url):
    # Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    try:
        response = requests.get(url,timeout=40,headers=headers)
        response.raise_for_status()

        response.encoding = response.apparent_encoding

        return response.text
    except:
        import traceback
        traceback.print_exc()

def download_file(download_url, publisher, filename):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    paper_title=filename[:-1].replace(' ', '_').replace(':','')
    
    # req = urllib.request.Request(download_url, None, {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'})
    if publisher == 'acm':
        download_url = 'https://dl.acm.org/doi/pdf/' + download_url[16:]
        try:
            response = requests.get(download_url, timeout=80, headers=headers)
            with open('papers_missed/' + paper_title+'.pdf','wb') as f:
                f.write(response.content)
            return True
        except:
            print('Cannot donload paper: ' + paper_title) 
            return False        
    elif publisher == 'ieee':
        try:
            response = requests.get(download_url, timeout=80, headers=headers)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            paper_link = soup.find("link", {"rel":"canonical"})['href']
            arcNum = paper_link.split('/')[-2]
            print(paper_link)
            # pdfUrl='http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+arcNum+'&ref='   
            pdfUrl = 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={}&ref='.format(arcNum) 
            # soup = BeautifulSoup(getHtml(pdfUrl), 'html.parser')
            # result = soup.body.find_all('iframe')
            # downloadUrl = result[-1].attrs['src']
            # print(pdfUrl)
            # print(downloadUrl)
            response = requests.get(pdfUrl, timeout=80, headers=headers)


            # print(paper_title)
            with open('papers_missed/' + paper_title+'.pdf','wb') as f:
                # print('start download file ',paper_title)
                f.write(response.content)
            return True
        except:
            print('Cannot donload paper: ' + paper_title)         
            return False
    elif publisher == 'springer':
        try:
            response = requests.get(download_url, timeout=80, headers=headers)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.body.find_all("a")
            download_link = None
            for link in links:
                if link["class"][0] == "c-pdf-download__link":
                    download_link = link["href"]
                    break
            if download_link:
                # downloadUrl = 'https://link.springer.com' + download_link
                response = requests.get(download_link, timeout=80, headers=headers)


                # print(paper_title)
                with open('papers_missed/' + paper_title+'.pdf','wb') as f:
                    # print('start download file ',paper_title)
                    f.write(response.content)
                return True
            else:
                return False
        except:
            print('Cannot donload paper: ' + paper_title) 
            return False
    elif publisher == 'ScienceDirect':

        browser.get(download_url)
        time.sleep(5)
        index = browser.current_url.split('/')[-1].split('?')[0]
        pdf_url="https://www.sciencedirect.com/science/article/pii/{}/pdfft?isDTMRedir=true&amp;download=true".format(index)
        response = requests.get(pdf_url, timeout=80, headers=headers)
        with open('papers_missed/' + paper_title+'.pdf','wb') as f:
            print('start download file ',paper_title)
            f.write(response.content)
            # with requests.get(url, stream=True, headers=HEADERS) as r:
            #     if r.status_code == 200:
            #         for chunk in r.iter_content(chunk_size=1024*1024):
            #             file_to_save.write(chunk)


    
    elif publisher == "wiley":
        url = "https://onlinelibrary.wiley.com/doi/pdfdirect/{}?download=true".format(download_url[16:])
        try:
            response = requests.get(url, timeout=80, headers=headers)
            with open('papers_missed/' + paper_title+'.pdf','wb') as f:
                print('start download file ',paper_title)
                f.write(response.content)
                return True

        except:
            print('Cannot donload paper: ' + paper_title) 
            return False
def download(df):
    for row in df[['publisher', 'title']].values:
        # if count < 172:
        #     count += 1
        #     continue
        # print(row[2])
        if 'ACM' in row[0]:
            publisher = 'acm'
        elif 'IEEE' in row[0]:
            publisher = 'ieee'
        elif 'Springer' in row[0]:
            publisher = 'springer'
        elif 'ScienceDirect' in row[0]: 
            publisher = 'ScienceDirect'
        elif 'Wiley' in row[0]:
            publisher = 'wiley'

        doi_link = get_doi(row[1])
        if not doi_link:
            # count += 1
            continue
        success = download_file(doi_link, publisher, row[1])

        # count += 1
        time.sleep(random.randint(5, 25))

    # np.save("download_list.npy",np.array(download_list))

def download_from_strach():
    count = 0
    df = pd.read_csv('new_conf.csv')
    download_list = df['title'].values.tolist()[172:]
    download(df, download_list)

def download_from_list():
    # download_list = np.load("download_list.npy")
    df = pd.read_csv("journal_paper.tsv", sep='\t', names=['conf', 'year', 'publisher', 'track', 'title'])
    df = df[df['publisher'] == 'ScienceDirect']
    # df_list = df[df['title'].isin(download_list.tolist())]
    download(df)

# download_from_list()
if __name__ == "__main__":
    # client = ElsClient("e8bf6ad1d9d120ec76d44f926ff5bf28")
    display = Display(visible=0, size=(800, 800))  
    display.start()
    browser = webdriver.Chrome('/opt/WebDriver/bin/chromedriver')

    # df = pd.read_csv("missed_papers.tsv", sep='\t', names=['conf', 'year', 'publisher', 'track', 'title'])
    # get_doi(df)
    download_from_list()