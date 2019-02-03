'''
Created on Mar 23, 2018

@author: marcel.zoll
'''

from ..State_building.classes import StateBuilder
from sklearn.base import TransformerMixin

class StateBuilderTransPort(TransformerMixin, object):
    """ select all columns which are produced by these StateBuilders
    
    Parameters
    ----------
    pb_list : list ob StateBuilder obj
        transport and expose these StateBuilders
    """
    def __init__(self, sb_list):
        self.sb_list = sb_list
        self.feature_names = []
        for sb in sb_list:
            assert( isintance(sb, StateBuilder) )
            self.feature_names.extend(sb.outkeys)
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X):
        return X[self.feature_names]
    def getStateBuilders(self):
        return self.pb_list    
    def get_feature_names(self):
        return self.feature_names
    def transform_dict(self, d):
        #pick and choose
        return { k:d[k] for k in self.feature_names }
        