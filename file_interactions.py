from os import getcwd
import heapq
import re
# functions used for file interactions

def find_wordlist(category):
        
    wordlist  = list()
    path      = ("/wordlists/" + category + ".txt")
    wordlist = file_reader(path)    
    return wordlist


def file_reader(path):

    path    = getcwd() + path
    path    = path.replace("\\", "/")
    content = list()
    file    = open(path,"r")

    for line in file:

        content.append(line.strip())

    file.close()
    return content


def check_from_word_list(wordlist,search_list,single,high_value_phrase=None,position=0):

    return_list = list()

    if(high_value_phrase!=None):

        words   = high_value_phrase.lower().split(" ")
        words.sort()
        pattern = re.compile('|'.join(re.escape(w) for w in words))

        for item in list(search_list):
            
            if(single):

                comparison = item

            else:

                comparison = item[position]

        
            matches = list(set(re.findall(pattern,comparison)))
            matches.sort()

            if (len(matches)==len(words)):

                return [(-1000,item)]

            else:

                if(len(matches)>0):

                    value = -1000*(len(matches)/len(words))
                    heapq.heappush(return_list,(value,item))
                    search_list.remove(item)    
                    [].remove
    
    pattern = re.compile('|'.join(re.escape(w) for w in wordlist))

    for item in search_list:

        value = 0

        if(single):
    
            temp = item.lower()

        else:

          temp = item[position].lower()


        matches = list(set(re.findall(pattern,temp)))
        matches.sort()

        if(len(matches)>0):
            
            value = -100*(len(matches)/len(wordlist))
            heapq.heappush(return_list,(value,item))

    return return_list