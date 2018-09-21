'''
Created on Oct 2, 2017

@author: marcel.zoll

Definitions for StateBuilders
'''

from tslearn.classes import State 

class StateBuilder():
    """ A Builder class specifying how a certain aspect of the _state_ is incrementally constructed from previous (stale) state and
    newly provided input in the _incident_

    Parameters
    ----------
    name : str
        a name to the StateBuilder; NOTE this name will be used when specifying dependencies
    dep : list of str
        a list of names of StateBuilders this StateBuilder is dependency
    inkeys : list if str
        list of fully qualified names of keys which are input to this stateBuilder, ie 'myInKey'
    outkeys : list of str   
        list of fully qualified names of keys which are output to this stateBuilder, ie 'now__myOutKey'
    """
    def __init__(self,
            name = '',
            dep = [],
            inkeys = [],
            outkeys = []):
        self.name = name
        self.dep = dep
        self.inkeys = inkeys
        self.outkeys = outkeys
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        """ to be overwritten: convolute an _oldState_ with info from an _incident_ to augment a _newState_
        
        Parameters
        ----------
        incident : dict
            new current input
        oldState : State object
            an old stale state
        newState : State object
            a new partially updated state that to be further updated
        newSession : bool
            flag if this is the start of a new session
        reset : bool
            flag if this is an inital construction of a state
        """
        raise NotImplementedError()


#=== Mixin's
# use this to signal on what condition a StateBuilder needs to be called; every derived StateBuilder should implement
# one of the following Mixings. This will be heavily used in the actuall StateBuiding process, where it leviates unneccessary
# double computations
class EveryMixin():
    ''' Mixin for StateBuilders are to be executed all the time '''
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        raise NotImplementedError()

class SessionMixin():
    ''' Mixin for StateBuilders which are to be executed only at the start of each session '''
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        if newSession:
            raise NotImplementedError()

class OnceMixin():
    ''' Mixin for StateBuilders which are to be executed only once at initial encounter'''
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        if reset:
            raise NotImplementedError()
