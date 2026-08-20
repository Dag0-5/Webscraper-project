import pages
import robots
import sitemap

def noRobots(url):
    raise NotImplementedError

def hasSitemap(url,map):
    raise NotImplementedError

def noSitemap(url):
    raise NotImplementedError

def find_worlist(category):
    raise NotImplementedError

def search(category,item=None):
    file = open("Archery URLS.txt","r")
    for line in file:
        url = line.strip()
        robot = robots.find_robots(url)
        if(robot == None):
            noRobots(url)
        
        else:
            map = robots.find_sitemap(robot)

            if(map != None):
                hasSitemap(url,map)

            else:
                noSitemap(url)