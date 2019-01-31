"""
Created on Jul 11, 2018

@author: marcel.zoll
"""

import pandas as pd
from tslearn.state_building.classes import StateBuilder
from tslearn.prime_building.classes import PrimeBuilder


class Scorer(object):
    """
    Non mandatory proto-class to be used in ScorerModel::scorer that implements the following interface
    """

    def score(self, prime_data):
        """ absolutly essential: prime_data a dictionary of proto-features"""
        raise NotImplementedError("Overwrite derived function __::score !")
        return {'<result_name>': '<result_value>'}

    def getPrimeBuilders(self):
        """ optional to implement, but neccessary if PrimeBuilders nested """
        raise NotImplementedError("Overwrite derived function __::getPrimeBuilders !")
        return [PrimeBuilder()]

    def getStateBuilders(self):
        """ optional to implement, but neccessary if StateBuilders nested """
        raise NotImplementedError("Overwrite derived function __::getStateBuilders !")
        return [StateBuilder()]

    def fit(self, X_primes, y_outcomes, **fit_params):
        """ optional to implement, but mandatory if underlying object should be trainable """
        raise NotImplementedError("(optional) Overwrite derived function __::fit !")
        return self

    def predict(self, X_primes):
        """ optional to implement, but mandatory if underlying object should be verifiable """
        raise NotImplementedError("Overwrite derived function __::predict !")
        return pd.DataFrame()  # shape [n,1] with index as as X_primes
