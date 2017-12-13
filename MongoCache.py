import pickle
import zlib
from datetime import datetime,timedelta
from pymongo import MongoClient
from bson.binary import Binary

class MongoCache:
    def __init__(self,client = None,expires = timedelta(days=30)):
        #如果没有传递MongoClient对象,创建一个默认对象
        if client is None:
            self.client = MongoClient("localhost",12345)
        #创建一个连接想数据库中缓存数据
        self.db = self.client.cache
        self.db.webpage.create_index("timestamp",expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        '''
        从数据库中获得该url的值
        '''
        record = self.db.webpage.find_one({"_id":url})
        print(record)
        if record:
            return pickle.loads(zlib.decompress(record["result"]))
            #return record["result"]
        else:
            raise KeyError(url+"不存在")
    def __setitem__(self, url,result):
        '''
        将数据储存到数据库中
        '''
        record = {"result":Binary(zlib.compress(pickle.dumps(result))),
                  "timestamp":datetime.utcnow()}
        #record = {"result":result,"timestamp":datetime.utcnow()}
        self.db.webpage.update({"_id":url},{"$set":record},upsert=True)
        


