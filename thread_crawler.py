import time
import threading
import re
import urllib.parse
import datetime


from bs4 import BeautifulSoup
from Downloader import Downloader
from MongoCache import MongoCache

SLEEP_TIME = 1

def get_links(html):
    '''
    获得一个页面上的所有链接
    '''
    bs = BeautifulSoup(html, "lxml")
    link_labels = bs.find_all("a")
    # for link in link_labels:
    return [link_label.get('href', "default") for link_label in link_labels]

def same_domain(url1, url2):
    '''
    判断域名书否相同
    '''
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc

def normalize(seed_url, link):
    '''
    用于将绝对路径转换为相对路径
    '''
    link, no_need = urllib.parse.urldefrag(link)

    return urllib.parse.urljoin(seed_url, link)

def threader_crawler(seed_url,resource_regiex=None,link_regiex = ".*",delay=5,cache=None,download_source_callback=None,user_agent="wswp",proxies=None, num_retries=1, max_threads=10, timeout=60,max_url=500):


    downloaded = []

    crawl_queue = [seed_url]

    seen = set([seed_url])

    D = Downloader(cache = cache,delay = delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,timeout=timeout)
    print(user_agent)
    def process_queue():
        while True:

            links = []
            try:
                url = crawl_queue.pop()
            except IndexError:
                break
            else:
                html = D(url)
                downloaded.append(url)

                if download_source_callback:
                    if resource_regiex and re.match(resource_regiex,url):
                        download_source_callback(url,html)
                links.extend([link for link in get_links(html) if re.match(link_regiex,link)])
                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen.add(link)

                        if same_domain(seed_url,link):
                            crawl_queue.append(link)
                print("已经发现的总网页数目为",len(seen))
                print("已经下载过的网页数目为",len(downloaded))
                print("还没有遍历过的网页数目为",len(crawl_queue))
    threads=[]
    while threads or crawl_queue:
        if len(downloaded) == max_url:
            return
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            print("线程数量为", len(threads))
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            print("线程数量为", len(threads))
            threads.append(thread)

def main():
    starttime = datetime.datetime.now()
    threader_crawler("http://www.bilibili.com/",max_threads=1,max_url=10,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    endtime = datetime.datetime.now()
    print("花费时间",(endtime-starttime).total_seconds())
if __name__ == "__main__":
    main()

