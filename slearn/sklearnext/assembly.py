'''
Created on Nov 3, 2017

@author: marcel.zoll

Extends the classes sklearn::assembly to support the interface getStateBuilders() also in nested calls
'''

import numpy as np
from sklearnext import assembly

#=================
# ColumnsSelect
#=================
class ColumnsAll(assembly.ColumnsAll):
    def getStateBuilders(self):
        return []
    @property
    def inkeys(self):
        return self.feature_names

class ColumnsSelect(assembly.ColumnsSelect):
    def __init__(self, feature_names):
        assembly.ColumnsSelect.__init__(self, feature_names)
    def getStateBuilders(self):
        return []
    @property
    def inkeys(self):
        return self.feature_names


#=================
# FeatureUnion
#=================
class FeatureUnion(assembly.FeatureUnion):
    def getStateBuilders(self):
        sb_set = set()
        for t in self.transformer_list:
            sb_set.update(t[1].getStateBuilders())
        return list(sb_set)
    @property
    def inkeys(self):
        inkey_set = set()
        for t in self.transformer_list:
            inkey_set.update(t[1].inkeys)
        return inkey_set


#=================
# Pipeline
#=================
class Pipeline(assembly.Pipeline):
    def getStateBuilders(self):
        return self.steps[0][1].getStateBuilders()
    def get_feature_importances(self):
        imps = self.steps[-1][1].feature_importances_
        if len(self.steps) >= 2:
            fnames = self.steps[-2][1].get_feature_names()
        else:
            fnames = np.repeat( None, len(imps))
        return list(zip( fnames, imps ))
    @property
    def inkeys(self):
        return self.steps[0][1].inkeys


class TransformerPipe(assembly.TransformerPipe):
    def getStateBuilders(self):
        return self.steps[0][1].getStateBuilders()
    @property
    def inkeys(self):
        return self.steps[0][1].inkeys


class FeatureSelectPipeline(assembly.FeatureSelectPipeline):
    def getStateBuilders_null(self):
        return self.feature_union_null.getStateBuilders()
    def getStateBuilders_apt(self):
        return self.feature_union_apt.getStateBuilders()
    def getStateBuilders(self):
        if hasattr(self, 'feature_union_apt'):
            return self.getStateBuilders_apt()
        else:
            return self.getStateBuilders_null()
        return self.feature_union_apt.getStateBuilders()
    @property
    def inkeys(self):
        raise NotImplementedError()


#==========================
# Forks
#==========================
class CategoryFork(assembly.CategoryFork):
    def getStateBuilders(self):
        return self.pipeline.steps[0][1].getStateBuilders()
    @property
    def inkeys(self):
        raise NotImplementedError()


class SplitterFork(assembly.SplitterFork):
    def getStateBuilders(self):
        sb0 = self.cat_trans.getStateBuilders()
        sb1 = self.pre_trans.getStateBuilders()
        sb2 = self.sub_pipe.getStateBuilders()
        return set(sb0) | set(sb1) | set(sb2)
    @property
    def inkeys(self):
        raise NotImplementedError()