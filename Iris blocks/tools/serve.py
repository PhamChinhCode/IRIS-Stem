#!/usr/bin/env python3
"""Serve the stnapp web IDE locally, telling browsers to always revalidate.

`python3 -m http.server` sends no Cache-Control header, so browsers fall back to
heuristic caching and keep using an old .js, .css, .po or lesson .ubp after it has
been edited -- in a classroom, some machines get the update and some do not.
`no-cache` makes the browser ask the server every time; an unchanged file still
comes back as a cheap 304.

Usage:  python3 tools/serve.py [port]          (default port 8000)
Then:   http://localhost:8000/purejs.html
"""
import functools, http.server, os, sys

WEBAPP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'chromeApp', 'webapp')


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
handler = functools.partial(NoCacheHandler, directory=os.path.normpath(WEBAPP))
with http.server.ThreadingHTTPServer(('', port), handler) as server:
    print(f'stnapp: http://localhost:{port}/purejs.html', flush=True)
    server.serve_forever()
