#!usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from IPython import embed
import urllib
import io, shutil
import json
import time
import threading
import sys
from database import Database

cfg = json.load(open('settings.conf'))

database = Database()


class ProjectHTTPRequestHandler(BaseHTTPRequestHandler):
    METHODS = {'insert', 'delete', 'get', 'update'}
    BOOL_MAP = {True: 'true', False: 'false'}

    @staticmethod
    def parse_input(input_str):
        ret = dict()
        inputs = input_str.split('&')
        for input in inputs:
            key, value = input.split('=')
            value = urllib.parse.unquote(value, encoding='utf-8', errors='replace')
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
        global database
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 2 and 'key' in ins and 'value' in ins), 'wrong input'
        key, value = ins['key'], ins['value']
        # works done here
        success = database.insert(key, value)
        outs = {'success': success}
        return outs

    def delete_request(self, ins):
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 1 and 'key' in ins), 'wrong input'
        key = ins['key']
        # works done here
        value = database.delete(key)
        if value:
            outs = {'success': True, 'value': value}
        else:
            outs = {'success': False, 'value': ""}
        return outs

    def get_request(self, ins):
        assert (self.command == "GET"), 'wrong HTTP method'
        assert (len(ins) == 1 and '?key' in ins), 'wrong input'
        key = ins['?key']
        # works done here
        value = database.get(key)
        if value:
            outs = {'success': True, 'value': value}
        else:
            outs = {'success': False, 'value': ""}
        return outs

    def update_request(self, ins):
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 2 and 'key' in ins and 'value' in ins), 'wrong input'
        key, value = ins['key'], ins['value']
        # works done here
        success = database.update(key, value)
        outs = {'success': success}
        return outs

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        try:
            request = self.path.split('/')
            request = [r for r in request if r != ""]
            assert (len(request) == 3)
            name, request, input_str = request
            assert (name == 'kv'), 'wrong name'
            assert (request in ProjectHTTPRequestHandler.METHODS), 'no such method'
            ins = self.parse_input(input_str)
            print("receive request: {} {}".format(request, input_str))
            out_dict = getattr(self, request + "_request")(ins)
            out_str = self.gen_output(out_dict)
        except Exception as e:
            print("exception {}".format(e))
            out_dict = {'success': False, 'debug_info': str(e)}
            out_str = self.gen_output(out_dict)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(out_str.encode(encoding="utf_8"))
        print("end request")


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass


server = ThreadingHttpServer((cfg['primary'], int(cfg['port'])), ProjectHTTPRequestHandler)
print("Server started at {}".format(server.server_address))
server.serve_forever()
