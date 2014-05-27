# -*- coding: UTF-8 -*-
import os,socket
import urllib
import urllib.request,threading,time
import re,sys
global manhuaweb,weburl,floder,chapterbegin,currentthreadnum,threadcount
global mutex,mutex2
global opener

proxy_support=urllib.request.ProxyHandler({' http' :' http://218.75.100.114:8080' })
#proxy_support=urllib.request.ProxyHandler({' http' :' http://123.233.121.164:80' })
#proxy_support=urllib.request.ProxyHandler({' http' :' http://63.149.98.23:80' })
opener=urllib.request.build_opener(proxy_support, urllib.request.HTTPHandler)
#opener=urllib.request.build_opener();
headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
'Accept':'text/html;q=0.9,*/*;q=0.8',
'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Accept-Encoding':'gzip',
'Connection':'close',
'Referer':None
}
for item in headers:
    opener.addheaders=[(item,headers[item])]
urllib.request.install_opener(opener)

def hexc(x,y):
    if x==0:
        return '0'
    ans=''
    while (x>0):
        tmp=x%y
        x=x//y
        if tmp>9:
            ans=chr(ord('a')+tmp-10)+ans
        else:
            ans=str(tmp)+ans
    return ans

def urlparse(p,a,c,k):
    d={}
    while c:
        c-=1
        if not k[c]:
            d[hexc(c,36)]=hexc(c,36)
        else:
            d[hexc(c,36)]=k[c]
    newstr=''
    for i in range(len(p)):
        tempi=ord(p[i])
        if tempi>=ord('a') and tempi<=ord('f'):
            newstr+=d[chr(tempi)]
        elif tempi>=ord('0') and tempi<=ord('9'):
            newstr+=d[chr(tempi)]
        else:
            newstr+=chr(tempi)
    return newstr

def meispower(s):
    p=re.compile(r'(?=\}\().*',re.IGNORECASE)
    s=p.findall(s)
    #print('s=',s)
    s=s[0][:-19]
    par=s.split(',')
    par[3]=par[3][1:]
    answer=par[3].split('|')
    #print('par0=',par[0],int(par[1]),'answer=',answer)
    chapterpath=urlparse(par[0],int(par[1]),int(par[2]),answer)
    #print('chapter=',chapterpath)
    allurl=re.findall(r'imgpath=[^;]*',chapterpath)[0][10:-2]
    return allurl

def pictofile(weburl,filename,loop=3):
    #print('weburl=',weburl,'filename=',filename,'loop=',loop)
    if loop<0:
        print('Can\'t download %s'%weburl)
        return
    loop-=1
    if os.path.exists(filename):
        return
    try:
        data=opener.open(weburl).read()
        #print('Read data from',weburl)
        if len(data)<1024*2:
            print('Image is bad')
            pictofile(weburl,filename,loop)
        elif len(data)<1024*100:
            print('Please goto homepage')
            pictofile(weburl,filename,loop)
        else:
            print('Download from %s name is %s\n'%(weburl,filename))
            open('%s'%filename,'wb+').write(data)
    finally:
        pass

def downloadpic(url,loadpicdir,num):
    #print(url,'local=',loadpicdir,'num=',num,'\n')
    global currentthreadnum,mutex,mutex2
    num-=1
    try:
        mutex2.acquire()
        os.chdir(loadpicdir)
        mutex2.release()
    except:
        print("Floder %s will be create"%loadpicdir)
        try:
            if(mutex2.locked()):
                os.mkdir(loadpicdir)
                os.chdir(loadpicdir)
                mutex2.release()
            print('Create floder succeed')
        except:
             print("can't create floder %s"%loadpicdir)
             if(mutex.acquire()):
                 mutex.release()
                 quit(0)
    mymode=re.compile(r'[0-9a-z.]*\Z')
    name=mymode.findall(url)
    filename=name[0]
    pictofile(url,loadpicdir+'/'+str(num)+'-'+filename)
    mutex.acquire()
    currentthreadnum-=1
    mutex.release()

def downloadchapter(url,loadpicdir,num,begin=0):
    global manhuaweb,threadcount,currentthreadnum,mutex,opener
    webdata=opener.open(manhuaweb+url).read()
    webdata=webdata.decode('UTF-8')
    chaptername=re.findall(r'<title>[^_]*',webdata)[0][7:]
    if chaptername[-2]=='试' and chaptername[-1]=='看':
        return;
    webscrip=re.findall(r'eval.*[^<>]',webdata)[0]
    chapterurl=meispower(webscrip)
    chapterurl='http://mhimg1.ali213.net'+chapterurl
    print('Downloading Chapter',chaptername);
    for i in range(begin,num):
        try:
            while(currentthreadnum>=threadcount):
                time.sleep(5)
            mutex.acquire()
            currentthreadnum+=1
            mutex.release()
            threading.Thread(target=downloadpic,args=(r'%s%d.jpg'%(chapterurl,i),loadpicdir+chaptername,num)).start()
        except socket.error:
            #print('in rang : i=',i)
            mutex.acquire()
            i-=1
            currentthreadnum-=1
            mutex.release()
        except Exception as error:
            print(error,'break')
            print('Picture %d makes an error.'%i)
            break

if __name__=='__main__':
    chapterbegin=0
    currentthreadnum=0
    threadcount=10
    weburl='http://manhua.ali213.net/comic/2184/'
    floder='C:/Users/YogyKwan/Documents/IDLE/data/'
    manhuaweb=r'http://manhua.ali213.net'
    socket.setdefaulttimeout(60.0)
    mutex=threading.Lock()
    mutex2=threading.Lock()
    webfile=opener.open(weburl)
    webdata=webfile.read()
    open('ali.txt','wb+').write(webdata)
    webdata=webdata.decode('UTF-8')
    meshmode=re.compile(r'<div class="detail_body_right_sec_con">.*</div>')
    meshdata=meshmode.findall(webdata)[0]
    indexmode=re.compile(r'([0-9]*页)')
    indexdata=indexmode.findall(meshdata)
    #print(indexdata)
    picurlmode=re.compile(r'/comic/[0-9/]*.html')
    picurldata=picurlmode.findall(meshdata)
    chapterlength=len(picurldata)
    nummode=re.compile(r'[\d]+')
    i=chapterbegin=chapterlength-6
    while i<chapterlength:
        manhuachapter=picurldata[chapterlength-i-1]
        downloadchapter(manhuachapter,floder,int(nummode.findall(indexdata[chapterlength-i-1])[0]))
        i+=1
    print('FINISHED!!!!')












    
    
