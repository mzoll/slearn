'''
Created on Aug 2, 2018

@author: marcel.zoll
'''

from realtimemachine.classes import Prime, State
from realtimemachine.prime_building.classes import PrimeBuilder
from realtimemachine.state_building.bypass import BypassStateBuilder

class BypassPrimeBuilder(PrimeBuilder):
    """ Bypass the PrimeBuilding process in combination with the BypassStateBuilder.
    
    All specified varibales will effectively be plain copied from the Incident::data into the Prime::data
     """
    def __init__(self, name, inkey_list):
        self.name = name
        self.sb_list = [ BypassStateBuilder(name+'_StateBuilder', inkey_list) ]
        self.inkeys = ['now__'+k for k in inkey_list]
        self.outkeys = inkey_list
    def _inner_conv(self, *vars):
        return vars
