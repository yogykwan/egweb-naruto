# -*- coding: utf-8 -*-
import urllib.request
import re

def getHtml(url):
    page=urllib.request.urlopen(url)
    html=page.read()
    #open('temp.txt','wb+').write(html)
    return html

def getTxt(html,con=0):
    pattern=re.compile(b'<div id="post_content_.*?class="d_post_content j_d_post_content ">(.*?)</div>')
    txtlist=re.findall(pattern,html)
    cnt=1
    for item in txtlist:
        item=item.decode('gbk')
        item=item.replace('<br>','\n')
        item=item.replace('                                        ','')
        print('%s章 -'%str(con),'%s楼\n'%str(cnt),'%s\n'%item)
        cnt=cnt+1
  
print('开始逛\n') 
url='http://tieba.baidu.com/p/1677652007?see_lz=1'
html=getHtml(url)
getTxt(html)
print('看完走人')
    
