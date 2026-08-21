import requests

def find_sitemap(robots):
    for line in robots.splitlines():
        if "Sitemap" in line:
            return line[line.find("https"):]
    return None

def find_robots(url):
    try:
        session = requests.session()
        page = session.get(url+"/robots.txt")
        
        return page.text
    except:
        return None

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

    return allow,disallow

def find_crawl_delay(robots):
    delay = 10
    agent_found = False
    for line in robots.splitlines():
        if ("User-agent" in line and "*" in line):
            agent_found = True

        if("Crawl-Delay" in line and agent_found):
            delay  = line[line.find["[":(len(line)-1)]]
            
            return delay
    return delay