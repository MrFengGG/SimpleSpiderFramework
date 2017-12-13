from lxml import etree
from pymongo import MongoClient
import urllib.request
import re

class download_source_callback:
    def __init__(self,client=None):
        if client:
            self.client = client
        else:
            self.client = MongoClient("localhost",12345)
        self.db = self.client.cache


    def __call__(self,url,html):
        title_regiex = "<title>(.*?)</title>"
        class_regiex = "类　　别(.*?)<"
        director_regiex = ".*导　　演(.*?)<"
        content_regiex = "简　　介(.*?)<br /><br />◎"
        imdb_regiex = "IMDb评分&nbsp;(.*?)<"
        douban_regiex = "豆瓣评分(.*?)<"
        html = html.decode("gbk","ignore")
        m = re.search(title_regiex,html)
        if m:
            title = m.group(1)
        else:
            title = None
        m = re.search(class_regiex,html)
        if m:
            class_name = m.group(1)
        else:
            class_name = None
        m = re.search(content_regiex,html)
        if m:
            text = m.group(1).replace("<br />","")
            content = text
        else:
            content = None
        m = re.search(douban_regiex,html)
        if m:
            douban = m.group(1)
        else:
            douban = None
        m = re.search(imdb_regiex,html)
        if m:
            imdb = m.group(1)
        else:
            imdb = None
        print(title,class_name,content,douban,imdb)
        move = {
            "name":title,
            "class":class_name,
            "introduce":content,
            "douban":douban,
            "imdb":imdb
        }
        self.db.moves.update({"_id":title},{"$set":move},upsert=True)
        print("成功储存一部电影"+title)



if __name__ == "__main__":
    html= open("f:\资源.txt").read()

    a = download_source_callback()
    a("http://www.dytt8.net/html/gndy/jddy/20170529/54099.html",html)

