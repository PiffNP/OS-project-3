#!usr/bin/env python3
import http.client
import threading
import json
import time
import sys
import os
from read_write_lock import ReadWriteLock

cfg = json.load(open('conf/settings.conf'))

server_url = cfg['primary'] + ":" + cfg['port']

keys = [str(i) for i in range(10)]
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

    def request(self, method_str, request_str, request_type=None,expect_value=None):
        def func(request):
            if request_type == 'insert':
                self.total_insert_num += 1

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

            if len(sys.argv) == 1 and sys.argv[0] == '-d':
                print("request {}".format(request_str))
            res = conn.getresponse()
            res_json = json.loads(res.read().decode('utf-8'))
            if expect_value is not None and res_json['value']!=expect_value:
                print("failed at {}!={}".format(expect_value,res_json['value']))
                self.result_flag='fail'
            # maybe we should convert the value to a unicode string before output it
            if len(sys.argv) == 1 and sys.argv[0] == '-d':
                print("{}:{}".format(request_str, res_json))

            finish = time.clock()

            if request_type != 'get' and request_type != 'insert':
                return None
            if res_json['success'] != 'true':
                return None
            if request_type == 'insert':
                self.suc_insert_num += 1
            if request_type == 'get':
                mLock = self.get_lock
                mArray = self.get_statistic
            else:
                mLock = self.insert_lock
                mArray = self.insert_statistic
            mLock.acquire_write()
            mArray.append((finish - start) * 1000)
            mLock.release_write()

        t = threading.Thread(target=func, args=(request_str,))
        t.start()

    def analysis(self):
        print('Result: {0}'.format(self.result_flag))
        print('Insertion: {0}/{1}'.format(self.suc_insert_num, self.total_insert_num))
        print(
            'Averge latency: {0:.2f}ms/{1:.2f}ms'.format(sum(self.insert_statistic) / float(len(self.insert_statistic)),
                                                         sum(self.get_statistic) / float(len(self.get_statistic))))
        self.insert_statistic.sort()
        self.get_statistic.sort()
        if len(self.insert_statistic) == 0:
            self.insert_staistic.append(0)
        if len(self.get_statistic) == 0:
            self.get_staistic.append(0)
        print('Percentile latency: {0:.2f}ms/{1:.2f}ms, {2:.2f}ms/{3:.2f}ms, {4:.2f}ms/{5:.2f}ms, {6:.2f}ms/{7:.2f}ms'
              .format(self.insert_statistic[round(len(self.insert_statistic) * 0.2)],
                      self.get_statistic[round(len(self.get_statistic) * 0.2)],
                      self.insert_statistic[round(len(self.insert_statistic) * 0.5)],
                      self.get_statistic[round(len(self.get_statistic) * 0.5)],
                      self.insert_statistic[round(len(self.insert_statistic) * 0.7)],
                      self.get_statistic[round(len(self.get_statistic) * 0.7)],
                      self.insert_statistic[round(len(self.insert_statistic) * 0.9)],
                      self.get_statistic[round(len(self.get_statistic) * 0.9)]))

    def main(self):
        # os.system("bin//start_server -p")
        # os.system("bin//start_server -b")
        time.sleep(2)
        for key in keys:
            self.request("POST", insert_url.format(key, key), 'insert')
        time.sleep(2)
        for key in keys:
            self.request("GET", query_url.format(key), 'get')
        time.sleep(2)
        for key in keys:
            self.request("POST", update_url.format(key, key + key))
        time.sleep(2)
        for key in keys:
            self.request("GET", query_url.format(key), 'get')
        time.sleep(10)

        # os.system("bin//stop_server -p")
        # os.system("bin//stop_server -b")
        # request("GET","/kvman/countkey")
        # request("GET","/kvman/dump")
    def single_key_pressure_test(self):
        time.sleep(2)
        key="test_key"
        value="init_val"
        iteration_time=1000
        self.request("POST",insert_url.format(key,value),'insert')
        for i in range(iteration_time):
            self.request("POST",update_url.format(key,str(i)),'update')
            time.sleep(0.025)
            self.request("GET",query_url.format(key),'get',expect_value=str(i))
            time.sleep(0.025)

        time.sleep(2)

a = Test()
a.single_key_pressure_test()
a.main()
a.analysis()
