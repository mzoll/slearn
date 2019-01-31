"""
Created on Jul 11, 2018

@author: marcel.zoll
"""

from tslearn.model.model import ScoreModel

import pandas as pd
import datetime as dt
from tslearn.externals.common_tools.tools.sort_emit import topoSort_gen, list_of_uniques, list_of_uniquelistelements
from tslearn.classes import State, Prime, Result
from tslearn.prime_building.constructor import PrimeConstructor
from tslearn.prime_building.convoluter import PrimeConvoluter


class CompositeScoreModel(object):
    """ A composition of Models that can be applied as if they are only one big model
    
    This Model allows to have also dependent models; on each iteration the next following model can access the previously
    preduced scores by accessing them with prefixed 'score__' in the prime
    
    Parameters
    ----------
    models : list of ScoreModel
        the list of submodels that are combined in this CompountModel
    meta : dict
        meta information about the model

    Properties
    ----------
    stateBuilders : list of StateBuilders
        the list of statebuilders
    primeBuilders : list of PrimeBuilders
        the list of primeBuilders

    Examples
    --------
    m0 = Model('MyFirstSimpleModel', 0)
    m1 = Model('MySecondSimpleModel', 1)
    cm = CompositeModel('MyCompModel', 42, [m0, m1])
    """
    def __init__(self, models = [], meta):
        self.models = models
        self.meta = meta
        #------------------
        self.primeBuilders = self.getPrimeBuilders()
        self.stateBuilders = self.getStateBuilders()
    def addModel(self, model):
        """ add a new model and update the prime and statebuilder """
        self.models.append(model)
        self.primeBuilders = self.getPrimeBuilders()
        self.stateBuilders = self.getStateBuilders()
    def getPrimeBuilders(self):
        pb_list = []
        for m in self.models: 
            for pb in m.primeBuilders:
                pb_list.append(pb)
        return list_of_uniquelistelements(pb_list, lambda e: e.outkeys)
    def getStateBuilders(self):
        sbraw_list = []
        for m in self.models: 
            for sb in m.stateBuilders:
                sbraw_list.append(sb)
        topo = topoSort_gen(sbraw_list, lambda e: e.name, lambda e: e.dep)
        return list_of_uniques(topo, lambda e: e.name)
    def eval(self, state):
        """ evaluate from a single State object, resulting in a dictionary """
        prime = PrimeConstructor(self.primeBuilders)(state)
        return self.score(prime)
    def evaluate(self, X_states):
        """ evaluate from a dataframe of state variables, resulting in a dataframe of results """
        X_primes = PrimeConvoluter(self.getPrimeBuilders())(X_states)
        Y_pred = self.predict(X_primes)
        return Y_pred
    def predict(self, X_primes):
        """ evaluate from a dataframe of prime variables, resulting in a dataframe of results """
        results = []
        for m in self.models:
            result_df = m.predict(X_primes)
            results.append( result_df )
            X_primes = pd.concat([X_primes,result_df], axis=0)
        Y_pred = pd.concat(results, axis=0)
        return Y_pred
    def score(self, prime):
        """ evaluate a Prime, resulting in a Result object"""
        result_scores = {}
        for m in self.models:
            result = m.score(prime)
            result_scores.update( result.results )
            # make the scores of the previous run models available in the prime for the next model
            prime.data.update( {'score__'+s:v for s,v in result.results} )
        
        r = Result(prime.uid, prime.targetid, dt.datetime.now(), prime.routingkey, prime.meta)
        r.results = result_scores
        r.meta['TimeComputed'] = dt.datetime.now()
        return  r
    def prepare(self):
        """ this should be function, which is called before the model configuration time
        in order to prepare scorers and others """
        return self
