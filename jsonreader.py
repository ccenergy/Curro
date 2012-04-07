#!/usr/bin/python

""" 
@file jsonreader.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief This file implements a simple argument and configuration validator.
Tested on Python 2.6
"""

VERSION = '00.00.01'

# Third-Party modules
try: import simplejson as json
except ImportError: import json

""" instantiate command-line arguments as class objects """
class JSONReader:
  def __init__(self,path=None, **keywords):
    self.data = keywords
    self.data.update(self._fileLoad(path))
	  
  def _fileLoad(self, path):
    try:
      if not path:
        return {}
      # retrieve file data
      f = open(path, 'rU')
      data = json.loads(f.read())
      f.close()
      return data
    except Exception, err:
      raise Exception("File " + path + " error: " + str(err))
    
  def fileSave(self, path):
    # store file data in json file
    f = open(path, 'w')
    f.write(json.dumps(self.data))
    f.close()

def main():
  dirpath = os.path.relpath("test")
  configpath = os.path.join(dirpath,"config.json")
  testpath = os.path.join(dirpath,"test.json")
  args = JSONReader(configpath,test_bool=True,test_int=0,test_str="hello world")
  print
  print "Test loading data from 'config.json' with dict merge..."
  
  print
  print args.data
  print
  
  print "Test 'fileSave' to 'test.json'..."
  args.fileSave(testpath)
  
  f = open(testpath,'r')
  print
  print f.read()
  print
  f.close()
  
  print "Cleaning up..."
  os.remove(testpath)

if __name__ == '__main__':
  import os
  main()
