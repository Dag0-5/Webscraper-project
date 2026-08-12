from bs4 import BeautifulSoup
import requests
import csv
import heapq
import time 
import random
import usp
import sitemap

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
        hits = hits_from_word_list([("recurve",2),("recurve-limbs",10),("limb",5),("bow",5)],url_list)
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


def get_next_page_query_type(url):
    session = requests.session()
    page = session.get(url)
    print(page.history)#check
    soup = BeautifulSoup(page.text, "html.parser")
    
    print(original_hash)
    types = ["?page=","?p="]

    for type in types:

        new_url = url+type+"2"
        print(new_url)
        page = session.get(new_url)
        print(page.history)#check
        page = BeautifulSoup(page.text,"html.parser")
        new_page_hash = page_hash(page)
        print(new_page_hash)

        if(new_page_hash != original_hash):
            #return type
            print("")

    raise NotImplementedError
        
def find_next_page(url):
    session = requests.session()
    page = session.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    url_list = find_urls(url)
    next_pages = check_from_word_list([("next",5),("next-page",20),("page",3),("scroll",3)],url_list)
    if len(next_pages)>0:
        for next_page in next_pages:
            if url not in next_page:
                next_pages.remove(next_page)
        
    print(next_pages)

def find_robots(url):
    session = requests.session()
    page = session.get(url+"/robots.txt")
    #print(page.text)
    return page.text

def find_allow_disallow_list(robots):
    disallow = list()
    allow = list()
    agent_found = False
    for line in robots.splitlines():
        if("User-agent" in line):
            if "*" in line:
                agent_found = True
            else:
                agent_found = False
                
        if "Allow" in line and agent_found:
            allow.append(line[line.find("/"):])

        if "Disallow" in line and agent_found:
            disallow.append(line[line.find("/"):])

    print(allow)
    print(disallow)

    return (allow,disallow)


"""
url = "https://quotes.toscrape.com/tag/"
collection = page_scraper(url,["love","inspirational","life","humor","books","reading","not a tag","friendship","friends","truth","simile"])
export("testdump.csv",collection)
"""

#print(find_urls("https://walesarchery.com"))

#multi_site_scan("Archery URLs.txt")

#find_target_page("https://quotes.toscrape.com/","love",[("love",10)],2,time.time())

#print(find_next_page("https://www.quicksarchery.co.uk/bows/recurve-target-bows/"))

#find_allow_list(find_robots("https://www.altservices.co.uk/"))

#print(sitemap.find_sitemap_in_robots(find_robots("https://www.merlinarchery.co.uk/")))
#sitemap.find_urls("https://merlinarchery.co.uk/sitemaps/sitemap.xml")
temp = sitemap.find_sitemaps("https://merlinarchery.co.uk/sitemaps/sitemap.xml")

for t in temp:
    print(sitemap.find_urls(t))
    break