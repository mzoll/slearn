'''
Created on Aug 28, 2018

@author: marcel.zoll
'''

import pandas as pd

from joblib import Parallel, delayed

from .classes import PrimeBuilder
from .transport import StateBuilderTransPort

import logging
logger = logging.getLogger('PrimeConvoluter')


class PrimeConvoluter():
    ''' caller class, similar to PrimeConstructor, that convolutes a dataframe of State-variables to a dataframe of Prime-variables
    
    Parameters
    ----------
    primeBuilder_list : list of PrimeBuilder
        the PrimeBuilder list; will be parted up into convolutional and identity primebuilders for accellerated processing
    n_jobs : int
        number of parallel executed tasks
    '''
    def __init__(self,
            primeBuilder_list,
            n_jobs = 1):
        self.primeBuilder_list = primeBuilder_list
        self.n_jobs= n_jobs
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
    def __call__(self, states_df):
        results = Parallel(n_jobs=self.n_jobs)(
            delayed(_convolute_one_primeBuilder)(pb, states_df) 
            for pb in self.convPB)
        results.append( states_df[self.direct_keys] )
        primes_df = pd.concat(results, axis=1)
        return primes_df


def _convolute_one_primeBuilder(pb, states_df):
    logger.info('Convoluting {}'.format(pb.name))
    return pb.dfapply(states_df)
    