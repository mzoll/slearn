'''
Created on Jun 8, 2018

@author: marcel.zoll
'''

from ..prime_building.utils import extractUniquePrimeBuilders, extractUniqueStateBuilders

from sklearnext.feature_dict.facility import FeatureTransformFacility

class FeatureTransformFacility(FeatureTransformFacility):
    def getPrimeBuilders(self):
        pb_list = [p for t in self.pipeline_dict.values() for p in t.getPrimeBuilders()]
        return extractUniquePrimeBuilders(pb_list)
    def getStateBuilders(self):
        return extractUniqueStateBuilders(self.getPrimeBuilders())
