import requests
import re
import networkx as nx
from pyquery import PyQuery as pq
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import SKOS
from nltk.tokenize import word_tokenize
import csv

class crawler:


    def __init__(self):
        self.to_visit = list()
        self.visited = set()
        self.counter = 0
        self.g = Graph()
        self.pag = nx.Graph()

    def fetch(self, url):
        print('now fetching.. ' , url)
        try:
            return requests.get(url).content
        except Exception as e:
            e.args
            return 0


    def get_current_url(self):
            res = self.to_visit.pop(0)
            while res in self.visited:
                res = self.to_visit.pop(0)
            return res


    def get_links(self, current_url, content, now ):
        p = pq(content)
        info = URIRef(current_url)
        self.g.add( (info , RDF.type, SKOS.information))
        self.g.add( [info , SKOS.sameas , Literal(now)] )
        word_tokens = word_tokenize(now)
        filtered = [w for w in word_tokens if not w in [']','[',')','(','_','+'] ]
        ls = []
        for w in filtered :
            tempo = w
            if '_' == w[len(w)-1] : 
                tempo = w[0:len(w)-1]
            ls.append(tempo)
        temp = []
        for w in ls :
            if '_' in w:
                temp.append(w.replace("_"," "))
        for w in filtered:
            self.g.add( [info , SKOS.sameas , Literal(w)] )
        for w in ls :
            self.g.add( [info , SKOS.sameas , Literal(w)] )
        for w in temp :
            self.g.add( [info , SKOS.sameas , Literal(w)] )
        t =  p("div#mw-content-text")
        self.counter+=1
        out = open("data\\"+str(self.counter)+".txt","w", encoding="utf-8")
        out.write(current_url+'\n')
        out.write(t.text())
        out.close()
        urls = re.findall('<a href="([^"]+)" title="([^"]+)">', str(t))
        url = [temp[0] for temp in urls]
        for temp in url:
            if temp[0] == '/':
                self.g.add( [info , SKOS.knows , Literal(temp[6:])] )
                temp = "https://en.wikipedia.org/"+ temp[1:]
            pattern = re.compile('https?')
            if pattern.match(temp):
                    self.to_visit.append(temp)
                    self.pag.add_edge(current_url,temp)


    def  crawl(self, url, depth=20):
        self.to_visit.append(url)
        while len(self.visited) <= depth:
            current_url = self.get_current_url()
            content = self.fetch(current_url)
            if content == 0 :
                continue
            self.visited.add(current_url)
            now = current_url.replace("https://en.wikipedia.org/wiki/","")
            self.get_links(current_url, content,now)
    

    def doneFromCrawling(self):
        self.g.serialize(destination='data\\ontology.nt', format='nt')
        temp = nx.pagerank(self.pag)
        with open("data//PageRank.csv",'w',encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            for x ,t1 in temp.items():
                ls = list()
                ls.append(x)
                ls.append(t1)
                csv_writer.writerow(ls)
        

c = crawler()
c.crawl('https://en.wikipedia.org/wiki/Python_(programming_language)')
c.doneFromCrawling()
