"""
Created on Jul 11, 2018

@author: marcel.zoll
"""

from tslearn.prime_building.classes import PrimeBuilder


class ModelScoreTransPort(PrimeBuilder, object):
    """ provide a PrimeBuilder in charge for transporting scores, which are the result from another model.
    This will implicitly make a scorer dependent on another model.
    This class should be used when building composite-models with interdependecies """

    def __init__(self, modelname, score_list):
        self.modelname = modelname
        # ---
        self.sb_list = []
        self.inkeys = score_list
        self.outkeys = score_list
        self.name = '_'.join(['DUMMY'] + self.inkeys)

    def __call__(self, state, prime):
        for ik in self.inkeys:
            prime.data[ik] = state.data.get(ik)

    def _inner_conv(self, *invars):
        return invars
