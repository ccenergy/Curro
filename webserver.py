#!/usr/bin/python

""" 
@file webserver.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief This webserver implements a simple lightweight JSON-RPC for queue object calls.
Tested on Python 2.6
"""

VERSION = '00.00.01'

import cgi, os, time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import sqlite3

# Third-Party modules
#try: import simplejson as json
#except ImportError: import json
import json

#HACK DUE TO 2.6.6 BUG WHERE UNICODE DICTS CANNOT BE PASSED AS ARGS
#BEGIN HACK {
def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
           key = key.encode('utf-8')
        if isinstance(value, unicode):
           value = value.encode('utf-8')
        elif isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv
#} END HACK

""" json-rpc """
class Result(dict):
  def json(self):
    keys = ['data','error','id']
    map(self.setdefault,keys)
    return json.dumps(dict( (k,v) for k,v in self.items() if k in keys ))
      
""" webserver request handler """
class Handler(BaseHTTPRequestHandler):

  BINARY_EXT = ['jpg','png','pdf']

  CONTENT_TYPES = {
    'js'  : 'text/javascript',
    'css' : 'text/css',
    'jpg' : 'image/jpg',
    'gif' : 'image/gif',
    'png' : 'image/png',
    'pdf' : 'application/pdf',
    'mp3' : 'audio/mpeg',
    'html' : 'text/html'
  }
 
  def handle_response(self, data):
    if self.server.debug: print data
    if (data):
      self.render_json(Result(data=data,id=self.req['id']).json())
    else:
      self.render_json(Result(error=True,id=self.req['id']).json())
    self.response = True

  """ write file to http response """
  def render_file(self, filename):
    try:
      extension = filename.split('.')[-1]
      mode = 'r'
      if extension in self.BINARY_EXT:
        mode = 'rb'
      f = open(filename,  mode) # not secure
      self.send_response(200)
      self.send_header('Content-type',self.CONTENT_TYPES[extension])
      self.send_header('charset','utf-8')
      self.end_headers()
      self.wfile.write(f.read())
      f.close()
    except Exception, errtxt:
      print 'Render_file error:',errtxt

  """ write json to http response """
  def render_json(self, jsonData):
    try:
      if self.server.debug: print jsonData
      self.send_response(200)
      self.send_header('Content-type','application/json')
      self.end_headers()
      self.wfile.write(jsonData)
    except Exception, errtxt:
      print 'Server response error:',errtxt

  """ handle GET requests """
  def do_GET(self):
    #path = os.path.basename(self.path)
    path = self.path
    if path[0] == "/":
      path = path[1:]
    try:
      if path.endswith(".html"):
        self.render_file(os.path.join(self.server.pagespath,path))
      elif any(map(path.endswith,[".js",".css",".png",".jpg",".gif",".pdf",".mp3"])):
        self.render_file(os.path.join(self.server.staticpath,path))
      else:
        self.render_file(os.path.join(self.server.pagespath,"index.html"))
    except IOError:
      self.send_error(404,'File Not Found: %s' % path)

  """ handle post (json-rpc) requests """
  def do_POST(self):
    try:
      ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
      if ctype == 'application/json':
        length = self.headers.getheader('content-length')
        req = json.loads(self.rfile.read(int(length)), object_hook=_decode_dict)
        self.req = req
        self.response = False
        self.server.workers[req['object']].put([req['method'],req['params']], self.handle_response)
        while not self.response:
          pass
      else:
        print 'Ctype error: header is not application/json'
        raise
    except Exception, errtxt:
      print 'JSON-RPC error :',errtxt
      self.render_json(Result(error=True,id=req['id']).json())
    except:
      print 'JSON-RPC error'
      self.render_json(Result(error=True).json())

  def address_string(self):
    host, port = self.client_address[:2]
    return host

  def log_request(self, code=None, size=None):
    if self.server.debug: print 'http[' + str(code) + ']'

  # speeds up EXTREMELY SLOW FQDN lookup on WIN32 systems
  def log_message(self, format, *args):
    if self.server.debug: print 'from[' + str(format) + ']'

class Server(HTTPServer):
  def set_args(self, workers, debug=False, **kwargs):
    self.workers = workers
    self.debug = debug
    keys = ["dbpath","pagespath","staticpath"]
    for k,v in kwargs.items():
      if k in keys:
        setattr(self,k,v)
    
""" runs the webserver """
def main():
  try:
    dirpath = os.path.relpath(os.path.join("test","webserver"))
    paths = {
      "dbpath" : os.path.join("test","data.db"),
      "pagespath" : os.path.join(dirpath,"pages"),
      "staticpath" : os.path.join(dirpath,"static"),
    }
    class Worker():
      def _filter(self,arr):
        obj = None
        for i in arr:
          if i[0] == "attr":
            obj = getattr(self, i[1])
        return obj
      def put(self,item,callback):
        callback(self._filter(item[0])(*item[1]))
      def add(self,a,b):
        return a + b
      def sub(self,a,b):
        return a - b
      def helloworld(self):
        return "hello world!"
    wo = Worker()

    # start webserver
    server = Server(('', 8000), Handler)
    server.set_args({"math":wo,"str":wo}, debug=True, **paths)
    print 'started on http://localhost:' + str(8000) + '...'
    server.serve_forever()

  except KeyboardInterrupt:
    print '^C received, shutting down server'
    server.socket.close()

if __name__ == '__main__':
  main()

