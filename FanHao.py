#-*- coding:utf-8 -*
import urllib
import urllib2
import re 
import random
import httplib
from bs4 import BeautifulSoup

'''
import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar
ssl.wrap_socket = sslwrap(ssl.wrap_socket)
'''

enable_proxy = False

print '#'*40
print '# FanHao'
print '#'*40

proxy_select = raw_input("Do you want to configure proxy?(Y/N):")
if proxy_select == 'Y' or proxy_select == 'y':
    enable_proxy = True
else:
    enable_proxy = False

class ProxyServer:
    def __init__(self,proxy_address,proxy_http,speed,proxy_type,country):
        self.proxy_address=proxy_address
        self.proxy_http=proxy_http
        self.speed=speed
        self.proxy_type=proxy_type
        self.country=country

class FanHao:
    def __init__(self,title,file_size,downloading_count,magnet_url):
        self.title = title
        self.file_size = file_size
        self.downloading_count = downloading_count
        self.magnet_url = magnet_url

def proxy_test():
    test_headers = {'User-Agent:':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
    test_url = 'http://www.google.com'
    test_request = urllib2.Request(test_url,headers=test_headers)
    try:
        test_response = urllib2.urlopen(test_request,timeout=10)
        #print test_response.getcode()
        if test_response.getcode()==200:
            print u'Configured proxy successfully!'
            global proxy_configured 
            proxy_configured = True
    except Exception:
        print u'Failed to configure proxy!'
    
def find_highest_speed(proxy_list):
    temp_proxy = None
    highest_speed = 0
    for proxy_server in proxy_list:
        proxy_server_speed = proxy_server.speed.split('kbit')[0]
        print 'proxy_server.proxy_address = %s'%proxy_server.proxy_address
        print 'proxy_server.speed = %skbit/s'%proxy_server_speed
        if proxy_server_speed !='-':
            if float(proxy_server_speed) > highest_speed:
                highest_speed = float(proxy_server_speed)
                temp_proxy = proxy_server
    print '*'*40
    print 'Temp Proxy Address %s'%temp_proxy.proxy_address
    print 'Temp Proxy Speed %s'%temp_proxy.speed
    print '*'*40
    proxy_list.remove(temp_proxy)
    return temp_proxy,proxy_list

def get_proxy_list():
    proxy_headers = {'User-Agent:':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
    proxy_url = 'http://proxy-list.org/english/index.php'
    proxy_request = urllib2.Request(proxy_url,headers=proxy_headers)

    try:
        response = urllib2.urlopen(proxy_request,timeout=10)
        html = response.read()
    except urllib2.HTTPError,e:
        print e.code

    name_ul = re.compile("(?isu)<ul>(.*?)</ul>")
    name_li = re.compile("(?isu)<li[^>]*>(.*?)</li>")

    proxy_list_txt = open('proxy_list.txt','w')
    proxy_list=[]
    
    for row in name_ul.findall(html):
        proxy_address = ''.join(name_li.findall(row)[0:1])
        proxy_http = ''.join(name_li.findall(row)[1:2])
        speed = ''.join(name_li.findall(row)[2:3])
        proxy_type = ''.join(name_li.findall(row)[3:4])
        name_country = re.compile('title="(.*?)"')
        country_name=None
        for country in name_li.findall(row)[4:5]:
            country_name = ''.join(name_country.findall(country))
            if '&nbsp;' in country_name:
                country_name=country_name.split('&nbsp;')[0]+' '+country_name.split('&nbsp;')[1]
        
        proxy_server = ProxyServer(proxy_address,proxy_http,speed,proxy_type,country_name)
        proxy_list.append(proxy_server)
        proxy_list_txt.write(proxy_server.proxy_address+'\n')
        
    proxy_list_txt.close()
    
    return proxy_list

def proxy_setting(proxy_list):
    random_proxy,new_proxy_list = find_highest_speed(proxy_list)
    proxy_handler = urllib2.ProxyHandler({'http':'http://%s'%random_proxy.proxy_address})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    return random_proxy,new_proxy_list

if enable_proxy == True:
    proxy_list = get_proxy_list()
    proxy_configured = False
    while not proxy_configured:
        current_proxy,proxy_list = proxy_setting(proxy_list)
        proxy_test()
    print 'Current Proxy Address %s'%current_proxy.proxy_address
    print 'Current Proxy Location %s'%current_proxy.country

fanhao = raw_input("请输入想要查找的番号:")

proxy_headers = {'User-Agent:':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
fanhao_url = 'http://www.cili.tv/search/'+fanhao+'_ctime_1.html'

fanhao_request = urllib2.Request(fanhao_url)
fanhao_response = urllib2.urlopen(fanhao_request)
fanhao_html = fanhao_response.read()
#print fanhao_html

#for fanhao in name_fanhao.findall(fanhao_html):
#    print fanhao

soup = BeautifulSoup(fanhao_html)
soup_items = soup.find_all("div",attrs={"class":"item"})

if soup_items:
    fanhaos = []
    for item in soup_items:
        title = item.a.text.strip()
        info = item.find("div",attrs={"class":"info"}) 
        spans = info.find_all("span")
        file_size = str(spans[1].b.text)
        downloading_count = str(spans[2].b.string)
        magnet_url = str(spans[3].find("a").get('href'))
        fanhao = FanHao(title,file_size,downloading_count,magnet_url)
        fanhaos.append(fanhao)
    
    for fanhao in fanhaos:
        print u'名称:'+fanhao.title
        print u'文件大小:'+fanhao.file_size
        print u'热度:'+fanhao.downloading_count
        print u'磁力链接:'+fanhao.magnet_url
        print '-'*40


else:
    print u'抱歉未找到相关资源！'
