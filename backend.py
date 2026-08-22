import pages
import robots
import sitemap
import heapq
import time 
import re
from file_interactions import find_wordlist,check_from_word_list
# --------------- Search class ---------------

class Search():

    def __init__(self,item=None):
        self.crawl_delay = 0.01
        self.allow = list()
        self.disallow = list()
        self.wordlist = list()
        self.item = item

    
    def search(self,category,sites,item=None):

        results       = list()
        self.wordlist = find_wordlist(category)
        self.item     = item
        
        for url in sites:

            #TODO remove
            #Use for testing
            #url = "https://www.quicksarchery.co.uk/"
            #
            #TODO remove  
            robot = robots.find_robots(url)
            

            if(robot == None):

                page = pages.Page(url)
                page.find_soup()
                result = self.no_sitemap_search(page)
            
            else:

                map                      = robots.find_sitemap(robot)
                self.crawl_delay         = robots.find_crawl_delay(robot)/1000
                self.allow,self.disallow = robots.find_allow_disallow_list(robot)

                if(map != None):
                    map    = sitemap.Sitemap(map)
                    map.find_sitemaps()
                    result = self.sitemap_search(map)

                else:

                    page = pages.Page(url)
                    page.find_soup()
                    result = self.no_sitemap_search(page)

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
        #TODO implement html error handling i.e. error 404
        
        time.sleep(self.crawl_delay)
        url_list = map.find_urls()
        url_list = self.remove_disallowed(url_list)

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

    
    def no_sitemap_search(self,page):

        if(page.soup == None):

            page.find_soup()

        print(page)

        time.sleep(self.crawl_delay)
        children = list()

        page.find_urls()
        next_pages = page.find_next_pages()

        for next_page in next_pages:

            page.url_list.append(next_page)

        return page.url_list
    
        if(page.url_list != None):

            page.url_list         = self.remove_disallowed(page.url_list)    
            possible_matches = check_from_word_list(self.wordlist,page.url_list,True,self.item)

            for match in possible_matches:
                
                children.append(pages.Page(match[1],page))

            page.children = children

            found,item    = self.check_matches(page.children,False)

            if(found):

                return True,item

            else:

                if(possible_matches == []):

                    best_fit = (0,None)

                else:

                    best_fit = possible_matches[0]

                for child in page.children:

                    found,item = self.no_sitemap_search(child)

                    if(found):
                        return found,item

                    else:
                        if item[0] < best_fit[0]:
                            best_fit = item

                return False,best_fit 


    def check_matches(self,possible_matches,sitemap_search):
        
        while (possible_matches != []):
            
            _,match = heapq.heappop(possible_matches)

            if(sitemap_search):

                link  = match[0]
                title = match[1].lower()

            else:
                
                link  = match.url
                title = match.find_title()

            if self.item.lower() in link or self.item.lower() in title:

                if(sitemap_search):

                    page  = pages.Page(link)
                    page.find_soup()
                    price = page.find_price()
                    image = match[2]

                else:

                    match.find_soup()
                    image = match.find_image()
                    price = match.find_price()

                    if(image == None or price == None):
                        return True,None

                return True, (link,title,image,price)

        return False, None

    def remove_disallowed(self,url_list,single=False):

        disallowed_pattern = re.compile('|'.join(re.escape(w) for w in self.disallow))

        for url in url_list:

            if(not single):

                link = url[0]

            else:

                link = url

            if re.search(disallowed_pattern,link) != None:

                url_list.remove(url)

        return url_list


start = time.time()
test = Search()
test.search("recurve_limbs",find_wordlist("archery_urls",False),"Mybo Star Wood Core Recurve Limbs")
end = time.time()

print("Time take = ", end-start)