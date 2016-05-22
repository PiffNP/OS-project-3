#!usr/bin/env python3
import http.client
import threading
import time

server_url = "localhost:8888"
insert_url = "/kv/insert/key=k&value=El%20Ni%C3%B1o"
query_url = "/kv/get/?key=k"
update_url = "/kv/update/key=k&value=xxx"
delete_url = "/kv/delete/key=k"


def request(method_str, request_str):
    def func(request):
        conn = http.client.HTTPConnection(server_url)
        conn.request(method=method_str, url=request_str)
        # print("request {}".format(request_str))
        res = conn.getresponse()
        print("{}:{}".format(request_str, res.read()))

    t = threading.Thread(target=func, args=(request_str,))
    t.start()


def main():
    request("POST", insert_url)
    time.sleep(0.1)
    request("GET", query_url)
    time.sleep(0.1)
    request("POST", update_url)
    time.sleep(0.1)
    request("GET", query_url)
    time.sleep(0.1)
    request("POST", delete_url)


if __name__ == '__main__':
    main()
