#!/usr/bin/env python

import http.server
import os


class MbsHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        """Translate request path to filesystem path, checking for files with extensions.

        Args:
            path: URL path from request

        Returns:
            Filesystem path to serve
        """
        p = http.server.SimpleHTTPRequestHandler.translate_path(self, path)
        if not os.path.exists(p):
            for possible_ext in ("html", "css", "png", "jpeg"):
                maybe_name = f"{p}.{possible_ext}"
                if os.path.exists(maybe_name):
                    return maybe_name
        return p


if __name__ == "__main__":
    os.chdir("www")
    # Run the server with port 8000
    server = http.server.HTTPServer(("", 8000), MbsHandler)
    print("Serving at http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        server.shutdown()
