import threading
import time

def print_time(threadname,delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count+=1
        print("%s:%s"%(threadname,"11"))

threading._start_new_thread(print_time,("thread-1",2,))
threading._start_new_thread(print_time,("thread-2",5,))
while 1:
    pass
