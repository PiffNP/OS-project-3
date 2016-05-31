#!usr/bin/env python3
import http.client
import threading
import json
import time
from read_write_lock import ReadWriteLock
keys=[str(i) for i in range(10)]
server_url = "localhost:8888"
insert_url = "/kv/insert/key={0}&value=El%20Ni%C3%B1o{1}"
query_url = "/kv/get/?key={0}"
update_url = "/kv/update/key={0}&value={1}"
delete_url = "/kv/delete/key={0}"

class Test:
    insert_statistic = []
    insert_lock = ReadWriteLock()
    get_statistic = []
    get_lock = ReadWriteLock()
    total_insert_num = 0
    suc_insert_num = 0
    result_flag = 'success'

    def request(self, method_str, request_str, request_type = None):
        def func(request):

            start = time.clock()
        
            flag = False
            fail_num = 0
            while not flag and fail_num < 2:
                try:
                    conn = http.client.HTTPConnection(server_url)
                    conn.request(method=method_str, url=request_str)
                    flag = True
                except ConnectionRefusedError and ConnectionResetError:
                    fail_num += 1

            print("request {}".format(request_str))
            res = conn.getresponse()
            res_json = json.loads(res.read().decode('utf-8'))
            # maybe we should convert the value to a unicode string before output it
            print("{}:{}".format(request_str, res_json))
        
            finish = time.clock()
        
            if request_type != 'get' and request_type != 'insert':
                return None
            elif request_type == 'insert':
                self.total_insert_num += 1
            if res_json['success'] != 'true':
                return None
            elif request_type == 'insert':
                self.suc_insert_num += 1
            if request_type == 'get':
                mLock = self.get_lock
                mArray = self.get_statistic
            else:
                mLock = insert_lock
                mArray = insert_statistic
            mLock.acquire_write()
            mArray.append((finish - start) / 1000)
            mLock.release_write()

        t = threading.Thread(target=func, args=(request_str,))
        t.start()

    def analysisi(self):
        print('Result: {0}'.format(result_flag))
       # print('Insertion: {0}/{1}', ) 


        print(len(insert_statistic))
        print(len(get_statistic))

    def main(self):
        for key in keys:
            self.request("POST", insert_url.format(key,key), 'insert')
        time.sleep(0.1)
        for key in keys:
            self.request("GET", query_url.format(key), 'get')
        time.sleep(0.1)
        for key in keys:
            self.request("POST", update_url.format(key,key+key))
        time.sleep(0.1)
        for key in keys:
            self.request("GET", query_url.format(key), 'get')
        time.sleep(10)

        #request("GET","/kvman/countkey")
        #request("GET","/kvman/dump")

a = Test()
a.main()
