from bs4 import BeautifulSoup
import requests

def find_urls(url):

    session = requests.session()
    sitemap = session.get(url)
    soup = BeautifulSoup(sitemap.text,"xml")

    urls = list()

    urls_cluttered = soup.find_all("url")

    for url in urls_cluttered:
        urls.append(url.find("loc").text)

    
    #print(urls,"@")
    return urls

def find_sitemaps(url):
    sitemaps = list()
    session = requests.session()
    sitemap = session.get(url)
    soup = BeautifulSoup(sitemap.content,"xml")
    
    sitemaps_cluttered = soup.find_all("sitemap")
    
    for sitemap in sitemaps_cluttered:
       loc = sitemap.find("loc")
       sitemaps.append(loc.text)
   
    return sitemaps
