'''
Created on Nov 3, 2017

@author: marcel.zoll

Extends the classes sklearn::assembly to support the interface getPrimeBuilders() also in nested calls
'''

import numpy as np
from sklearnext import assembly

#=================
# ColumnsSelect
#=================
class ColumnsAll(assembly.ColumnsAll):
    def getPrimeBuilders(self):
        return []

class ColumnsSelect(assembly.ColumnsSelect):
    def __init__(self, feature_names):
        assembly.ColumnsSelect.__init__(self, feature_names)
    def getPrimeBuilders(self):
        return []

#=================
# FeatureUnion
#=================
class FeatureUnion(assembly.FeatureUnion):
    def getPrimeBuilders(self):
        sb_set = set()
        for t in self.transformer_list:
            sb_set.update(t[1].getPrimeBuilders())
        return list(sb_set)
    
#=================
# Pipeline
#=================
class Pipeline(assembly.Pipeline):
    def getPrimeBuilders(self):
        return self.steps[0][1].getPrimeBuilders()
    def get_feature_importances(self):
        imps = self.steps[-1][1].feature_importances_
        if len(self.steps) >= 2:
            fnames = self.steps[-2][1].get_feature_names()
        else:
            fnames = np.repeat( None, len(imps))
        return list(zip( fnames, imps ))


class TransformerPipe(assembly.TransformerPipe):
    def getPrimeBuilders(self):
        return self.steps[0][1].getPrimeBuilders()


class FeatureSelectPipeline(assembly.FeatureSelectPipeline):
    def getPrimeBuilders_null(self):
        return self.feature_union_null.getPrimeBuilders()
    def getPrimeBuilders_apt(self):
        return self.feature_union_apt.getPrimeBuilders()
    def getPrimeBuilders(self):
        if hasattr(self, 'feature_union_apt'):
            return self.getPrimeBuilders_apt()
        else:
            return self.getPrimeBuilders_null()
        return self.feature_union_apt.getPrimeBuilders()
    
#==========================
# Forks
#==========================
class CategoryFork(assembly.CategoryFork):
    def getPrimeBuilders(self):
        return self.pipeline.steps[0][1].getPrimeBuilders()
        
class SplitterFork(assembly.SplitterFork):
    def getPrimeBuilders(self):
        sb0 = self.cat_trans.getPrimeBuilders()
        sb1 = self.pre_trans.getPrimeBuilders()
        sb2 = self.sub_pipe.getPrimeBuilders()
        return set(sb0) | set(sb1) | set(sb2)
    