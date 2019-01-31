'''
Created on Jan 7, 2018

@author: marcel.zoll

Models can be in dependency, specified by their name; customer Id is a must match (not neccessaryly implicit checked)
'''

import pandas as pd
import datetime as dt
from realtimemachine.classes import State, Prime, Result
from realtimemachine.model.scorer import Scorer
from realtimemachine.prime_building.constructor import PrimeConstructor
from realtimemachine.prime_building.convoluter import PrimeConvoluter


class ScoreModel(object):
    """ rather shallow collection that wraps around a scoring function making it into a model
    
    Parameters
    ----------
    scorer : Scorer object
        A scorer needs to support some basic functionality like `predict` and `score`
    meta : dict
        meta information about the model


    Properties
    ----------
    stateBuilders : list of StateBuilders
        the list of statebuilders
    primeBuilders : list of PrimeBuilders
        the list of primeBuilders
    """

    def __init__(self, scorer, meta):
        """ configure with minimal information """
        self.scorer = scorer
        self.stateBuilders = None
        self.primeBuilders = None
        # ------------------
        self.meta = meta

    def getPrimeBuilders(self):
        return self.primeBuilders

    def getStateBuilders(self):
        return self.stateBuilders

    def prepare(self):
        """ this should be function, which is called before the model configuration time
        in order to prepare scorers and others """
        return self

    def eval(self, state):
        """ evaluate from a single State object, resulting in a dictionary """
        # DEPRECATED
        prime = PrimeConstructor(self.primeBuilders)(state)
        return self.score(prime)

    def evaluate(self, X_states):
        """ evaluate from a dataframe of state variables, resulting in a dataframe of results """
        # DEPRECATED
        X_primes = PrimeConvoluter(self.primeBuilders())(X_states)
        Y_pred = self.predict(X_primes)
        return Y_pred

    def predict(self, X_primes):
        """ evaluate from a dataframe of prime variables, resulting in a dataframe of results """
        Y_pred = self.scorer.predict(X_primes)
        return Y_pred

    def score(self, prime):
        """ evaluate a single Prime object, resulting in a Result """
        results_dict = self.scorer.score(prime.data)
        r = Result(prime.uid, prime.targetid, dt.datetime.now(), prime.meta)
        r.results = results_dict
        return r
