#!usr/bin/env python3
import http.client
import threading
import time
keys=[str(i) for i in range(200)]
server_url = "localhost:8888"
insert_url = "/kv/insert/key={0}&value=xx{1}"
query_url = "/kv/get/?key={0}"
update_url = "/kv/update/key={0}&value={1}"
delete_url = "/kv/delete/key={0}"


def request(method_str, request_str):
    def func(request):
        conn = http.client.HTTPConnection(server_url)
        conn.request(method=method_str, url=request_str)
        #print("request {}".format(request_str))
        res = conn.getresponse()
        # maybe we should convert the value to a unicode string before output it
        print("{}:{}".format(request_str, res.read()))

    t = threading.Thread(target=func, args=(request_str,))
    t.start()


def main():
    for key in keys:
        request("POST", insert_url.format(key,key))
    time.sleep(1)
    for key in keys:
        request("GET", query_url.format(key))
    time.sleep(1)
    for key in keys:
        request("POST", update_url.format(key,key+key))
    time.sleep(1)
    for key in keys:
        request("GET", query_url.format(key))
    time.sleep(5)
    request("GET","/kvman/countkey")
    request("GET","/kvman/dump")
if __name__ == '__main__':
    main()
