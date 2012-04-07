r"""

@file fi/__init__.py 
@author Charles 'Chuck' Cheung <chuck@cc-labs.net>
@brief A simple, fast, lightweight webGUI JSON-RPC framework for class function calls.
Tested on Python 2.6
"""
__version__ = '0.1'
__all__ = [
    'ObjectServer', 'JSONReader'
]

from objectserver import ObjectServer
from jsonreader import JSONReader