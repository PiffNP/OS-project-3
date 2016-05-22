#!usr/bin/env python3
import http.client
from IPython import embed

server_url = "localhost:8888"
insert_url = "/kv/insert/key=k&value=El%20Ni%C3%B1o"
delete_url = "/kv/delete/key=k"
import threading


def request(request_str):

    def func(request):
        conn = http.client.HTTPConnection(server_url)
        conn.request(method="POST", url=request_str)
        print("request {}".format(request_str))
        res = conn.getresponse()
        print(res.read())
    t = threading.Thread(target=func, args=(request_str,))
    print("new thread runs")
    t.start()
for i in range(10):
    request(insert_url)
    request(delete_url)