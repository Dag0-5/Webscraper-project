from os import getcwd
import heapq
import re
# functions used for file interactions

def find_wordlist(category,values=True):
        
        wordlist  = list()
        path      = ("/wordlists/" + category + ".txt")
        cluttered = file_reader(path)

        if(values):

            for line in cluttered:

                word,value = line.split(",")
                value      = int(value)
                wordlist.append([word,value])

        else:

            wordlist = cluttered
            
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

        for item in search_list:

            if(single):

                comparison = item

            else:

                comparison = item[position]

        
            matches = list(set(re.findall(pattern,comparison)))
            matches.sort()
            
            if (matches == words):

                return [(-1000,item)]

            else:

                if(len(matches)>0):

                    return_list.append((-1000/len(matches),item))
                    search_list.remove(item)    

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