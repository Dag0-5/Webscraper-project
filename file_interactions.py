from os import getcwd
import heapq
# functions used for file interactions

def find_wordlist(category,values=True):
        wordlist = list()
        path = ("/wordlists/" + category + ".txt")

        cluttered = file_reader(path)
        if(values):
            for line in cluttered:
                word,value = line.split(",")
                value = int(value)
                wordlist.append([word,value])
        else:
            wordlist = cluttered
            
        return wordlist


def file_reader(path):
    path = getcwd() + path
    path = path.replace("\\", "/")
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