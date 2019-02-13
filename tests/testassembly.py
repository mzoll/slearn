"""
Created on Feb 4, 2018

@author: marcel.zoll
"""

import unittest

import pandas as pd
from slearn.sklearnext.assembly import Pipeline, TransformerPipe, FeatureUnion, ColumnsAll, ColumnsSelect
from sklearnext.sklearn.estimators.dummy import DummyClassifier
from sklearnext.transformers.sequence_vector import SequenceVectorCheckboxes
from sklearnext.estimators.wrappers import SKLEstimatorExtender


class Test(unittest.TestCase):

    def testDictPredict(self):
        dummy = SKLEstimatorExtender( DummyClassifier([1]) )
        
        X= pd.DataFrame( {'A': [0,1], 'B': [0,1], 'Vec': [['a'],[]]} )
        y= pd.Series( [1,1] )

        main_pipe = Pipeline([
            ('all', ColumnsAll()),
            ('fu', FeatureUnion([
                ('tb', TransformerPipe([
                    ('cs', ColumnsSelect('Vec')),
                    ('checkbox', SequenceVectorCheckboxes(['a','b','c'], default_name='d'))
                ])),
                ('ca', ColumnsSelect(['A','B']))
            ])),
            ('dummy', dummy),                
        ])
        
        main_pipe.fit(X, y)
        
        d = {'A': 0, 'B': 1, 'Vec':['a','e']}
        
        print("predict", main_pipe.predict_dict(d))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDictPredict']
    unittest.main()
