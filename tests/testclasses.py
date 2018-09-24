'''
Created on Jan 25, 2018

@author: marcel.zoll
'''
import unittest

from tslearn.classes import State
from tslearn.classes import Incident
from tslearn.classes import Prime
from tslearn.classes import Result

import datetime as dt

_now = dt.datetime.now()

class Test(unittest.TestCase):
    
    def testIncident(self):
        i = Incident(123, 'AAAA', _now, 'rkey',
                    meta = {'CustomerId': 99, 'WeblogId': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now})
        i.data = {'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]}

    def testState(self):
        _now = dt.datetime.now()
        s = State(123, 'AAAA', _now, 'rkey',
                    meta = {'UUID': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now})
        s.data.now = {'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]}

        sJSON = s.toJSON()
        _ = s.fromJSON(sJSON)
        
    def testPrime(self):
        p = Prime(123, 'AAAA', _now, 'rkey',
                    meta = {'CustomerId': 99, 'WeblogId': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now})
        p.data = {'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]}
    
    def testResult(self):
        r = Result(123, 'AAAA', _now, 'rkey',
                    meta = {'CustomerId': 99, 'WeblogId': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now})
        r.data = {'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]}

    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRequest']
    unittest.main()