from bs4 import BeautifulSoup
import requests
import heapq
import time 
import random
import re

def find_urls(url,redirects=30):
    session = requests.session()
    session.max_redirects = redirects

    page = session.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # print(soup.prettify())
    url_list = list()
    for link in soup.find_all('a'):
        if(link.get("href")!= None):
            url_list.append(link.get("href"))
    return list(set(url_list))


def multi_site_scan(url_file_name):
    file = open(url_file_name,"r")
    for line in file:
        url = line.strip()
        print(url+" - - - - - - - - -")
        url_list = find_urls(url)
        hits = check_from_word_list([("recurve",2),("recurve-limbs",10),("limb",5),("bow",5)],url_list)
        print(heapq.heappop(hits))
        #print(hits)
    file.close()

def check_from_word_list(word_list,in_list):
    return_list = list()
    for item in in_list:
        count = 0
        for word,value in word_list:
            if word in item:
                count+=value

        if count != 0:
            heapq.heappush(return_list,(-count,item))
    return return_list

def find_target_page(current_url,key_word,word_list,max_redirects,start_time,redirects=0):

    print(str(time.time()-start_time)," - - ",redirects)

    if redirects >=max_redirects or time.time()-start_time>=2:
        return
    
    if key_word in current_url:
        return current_url
    else: 
        url_list = find_urls(current_url)
        hits = check_from_word_list(word_list,url_list)
        value,next_url = heapq.heappop(hits)
        print(next_url)
        if key_word in next_url:
            time.sleep(random.random()*0.1)
            return find_target_page(next_url,key_word,word_list,max_redirects,start_time,redirects+1)
        
def find_next_page(url):
    session = requests.session()
    page = session.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    url_list = find_urls(url)
    
    next_pages = check_from_word_list([("next",5),("next-page",20),("page",3),("scroll",3),("?p=",3),("?P=",3)],url_list)
    

    if len(next_pages)>0:
        for i in range(len(next_pages)-1,0,-1):
            next_page = next_pages[i]
            if ("http" in next_page[1] and url not in next_page[1]):
                next_pages.remove(next_page)

    return next_pages


def find_price(url):
    
    session = requests.session()
    page = session.get(url)
    soup = BeautifulSoup(page.text,"html.parser")

    price = soup.find(class_=re.compile("price"))

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

def find_options(url):
    #finds options on page
    #TODO improve
    #Current system only works for 4 websites, needs to be expanded
    session = requests.session()
    page = session.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    options = list()
    options_cluttered = list()
    successful = list()

    current_length = 0

    wordlist = ["product-content","product-form","select","form-control"]
    blacklist = ["cart","buy","basket","notify","country","Country","address","Notify","notify"] 

    for phrase in wordlist:
        options_cluttered += soup.find_all(class_=re.compile(phrase))
        
        if len(options_cluttered) != current_length:
            successful.append(phrase)
            
            for i in range(len(options_cluttered)-1, -1, -1):
                option = options_cluttered[i]
                if any(word in option.text for word in blacklist):
                    del options_cluttered[i]
            current_length = len(options_cluttered)
            
    for phrase in successful:
        print(phrase)
        options+= get_option_text(phrase,options_cluttered)

    return options

def get_option_text(phrase,tag_list):
    new_list = list()
    if (phrase == "product-content"):
        for tag in tag_list:
            new_list += tag.find_all(class_="product-item-name")
            

    elif (phrase == "product-form"):
        for tag in tag_list:
            temp = len(new_list)
            new_list += tag.find_all("label")
            if(len(new_list)>temp):
                print(tag.text)

    elif (phrase == "form-control" or phrase == "select"):
        for tag in tag_list:
            new_list += tag.find_all("option")

    print(new_list)
    if(new_list!= []):
        for i in range (0,len(new_list)):
            new_list[i] = new_list[i].find(string=True, recursive=False).strip()

    return new_list
        
