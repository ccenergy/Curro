#!/usr/bin/python

""" 
@file daemon.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief Implements a threading.py Module wrapper for an infinite loop
Tested on Python 2.6
"""

import threading

class Daemon (threading.Thread):
  def __init__(self, function, args = ()):
    threading.Thread.__init__(self)
    self.function = function
    self.args = args
    self.loop = True
    self.daemon = True
  def run(self):
    while self.loop:
      self.function(* self.args)
  def stop(self):
    self.loop = False

def createLock ():
  return threading.RLock()
