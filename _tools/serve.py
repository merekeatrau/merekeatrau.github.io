#!/usr/bin/env python3
"""Local preview that behaves like GitHub Pages: /other serves other.html,
and video byte ranges work (seeking). Run from anywhere:
    python3 _tools/serve.py        → http://localhost:8766
"""
import http.server
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        # like GitHub Pages: /other serves other.html
        base, _, query = self.path.partition('?')
        p = self.translate_path(base)
        if not os.path.exists(p) and os.path.exists(p + '.html'):
            self.path = base + '.html' + ('?' + query if query else '')
        rng = self.headers.get('Range')
        path = self.translate_path(self.path)
        if not rng or os.path.isdir(path) or not os.path.exists(path):
            return super().send_head()
        m = re.match(r'bytes=(\d*)-(\d*)', rng)
        size = os.path.getsize(path)
        start = int(m.group(1) or 0)
        end = min(int(m.group(2) or size - 1), size - 1)
        f = open(path, 'rb')
        f.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, src, dst):
        rem = getattr(self, '_remaining', None)
        if rem is None:
            return super().copyfile(src, dst)
        while rem > 0:
            buf = src.read(min(65536, rem))
            if not buf:
                break
            dst.write(buf)
            rem -= len(buf)
        self._remaining = None


http.server.ThreadingHTTPServer(('', 8766), Handler).serve_forever()
