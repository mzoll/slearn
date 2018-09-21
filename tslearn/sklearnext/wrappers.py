'''
Created on Jan 22, 2018

@author: marcel.zoll
'''
import pandas as pd
import datetime as dt

from realtimemachine.classes import Prime, Result

from realtimemachine.model.scorer import Scorer
from realtimemachine.model.model import ScoreModel

from realtimemachine.model.utils import extractUniquePrimeBuilders, extractUniqueStateBuilders


class SklearnextScorer(Scorer, object):
    """ take a sklearnext predictor (a pipeline) and provide the score function, returning a result
    
    Parameters
    ----------
    predictor : object
        A class that supports `fit`, `predict` and `predict_dict`
    scorename : str
        A name to the outcome score
    """
    def __init__(self, sklext_predictor, scorenames):
        self.predictor = sklext_predictor
        self.scorenames = scorenames
    def getPrimeBuilders(self):
        return extractUniquePrimeBuilders(self.predictor.getPrimeBuilders())
    def getStateBuilders(self):
        return extractUniqueStateBuilders(self.getPrimeBuilders())
    def fit(self, X_primes, y_outcomes, **fit_params):
        self.predictor.fit(X_primes, y_outcomes, **fit_params)
    def predict(self, X_primes):
        y_pred = self.predictor.predict(X_primes)
        #NOTE at this place we convert the Series into a Dataframe
        return pd.DataFrame(y_pred, columns=self.scorenames)
    def score(self, prime_data):
        results = self.predictor.predict_dict(prime_data)
        return dict(zip(self.scorenames, results))
        

class SklearnextModel(ScoreModel, object):
    """ a quasi-wrapper for sklearn-models to become a ScoreModel """
    def __init__(self,
                name,
                modelid,
                sklext_scorer):
        ScoreModel.__init__(self, name, modelid)
        self.scorer = sklext_scorer
        
        self.primeBuilders = extractUniquePrimeBuilders(self.scorer.getPrimeBuilders())
        
        self.stateBuilders = extractUniqueStateBuilders(self.primeBuilders)
        