"""
Created on Aug 28, 2018

@author: marcel.zoll
"""

import pandas as pd
import datetime as dt

from realtimemachine.model.model import ScoreModel
from realtimemachine.classes import Result


class BypassScorerModel(ScoreModel):
    """ A blank bypass Model, which is inert except for optionally holding and executing statebuilders.
    There will only be a zero output for the specified scorename. This construct might be usefull when constructing states for the purpose 
    of priming caches and stores or just to check the correct setup of other realtimemachine infrastructure components.
    
    Parameters
    ----------
    score_name : str
        a name to the output score which is always zero
    
    Attributes
    ----------
    stateBuilders : list of StateBuilders
    """

    def __init__(self, score_name):
        ScoreModel.__init__(score_name, -1)
        self._score_name = score_name
        self._stateBuilders = []

    def getPrimeBuilders(self):
        return []

    def getStateBuilders(self):
        return self._stateBuilders

    def prepare(self):
        return self

    def predict(self, X_primes):
        """ evaluate from a dataframe of prime variables, resulting in a dataframe of results """
        Y_pred = pd.DataFrame(0., index=X_primes.index, columns=[self.scorer_name])
        return Y_pred

    def score(self, prime):
        """ evaluate a single Prime object, resulting in a Result """
        r = Result(prime.uid, prime.targetid, dt.datetime.now(), prime.meta)
        r.results = {}
        return r
