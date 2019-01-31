'''
Created on Jul 11, 2018

@author: marcel.zoll
'''

import numpy as np

from tslearn.sklearnext.assembly import Pipeline, FeatureUnion
from tslearn.prime_building.transport import StateBuilderTransPort
from tslearn.sklearnext.transport import PrimeBuilderTransPort
from sklearnext.estimators.wrappers import SKLEstimatorExtender

from tslearn.sklearnext.wrappers import SklearnextScorer

from sklearnext.sklearn.estimators.dummy import DummyClassifier
from tslearn.state_building.dummy import DummyStateBuilder

from tslearn.model.model import ScoreModel
from tslearn.model.utils import extractUniquePrimeBuilders, extractUniqueStateBuilders


class DummyModel(ScoreModel):
    """ A dummy model for testing of stuff """
    def __init__(self, name, modelid, score_name):
        ScoreModel.__init__(self, name, modelid)
        
        mydummy_0 = DummyClassifier(np.array([0,1]))
        main_pipe_0 = Pipeline([
            ('fu', FeatureUnion([
                ('sessionRefExtr', PrimeBuilderTransPort([StateBuilderTransPort([ DummyStateBuilder() ])] ))
            ])),
            ('cc0', SKLEstimatorExtender( mydummy_0 ))])
        
        self.scorer = SklearnextScorer(main_pipe_0, [score_name])
        
        self.primeBuilders = extractUniquePrimeBuilders(self.scorer.getPrimeBuilders())
        self.stateBuilders = extractUniqueStateBuilders(self.primeBuilders)
        