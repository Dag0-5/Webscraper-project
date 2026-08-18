from bs4 import BeautifulSoup
import requests
import csv
import sitemap
import pages
import robots

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
"""temp = sitemap.find_sitemaps("https://merlinarchery.co.uk/sitemaps/sitemap.xml")

for t in temp:
    info = sitemap.find_urls(t)
    url,title,image = info[0]
    print(len(info))
    print(url+"-[]-"+title+"-[]-"+image)
"""

#print(pages.find_price("https://www.merlinarchery.co.uk/mybo-star-wood-core-recurve-limbs.html"))

#sitemap.find_images("https://www.merlinarchery.co.uk/sitemap-1-1.xml")

"""
info = sitemap.find_urls("https://www.merlinarchery.co.uk/sitemap-1-1.xml")
url,title,image = info[0]
print(len(info))
#print(url+"-[]-"+title+"-[]-"+image)

urls = list()
for url,_,_ in info:
    urls.append(url)

hits = pages.check_from_word_list([("recurve",2),("recurve-limbs",10),("limb",5),("bow",5)],urls)
print(len(hits))
"""

#print(pages.find_next_page("https://www.quicksarchery.co.uk/bows/recurve-target-bows/"),"<>")
pages.find_options("https://walesarchery.com/collections/recurve-risers/products/hoyt-gmx3-grand-prix-riser")

