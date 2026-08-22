from bs4 import BeautifulSoup
import requests
import csv
import sitemap
import pages
import robots
import re

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

"www.merlinarchery.co.uk/mybo-star-wood-core-recurve-limbs.html"
words   = "Mybo Star Wood Core Recurve Limbs".lower().split(" ")
pattern = re.compile('|'.join(re.escape(w) for w in words))
matches = list(set(re.findall(pattern,"www.merlinarchery.co.uk/mybo-star-wood-core-recurve-limbs.html")))
print(matches)