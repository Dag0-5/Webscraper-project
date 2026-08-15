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

def check_from_word_list(word_list,url_list):
    return_list = list()
    for url in url_list:
        count = 0
        for word,value in word_list:
            if word in url:
                count+=value

        if count != 0:
            heapq.heappush(return_list,(-count,url))
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
    print("Good")
    next_pages = check_from_word_list([("next",5),("next-page",20),("page",3),("scroll",3),("?p=",3),("?P=",3)],url_list)
    print("better")
    print(next_pages)

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
    
    non_digit =re.findall("\D", temp[start+1:])

    
    if(non_digit != [] and non_digit != ["."]):
        for char in non_digit:
            if char != ".":
                print(char+"!!!")
                break
        end = temp[start:].find(char)
        price = temp[start:start+end]
    
    return price