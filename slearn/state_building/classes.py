'''
Created on Oct 2, 2017

@author: marcel.zoll

Definitions for StateBuilders
'''

from slearn.classes import State

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

    class ExecTrigger():
        """
        Defines how often a Session Trigger shoulöd be executed :
        on every tick, only on ticks which trigger a newsession, or only once
        """
        every = 0
        session = 1
        once = 2

    def __init__(self,
            name = '',
            dep = [],
            inkeys = [],
            outkeys = [],
            exec_trigger = None):
        self.name = name
        self.dep = dep
        self.inkeys = inkeys
        self.outkeys = outkeys
        if exec_trigger is None:
            self._exec_trigger = self.ExecTrigger.every
        else:
            self._exec_trigger = exec_trigger
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
