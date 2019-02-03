"""
Created on Jun 8, 2018

@author: marcel.zoll
"""

from ..state_building.utils import extractUniqueStateBuilders
from sklearnext.feature_dict.facility import FeatureTransformFacility

class FeatureTransformFacility(FeatureTransformFacility):
    def getStateBuilders(self):
        return extractUniqueStateBuilders(self.getStateBuilders())
