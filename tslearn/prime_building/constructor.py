'''
Created on Sep 25, 2017

@author: marcel.zoll
'''

import datetime as dt

from realtimemachine.classes import State, Prime
from tslearn import PrimeBuilder
from tslearn import StateBuilderTransPort

import logging
logger = logging.getLogger('PrimeConstructor')

class PrimeConstructor():
    ''' caller class that convolutes a State to a Prime and is smart about it
    
    Parameters
    ----------
    primeBuilder_list : list of PrimeBuilder
        the PrimeBuilder list; will be parted up into convolutional and identity primebuilders for accellerated processing
    '''
    def __init__(self,
            primeBuilder_list):
        self.primeBuilder_list = primeBuilder_list
        #--- split the pb up into dummies and convolutionary ones ;
        #--- this step can be in principle omitted as generalization by call structure exists
        #--- but provides a considerable speedup, because of shallower call structure
        self.dummyPB = []
        self.convPB = []
        for pb in self.primeBuilder_list:
            if isinstance(pb, (StateBuilderTransPort)):
                self.dummyPB.append(pb)
            else:
                if len(pb.outkeys) > 1:
                    logger.debug("Outkeys of primeBuilder '%s' has more than 1 outkey" % (str(pb)))
                self.convPB.append(pb)
        self.direct_keys = [ok for pb in self.dummyPB for ok in pb.outkeys]
    def __call__(self, state):
        prime = Prime(state.uid, state.targetid, dt.datetime.now(), state.routingkey, state.meta)
        for pb in self.convPB: #invoce the convoluting primeBuilders       
            pb(state, prime)
        for dk in self.direct_keys: #place the direct keys
            prime.data[dk] = state.data[dk]
        return prime
    
