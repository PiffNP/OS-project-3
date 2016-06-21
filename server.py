#!usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib
import json
import time
import http.client
import sys
import os
from database import Database
cfg = json.load(open('conf/settings.conf'))

database = Database()

backup_server_url = cfg['backup'] + ":" + cfg['port']


def load_database():
    conn = http.client.HTTPConnection(backup_server_url)
    try:
        conn.request(method="GET", url="/bak_kv/serialize")
    except (ConnectionRefusedError, ConnectionResetError):
        print("backup server not found")
        return
    res = conn.getresponse()
    res = json.loads(res.read().decode('utf-8'))
    database.load(res['data'])
    print("recover complete")


load_database()


def inform_backup(method_str, request_str):
    conn = http.client.HTTPConnection(backup_server_url)
    try:
        conn.request(method=method_str, url=request_str, headers={"Time": str(time.time())})
    except ConnectionRefusedError and ConnectionResetError:
        print("backup server not found")
        return None, False
    res = conn.getresponse()
    res = json.loads(res.read().decode('utf-8'))
    # print('from backup server: {}'.format(res))
    success = False
    if 'success' in res:
        success = res['success']
    return res, success


class ProjectHTTPRequestHandler(BaseHTTPRequestHandler):
    METHODS = {'insert', 'delete', 'get', 'update', 'serialize', 'countkey', 'dump', 'shutdown'}
    BOOL_MAP = {True: 'true', False: 'false'}

    @staticmethod
    def parse_input(input_str):
        if input_str is None:
            return dict()
        ret = dict()
        inputs = input_str.split('&')
        for input in inputs:
            key, value = input.split('=')
            value = urllib.parse.unquote(value, encoding='utf-8', errors='replace')
            ret[key] = value
        return ret

    @staticmethod
    def gen_output(output_dict):
        if isinstance(output_dict, dict):
            for k, v in output_dict.items():
                if v in ProjectHTTPRequestHandler.BOOL_MAP:
                    output_dict[k] = ProjectHTTPRequestHandler.BOOL_MAP[v]
        ret = json.dumps(output_dict)
        # print("output:{}".format(ret))
        return ret

    def countkey_request(self, ins):
        assert (self.command == "GET"), "wrong HTTP method"
        keycount = database.countkey()
        outs = {'result': str(keycount)}
        return outs

    def dump_request(self, ins):
        assert (self.command == "GET"), "wrong HTTP method"
        outs = database.dump()
        return outs

    def shutdown_request(self, ins):
        os.system('bin/stop_server -p')

    def serialize_request(self, ins):
        # we need to verify it is the backup server that calls us
        assert (self.command == "GET"), "wrong HTTP method"
        data_str = database.serialize()
        outs = {'data': data_str}
        return outs

    def insert_request(self, ins):
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 2 and 'key' in ins and 'value' in ins), 'wrong input'
        key, value = ins['key'], ins['value']
        quote_value = urllib.parse.quote(value, safe='/', encoding='utf-8', errors=None)
        success = database.insert(key, value, inform_backup,
                                  ('POST', '/bak_kv/insert/key={}&value={}'.format(key, quote_value)))
        outs = {'success': success}
        return outs

    def delete_request(self, ins):
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 1 and 'key' in ins), 'wrong input'
        key = ins['key']
        value = None
        value = database.delete(key, inform_backup, ('POST', '/bak_kv/delete/key={}'.format(key)))
        if value:
            outs = {'success': True, 'value': value}
        else:
            outs = {'success': False, 'value': ""}
        return outs

    def get_request(self, ins):
        assert (self.command == "GET"), 'wrong HTTP method'
        assert (len(ins) == 1 and '?key' in ins), 'wrong input'
        key = ins['?key']
        value = database.get(key, inform_backup,
                             ('GET', '/bak_kv/get/?key={}'.format(key)))
        if value:
            outs = {'success': True, 'value': value}
        else:
            outs = {'success': False, 'value': ""}
        return outs

    def update_request(self, ins):
        assert (self.command == "POST"), 'wrong HTTP method'
        assert (len(ins) == 2 and 'key' in ins and 'value' in ins), 'wrong input'
        key, value = ins['key'], ins['value']
        quote_value = urllib.parse.quote(value, safe='/', encoding='utf-8', errors=None)
        success = database.update(key, value, inform_backup,
                                  ('POST', '/bak_kv/update/key={}&value={}'.format(key, quote_value)))
        outs = {'success': success}
        return outs

    def do_GET(self):
	    if "?" in self.path:
			self.path=self.path.replace("?","/?",1)
        self.handle_request()

    def do_POST(self):
        success=True
        try:
            length=int(self.headers["Content-Length"])
            input_str=self.rfile.read(length).decode("utf-8")
            self.path+="/"+input_str
        except Exception as e:
            print(e)
            success=False
        self.handle_request(success)

    def handle_request(self,success=True):
        try:
            assert(success),"POST fail"
            request = self.path.split('/')
            request = [r for r in request if r != ""]
            if len(request) == 3:
                name, request, input_str = request
            elif len(request) == 2:
                name, request = request
                input_str = None
            else:
                assert (False), 'wrong input size'
            assert (name in ('kv', 'kvman')), 'wrong name'
            assert (request in ProjectHTTPRequestHandler.METHODS), 'no such method'
            ins = self.parse_input(input_str)
            # print("receive request: {} {}".format(request, input_str))
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
        # print("end request")


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass


server = ThreadingHttpServer((cfg['primary'], int(cfg['port'])), ProjectHTTPRequestHandler)
print("Server started at {}".format(server.server_address))
server.serve_forever()
