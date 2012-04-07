#!/usr/bin/python

""" 
@file objectqueue.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief Implements a threading routine to execute object commands in queue
Tested on Python 2.6
Filters are user-defined functions passed into the class.  Each filter 
should return a reference to a object, or the object itself.

A default filter is provided to allow attribute, iterable (dict, list), 
and argument access from an array of [type, value].
Type has the values of "attr", "iter", "args".

For instance, to call obj.webster['lol']('add',2)(1,2,3), the item would be 
formed as: [[["attr","webster"],["iter","lol"],["args",["add",2]]],[1,2,3]]
"""

VERSION = '00.00.01'

import Queue
import daemon

def default_filter(obj, item):
  for i in item:
    type = i[0]
    value = i[1]
    if type == "attr":
      obj = getattr(obj, value)
    elif type == "iter":
      obj = obj[value]
    elif type == "args":
      obj = obj(*value)
    else:
      print 'error filtering item...'
      raise
  return obj
  
class Worker:
  def __init__(self, obj, size = 0, delay = 0, filters = [default_filter]):
    self.obj = obj
    self.delay = delay # seconds
    self.queue = Queue.Queue(size)
    self.filters = filters
    self.thread = None

  def _flush(self):
    while not self.queue.empty():
      self.queue.get(False) # do not wait
      self.queue.task_done()
    
  def put(self, item, callback):
    try:
      for filter in self.filters:
        item[0] = filter(self.obj, item[0])
      self.queue.put((item, callback), True, self.delay)
    except Queue.Full:
      print 'queue full flushing queue...'
      self._flush()
    except:
      print 'error processing item...',item
      raise
    
  def _processItem(self, item):
    try:
      if isinstance(item[1], dict):
        return item[0](** item[1])
      elif isinstance(item[1], list):
        return item[0](* item[1])
      return item[0](item[1])
    except:
      print 'could not execute command:', item
      raise
  
  def _run(self):
    try:
      item, callback = self.queue.get(True) # wait
      data = self._processItem(item)
      callback(data)
      self.queue.task_done()
    except Exception, errtxt:
      print 'error running queue item',item
      print errtxt
      callback(None)
      self.queue.task_done()
  
  def start(self):
    self.thread = daemon.Daemon(self._run)
    self.thread.start()
    
  def stop(self):
    if self.thread:
      self.thread.stop()
    self._flush()
    
def main():
  try:
    def printfn(data):
      print "result",data
    class SubObject():
      def sub(self,a,b):
        return a - b
    class TestObject():
      subObj = SubObject()
      def add(self,a,b):
        return a + b
    
    print 'started object queue...'
    qworker = Worker(TestObject(), size = 2)
    qworker.start()
    while True:
      qworker.put([[["attr","add"]],[1,2]], printfn)
      qworker.put([[["attr","subObj"],["attr","sub"]],[5,2]], printfn)
      time.sleep(3)
      
  except KeyboardInterrupt:
    print '^C received, shutting down'
    qworker.stop()
    sys.exit()
    
  except Exception, errtxt:
    print errtxt
    sys.exit(2)

if __name__ == '__main__':
  # for testing in main
  import sys, time
  main()
