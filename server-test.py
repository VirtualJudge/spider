from http.server import HTTPServer, BaseHTTPRequestHandler
from os import path
from urllib.parse import urlparse
from VirtualJudgeSpider.Control import Controller
from VirtualJudgeSpider.Config import Account


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        querypath = urlparse(self.path)
        if querypath.path == '/':
            with open('server.html', 'rb') as f:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f.read())
        else:
            param_list = str(querypath.path).split('/')
            param_list.remove('')
            if len(param_list) == 2:
                self.send_response(200)
                self.end_headers()
                remote_oj = param_list[0]
                remote_id = param_list[1]
                account = Account('robot4test', 'robot4test')
                problem = Controller(remote_oj).get_problem(remote_id, account)
                if problem:
                    self.wfile.write(bytes(problem.html, encoding='utf-8'))
                else:
                    self.send_response(404)
            else:
                self.send_response(404)


def run():
    port = 8000
    print('starting server, port', port)

    # Server settings
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print('running server: http://localhost:8000 ...')
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run()
    except:
        print('bye bye')
