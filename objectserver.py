#!/usr/bin/python

""" 
@file objectserver.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief Implements the object server
Tested on Python 2.6
"""

from jsonreader import JSONReader
from objectqueue import Worker
from webserver import Server, Handler

class ObjectServer:
  def __init__(self, paths, objects, debug=False):
    self.paths = paths
    self.data = JSONReader(self.paths['configpath']).data
    self.objects = objects
    self.workers = {}
    self.debug = debug
    
  def start(self):
    for name,obj in self.objects.items():
      worker = Worker(obj,self.data['queue']['size'])
      worker.start()
      self.workers[name] = worker
    self.Server = Server(('',self.data['web']['port']), Handler)
    self.Server.set_args(self.workers,debug=self.debug,**self.paths)
    self.Server.serve_forever()
  
  def stop(self):
    self.Server.socket.close()
    for name,worker in self.workers.items():
      worker.stop()
    
""" runs the objectserver """
def main():
  try:
    dirpath = path.relpath(path.join("test","webserver"))
    paths = {
      "configpath" : path.join("test","config.json"),
      "dbpath"     : path.join("test","data.db"),
      "pagespath"  : path.join(dirpath,"pages"),
      "staticpath" : path.join(dirpath,"static")
    }
    class MathObject():
      def add(self,a,b):
        return a + b
      def sub(self,a,b):
        return a - b
    class StrObject():
      def helloworld(self):
        return "hello world!"
    mo = MathObject()
    so = StrObject()
    objects = {
      "math" : mo,
      "str"  : so
    }
    
    server = ObjectServer(paths, objects, debug=True)
    print 'started on http://localhost:' + \
      str(server.data['web']['port']) + '...'
    server.start()

  except KeyboardInterrupt:
    print '^C received, shutting down server'
    server.stop()

if __name__ == '__main__':
  from os import path
  main()