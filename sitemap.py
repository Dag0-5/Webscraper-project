from bs4 import BeautifulSoup
import requests

def find_urls(url):
    #finds all urls and there important info on the sitemap
    session = requests.session()
    sitemap = session.get(url)
    soup = BeautifulSoup(sitemap.text,"xml")

    urls = list()

    urls_cluttered = soup.find_all("url")

    for tag in urls_cluttered:
        link = find_link(tag)
        title = find_title(tag)
        image = find_default_image(tag)

        urls.append((link,title,image))

    return urls

def find_sitemaps(url):
    #finds all sitemaps on the sitemap
    sitemaps = list()
    session = requests.session()
    sitemap = session.get(url)
    soup = BeautifulSoup(sitemap.content,"xml")
    
    sitemaps_cluttered = soup.find_all("sitemap")
    
    for sitemap in sitemaps_cluttered:
       sitemaps.append(sitemap.text)
   
    return sitemaps

def find_images(url):
    #returns all images on sitemap
    session = requests.session()
    sitemap = session.get(url)
    soup = BeautifulSoup(sitemap.text,"xml")

    images = list()

    images_cluttered = soup.find_all("image:loc")

    for image in images_cluttered:
        images.append(image.text)

    return images

def find_title(tag):
    #returns the title of the image on the page
    #usually the same as the title of the item
    title = tag.find("image:title")
    if(title != None):
        return title.text
    else:
        return None
    

def find_default_image(tag):
    #returns the first image in the tag
    #usually the same as the default image on display    
    image = tag.find("image:loc")
    if(image != None):
        return image.text
    else:
        return None

def find_link(tag):
    #returns the contents of the first loc in the tag
    #usually the url to the page 
    loc = tag.find("loc")
    if(loc != None):
        return loc.text
    else:
        return None