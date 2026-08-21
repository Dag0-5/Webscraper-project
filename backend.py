import pages
import robots
import sitemap
from os import getcwd
import heapq
import time # debugging use 

# --------------- Search class ---------------

class Search():

    def __init__(self,item=None):
        self.crawl_delay = 10
        self.allow = list()
        self.disallow = list()
        self.wordlist = list()
        self.item = item

    def find_worlist(self,category):
        wordlist = list()
        path = getcwd()
        path = path + ("/wordlists/" + category + ".txt")
        path = path.replace("\\", "/")

        cluttered = file_reader(path)

        for line in cluttered:
            word,value = line.split(",")
            value = int(value)
            wordlist.append([word,value])

        return wordlist
    
    def search(self,category,item=None):
        results = list()
        self.wordlist = self.find_worlist(category)
        self.item = item
        sites = file_reader("wordlists/archery_urls.txt")
        
        for url in sites:
            robot = robots.find_robots(url)
            if(robot == None):
                result = self.no_sitemap_search(url)
            
            else:
                map = robots.find_sitemap(robot)
                self.crawl_delay = robots.find_crawl_delay(robot)
                self.allow,self.disallow = robots.find_allow_disallow_list(robot)

                if(map != None):
                    map = sitemap.Sitemap(map)
                    map.find_sitemaps()
                    result = self.sitemap_search(map)

                else:
                    result = self.no_sitemap_search(url)

            results.append([url,result])
            print(results)
            break

    def sitemap_search(self,map):
        #
        # Searches the sitemap for all possible matches
        # Orders them based on how many keywords are in url
        # Searches this based on if the item matches urls and titles 
        # Returns the best solution
        #
        #TODO implement crawl_delay, blacklist
        #TODO implement html error handling i.e. error 404
        url_list = map.find_urls()
        if url_list != []:
            possible_matches = check_from_word_list(self.wordlist,url_list,False,self.item)
            found,item = self.check_matches(possible_matches,True)
            
            if(found):
                return True,item

            else:
                if(possible_matches == []):
                    best_fit = (0,None)

                else:
                    best_fit = possible_matches[0]

                for child in map.children:
                    found,item = self.sitemap_search(child)

                    if(found):
                        return found,item

                    else:
                        if item[0] < best_fit[0]:
                            best_fit = item

                return False,best_fit 

        else:
            best_fit = (0,None)
            for child in map.children:
                found,item = self.sitemap_search(child)

                if(found):
                    return found,item

                else:
                    if item[0] < best_fit[0]:
                        best_fit = item

            return False,best_fit
    
    def no_sitemap_search(self,url):
        raise NotImplementedError

    def check_matches(self,possible_matches,sitemap_search):
        while (possible_matches != []):
            _,match = heapq.heappop(possible_matches)
            if(sitemap_search):
                link =  match[0]
                title = match[1].lower()
            else:
                link = match
                title = pages.find_title(link).lower()

            if self.item.lower() in link or self.item.lower() in title:
                price =  pages.find_price(link)
                if(not sitemap_search):
                    image = pages.find_image(link)
                else:
                    image = match[2]

                    if(image == None or price == None):
                        return True,None

                return True, (link,title,image,price)

        return False, None
    
def file_reader(path):
    content = list()
    file = open(path,"r")
    for line in file:
        content.append(line.strip())
    file.close()

    return content

def check_from_word_list(wordlist,search_list,single,high_value_phrase=None,position=0):
    return_list = list()

    if(high_value_phrase!=None):
        word =  high_value_phrase.lower().replace(" ","-")

        for item in search_list:
            if(single):
                if word in item:
                    return [(-1000,item)]
            else:
                if word in item[position]:
                    return [(-1000,item)]

    for item in search_list:
        count = 0
        for word,value in wordlist:
            if(single):
                temp = item.lower()
                if word in temp:
                    count+=value
            else:
                temp = item[position].lower()
                if word in temp:
                    count+= value

        if count != 0:
            if(count >= 1000):
                return [(-count,item)]
            heapq.heappush(return_list,(-count,item))
    return return_list

start = time.time()
test = Search()
test.search("recurve_limbs","Kap Challenger Carbon Recurve Limbs")
end = time.time()

print("Time take = ", end-start)