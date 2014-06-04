import SimpleHTTPServer
import BaseHTTPServer
import os

class MbsHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, path)
        if not os.path.exists(p):
            for possible_ext in ("html", "css", "png", "jpeg"):
                maybe_name = p + "." + possible_ext
                if os.path.exists(maybe_name):
                    return maybe_name
        return p

if __name__ == '__main__':
    os.chdir("htdocs")
    BaseHTTPServer.test(MbsHandler, BaseHTTPServer.HTTPServer)
