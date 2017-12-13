import time
import urllib.parse
import threading
import multiprocessing
import re
import lxml
import datetime

from MongoCache import MongoCache
from MongoQueue import MongoQueue
from Downloader import Downloader
from bs4 import BeautifulSoup
from download_source_callback import download_source_callback

class spider:
    def __init__(self,Downloader=None,Resource_Downloader=None,cache=None,link_regies=None,resource_regiex=None,user_agent="wswp"):

