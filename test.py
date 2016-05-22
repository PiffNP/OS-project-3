#!usr/bin/env python3
import http.client
from IPython import embed

server_url = "localhost:8888"
request_url = "/kv/insert/key=k&value=El%20Ni%C3%B1o"
print(request_url)
for i in range(1):
    print("send request {}".format(i))
    conn = http.client.HTTPConnection(server_url)
    conn.request(method="POST", url=request_url)
res = conn.getresponse()
print(res.read())
