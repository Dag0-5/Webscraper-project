from bs4 import BeautifulSoup
import requests
import csv
import heapq
import time 
import random

def page_scraper(url,wordlist):
    collection = list()
    for word in wordlist:
        try:
            page = requests.get(url+word+"/")
            soup = BeautifulSoup(page.text, "html.parser")
            page.raise_for_status()

            quotes = soup.find_all("span",attrs={"class":"text"})
            authors = soup.find_all("small",attrs={"class":"author"})
            collection.append((zip(quotes,authors),word))
            print(word)
        except ConnectionError:
            print("ConnectionError occurred")
            break
        except TimeoutError:
            print("TimeoutError occurred")
            break
        except requests.HTTPError:
            print("HTTP error occurred")
            break
        
    return collection


def export(file_name, collection):
    file = open(file_name,"w", encoding="utf-8")
    writer = csv.writer(file)
    writer.writerow(["QUOTE","AUTHOR","WORD"])
    for (references,word) in collection:
        for quote,author in references:
            print(quote.text+" - "+author.text+" - "+word)
            writer.writerow([quote.text,author.text,word])
    file.close()


def find_urls(url):
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # print(soup.prettify())
    url_list = list()
    for link in soup.find_all('a'):
        if(link.get("href")!= None):
            url_list.append(link.get("href"))
    return url_list


def multi_site_scan(url_file_name):
    file = open(url_file_name,"r")
    for line in file:
        url = line.strip()
        print(url+" - - - - - - - - -")
        url_list = find_urls(url)
        hits = hits_from_word_list([("recurve",2),("recurve-limbs",10),("limb",5),("bow",5)],url_list)
        print(heapq.heappop(hits))
        #print(hits)
    file.close()

def hits_from_word_list(word_list,url_list):
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
        hits = hits_from_word_list(word_list,url_list)
        value,next_url = heapq.heappop(hits)
        print(next_url)
        if key_word in next_url:
            time.sleep(random.random()*0.1)
            find_target_page(next_url,key_word,word_list,max_redirects,start_time,redirects+1)

"""
url = "https://quotes.toscrape.com/tag/"
collection = page_scraper(url,["love","inspirational","life","humor","books","reading","not a tag","friendship","friends","truth","simile"])
export("testdump.csv",collection)
"""

#print(find_urls("https://quotes.toscrape.com/"))

multi_site_scan("Archery URLs.txt")

#find_target_page("https://quotes.toscrape.com/","love",[("love",10)],2,time.time())
