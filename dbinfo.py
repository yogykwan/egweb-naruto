# -*- coding: utf-8 -*-
#  -*-  Yogy Kwan  -*-
import urllib.request
import re
import time

global opener

def getHtml(suf):
    global opener
    pre=r'http://movie.douban.com'
    url=pre+suf
    #print(url)
    cnt=0
    while(True):
        if(++cnt>10):
            print('Fail to get '+url)
            return None
        try:
            html=opener.open(url).read()
        except TypeError:
            continue
        else:
            return html

def getData(rule,html):
    pat=re.compile(rule,re.S)
    return pat.findall(html)

def initOpen():
    global opener
    #proxy_support=urllib.request.ProxyHandler({' http' :' http://218.75.100.114:8080' })
    #proxy_support=urllib.request.ProxyHandler({' http' :' http://123.233.121.164:80' })
    #proxy_support=urllib.request.ProxyHandler({' http' :' http://63.149.98.23:80' })
    #opener=urllib.request.build_opener(proxy_support,urllib.request.HTTPHandler)
    opener=urllib.request.build_opener(urllib.request.HTTPHandler)
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept':'text/html;q=0.9,*/*;q=0.8','Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding':'gzip','Connection':'close','Referer':None}
    for item in headers: opener.addheaders=[(item,headers[item])]
    urllib.request.install_opener(opener)

def getUrl():
    global opener
    html=getHtml('')[100:].decode('utf-8','ignore')
    if(html==None): return;
    rule=r'subject/([0-9]*)'
    data=getData(rule,html)
    url=list(set(data))
    url.sort(key=data.index)
    return url

def getDetail(file,url):
    rule=r'<div class="pl2">[^.]*<a href="[a-z:/\._0-9]*" class="">([\(\)\._\w ]*)[^0]*([^d]*)'
    html=html=getHtml(url)[100:].decode('utf-8','ignore')
    if(html==None): return;
    data=getData(rule,html)
    for i in data:
        star=getData(r'star([0-9])',i[1])
        if(star): file.write(i[0]+'：'+star[0]+'星\r\n')
        #else: file.write(i[0]+'：未评级\r\n') #如不需未评级注释该句
          
def getId(url,tot=-1):
    file=open(r'douban.txt','w+',encoding='utf-8')
    if(tot==-1 or tot>len(url)): tot=len(url)
    for i in range(tot):
        html=getHtml(r'/subject/'+url[i]+r'/collections')[100:].decode('utf-8','ignore')
        if(html==None): continue;
        title=getData(r'34;([^&]*)',html)[0]
        cloud=getData(r'([0-9]*)人参与评价',html)[0]
        bigstar=getData(r'bigstar([0-9]*)',html)[0]
        rating=getData(r'rating_num">([0-9.]*)',html)[0]
        print(str(i+1)+'. '+title+'\r\n'+cloud+'人参与评价，'+bigstar[0]+'.'+bigstar[1]+'星级，均分'+rating+'\r\n')
        file.write(str(i+1)+'. '+title+'\r\n'+cloud+'人参与评价，'+bigstar[0]+'.'+bigstar[1]+'星级，均分'+rating+'\r\n')
        for begin in range(2): #需要的评价数量*20
            getDetail(file,r'/subject/'+url[i]+r'/collections?start='+str(begin*20))
        file.write('\r\n')
        time.sleep(3) #暂停时间，如抓取较少电影可不暂停（本机测试可连续爬40）
        
initOpen()
url=getUrl()
getId(url,3) #第二个参量为首页要抓的电影数量，默认-1表示所有
