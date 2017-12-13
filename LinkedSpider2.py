import urllib.request
import urllib.parse
import urllib.error
import re
import queue
import datetime
import time
from bs4 import BeautifulSoup
from Downloader import Downloader
from download_source_callback import download_source_callback
from DiskCache import DiskCache
from MongoCache import MongoCache


def normalize(seed_url, link):
    '''
    
    用于将绝对路径转换为相对路径
    '''
    link, no_need = urllib.parse.urldefrag(link)

    return urllib.parse.urljoin(seed_url, link)


def same_domain(url1, url2):
    '''
    判断域名书否相同
    '''
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc


def get_links(html):
    '''
    获得一个页面上的所有链接
    '''
    bs = BeautifulSoup(html, "lxml")
    link_labels = bs.find_all("a")
    # for link in link_labels:
    return [link_label.get('href', "default") for link_label in link_labels]

def link_crawler(seed_url,link_regex=".*",resource_regex = ".*",delay=5,max_depth=-1,max_urls=-1,headers=None,user_agent="wswp",proxies=None,num_retries=1,download_source_callback=None,cache = None,data = None):
    '''
    
    '''
    #用于存储未被下载的页面
    craw_queue = [seed_url]
    #用于存储已经下载过的页面
    seen = [seed_url]
    #下载过的url数量
    num_urls = 0
    isdow = []
    downloader = Downloader(delay=delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,cache=cache)

    while craw_queue:
        url = craw_queue.pop()
        #depth = seen[]
        html = downloader(url)
        print(html)
        links = []
        isdow.append(url)
        seen.append(url)
        if download_source_callback and re.match(resource_regex,url):
            #如果是资源页面,下载页面上的所有资源
            print("属于资源,开始下载")
            download_source_callback(url,html)

        #if depth != max_depth:
        links.extend([link for link in get_links(html) if re.search(link_regex,link)])
        for link in links:
            link = normalize(seed_url,link)
            if link not in seen:
                seen.append(link)
                if same_domain(seed_url,link):
                    craw_queue.append(link)
                    print(link + "符合要求加入队列,现在队列的长度是"+str(len(craw_queue)))
                    #craw_queue.append(link)
                    #print(link + "符合要求加入队列,现在队列的长度是" + str(len(craw_queue)))
                    print("当前可怕去的url数量胃"+str(len(craw_queue)))
                    print("已经发现的总url数量为",str(len(set(seen))))
                    print("已经下载过的url数量为",str(len(isdow)))
        num_urls += 1
        if num_urls == max_urls:
            break
    print(seed_url+"上所有符合要求的网站下载完毕,一共遍历了"+str(len(seen))+"个网页")

if __name__ == "__main__":
    link_crawler("http://www.bilibili.com",cache =MongoCache
())






