import pages
import robots
import sitemap
from os import getcwd

def noRobots(url):
    raise NotImplementedError

def hasSitemap(url,map):
    raise NotImplementedError

def noSitemap(url):
    raise NotImplementedError

def find_worlist(category):
    path = getcwd()
    path = path + ("/wordlists/" + category + ".txt")
    path = path.replace("\\", "/")

    return file_reader(path)
    
def search(category,item=None):
    wordlist = find_worlist(category)
    sites = find_worlist("archery_urls")
    for url in sites:
        robot = robots.find_robots(url)
        if(robot == None):
            noRobots(url)
        
        else:
            map = robots.find_sitemap(robot)

            if(map != None):
                hasSitemap(url,map)

            else:
                noSitemap(url)

def file_reader(path):
    content = list()
    file = open(path,"r")
    for line in file:
        content.append(line.strip())

    return content

print(find_worlist("recurve_limbs"))