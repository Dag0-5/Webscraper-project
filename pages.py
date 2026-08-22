from bs4 import BeautifulSoup
import requests
import re
import heapq
from file_interactions import find_wordlist,check_from_word_list
# --------------- Page class ---------------

class Page():

    def __init__(self,url):
        self.url = url
        self.session = requests.session()
        self.page = None
        self.soup = None


    def find_soup(self):
        self.page = self.session.get(self.url)
        self.soup = BeautifulSoup(self.page.text,"html.parser")

        
    def find_urls(self):
        url_list = list()
        for link in self.soup.find_all('a'):
            if(link.get("href")!= None):
                url_list.append(link.get("href"))
        return list(set(url_list))

        
    def find_next_page(self):
        wordlist = find_wordlist("next_page")
        url_list = self.find_urls(self.url)
        next_pages = check_from_word_list(wordlist,url_list,True)

        if len(next_pages)>0:
            for i in range(len(next_pages)-1,0,-1):
                next_page = next_pages[i]
                if ("http" in next_page[1] and self.url not in next_page[1]):
                    next_pages.remove(next_page)

        return next_pages


    def find_price(self):

        price = self.soup.find(class_=re.compile("price"))

        if(price == None):
            return None
        
        temp = price.text.strip()

        start = temp.find("£")
        price = temp[start:]
        
        non_digit =re.findall('\\D', temp[start+1:])

        
        if(non_digit != [] and non_digit != ["."]):
            for char in non_digit:
                if char != ".":
                    break
            end = temp[start:].find(char)
            price = temp[start:start+end]
        
        return price


    def find_options(self):
        #finds options on page
        #TODO improve
        #Current system only works for 4 websites, needs to be expanded
       
        options = list()
        options_cluttered = list()
        successful = list()

        current_length = 0

        wordlist = find_wordlist("options_wordlist",False)
        blacklist = find_wordlist("options_blacklist",False)

        for phrase in wordlist:
            options_cluttered += self.soup.find_all(class_=re.compile(phrase))
            
            if len(options_cluttered) != current_length:
                successful.append(phrase)
                
                for i in range(len(options_cluttered)-1, -1, -1):
                    option = options_cluttered[i]
                    if any(word in option.text for word in blacklist):
                        del options_cluttered[i]
                current_length = len(options_cluttered)
                
        for phrase in successful:
            options+= self.get_option_text(phrase,options_cluttered)

        return options


    def get_option_text(self,phrase,tag_list):
        new_list = list()

        if (phrase == "product-content"):

            for tag in tag_list:
                new_list += tag.find_all(class_="product-item-name")
                
        elif (phrase == "product-form"):

            for tag in tag_list:
                new_list += tag.find_all("label")

        elif (phrase == "form-control" or phrase == "select"):
            for tag in tag_list:
                new_list += tag.find_all("option")

        if(new_list!= []):
            for i in range (0,len(new_list)):
                new_list[i] = new_list[i].find(string=True, recursive=False).strip()

        return new_list


    def find_title(self):
        remove_list = [".html","-en"]

        last = self.url.rfind("/")
        title = self.url[last+1:]

        for phrase in remove_list:

            if title.endswith(phrase):
                index = title.rindex(phrase)
                title = title[:index]

        title = title.split("-")
        replacement = ""

        for part in title:
            replacement += part.capitalize() +" "

        return replacement


    def find_image(self):
        #returns the second image as the first is sometimes a logo
        blacklist = find_wordlist("image_blacklist",False)
        must_contain = find_wordlist("url_must_contains",False)
        
        images = self.soup.find_all("img")
        image_urls = list()
        
        for image in images:
            source = image.get("src")
            if(source != "" and source != None):
                
                if (not any(word in source for word in blacklist)) and any(word in source for word in must_contain) :
                    image_urls.append(source)

        if(image_urls == []):
            return None
        
        return image_urls[1]
