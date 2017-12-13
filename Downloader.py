import urllib.request
import time
import datetime
import re
import socket
import random
from DiskCache import DiskCache

DEFAULT_AGENT = "wswp"
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60

class Downloader:
    '''
    用于下载html的类,可以传入的参数有
    proxies;代理ip列表,会随机的在列表中抽取代理ip进行下载
    delay:下载同一域名的等待时间,默认一秒
    user_agent:主机名,默认python
    num_retries:下载失败重新下载次数
    timeout;下载超时时间
    cache:缓存方式
    '''
    def __init__(self,proxies=None,delay = DEFAULT_DELAY,user_agent = DEFAULT_AGENT,num_retries = DEFAULT_RETRIES,timeout = DEFAULT_TIMEOUT,opener = None,cache=None):
        #设置超时时间
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.opener = opener
        self.cache = cache

    def   __call__(self,url):
        '''
        带有缓存功能的下载方法,通过类对象可以直接调用
        '''
        print(self.user_agent)
        print("开始下载"+url)
        result = None
        if self.cache:
            try:
                #从缓存中获取url对应的数据
                result = self.cache[url]
                print("测试代码4")
            except KeyError:
                #如果获得KeyError异常,跳过
                pass
            else:
                #如果是未成功下载的网页,重新下载
                if result["code"]:
                    if self.num_retries > 0 and 500<result["code"]<600:
                        result = None
        # 如果页面不存在,下载该页面
        if result is None:
            #延迟默时间
            self.throttle.wait(url)
            if self.proxies:
                #如果有代理IP,从代理IP列表中随机抽取一个代理IP
                proxy = random.choice(self.proxies)
            else:
                proxy = None
            #构造请求头
            headers = {"User-agent":self.user_agent}
            #下载页面
            result = self.download(url,headers,proxy = proxy,num_retries = self.num_retries)
            '''
            file = open("f:\\bilibili.html","wb")
            file.write(result["html"])
            file.close()
        '''
            if self.cache:
                #如果有缓存方式,缓存网页
                self.cache[url] = result
        print(url,"页面下载完成")
        return result["html"]


    def download(self,url,headers,proxy,num_retries,data=None):
        '''
        用于下载一个页面,返回页面和与之对应的状态码
        '''
        #构建请求
        request = urllib.request.Request(url,data,headers or {})
        request.add_header("Cookie","finger=7360d3c2; UM_distinctid=15c59703db998-0f42b4b61afaa1-5393662-100200-15c59703dbcc1d; pgv_pvi=653650944; fts=1496149148; sid=bgsv74pg; buvid3=56812A21-4322-4C70-BF18-E6D646EA78694004infoc; CNZZDATA2724999=cnzz_eid%3D214248390-1496147515-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1496805293")
        request.add_header("Upgrade-Insecure-Requests","1")
        opener = self.opener or urllib.request.build_opener()
        if proxy:
            #如果有代理IP,使用代理IP
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy))
        try:
            #下载网页
            response = opener.open(request)
            print("code是",response.code)
            html = response.read().decode()
            code = response.code
        except Exception as e:
            print("下载出现错误",str(e))
            html = ''
            if hasattr(e,"code"):
                code =e.code
                if num_retries > 0 and 500<code<600:
                    #如果错误不是未找到网页,则重新下载num_retries次
                    return self.download(url,headers,proxy,num_retries-1,data)
            else:
                code = None
        print(html)
        return {"html":html,"code":code}


class Throttle:
    '''
    按照延时,请求,代理IP等下载网页,处理网页中的link的类
    '''

    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        '''
        每下载一个html之间暂停的时间

        '''
        # 获得域名
        domain = urllib.parse.urlparse(url).netloc
        # 获得上次访问此域名的时间
        las_accessed = self.domains.get(domain)

        if self.delay > 0 and las_accessed is not None:
            # 计算需要强制暂停的时间 = 要求的间隔时间 - (现在的时间 - 上次访问的时间)
            sleep_secs = self.delay - (datetime.datetime.now() - las_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        # 存储此次访问域名的时间
        self.domains[domain] = datetime.datetime.now()
