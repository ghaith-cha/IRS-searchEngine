import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from rdflib import Graph, RDF
from rdflib.namespace import SKOS
import csv 

class indexer:


    def __init__(self):
        self.hashed_docs = dict()
        self.docs = dict()
        self.Stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.graph = Graph()
        self.dic = dict()
        self.tfdp = list()
        self.idfdp = list()


    def get_stem(self, word):
        return self.stemmer.stem(word)


    def build(self, NumberofDocuments):
        for i in range(1, NumberofDocuments):
            try:
                content = open("data/"+str(i)+".txt", "r", encoding="utf-8").readlines()
            except Exception as e:
                e.args
                continue
            is_url = 0
            for x in content:
                if is_url is 0:
                    self.hashed_docs.update({i:x})
                    self.docs.update({x:i})
                    is_url = 1
                else:
                    word_tokens = word_tokenize(x)
                    filtered = [w for w  in word_tokens if not w in self.Stop_words]
                    for w in filtered:
                        word = self.get_stem(w)
                        if word in self.dic:
                            ls = set(self.dic.get(word))
                            ls.add(i)
                            self.dic.update({word:ls})
                        else:
                            temp = set()
                            temp.add(i)
                            self.dic.update({word:temp})


    def Loadinde(self):
        self.graph.parse("data\\ontology.nt", format='nt')
        self.dic = np.load("data\\dic.npy",allow_pickle='TRUE').item()
        self.hashed_docs = np.load("data\\hasheddic.npy",allow_pickle='TRUE').item()
        self.docs = np.load("data\\docs.npy",allow_pickle='TRUE').item()
    

    def savedics(self):
        np.save("data\\dic.npy",self.dic)
        np.save("data\\hasheddic.npy",self.hashed_docs)
        np.save("data\\docs.npy",self.docs)


    def FindKthN(self,stri):
        ret = set()
        for person in self.graph.subjects(RDF.type,SKOS.information):
            for mbox in self.graph.objects(person, SKOS.sameas):
                if stri in mbox :
                    for mbox2 in self.graph.objects(person, SKOS.knows):
                        ret.add(mbox2)
        return ret


    def med(self,x , y):
        res = np.zeros((len(x), len(y)))
        for i in range(len(x)):
            res[i, 0] = i
        for j in range(len(y)):
            res[0 , j] = j
        for i in range(1, len(x)):
            for j in range(1, len(y)):
                c1= res[i, j-1] + 1
                c2= res[i-1, j] + 1
                if(x[i-1] == y[j-1]):
                    c3= res[i-1, j-1]
                else:
                    c3= res[i-1, j-1]+ 2
                res[i, j]= min(c1, c2, c3)
        return res[len(x)-1][len(y)-1]


    def findKey(self , word):
        steammedWord = self.get_stem(word)
        if(not steammedWord in self.dic.keys()):
            sim = set()
            for i in range(0,3):
                for key in self.dic.keys() :
                    if len(key)+i==len(word):
                        sim.add(key)
                    if len(key)-i==len(word):
                        sim.add(key)
            minimum = 1000000
            TheStr=""
            for x in sim:
                temp =self.med(steammedWord,x) 
                if(temp < minimum):
                    minimum = temp
                    TheStr = x
            return TheStr
        res = self.FindKthN(steammedWord)
        ret = self.dic.get(steammedWord)
        for x in res :
            temp = "https://en.wikipedia.org/"+x
            ret.add(self.docs.get(temp))
        return ret


    def makeURL(self, si):
        ret = set()
        for i in si:
            ret.add(self.hashed_docs.get(i))
        return ret


    def findWord(self, stri):
        ret = set()
        word = stri
        word_tokens = word_tokenize(stri)
        filtered = [w for w in word_tokens if not w in self.Stop_words]
        for x in filtered :
            temp = self.findKey(x)
            if(type(temp) is str):
                print(x)
                word = word.replace(x,temp)
                continue
            if(len(ret) == 0):
                ret = temp
            else :
                ret.union(temp)
        if(word is stri):
            return self.makeURL(ret)
        else:
            temp = dict()
            temp.update({word:self.makeURL(ret)})
            return temp



    def ORWord(self ,stri):
        ret = set()
        word_tokens = word_tokenize(stri)
        filtered = [w for w in word_tokens if not w in self.Stop_words]
        for x in filtered :
            ret.intersection(self.findKey(x))
        return self.makeURL(ret)


    def NotWord(self,stri):
        ret = set()
        temp = set()
        word_tokens = word_tokenize(stri)
        filtered = [w for w in word_tokens if not w in self.Stop_words]
        for x in filtered :
            temp.intersection(self.findKey(x))
        for x in self.hashed_docs.keys():
            if x in temp :
                continue
            else :
                ret.add(x)
        return self.makeURL(ret)

    def compute_tf(self,t , doc):
        counter = 0
        content = open("data\\"+str(doc)+".txt","r", encoding="utf-8").readlines()    
        counter = 0
        n = 0
        flag = 0
        for x in content:
            if flag != 0:
                flag = 1
                continue
            word_tokens = word_tokenize(x)
            for w in word_tokens:
                if self.get_stem(w) == t:
                    counter = counter+1
                n = n+1
        return counter/n


    def compute_idf(self, t):
        counter = 0
        for i in range(1, 21):
            try:
                content = open("data/"+str(i)+".txt", "r", encoding="utf-8").readlines()
            except Exception as e:
                e.args
                continue
            is_url = 0
            for x in content:
                if is_url is 0:
                    is_url = 1
                else:
                    word_tokens = word_tokenize(x)
                    filtered = [w for w  in word_tokens if not w in self.Stop_words]
                    for w in filtered:
                        word = self.get_stem(w)
                        if word == self.get_stem(t):
                            counter=counter+1
                            break
        return np.log2(len(self.dic.keys())/(counter+1))
        
        
    def tfidf(self):
        for x in self.dic.keys():
            te = list()
            te.append(x)
            idf = self.compute_idf(x)
            for temp in range(1,21):
                tf = self.compute_tf(x,temp)
                te.append(tf*idf)
            self.Writer("data\\tfidf.csv",te)
    
    #https://en.wikipedia.org/wiki/Stackless_Python
    def buildURLdic(self):
        urldic = dict()
        for x in self.docs.keys():
            temp = x[30:len(x)]
            temp2 = []
            temp3 = ""
            for i in temp:
                if(i == '(' or i == ')' or i == '\n'):
                    continue
                if(i=='_' or i == '-'):
                    temp2.append(temp3)
                    temp3 = ""
                else:
                    temp3+=i
            temp2.append(temp3)
            for i in temp2 :
                if i in urldic :
                    ls = set(urldic.get(i))
                    ls.add(self.docs.get(x))
                    urldic.update({i:ls})
                else:
                    ls = set()
                    ls.add(self.docs.get(x))
                    urldic.update({i:ls})
        print(urldic)

    def Writer(self,name,data):
        with open(name,'a',encoding="utf-8" , newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(data)
