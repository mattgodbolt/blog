#!/usr/bin/env python

import http.server
import http.server
import os

class MbsHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = http.server.SimpleHTTPRequestHandler.translate_path(self, path)
        if not os.path.exists(p):
            for possible_ext in ("html", "css", "png", "jpeg"):
                maybe_name = p + "." + possible_ext
                if os.path.exists(maybe_name):
                    return maybe_name
        return p

if __name__ == '__main__':
    os.chdir("www")
    http.server.test(MbsHandler, http.server.HTTPServer)
