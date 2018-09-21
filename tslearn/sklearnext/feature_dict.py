'''
Created on Jun 8, 2018

@author: marcel.zoll
'''

from common_tools.tools.sort_emit import topoSort_gen, list_of_uniques, list_of_uniquelistelements

from sklearnext.feature_dict.facility import FeatureTransformFacility

class FeatureTransformFacility(FeatureTransformFacility):
    def getPrimeBuilders(self):
        pb_list = [p for t in self.pipeline_dict.values() for p in t.getPrimeBuilders()]
        return list_of_uniquelistelements(pb_list, lambda e: e.outkeys)
    def getStateBuilders(self):
        sb_list = [sb for pb in self.getPrimeBuilders() for sb in pb.getStateBuilders() ]
        return list_of_uniques(topoSort_gen(sb_list, lambda e: e.name, lambda e: e.dep), lambda e: e.name)
