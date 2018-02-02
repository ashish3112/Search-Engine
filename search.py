import time
import sys
from stemming.porter import stem
import re
import stopword
import operator
import math
def process_query(queryt,dictionaryword,dictionarytitleq,dictionaryc):
    querydt=queryt.split(',')
    querytt=None
    query=None
    queryc=None
    for i in querydt:
        if 'T:' in i:
            querytt=i.split(':')
            querytt=querytt[1]
        elif 'B:' in i:
            query=i.split(':')
            query=query[1]
        elif 'C:' in i:
            queryc=i.split(':')
            queryc=queryc[1]
        else:
            query=i
            querytt=i
    if query is not None:
        queryterms=re.split("[^a-zA-Z]+",query)
        for word in queryterms:
            word=word.lower()
            if word not in stopword.stopword:
                word=stem(word)
                if word not in dictionaryword:
                    dictionaryword[word]=1
                else:
                    dictionaryword[word]+=1
    if querytt is not None:
        queryterms=re.split("[^a-zA-Z]+",querytt)
        for word in queryterms:
            word=word.lower()
            if word not in stopword.stopword:
                word=stem(word)
                if word not in dictionarytitleq:
                    dictionarytitleq[word]=1
                else:
                    dictionarytitleq[word]+=1
    if queryc is not None:
        queryterms=re.split("[^a-zA-Z]+",queryc)
        for word in queryterms:
            word=word.lower()
            if word not in stopword.stopword:
                word=stem(word)
                if word not in dictionarytitleq:
                    dictionaryc[word]=1
                else:
                    dictionaryc[word]+=1
def getoffset(dictionary):
    offset=open("offset.txt",'r+')
    #global offset
    #offs=offset.read()
    for line in offset:
        tmp=line.split(' ')
        dictionary[tmp[0]]=int(tmp[1])
    offset.close()
def getlengths(dictionarylength):
    lengthfile=open("lengthfile.txt",'r+')
    for line in lengthfile:
        tmp=line.split(' ')
        dictionarylength[tmp[0]]=int(tmp[1])
    lengthfile.close()
def gettitle(dictionarytitle):
    titlefile=open("titlefile.txt",'r+')
    for line in titlefile:
        tmp=line.split(':')
        dictionarytitle[tmp[0]]=tmp[1]
    titlefile.close()
def gettitleposting(dictionarytindex):
    tindex=open("tindex.txt",'r+')
    for line in tindex:
        tmp=line.split(' ')
        dictionarytindex[tmp[0]]=tmp[1]
    tindex.close()
def getcategory(dictionarycindex):
    cindex=open("cindex.txt",'r+')
    for line in cindex:
        tmp=line.split(' ')
        dictionarycindex[tmp[0]]=tmp[1]
    cindex.close()
def search(index,dictionarytitle,dictionarylength,dictionaryword,dictionarytindex,dictionarytitleq,dictionaryc,dictionarycindex,dictionary):
    scores={}
    for queryterms in dictionaryword:
        if queryterms in dictionary:
            toff=dictionary[queryterms]
            index.seek(int(toff),0)
            docs=index.readline()
            docs=docs.rstrip()
            doclist=docs.split(' ')
            doclist=doclist[1]
            doclist=doclist.split(':')
            #print len(dictionarylength)
            idf=math.log10(len(dictionarylength)/(len(doclist)+1.0))
            tf=1+math.log10(int(dictionaryword[queryterms]))
            wtq=idf*tf
            for doc in doclist:
                #print doc
                if doc!='':
                    tmp=doc.split('b')
                    if tmp[0] not in scores:
                        scores[tmp[0]]=float(tmp[1])*wtq
                    else:
                        scores[tmp[0]]+=(float(tmp[1])*wtq)
        # Coming Title have lot of value
    for queryterms in dictionarytitleq:
        if queryterms in dictionarytindex:
            docs=dictionarytindex[queryterms]
            docs=docs.rstrip()
            doclist=docs.split(':')
            for doc in doclist:
                if doc!='':
                    tmp=doc.split('t')
                    if tmp[0] not in scores:
                        scores[tmp[0]]=3.0
                    else:
                        scores[tmp[0]]+=3.0
    for queryterms in dictionaryc:
        if queryterms in dictionarycindex:
            docs=dictionarycindex[queryterms]
            docs=docs.rstrip()
            doclist=docs.split(':')
            for doc in doclist:
                if doc!='':
                    tmp=doc.split('c')
                    if tmp[0] not in scores:
                        scores[tmp[0]]=3.0
                    else:
                        scores[tmp[0]]+=3.0
            #for key in scores:
            #    scores[key]=(scores[key]/dictionarylength[key])
    cou=0
    for key in sorted(scores,key=scores.get,reverse=True):
        print key,scores[key],
        if key in dictionarytitle:
            tmp=dictionarytitle[key].replace(' ','_')
            print "https://en.wikipedia.org/wiki/"+tmp
        else:
            print "No proper name"
        cou+=1
        if cou==10:
            break
def main():
    if(len(sys.argv)!=2):
        print "Invalid format"
        exit()
    dictionary={}
    dictionaryword={}
    dictionarytitleq={}
    dictionarylength={}
    dictionarytitle={}
    dictionarytindex={}
    dictionaryc={}
    dictionarycindex={}
    index=open("output.txt",'r+')
    query=sys.argv[1]
    getoffset(dictionary)
    getlengths(dictionarylength)
    gettitle(dictionarytitle)
    gettitleposting(dictionarytindex)
    getcategory(dictionarycindex)
    process_query(query,dictionaryword,dictionarytitleq,dictionaryc)
    doclist=search(index,dictionarytitle,dictionarylength,dictionaryword,dictionarytindex,dictionarytitleq,dictionaryc,dictionarycindex,dictionary)
main()
