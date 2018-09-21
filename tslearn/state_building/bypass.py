'''
Created on Aug 1, 2018

@author: marcel.zoll
'''

from .classes import StateBuilder, EveryMixin

class BypassStateBuilder(StateBuilder, EveryMixin):
    """ A statebuilder that will just copy the specified keys to into the state's now portion """
    def __init__(self, name, inkey_list):
        self.name = name
        self.inkeys = inkey_list
        self.outkeys = ['now__'+ik for ik in self.inkeys]
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        for k in self.inkeys:
            newState.data.now[k] = incident.data[k]   