'''
Created on Jan 25, 2018

@author: marcel.zoll
'''
import unittest
import uuid

from slearn.classes import State, Incident

import datetime as dt

_now = dt.datetime.now()

class Test(unittest.TestCase):
    
    def testIncident(self):
        i = Incident(
            uid=uuid.uuid4(), targetid=uuid.uuid4(), timestamp=_now,
            meta={'CustomerId': 99, 'WeblogId': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now},
            data={'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]})

    def testState(self):
        s = State(123, 'AAAA', _now, 'rkey',
                    meta = {'UUID': 1234, 'UserKey': "AAAA", 'SessionKey': "BBBB", 'LogTime': _now})
        s.data.now = {'Key0': 0, 'LogTime': _now, 'TimeVec': [_now, _now]}

        sJSON = s.toJSON()
        _ = s.fromJSON(sJSON)
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRequest']
    unittest.main()