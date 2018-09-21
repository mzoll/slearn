'''
Created on Mar 23, 2018

@author: marcel.zoll
'''

from ..prime_building.classes import PrimeBuilder
from sklearn.base import TransformerMixin

class PrimeBuilderTransPort(TransformerMixin, object):
    """ select all columns which are produced by these PrimeBuilders
    
    Parameters
    ----------
    pb_list : list ob PrimeBuilder obj
        transport and expose these PrimeBuilders
    """
    def __init__(self, pb_list):
        self.pb_list = pb_list        
        self.feature_names = []
        for pb in pb_list:
            self.feature_names.extend(pb.outkeys) 
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X):
        return X[self.feature_names]
    def getPrimeBuilders(self):
        return self.pb_list    
    def get_feature_names(self):
        return self.feature_names
    def transform_dict(self, d):
        #pick and choose
        return { k:d[k] for k in self.feature_names }
        