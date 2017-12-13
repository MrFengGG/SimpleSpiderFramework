from datetime import datetime,timedelta
from pymongo import MongoClient,errors

class MongoQueue:
    '''
    用Mongo写的队列,一个url有三种状态,OUTSTANDING表示还未处理,PROCESSING表示正在下载,COMPLETE表示下载过的url
    '''
    OUTSTANDING,PROCESSING,COMPLETE = range(3)

    def __init__(self,client = None,timeout=300):
        if client is None:
            self.client = MongoClient("localhost",12345)
        else:
            self.client = client
        self.db = self.client.cache
        self.timeout = timeout

    def __nonzero__(self):
        '''
        特殊方法,将队列转化为bool值时调用
        '''
        #查询在队列中status的值不为COMPLETE的值,即可以被处理的url $ne在mongodb中表示!=
        record = self.db.reawl_queue.find_one(
            {"status":{"$ne":self.COMPLETE}}
        )
        if record:
            return True
        else:
            return False

    def push(self,url):
        '''
        向队列中加入一个url
        '''
        try:
            self.db.crawl_queue.insert({"_id":url,"status":self.OUTSTANDING})
            print('加入一个url',url,"目前一共有",self.len_of_downloaded()[0],"等待被下载")
        except:
            pass

    def pop(self):
        '''
        从队列中取出一个url,如果成功取出,将url的状态改为正在处理
        '''
        record = self.db.crawl_queue.find_and_modify(
            #此操作用于查询获得一个未处理的url
            query={"status":self.OUTSTANDING,},
            #此操作用于将查询到的url状态置为PROCESSING,并且记录当前的时间戳
            update={"$set":{"status":self.PROCESSING,"timestamp": datetime.now()}}
        )
        if record:
            print("拿出一个url目前一共有", self.len_of_downloaded()[1], "已经被下载")
            return record["_id"]
        else:
            print("数据库中目前还没有可以下载的url")
            self.repair()
            raise KeyError()

    def complete(self,url):
        '''
        将一个url的状态置为处理完毕
        '''
        self.db.crawl_queue.update({"_id":url},{"$set":{"status":self.COMPLETE}})
    def repair(self):
        '''
        将处理超时的url置重新置为OUTSTANDING未处理
        '''
        #查询处理超时的url,并且讲状态置为OUTSTANDING
        record = self.db.crawl_queue.find_and_modify(
            query={
                "timestamp":{"$lt":datetime.now()-timedelta(self.timeout)},
                "status": {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.OUTSTANDING}}
        )
    def clear(self):
        '''
        清空队列 
        '''
        self.db.crawl_queue.drop()
    def len_of_downloaded(self):
        '''
        返回队列中各种状态的url的长度
        '''
        no_download = [ele for ele in self.db.crawl_queue.find({"status":self.OUTSTANDING})]
        is_download = [ele for ele in self.db.crawl_queue.find({"status":self.COMPLETE})]
        is_processing = [ele for ele in self.db.crawl_queue.find({"status":self.PROCESSING})]
        return len(no_download),len(is_download),len(is_processing)
