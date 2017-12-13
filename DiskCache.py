import pickle
import os
import re
import urllib.parse

class DiskCache:
    def __init__(self,cache_dir = "cache"):
        self.cache_dir = cache_dir
        self.max_length = 25
    def url_to_path(self,url):
        #将url分割,获取相对路径
        components = urllib.parse.urlsplit(url)
        path = components.path

        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        # 将非字符替换成_
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        # 限制文件长度在25以内
        filename = '/'.join(segment[:25] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)
    def __getitem__(self, url):
        """使用url从文件中反序列化
        """
        path = self.url_to_path(url)
        if os.path.exists(path):
            #如果存在文件,返回内容
            with open(path, 'rb') as fp:
                return pickle.load(fp)
        else:
            # 如果不存在,抛出异常
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """序列化文件
        """
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        data = pickle.dumps((result))

        with open(path, 'wb') as fp:
            fp.write(data)