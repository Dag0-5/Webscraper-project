import pages
import robots
import sitemap
import heapq
import time # debugging use 
from file_interactions import find_wordlist,check_from_word_list
# --------------- Search class ---------------

class Search():

    def __init__(self,item=None):
        self.crawl_delay = 10
        self.allow = list()
        self.disallow = list()
        self.wordlist = list()
        self.item = item

    
    def search(self,category,sites,item=None):
        results = list()
        self.wordlist = find_wordlist(category)
        self.item = item
        
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
            break # TODO remove after testing


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

            page = pages.Page(link)
            page.find_soup()

            if self.item.lower() in link or self.item.lower() in title:
                price =  page.find_price()
                if(not sitemap_search):
                    image = page.find_image()
                else:
                    image = match[2]

                    if(image == None or price == None):
                        return True,None

                return True, (link,title,image,price)

        return False, None


start = time.time()
test = Search()
test.search("recurve_limbs",find_wordlist("archery_urls",False),"Kap Challenger Carbon Recurve Limbs")
end = time.time()

print("Time take = ", end-start)