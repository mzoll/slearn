'''
Created on Jan 31, 2018

@author: marcel.zoll
'''

import unittest

import datetime as dt

from common_tools.localcache.managed import ManagedCache_Master
from realtimemachine.classes import State

class Test(unittest.TestCase):
    def testStateCache(self):
        cache = ManagedCache_Master()
        cache.setup()
        
        routingkey= 1
        uid = 111
        targetid = 'ABC'
        
        #make some fake state
        s0 = State(uid, targetid, dt.datetime.now)
        s0.data['now__abc'] = 42
        s0.meta['test']= 'val00'

        cache.insert(routingkey, targetid, s0)
        sx = cache.fetch(routingkey, targetid)
        
        #check that s0 and s0_x are identical
        assert(sx.uid == sx.uid)
        
        #make a new slightly altered state that overwrites the previous one
        s1 = s0.copy()
        s1.uid = 222
        
        cache.insert(routingkey, targetid, s1)
        sx = cache.fetch(routingkey, targetid)
        
        #check that s1_x as an altered state
        assert(sx.uid == s1.uid)
        
        cache.teardown()
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

