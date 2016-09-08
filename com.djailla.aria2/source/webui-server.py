#!/usr/bin/python

import web
import os
import sys
import urllib
import posixpath
import json


RAINBOW_PATH = os.getenv("RAINBOW_WEB_PATH").rstrip('/')

urls = (
    "/", "root_index",
    RAINBOW_PATH, "root_index",
    RAINBOW_PATH+"/", "root_index",
    RAINBOW_PATH+"/webui", "root_index",
    #"/aria2(.*)", "root_redirect",
    #"/webui", "root_index",
    "/favicon.ico", "favicon",
    "/rpc/(.*)", "rpc",
    RAINBOW_PATH+"/rpc/(.*)", "rpc"
)


app = web.application(urls, globals())


class root_index:
    def GET(self):
        raise web.redirect(RAINBOW_PATH+"/webui/")


class favicon:
    def GET(self):
        raise web.redirect(RAINBOW_PATH+"/webui/favicon.ico")


class rpc:
    SHARE_BASE = '/shares'

    def get_shares(self):
        shares_list = []
        if os.path.exists(self.SHARE_BASE):
            for name in os.listdir(self.SHARE_BASE):
                dir_path = os.path.join(self.SHARE_BASE, name)
                if os.path.isdir(dir_path):
                    shares_list.append(dir_path)
        shares_list.sort()

        return json.dumps(shares_list)

    def GET(self, name):
        get_output = ''
        if (name == 'get_shares'):
            web.header('Content-Type', 'application/json')
            get_output = self.get_shares()
        else:
            get_output = "Invalid RPC call"

        return get_output


class StaticMiddleware:
    """WSGI middleware for serving static files."""
    def __init__(self, app, prefix=RAINBOW_PATH+'/webui/', root_path='/webui/'):
        self.app = app
        self.prefix = prefix
        self.root_path = root_path

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        path = self.normpath(path)

        if path.startswith(self.prefix):
            environ["PATH_INFO"] = os.path.join(self.root_path, web.lstrips(path, self.prefix))
            return web.httpserver.StaticApp(environ, start_response)
        else:
            return self.app(environ, start_response)

    def normpath(self, path):
        path2 = posixpath.normpath(urllib.unquote(path))
        if path.endswith("/"):
            path2 += "/"
        return path2


if __name__ == "__main__":
    SERVER_PORT = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        SERVER_PORT = int(sys.argv[1])
    wsgifunc = app.wsgifunc()
    wsgifunc = StaticMiddleware(wsgifunc)
    #wsgifunc = web.httpserver.LogMiddleware(wsgifunc)
    server = web.httpserver.WSGIServer(("0.0.0.0", SERVER_PORT), wsgifunc)
    #print "http://%s:%d/" % ("0.0.0.0", SERVER_PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
