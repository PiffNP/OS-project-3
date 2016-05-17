#!usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from IPython import embed
import io, shutil
import json


class ProjectHTTPRequestHandler(BaseHTTPRequestHandler):
    METHODS = {'insert', 'delete', 'get', 'update'}
    BOOL_MAP = {True: 'true', False: 'false'}

    @staticmethod
    def parse_input(input_str):
        ret = dict()
        inputs = input_str.split('&')
        for input in inputs:
            key, value = input.split('=')
            ret[key] = value
        return ret

    @staticmethod
    def gen_output(output_dict):
        for k, v in output_dict.items():
            if v in ProjectHTTPRequestHandler.BOOL_MAP:
                output_dict[k] = ProjectHTTPRequestHandler.BOOL_MAP[v]
        ret = json.dumps(output_dict)
        print("output:{}".format(ret))
        return ret

    def insert_request(self, ins):
        assert (self.command == "POST")
        key, value = ins['key'], ins['value']
        print("insert with key={} value={}".format(key, value))
        # works done here
        outs = {'sucess': True}
        return outs

    def delete_request(self, ins):
        assert (self.command == "POST")
        key = ins['key']
        print("delete with key={}".format(key))
        # works done here
        outs = {'sucess': True, 'value': "deleted_val"}
        return outs

    def get_request(self, ins):
        assert (self.command == "GET")
        key = ins['key']
        print("get with key={}".format(key))
        # works done here
        outs = {'sucess': True, 'value': "get_val"}
        return outs

    def update_request(self, ins):
        assert (self.command == "POST")
        key, value = ins['key'], ins['value']
        print("update with key={} value={}".format(key, value))
        # works done here
        outs = {'sucess': True}
        return outs

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        request = self.path.split('/')
        request = [r for r in request if r != ""]
        assert (len(request) == 3)
        name, request, input_str = request
        assert (name == 'kv'), 'name error'
        assert (request in ProjectHTTPRequestHandler.METHODS), 'method error'
        ins = self.parse_input(input_str)
        out_dict = getattr(self, request + "_request")(ins)
        out_str = self.gen_output(out_dict)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(out_str.encode(encoding="utf_8"))


server = HTTPServer(("", 8888), ProjectHTTPRequestHandler)
print("Server started at {}".format(server.server_address))
server.serve_forever()
