from bs4 import BeautifulSoup
import requests


# --------------- Sitemap class ---------------

class Sitemap:

    def __init__(self,map,children = None, parent=None):

        self.map      = map
        self.children = children
        self.parent   = parent

    def find_urls(self):
        #finds all urls and there important info on the sitemap
        session        = requests.session()
        sitemap        = session.get(self.map)
        soup           = BeautifulSoup(sitemap.text,"xml")
        urls           = list()
        urls_cluttered = soup.find_all("url")
        
        for tag in urls_cluttered:

            link  = self.find_link(tag)
            title = self.find_title(tag)
            image = self.find_default_image(tag)

            if(link != None and title != None and image != None):

                urls.append((link,title,image))

        return urls

    def find_sitemaps(self):
        #finds all sitemaps on the sitemap
        
        sitemaps           = list()
        session            = requests.session()
        sitemap            = session.get(self.map)
        soup               = BeautifulSoup(sitemap.content,"xml")
        sitemaps_cluttered = soup.find_all("sitemap")
        
        for sitemap in sitemaps_cluttered:

            index = sitemap.text.index(".xml")

            if(sitemap.text[index+4]!="?"):

                link = sitemap.text[:index+4].strip()

            else:

                link = sitemap.text.strip()

            sitemaps.append(Sitemap(link,None,map))

        for sitemap in sitemaps:

            sitemap.find_sitemaps()
        
        self.children = sitemaps

    def find_images(self):
        #returns all images on sitemap
        
        session          = requests.session()
        sitemap          = session.get(self.map)
        soup             = BeautifulSoup(sitemap.text,"xml")
        images           = list()
        images_cluttered = soup.find_all("image:loc")

        for image in images_cluttered:

            images.append(image.text)

        return images

    def find_title(self,tag):
        #returns the title of the image on the page
        #usually the same as the title of the item
        
        title = tag.find("image:title")

        if(title != None):

            return title.text

        else:

            return None
        

    def find_default_image(self,tag):
        #returns the first image in the tag
        #usually the same as the default image on display    
        
        image = tag.find("image:loc")

        if(image != None):

            return image.text

        else:

            return None


    def find_link(self,tag):
        #returns the contents of the first loc in the tag
        #usually the url to the page 
  
        loc = tag.find("loc")

        if(loc != None):

            return loc.text

        else:

            return None