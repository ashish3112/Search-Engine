import os,time,csv
import math
import codecs
import re
import xml.etree.ElementTree as etree
import sys
import stopword
import operator
from stemming.porter import stem
import threading
reload(sys)
sys.setdefaultencoding('utf-8')

if len(sys.argv)!=3:
    print "Incorrect argument format"
    exit()
PATH_WIKI_XML = "./"
FILENAME_WIKI = sys.argv[1]
FILENAME_ARTICLES = 'articles.csv'
FILENAME_REDIRECT = 'articles_redirect.csv'
FILENAME_TEMPLATE = 'articles_template.csv'
FILENAME_TEXT = "text.csv"
ENCODING = "utf-8"


# Nicely formatted time string.
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

# Used to strip the namespace from the tags.
def strip_tag_name(t):
    t = elem.tag
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)

totalCount = 0
totaldocs = 0
offset=0
articleCount = 0
redirectCount = 0
templateCount = 0
numofdoc = 1000
chunknum=0;
title = None
start_time = time.time()
invid={}
invit={}
invic={}
lengthfile=open("lengthfile.txt",'w+')
titilefile=open("titlefile.txt",'w+')
class writeParallel(threading.Thread):
    def __init__(self,filep,dictionaryw):
        threading.Thread.__init__(self)
        self.filep=filep
        self.dictionaryw=dictionaryw
    def run(self):
        for key in sorted(self.dictionaryw):
            self.filep.write(key+' '+self.dictionaryw[key]+'\n')
        self.filep.close()
# For merging
def merge():
	global offset
	global chunknum
	global numofdoc
	outtxt= open("output.txt",'w+')
	offtxt= open("offset.txt",'w+')
	files = [open("./chunk_"+str(i)) for i in range(chunknum)]
	com_read=[0 for i in range(chunknum)]
	lines = [j.readline() for j in files]
	print lines
	while 1:
		words=[]
		postings=[]
		for i in range(len(lines)):
			if com_read[i]==0:
		#print lines[i]+'*'
				tmp=lines[i].split(' ')
		#print tmp
				tmp1=tmp[0]
				tmp2=tmp[1]
				words.append(tmp1)
				postings.append(tmp2.rstrip())
			else:
				words.append('~')
				postings.append('~')
	#print words
		mini=min(words)
		ind=[]
		for i in range(len(words)):
			if words[i]==mini and com_read[i]==0:
				ind.append(i)
		#print ind
		to_write=mini+' '
		to_write1=''
		for i in ind:
			to_write1+=postings[i]
			line=files[i].readline()
			if not line:
				lines[i]="~"
				com_read[i]=1
			else:
				lines[i]=line
		tmp=to_write1.split(':')
		idf = math.log10(totaldocs/len(tmp))
		for i in tmp:
			if i!='':
				tmp1=i.split('b')
				tf=1+math.log10(int(tmp1[1]))
				wt=tf*idf
				to_write=to_write+':'+tmp1[0]+'b'+str('%.2f' %wt)
		#print com_read
		#print to_write
		offtet=mini+' '+str(offset)
		offset+=(len(to_write)+1)
		offtxt.write(offtet+'\n')
		outtxt.write(to_write+'\n');
		flag=0
		for i in range(chunknum):
			if com_read[i]==0:
				flag=1
		if flag==0:
			#pass
			break
	outtxt.close()
	offtxt.close()
	#print ind
for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
    tname = strip_tag_name(elem.tag)

    if event == 'start':
        if tname == 'page':
            title = ''
            hitext = ''
            rtitle = ''
            id = -1
            redirect = ''
            inrevision = False
            ns = 0
            l_hitext=[]
            dicw={}
        elif tname == 'revision':
            # Do not pick up on revision id's
            inrevision = True
        elif tname == 'redirect':
            dicw={}
            rtitle=elem.attrib;
            if rtitle is not None:
                l_hitext=re.split("[^a-zA-Z]+", rtitle['title'])
            for word in l_hitext:
                word=word.lower()
                if word not in stopword.stopword:
                    word=stem(word)
                    if word not in dicw:
                        dicw[word]=1
                    else:
                        dicw[word]+1
            for key in dicw:
                if key not in invit:
                    invit[key]=id+'t'+str(dicw[key])+':'
                else:
                    invit[key]=invit[key]+(id+'t'+str(dicw[key])+':')
            l_hitext=[]
            dicw={}
    else:
        if tname == 'title':
            title = elem.text
        elif tname == 'id' and not inrevision:
            id = elem.text
            #print 'Current ID in processing:',id
        elif tname == 'redirect':
        	pass
	elif tname == 'text':
            dicw={}
            hitext = elem.text
            lengthdoc=0;
            if hitext is not None:
                l_hitext = re.split("[^a-zA-Z]+", hitext)
                lengthdoc=len(l_hitext)
            lengthfile.write(str(id)+' '+str(lengthdoc)+'\n')
            for word in l_hitext:
                word=word.lower()
                if word not in stopword.stopword:
                    word=stem(word)
                    if word not in dicw:
                        dicw[word]=1
                    else:
                        dicw[word]+=1
            for key in dicw:
                if key not in invid:
                    invid[key]=id+'b'+str(dicw[key])+':'  #Using b to identify body
                else:
                    invid[key]=invid[key]+(id+'b'+str(dicw[key])+':')
            dicw={}
            hitext=elem.text
            hitext=str(hitext)
            c_hitext=re.findall('Category:[a-zA-Z ]+',hitext)
            l_hitext=[]
            for cat in c_hitext:
                #print cat
                temp=re.split('[: ]',cat)
                for tlit in temp:
                    if tlit!='Category':
                        l_hitext.append(tlit)
            #print l_hitext
            for word in l_hitext:
                word=word.lower()
                if word not in stopword.stopword:
                    word=stem(word)
                    if word not in dicw:
                        dicw[word]=1
                    else:
                        dicw[word]+=1
            for key in dicw:
                if key not in invic:
                    invic[key]=id+'c'+str(dicw[key])+':'
                else:
                    invic[key]=invic[key]+(id+'c'+str(dicw[key])+':')
        elif tname== 'page':
            totalCount+=1
            totaldocs+=1
            if title is not None:
                titilefile.write(id+':'+title+'\n')
            if totalCount==numofdoc:
                print totalCount
                totalCount=0
                tf=open("chunk_"+str(chunknum),'w+')
                chunknum+=1
                for key in sorted(invid):
                    tf.write(key+' '+invid[key]+'\n')
                tf.close()
                invid={}
            dicw={}
            l_hitext=[]
            rtitle=title
            if rtitle is not None:
                l_hitext=re.split("[^a-zA-Z]+",rtitle)
            for word in l_hitext:
                word=word.lower()
                if word not in stopword.stopword:
                    word=stem(word)
                    if word not in dicw:
                        dicw[word]=1
                    else:
                        dicw[word]+1
            for key in dicw:
                if key not in invit:
                    invit[key]=id+'t'+str(dicw[key])+':'
                else:
                    invit[key]=invit[key]+(id+'t'+str(dicw[key])+':')
            l_hitext=[]
            dicw={}
        elif tname == 'ns':
            ns = int(elem.text)
        elem.clear()
tf=open("chunk_"+str(chunknum),'w+')
chunknum+=1
for key in sorted(invid):
    tf.write(key+' '+invid[key]+'\n')
tf.close()
invid={}
lengthfile.close()
titilefile.close()
merge()
tindex=open("tindex.txt",'w+')
cindex=open("cindex.txt",'w+')
tthread=writeParallel(tindex,invit)
cthread=writeParallel(cindex,invic)
tthread.start()
cthread.start()
tthread.join()
cthread.join()
#for key in sorted(invit):
#    tindex.write(key+' '+invit[key]+'\n')
#tindex.close()

#for key in sorted(invic):
#    cindex.write(key+' '+invic[key]+'\n')
elapsed_time = time.time() - start_time
print("Total pages: {:,}".format(totalCount))
print("Elapsed time: {}".format(hms_string(elapsed_time)))
